## Why

当前系统虽然能够生成用户的人格画像（soul.md），但缺少一个完整的工作流来引导用户完成题目生成、确认 soul，并让 agent 基于 soul 作为用户代理来处理需要人工决策的场景。用户需要手动运行多个独立的命令，且 agent 在需要"ask human"时无法自动参考 soul 中的决策偏好。

现在需要提供一个统一的命令行工具，将题目引导、soul 确认、以及代理决策整合为一个流畅的工作流，使 agent 能够真正成为基于用户人格画像的智能代理。

## What Changes

- 新增统一的 CLI 入口，提供交互式题目引导流程
- 新增 soul 确认机制，在生成 soul 后要求用户确认或调整
- 新增代理决策模式，当 agent 遇到需要"ask human"的决策时，自动参考 soul 中的决策偏好进行代理
- 新增决策日志记录，追踪 agent 代理决策的过程和依据
- 优化现有的 chat.py，使其能够无缝集成到新的工作流中

## Capabilities

### New Capabilities

- `problem-guidance`: 提供交互式题目引导流程，帮助用户完成 6 个核心问题的回答，生成初步的 soul 画像
- `soul-confirmation`: 在 soul 生成后提供确认机制，允许用户查看、理解和调整画像内容，确保画像准确反映用户偏好
- `proxy-decision-making`: 当 agent 遇到需要人工决策的场景时，基于 soul 中的决策偏好、风险态度和沟通风格自动进行代理决策，并记录决策依据
- `decision-logging`: 记录 agent 代理决策的完整过程，包括决策上下文、参考的 soul 规则、决策结果和置信度

### Modified Capabilities

- 无（现有 cli.py 和 chat.py 将被重构整合，但核心功能保持不变）

## Impact

- **代码结构**: 需要重构现有的 cli.py 和 chat.py，将其整合为统一的 CLI 工具
- **用户体验**: 用户将获得更流畅的端到端体验，从题目引导到代理决策一气呵成
- **依赖关系**: 可能需要新增依赖用于交互式 CLI（如 questionary 或 prompt-toolkit）
- **向后兼容**: 保持现有命令行参数的兼容性，旧的使用方式仍然可用
- **配置文件**: 可能需要新增配置文件来定义代理决策的边界和规则
