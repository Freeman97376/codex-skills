# Codex Skills

自制技能的公开发布副本。

## 技能目录

| 技能 | 用途 | 维护入口 |
| --- | --- | --- |
| c-c-colaborate | Codex 与 Claude Code 协作 | [SKILL.md](office/skills/c-c-colaborate/SKILL.md) |
| frontend-gacha | 五种前端设计方案探索 | [SKILL.md](office/skills/frontend-gacha/SKILL.md) |
| manage-agent-governance | 项目 Agent 与 Office 治理 | [SKILL.md](office/skills/manage-agent-governance/SKILL.md) |
| release-preflight | 发布检查、验收与恢复边界 | [SKILL.md](office/skills/release-preflight/SKILL.md) |
| mantle-server-ops | Mantle 服务器运维 | [SKILL.md](office/skills/mantle-server-ops/SKILL.md) |
| math-ai-blog | 数学与 AI 学习博客写作 | [SKILL.md](office/skills/math-ai-blog/SKILL.md) |
| govern-change-tests | 行为变更与已知错误的测试治理 | [SKILL.md](testing/govern-change-tests/SKILL.md) |
| piecewise-alignment | 逐题或分组需求对齐 | [SKILL.md](workflow/piecewise-alignment/SKILL.md) |
| build-and-benchmark-skills | 技能制作与预算受控评测 | [SKILL.md](workflow/build-and-benchmark-skills/SKILL.md) |

本仓库包含 9 个技能及其脚本、模板、参考文档，以及支持治理技能的通用 Office 结构。历史任务记录、私人连接配置、评测运行数据、截图和原仓库历史不包含在此发布副本中。

个人绝对路径与部署地址已替换为示例值；使用时应先填写自己的路径和配置。通用 Office records 文件由空白模板生成，不包含原项目历史。

每个表格链接指向该技能的维护入口；使用时保留技能文件夹及其子目录。manage-agent-governance 依赖同仓库的 office/scripts、office/templates 和 office/tests，请保留该目录结构。

第三方流程参考与署名见 [frontend-gacha 来源说明](office/skills/frontend-gacha/references/sources.md)。本仓库不包含另行安装的第三方技能。

## 本次更新

完善 Agent 启动读取、共用事实与收尾更新；保留各技能专项证据、权限和只读边界。Piecewise 支持 Standard 单题与 Range 分组模式。发布包中的人/Agent 入口和共用事实是通用待填写模板，不是维护者项目的进展或历史。

[记录阅读首页](office/records/README.md) · [Agent 入口](office/records/agent-index.md)。维护规则不等于后台同步或实际工作流已通过验证。
