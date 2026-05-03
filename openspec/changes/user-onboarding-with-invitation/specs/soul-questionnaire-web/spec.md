## ADDED Requirements

### Requirement: 显示问卷问题

系统 SHALL 逐题显示 SOUL 问卷的 6 个问题。

#### Scenario: 显示第一个问题
- **WHEN** 用户开始问卷
- **THEN** 系统显示问题 1（未知应对）及其 4 个选项

#### Scenario: 显示后续问题
- **WHEN** 用户回答当前问题
- **THEN** 系统显示下一个问题

#### Scenario: 显示所有问题
- **WHEN** 用户完成所有问题
- **THEN** 系统显示完成提示

### Requirement: 问题内容完整性

系统 SHALL 显示完整的问题内容，包括标题、提示和选项。

#### Scenario: 问题结构
- **WHEN** 系统显示问题
- **THEN** 问题 SHALL 包含：
  - 问题标题
  - 问题提示
  - 维度名称
  - 4 个选项（A、B、C、D）

#### Scenario: 选项内容
- **WHEN** 系统显示选项
- **THEN** 每个选项 SHALL 包含选项文本和简短说明

### Requirement: 用户选择答案

系统 SHALL 允许用户选择问题的答案。

#### Scenario: 选择答案
- **WHEN** 用户点击某个选项
- **THEN** 系统记录用户的选择

#### Scenario: 修改答案
- **WHEN** 用户返回上一题
- **THEN** 系统允许用户修改之前的选择

### Requirement: 可选填写原因

系统 SHALL 允许用户为答案填写原因（可选）。

#### Scenario: 填写原因
- **WHEN** 用户选择答案后
- **THEN** 系统显示可选的原因输入框

#### Scenario: 跳过原因
- **WHEN** 用户不填写原因直接进入下一题
- **THEN** 系统接受空原因并继续

### Requirement: 显示进度指示器

系统 SHALL 显示问卷的完成进度。

#### Scenario: 进度显示
- **WHEN** 用户在问卷页面
- **THEN** 系统显示当前进度（如"问题 2/6"）

#### Scenario: 进度更新
- **WHEN** 用户回答问题
- **THEN** 系统更新进度指示器

### Requirement: 保存问卷进度

系统 SHALL 支持保存问卷的进度。

#### Scenario: 自动保存
- **WHEN** 用户回答问题
- **THEN** 系统自动保存答案到数据库

#### Scenario: 恢复问卷
- **WHEN** 用户中断问卷后重新进入
- **THEN** 系统恢复到上次回答的问题

### Requirement: 生成个性化画像

系统 SHALL 根据问卷答案生成个性化画像。

#### Scenario: 计算特质分数
- **WHEN** 用户完成所有问题
- **THEN** 系统根据答案计算 13 个特质维度的分数

#### Scenario: 生成 soul 文件
- **WHEN** 计算完成
- **THEN** 系统生成 soul.md 和 soul.meta.yaml 文件

#### Scenario: 画像内容
- **WHEN** 生成 soul.meta.yaml
- **THEN** 文件 SHALL 包含：
  - version
  - source
  - question_count
  - confidence
  - raw_answers
  - traits
  - core_traits
  - decision_profile
  - agent_directives

### Requirement: 问卷问题数据

系统 SHALL 使用与 CLI 相同的问卷问题数据。

#### Scenario: 问题一致性
- **WHEN** 系统加载问卷问题
- **THEN** 问题 SHALL 与 question_guide.py 中的 QUESTIONS 常量一致

#### Scenario: 问题数量
- **WHEN** 系统显示问卷
- **THEN** 系统 SHALL 显示 6 个问题

#### Scenario: 选项效果
- **WHEN** 用户选择选项
- **THEN** 系统根据选项的 effects 字段更新特质分数
