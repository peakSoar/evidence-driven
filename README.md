# Evidence Driven

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

`evidence-driven` 是一套面向 Codex 的证据驱动工程 Harness Skill，用于把长期 AI 协作开发收敛为可恢复、可审计、可验证的仓库工作流。

## 能力

- 初始化或转换仓库级 AI Harness；
- 按普通任务或阶段任务执行证据驱动工作流；
- 审计状态权威、owner、测试证据、权限和跨会话接力；
- 提供可按项目事实定制的 `AGENTS.md`、阶段、验证和验收模板。
- 明确要求完整结构时，通过固定 manifest 脚本确定性生成文件，避免目录和文件漂移。

## 目录

```text
skills/evidence-driven/   Codex Skill 本体
  scripts/                完整 Harness 的确定性生成脚本
docs/使用指南.md          安装、调用和维护方式
docs/设计说明.md          工作流模型与设计边界
LICENSE                   MIT License
```

## 快速开始

将 `skills/evidence-driven` 复制到以下任一位置：

- 用户级：`~/.agents/skills/evidence-driven`
- 仓库级：`<repo>/.agents/skills/evidence-driven`

随后在 Codex 中显式调用：

```text
$evidence-driven
```

Codex 也可以在请求与 Skill 的 `description` 匹配时隐式调用它。

完整结构生成脚本需要 Python 3.10 或更高版本，只使用标准库，不需要安装额外依赖。

详细使用方法见 [使用指南](docs/使用指南.md)，设计原则见 [设计说明](docs/设计说明.md)。

## 许可证

本项目采用 [MIT License](LICENSE)。
