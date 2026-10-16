"""Office-indexed, bounded context. Offline preparation; never invokes a model."""
from __future__ import annotations
import copy
import json
from pathlib import Path
from runtime import BridgeError

GROUPS = ('brief', 'contracts', 'changes', 'dependencies', 'tests')


def load_index(api, root, relative):
    if not isinstance(relative, str) or not relative.startswith('office/'):
        raise BridgeError('Context index must live under project office/')
    path = api.confined(root, relative, source=True)
    raw = path.read_bytes()
    if len(raw) > 100000:
        raise BridgeError('Context index is too large; store references, not source copies')
    data = json.loads(raw.decode('utf-8-sig'))
    if not isinstance(data, dict) or set(data) != set(GROUPS):
        raise BridgeError('Office index requires brief, contracts, changes, dependencies, tests')
    entries = {}
    for group in GROUPS:
        values = [data[group]] if group == 'brief' else data[group]
        if not isinstance(values, list) or (group == 'changes' and not values):
            raise BridgeError('Index groups must be lists; changes must identify review targets')
        for value in values:
            if isinstance(value, str):
                entry = {'path': value}
            elif isinstance(value, dict) and set(value) == {'path', 'ranges'} and group in {'contracts', 'dependencies'}:
                entry = value
            else:
                raise BridgeError('Only contracts and dependencies may use explicit line ranges')
            name = entry['path']
            api.confined(root, name, source=True)
            if name == relative or name in entries:
                raise BridgeError('Duplicate/self-referencing Office context entry')
            if group in {'brief', 'contracts'} and not name.startswith('office/'):
                raise BridgeError('Brief and contract references must be under office/')
            ranges = entry.get('ranges')
            if ranges is not None:
                if name in api.GOVERNANCE or not isinstance(ranges, list) or not ranges:
                    raise BridgeError('Governance must be complete; excerpts need non-empty ranges')
                previous = 0
                for pair in ranges:
                    if (not isinstance(pair, list) or len(pair) != 2 or any(type(n) is not int for n in pair)
                            or not previous < pair[0] <= pair[1]):
                        raise BridgeError('Ranges must be ordered, non-overlapping positive integer pairs')
                    previous = pair[1]
            entries[name] = {'role': group, 'ranges': ranges}
    return entries, api.digest(raw)


def selection(api, root, spec):
    config = spec.get('context_index')
    if config is None:
        return {}
    if not isinstance(config, dict) or set(config) != {'path', 'sha256'}:
        raise BridgeError('context_index requires path and sha256')
    entries, sha = load_index(api, root, config['path'])
    if sha != config['sha256']:
        raise BridgeError('Office context index changed; prepare a new spec before confirmation')
    if set(entries) != set(spec['files']):
        raise BridgeError('Selected files must exactly match the confirmed Office index')
    return entries


def prepare(api, spec, index, output, max_chars=None, project_structure=None):
    spec = copy.deepcopy(spec)
    root = api.validate_spec(spec)
    entries, sha = load_index(api, root, index)
    spec['files'] = list(entries)
    spec['context_index'] = {'path': index, 'sha256': sha}
    spec['max_packet_chars'] = min(spec['max_packet_chars'], 120000) if max_chars is None else max_chars
    if project_structure is not None:
        if 'restricted_read' in spec:
            raise BridgeError('Prepare project mode from a base without an existing read configuration')
        deferred = [name for name, entry in entries.items()
                    if name != project_structure and name not in api.GOVERNANCE
                    and entry['role'] != 'brief'
                    and name.rsplit('/', 1)[-1].lower() not in {'agents.md', 'claude.md', 'claude.local.md'}]
        spec['restricted_read'] = {'mode': 'project', 'structure': project_structure, 'files': deferred,
                                  'max_requests': 24, 'max_response_chars': 12000,
                                  'max_total_chars': 120000, 'max_turns': 12}

    api.validate_spec(spec)
    # Refuse to overwrite a confirmed run or any existing draft.
    output = Path(output).resolve()
    if output.is_relative_to(root / api.RECORDS):
        raise BridgeError('Draft specs belong outside immutable collaboration run records')
    api.write_new(output, spec)
    return {'draft': str(output), 'selected_files': len(entries), 'max_packet_chars': spec['max_packet_chars'],
            'status': 'unconfirmed_draft', 'model_calls': 0}


def project_sources(api, root, spec, sources, changed):
    entries = selection(api, root, spec)
    projected = {}
    # Stable governance/contracts/unchanged dependencies precede per-revision source.
    def order(name):
        role = entries.get(name, {}).get('role')
        stable = name in api.GOVERNANCE or (role in {'contracts', 'dependencies'} and name not in changed)
        return (not stable, name)
    for name in sorted(sources, key=order):
        text = sources[name]
        ranges = entries.get(name, {}).get('ranges')
        if ranges is None:
            projected[name] = text
            continue
        if name in changed:
            raise BridgeError('Changed files require full source, not excerpts: ' + name)
        if text is None:
            raise BridgeError('Deleted files cannot be excerpted')
        lines = text.splitlines(keepends=True)
        if ranges[-1][1] > len(lines):
            raise BridgeError('Excerpt exceeds actual source length: ' + name)
        projected[name] = {'line_count': len(lines), 'excerpts': [
            {'start': start, 'end': end, 'text': ''.join(lines[start-1:end])} for start, end in ranges]}
    return projected


def metrics(packet, prompt, limit):
    sizes = []
    for name, source in packet['sources'].items():
        if isinstance(source, dict):
            size = sum(len(e['text']) for e in source['excerpts'])
            mode = 'deferred' if name in packet.get('restricted_read', {}).get('catalog', {}) else 'excerpt'
        else:
            size = len(source or '')
            mode = 'deleted' if source is None else 'full'
        sizes.append({'path': name, 'characters': size, 'mode': mode})
    chars = len(prompt)
    result = {'prompt_characters': chars, 'limit_characters': limit, 'within_limit': chars <= limit,
            'source_files': len(sizes), 'largest_sources': sorted(sizes, key=lambda x: -x['characters'])[:10],
            'unreviewed_changed_paths': packet['coverage']['unreviewed_changed_paths'],
            'warnings': (['Large packet: narrow the Office index before dispatch'] if chars > 120000 else []),
            'token_estimate': 'not provided; characters are not tokens', 'model_calls': 0}
    if 'restricted_read' in packet:
        result['restricted_read'] = packet['restricted_read']
        result['initial_plus_read_chars_limit'] = chars + packet['restricted_read']['limits']['max_total_chars']
        result['read_budget_note'] = 'Counts payload characters once; not cumulative model input tokens or billing'
    return result


def cache_observation(metadata):
    usage = metadata.get('usage', {})
    fields = ('cache_read_input_tokens', 'cache_creation_input_tokens', 'input_tokens')
    values = [usage.get(k) for k in fields]
    if any(type(v) is not int or v < 0 for v in values):
        return {'status': 'unavailable', 'note': 'Provider did not supply compatible input cache counters'}
    read, created, ordinary = values
    total = sum(values)
    return {'status': 'observed', 'read_fraction': round(read / total, 4) if total else None,
            'cache_read_input_tokens': read, 'cache_creation_input_tokens': created,
            'warning': 'Low cache reuse; narrow/reorder the next packet before another call' if total > 20000 and read / total < 0.2 else None,
            'note': 'Observed token reuse only; not subscription quota, price, or proof of future cache hits'}
