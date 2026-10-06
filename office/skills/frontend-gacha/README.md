# frontend-gacha

根据一份提示词生成 **5 个小范围的可交互前端演示**，在同一个比较页中筛选，保留全部方案并单独整理选中的代码。

## 使用

    $frontend-gacha 为阅读收藏工具做五种风格的小演示，展示三条收藏，并支持收藏切换和筛选。

现有项目会沿用其需求与约束。默认使用可直接预览的 HTML/CSS/JavaScript；明确要求框架时，采用隔离的框架预览并输出可独立查看的静态演示。

所有演示代码、说明、预览和选中结果都放在**目标项目根目录**的 ./office/frontend-gacha/ 下。每次重抽建立新轮次，已有方案保留。

    office/frontend-gacha/<主题>/round-01/
      index.html                 比较页
      brief.md                   共同需求与设计方向
      fixture.json               共用示例数据
      manifest.json              五个方案的名称与说明
      variants/A/ ... E/          独立演示代码
      selections/<选择编号>/     选中代码与来源记录

你可以在任务中回复“选 B”。也可以在比较页中选择并复制结果，再粘贴到任务中。比较页不会自动向 Codex 发消息；技能收到选择后才整理选中代码。融合或重抽可在后续消息中提出。

此技能负责小范围风格探索。助手生成演示内容，随附 Python 工具负责创建轮次、构建比较页和复制选中代码。选中后默认单独交付；整合到应用由后续明确请求决定。

## 来源与协议

多方案比较、反馈和融合流程参考 **0xdesigner 的 [Design Lab](https://github.com/0xdesign/design-plugin)**。上游 README 与插件元数据声明 MIT；核查版本未提供独立许可证文件。本包的比较页与辅助代码为独立实现，未复制上游源码。

风格资料由单独安装的 **[UI UX Pro Max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill)** 提供，其 MIT 许可与原始版权说明保留在它的安装目录中。

固定来源版本、许可条件与核查限制见 [sources.md](references/sources.md)。

## 维护

入口为 SKILL.md；命令与文件格式见 [output-contract.md](references/output-contract.md)。运行所需的 Python 工具只依赖标准库。结构校验、路径与代码保存测试、浏览器检查分别验证不同层面的行为；这些检查不等于独立模型的设计质量评测。
