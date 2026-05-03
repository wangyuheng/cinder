## ADDED Requirements

### Requirement: 验证邀请码有效性

系统 SHALL 验证用户输入的邀请码是否有效。

#### Scenario: 验证有效的邀请码
- **WHEN** 用户输入有效的邀请码
- **THEN** 系统返回验证成功并允许用户继续

#### Scenario: 验证无效的邀请码
- **WHEN** 用户输入无效的邀请码
- **THEN** 系统返回错误消息"邀请码无效"

#### Scenario: 验证已禁用的邀请码
- **WHEN** 用户输入已被禁用的邀请码
- **THEN** 系统返回错误消息"邀请码已被禁用"

### Requirement: 支持单次使用邀请码

系统 SHALL 支持只能使用一次的邀请码。

#### Scenario: 首次使用单次邀请码
- **WHEN** 用户首次使用单次邀请码
- **THEN** 系统验证成功并标记邀请码为已使用

#### Scenario: 重复使用单次邀请码
- **WHEN** 用户尝试使用已使用的单次邀请码
- **THEN** 系统返回错误消息"邀请码已被使用"

### Requirement: 支持多次使用邀请码

系统 SHALL 支持可以多次使用的邀请码。

#### Scenario: 使用多次邀请码
- **WHEN** 用户使用多次邀请码且未达到使用上限
- **THEN** 系统验证成功并增加使用次数

#### Scenario: 超过使用上限
- **WHEN** 用户使用多次邀请码且已达到使用上限
- **THEN** 系统返回错误消息"邀请码已达到使用上限"

### Requirement: 邀请码配置管理

系统 SHALL 支持通过配置文件管理邀请码。

#### Scenario: 从配置文件加载邀请码
- **WHEN** 系统启动时
- **THEN** 系统从 ~/.cinder/invitations.yaml 加载邀请码配置

#### Scenario: 邀请码配置格式
- **WHEN** 管理员创建邀请码配置
- **THEN** 配置文件 SHALL 包含 code、is_single_use、max_uses、description 字段

### Requirement: 记录邀请码使用状态

系统 SHALL 在数据库中记录邀请码的使用状态。

#### Scenario: 记录邀请码使用
- **WHEN** 用户成功使用邀请码
- **THEN** 系统在数据库中记录使用次数和时间

#### Scenario: 查询邀请码使用统计
- **WHEN** 管理员查询邀请码使用情况
- **THEN** 系统返回使用次数、使用时间等统计信息
