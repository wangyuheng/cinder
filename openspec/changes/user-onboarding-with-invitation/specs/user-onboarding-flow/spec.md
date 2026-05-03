## ADDED Requirements

### Requirement: 完整的用户引导流程

系统 SHALL 提供完整的用户引导流程，包括邀请码验证、信息收集和 SOUL 问卷。

#### Scenario: 首次访问用户
- **WHEN** 用户首次访问系统
- **THEN** 系统重定向到邀请码验证页面

#### Scenario: 完成引导流程
- **WHEN** 用户完成邀请码验证、信息填写和 SOUL 问卷
- **THEN** 系统标记用户引导流程为已完成并允许访问系统

#### Scenario: 未完成引导流程的用户访问受保护页面
- **WHEN** 未完成引导流程的用户访问受保护页面
- **THEN** 系统重定向到引导流程的当前步骤

### Requirement: 邀请码验证步骤

系统 SHALL 在引导流程的第一步验证邀请码。

#### Scenario: 输入邀请码
- **WHEN** 用户在邀请码验证页面输入邀请码
- **THEN** 系统验证邀请码有效性并显示结果

#### Scenario: 验证成功后继续
- **WHEN** 邀请码验证成功
- **THEN** 系统重定向到用户信息填写页面

### Requirement: 用户信息收集步骤

系统 SHALL 在引导流程的第二步收集用户基本信息。

#### Scenario: 填写用户姓名
- **WHEN** 用户在信息填写页面输入姓名
- **THEN** 系统保存用户姓名并允许继续

#### Scenario: 姓名验证
- **WHEN** 用户提交姓名
- **THEN** 系统验证姓名不为空且长度在 1-50 字符之间

#### Scenario: 信息填写完成后继续
- **WHEN** 用户完成信息填写
- **THEN** 系统重定向到 SOUL 问卷页面

### Requirement: SOUL 问卷步骤

系统 SHALL 在引导流程的第三步完成 SOUL 问卷。

#### Scenario: 开始问卷
- **WHEN** 用户进入问卷页面
- **THEN** 系统显示第一个问题

#### Scenario: 完成问卷
- **WHEN** 用户完成所有 6 个问题
- **THEN** 系统生成个性化画像并标记引导流程为已完成

### Requirement: 引导流程进度保存

系统 SHALL 支持保存引导流程的进度。

#### Scenario: 中途离开
- **WHEN** 用户在引导流程中途离开
- **THEN** 系统保存当前进度

#### Scenario: 恢复引导流程
- **WHEN** 用户再次访问系统
- **THEN** 系统恢复到上次离开的步骤

### Requirement: 引导流程状态追踪

系统 SHALL 追踪用户在引导流程中的状态。

#### Scenario: 查询引导状态
- **WHEN** 系统查询用户的引导流程状态
- **THEN** 系统返回当前步骤（invitation、profile、questionnaire、completed）

#### Scenario: 更新引导状态
- **WHEN** 用户完成某个步骤
- **THEN** 系统更新用户的引导流程状态
