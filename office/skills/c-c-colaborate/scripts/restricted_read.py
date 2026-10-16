"""Frozen, allowlisted MCP reader. Standard library only; never opens requested paths."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import sys

from runtime import BridgeError

TOOL = 'read_source'
SERVER = 'review_packet'
QUALIFIED_TOOL = 'mcp__review_packet__read_source'
LIMITS = {'max_requests': (1, 32), 'max_response_chars': (256, 50000),
          'max_total_chars': (256, 200000), 'max_turns': (2, 20)}


def encode(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def fingerprint(value):
    return hashlib.sha256(encode(value).encode('utf-8')).hexdigest()


def validate_config(api, root, spec):
    if 'restricted_read' not in spec:
        return
    config = spec['restricted_read']
    project = isinstance(config, dict) and config.get('mode') == 'project'
    fields = {'files', *LIMITS} | ({'mode', 'structure'} if project else set())
    if not isinstance(config, dict) or set(config) != fields:
        raise BridgeError('restricted_read requires files and all four documented limits')
    if spec['reviewers'] != ['claude']:
        raise BridgeError('Restricted reading currently supports only the Claude reviewer')
    if 'context_index' not in spec:
        raise BridgeError('Restricted reading requires an Office context index')
    entries = api.office_context.selection(api, root, spec)
    if project:
        if spec['mode'] != 'audit' or spec['base_ref'] is not None:
            raise BridgeError('Project reading requires a snapshot-only audit')
        structure = config['structure']
        api.confined(root, structure, source=True)
        if (not structure.startswith('office/') or structure not in entries
                or entries[structure]['ranges'] is not None):
            raise BridgeError('Project structure must be a complete indexed Office document')
    names = config['files']
    if (not isinstance(names, list) or not names or any(not isinstance(n, str) for n in names)
            or len(set(names)) != len(names)):
        raise BridgeError('Restricted read files must be a nonempty unique list')
    for name in names:
        api.confined(root, name, source=True)

        if (name.rsplit('/', 1)[-1].lower() in {'agents.md', 'claude.md', 'claude.local.md'}
                or name in api.GOVERNANCE or name not in entries
                or (project and (name == config['structure'] or entries[name]['role'] == 'brief'
                                 or entries[name]['ranges'] is not None))
                or (not project and entries[name]['role'] not in {'contracts', 'dependencies'})):
            raise BridgeError('Only indexed contracts/dependencies may be deferred; keep governance and targets inline')
        if project:
            from project_map import safe_source
            safe_source(root, name)
            for parent in [root, *list((root / name).parents)[:-1]]:
                if not parent.is_relative_to(root):
                    continue
                for policy in ('AGENTS.md', 'CLAUDE.md', 'CLAUDE.local.md'):
                    candidate = parent / policy
                    if candidate.is_file():
                        relative = candidate.relative_to(root).as_posix()
                        if relative not in api.GOVERNANCE and (relative not in entries
                                or entries[relative]['ranges'] is not None or relative in names):
                            raise BridgeError('Include applicable nested governance inline: ' + relative)

    for key, (lower, upper) in LIMITS.items():
        if type(config[key]) is not int or not lower <= config[key] <= upper:
            raise BridgeError('Invalid restricted read limit: ' + key)
    if config['max_response_chars'] > config['max_total_chars']:
        raise BridgeError('Per-read limit cannot exceed cumulative read limit')


def segments(source):
    if isinstance(source, str):
        return [{'start': 1, 'end': len(source.splitlines()), 'text': source}]
    return source['excerpts']


def defer(packet, config, changed):
    """Detach selected frozen content; no disk access and no mutation of original sources."""
    project = config.get('mode') == 'project'
    frozen = {}
    catalog = {}
    for name in config['files']:
        source = packet['sources'][name]
        if (name in changed and not project) or source is None:
            raise BridgeError('Changed/deleted sources must remain inline: ' + name)
        frozen[name] = source
        count = len(source.splitlines()) if isinstance(source, str) else source['line_count']
        catalog[name] = {'line_count': count, 'available_ranges': [
            [s['start'], s['end']] for s in segments(source) if s['end'] >= s['start']],
            'sha256': fingerprint(source)}
        packet['sources'][name] = {'line_count': count, 'excerpts': []}
    packet['restricted_read'] = {'tool': QUALIFIED_TOOL, 'catalog': catalog,
                                 'limits': {k: config[k] for k in LIMITS},
                                 'coverage_note': 'Available is not read. Unread ranges are NOT reviewed.'}
    packet['_restricted_bundle'] = {'sources': frozen, 'limits': {k: config[k] for k in LIMITS}}
    if project:
        packet['restricted_read'].update(mode='project', structure=config['structure'],
                                        search_tool='mcp__review_packet__search_sources')
        packet['_restricted_bundle']['mode'] = 'project'


def public_packet(packet):
    return {key: value for key, value in packet.items() if not key.startswith('_')}


def prompt_packet(packet):
    result = public_packet(packet)
    if packet.get('restricted_read', {}).get('mode') != 'project':
        return result
    # Full state remains in revision records and report validation. Avoid sending each
    # filename/hash three times just to describe deferred, unread contents.
    deferred = set(packet['restricted_read']['catalog'])
    result['sources'] = {name: source for name, source in packet['sources'].items() if name not in deferred}
    state = packet['coverage']
    result['coverage'] = {key: value for key, value in state.items()
                          if key not in {'source_hashes', 'unreviewed_changed_paths'}}
    result['coverage'].update(source_count=len(state['source_hashes']),
        source_hashes_fingerprint=fingerprint(state['source_hashes']),
        unreviewed_changed_paths_count=len(state['unreviewed_changed_paths']),
        unreviewed_changed_paths_sample=state['unreviewed_changed_paths'][:20],
        note='Complete fingerprints and outside-scope path list are retained in local snapshot records. Catalog hashes describe available content, not read coverage.')
    return result


def excerpt(bundle, name, start, end):
    if (not isinstance(name, str) or name not in bundle['sources'] or type(start) is not int
            or type(end) is not int or not 1 <= start <= end):
        raise BridgeError('Path or range is not allowlisted')
    source = bundle['sources'][name]
    # Exact dictionary lookup is the sole authority: no glob, normalization, path join or filesystem read.
    selected = []
    cursor = start
    for segment in segments(source):
        if segment['end'] < cursor:
            continue
        if segment['start'] > cursor:
            break
        stop = min(end, segment['end'])
        selected.extend(segment['text'].splitlines(keepends=True)[cursor-segment['start']:stop-segment['start']+1])
        cursor = stop + 1
        if cursor > end:
            return {'path': name, 'start': start, 'end': end, 'text': ''.join(selected),
                    'sha256': fingerprint(source)}
    raise BridgeError('Range extends outside frozen allowlisted lines')


class Reader:
    def __init__(self, bundle, audit_path):
        self.bundle = copy.deepcopy(bundle)
        self.audit_path = Path(audit_path)
        self.audit = {'bundle_hash': fingerprint(bundle), 'initialized': False,
                      'requests': 0, 'returned_chars': 0, 'events': [], 'denied': 0}
        # A reconnect must not reset the budget. Fail closed instead of starting another reader.
        with self.audit_path.open('x', encoding='utf-8') as stream:
            stream.write(encode(self.audit))

    def save(self):
        # Only this process writes; the adapter reads after exit. A torn write fails audit
        # validation and can never establish coverage. Avoid Windows rename/share races.
        self.audit_path.write_text(encode(self.audit), encoding='utf-8')

    def read(self, args, operation='read'):
        limit = self.bundle['limits']
        self.audit['requests'] += 1
        try:
            if self.audit['requests'] > limit['max_requests']:
                raise BridgeError('Read request limit exhausted; report missing context, do not retry')
            if operation == 'search':
                result = search(self.bundle, args)
                event = {'operation': 'search', 'query_sha256': fingerprint(args['query']),
                         'result': result}
            else:
                if not isinstance(args, dict) or set(args) != {'path', 'start', 'end'}:
                    raise BridgeError('Read requires exactly path, start and end')
                result = excerpt(self.bundle, args['path'], args['start'], args['end'])
                event = {k: result[k] for k in ('path', 'start', 'end', 'sha256')}
            text = encode(result)
            if len(text) > limit['max_response_chars']:
                raise BridgeError('Read response exceeds per-read character limit; request a smaller range')
            if self.audit['returned_chars'] + len(text) > limit['max_total_chars']:
                raise BridgeError('Cumulative read character limit exhausted; report missing context')
            self.audit['returned_chars'] += len(text)
            self.audit['events'].append({**event, 'characters': len(text)})
            self.save()  # Never deliver unrecorded content.
            return {'content': [{'type': 'text', 'text': text}], 'isError': False}
        except BridgeError as exc:
            self.audit['denied'] += 1
            self.save()
            return {'content': [{'type': 'text', 'text': str(exc)}], 'isError': True}

    def handle(self, request):
        if not isinstance(request, dict) or request.get('jsonrpc') != '2.0':
            return {'jsonrpc': '2.0', 'id': None, 'error': {'code': -32600, 'message': 'Invalid request'}}
        if 'id' not in request:
            return None
        response = {'jsonrpc': '2.0', 'id': request['id']}
        method = request.get('method')
        if method == 'initialize':
            self.audit['initialized'] = True
            self.save()
            response['result'] = {'protocolVersion': '2024-11-05', 'capabilities': {'tools': {}},
                                  'serverInfo': {'name': SERVER, 'version': '1.0.0'}}
        elif method == 'ping':
            response['result'] = {}
        elif not self.audit['initialized']:
            response['error'] = {'code': -32600, 'message': 'Initialize first'}
        elif method == 'tools/list':
            response['result'] = {'tools': [{'name': TOOL,
                'description': 'Read exact lines from the frozen review catalog only. No filesystem or network access.',
                'inputSchema': {'type': 'object', 'additionalProperties': False,
                    'required': ['path', 'start', 'end'], 'properties': {
                        'path': {'type': 'string'}, 'start': {'type': 'integer', 'minimum': 1},
                        'end': {'type': 'integer', 'minimum': 1}}},
                'annotations': {'readOnlyHint': True, 'destructiveHint': False, 'openWorldHint': False}}]}
            if self.bundle.get('mode') == 'project':
                response['result']['tools'].append(search_tool())
        elif method == 'tools/call':
            params = request.get('params', {})
            if (isinstance(params, dict) and params.get('name') == 'search_sources'
                    and self.bundle.get('mode') == 'project'):
                response['result'] = self.read(params.get('arguments'), 'search')
            elif not isinstance(params, dict) or params.get('name') != TOOL:
                # Charge malformed/unknown tool calls against the same budget.
                response['result'] = self.read(None)
            else:
                response['result'] = self.read(params.get('arguments'))
        else:
            response['error'] = {'code': -32601, 'message': 'Method unavailable'}
        return response


def verify_audit(bundle, audit):
    if (not isinstance(audit, dict) or audit.get('bundle_hash') != fingerprint(bundle)
            or audit.get('initialized') is not True):
        raise BridgeError('Restricted reader did not initialize against the frozen bundle')
    events = audit.get('events')
    if not isinstance(events, list) or len(events) > bundle['limits']['max_requests']:
        raise BridgeError('Invalid restricted read audit')
    total = 0
    for event in events:
        if event.get('operation') == 'search':
            verify_search_event(bundle, event)
            total += event['characters']
            continue
        value = excerpt(bundle, event['path'], event['start'], event['end'])
        size = len(encode(value))
        if (event['sha256'] != value['sha256'] or event['characters'] != size
                or size > bundle['limits']['max_response_chars']):
            raise BridgeError('Restricted read audit does not match frozen content')
        total += size
    if total != audit.get('returned_chars') or total > bundle['limits']['max_total_chars']:
        raise BridgeError('Restricted read cumulative audit mismatch')
    if (type(audit.get('requests')) is not int or type(audit.get('denied')) is not int
            or audit['denied'] < 0 or audit['requests'] != len(events) + audit['denied']):
        raise BridgeError('Restricted read request audit mismatch')
    return audit


def coverage_packet(packet, audit):
    bundle = packet['_restricted_bundle']
    verify_audit(bundle, audit)
    result = copy.deepcopy(public_packet(packet))
    for event in audit['events']:
        if event.get('operation') == 'search':
            continue
        value = excerpt(bundle, event['path'], event['start'], event['end'])
        result['sources'][event['path']]['excerpts'].append(
            {key: value[key] for key in ('start', 'end', 'text')})
    return result


def unread_ranges(bundle, audit):
    unread = {}
    for name, source in bundle['sources'].items():
        remaining = [(s['start'], s['end']) for s in segments(source) if s['end'] >= s['start']]
        for event in audit['events']:
            if event.get('operation') == 'search' or event['path'] != name:
                continue
            remaining = [(lo, hi) for a, b in remaining for lo, hi in (
                (a, min(b, event['start'] - 1)), (max(a, event['end'] + 1), b)) if lo <= hi]
        if remaining:
            unread[name] = remaining
    return unread


def search_tool():
    return {'name': 'search_sources',
            'description': 'Literal, case-sensitive search of frozen allowlisted source. Returns paths/lines only; read_source is required for evidence. Paginate using next_offset.',
            'inputSchema': {'type': 'object', 'additionalProperties': False,
                'required': ['query', 'path_prefix', 'offset', 'limit'], 'properties': {
                    'query': {'type': 'string', 'minLength': 1, 'maxLength': 256},
                    'path_prefix': {'type': 'string'},
                    'offset': {'type': 'integer', 'minimum': 0},
                    'limit': {'type': 'integer', 'minimum': 1, 'maximum': 100}}},
            'annotations': {'readOnlyHint': True, 'destructiveHint': False, 'openWorldHint': False}}


def search(bundle, args):
    if bundle.get('mode') != 'project':
        raise BridgeError('Search is not enabled')
    if not isinstance(args, dict) or set(args) != {'query', 'path_prefix', 'offset', 'limit'}:
        raise BridgeError('Search requires query, path_prefix, offset and limit')
    query, prefix, offset, limit = (args[k] for k in ('query', 'path_prefix', 'offset', 'limit'))
    if (not isinstance(query, str) or not 1 <= len(query) <= 256 or '\x00' in query
            or not isinstance(prefix, str) or len(prefix) > 512
            or any(c in prefix for c in ('\\', ':', '\x00')) or prefix.startswith('/')
            or any(p in {'.', '..'} for p in prefix.split('/'))
            or type(offset) is not int or not 0 <= offset <= 2_000_000
            or type(limit) is not int or not 1 <= limit <= 100):
        raise BridgeError('Invalid literal search arguments')
    found = []
    total = 0
    for name, source in sorted(bundle['sources'].items()):
        if not name.startswith(prefix):
            continue
        for segment in segments(source):
            for number, line in enumerate(segment['text'].splitlines(), segment['start']):
                if query in line:
                    if offset <= total < offset + limit:
                        found.append({'path': name, 'line': number})
                    total += 1
    return {'matches': found, 'total_matches': total,
            'next_offset': offset + len(found) if offset + len(found) < total else None}


def verify_search_event(bundle, event):
    if bundle.get('mode') != 'project' or set(event) != {'operation', 'query_sha256', 'result', 'characters'}:
        raise BridgeError('Unexpected search audit')
    digest = event['query_sha256']
    if not isinstance(digest, str) or len(digest) != 64 or any(c not in '0123456789abcdef' for c in digest):
        raise BridgeError('Invalid search query fingerprint')
    result = event['result']
    if (not isinstance(result, dict) or set(result) != {'matches', 'total_matches', 'next_offset'}
            or not isinstance(result['matches'], list) or len(result['matches']) > 100
            or type(result['total_matches']) is not int or result['total_matches'] < len(result['matches'])
            or (result['next_offset'] is not None and (type(result['next_offset']) is not int
                or not 0 < result['next_offset'] < result['total_matches']))):
        raise BridgeError('Invalid search result audit')
    for match in result['matches']:
        if not isinstance(match, dict) or set(match) != {'path', 'line'}:
            raise BridgeError('Invalid search location')
        excerpt(bundle, match['path'], match['line'], match['line'])
    size = len(encode(result))
    if type(event['characters']) is not int or event['characters'] != size or size > bundle['limits']['max_response_chars']:
        raise BridgeError('Search response audit mismatch')
    # Search exposes only coordinates, never source text; no coverage authority is granted.


def main():
    bundle_path, expected_hash, audit_path = sys.argv[1:]
    bundle = json.loads(Path(bundle_path).read_text(encoding='utf-8'))
    if fingerprint(bundle) != expected_hash:
        raise BridgeError('Frozen bundle fingerprint mismatch')
    reader = Reader(bundle, audit_path)
    # Limit malformed/protocol traffic as well as data reads. No user text is echoed in errors.
    for _ in range(bundle['limits']['max_requests'] + 32):
        raw = sys.stdin.buffer.readline(16385)
        if not raw:
            break
        if len(raw) > 16384:
            break
        try:
            request = json.loads(raw)
            response = reader.handle(request)
        except (ValueError, TypeError):
            response = {'jsonrpc': '2.0', 'id': None, 'error': {'code': -32700, 'message': 'Invalid JSON'}}
        if response is not None:
            sys.stdout.buffer.write((encode(response) + '\n').encode('utf-8'))
            sys.stdout.buffer.flush()
        if reader.audit['requests'] > bundle['limits']['max_requests']:
            break


if __name__ == '__main__':
    main()
