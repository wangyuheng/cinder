## ADDED Requirements

### Requirement: Phoenix 平台安装和配置

系统 SHALL 支持安装和配置 Phoenix 平台作为 trace 可视化工具。

#### Scenario: 安装 Phoenix 依赖

- **WHEN** 用户安装 cinder-cli
- **THEN** 系统自动安装 arize-phoenix 依赖
- **AND** 系统安装 opentelemetry-api 依赖
- **AND** 系统安装 opentelemetry-sdk 依赖
- **AND** 系统安装 opentelemetry-exporter-otlp 依赖

#### Scenario: 配置 Phoenix 连接

- **WHEN** 用户配置 trace 功能
- **THEN** 系统读取 cinder.yaml 中的 tracing 配置
- **AND** 系统支持配置 Phoenix 服务器地址
- **AND** 系统支持配置是否启用 trace

### Requirement: Phoenix 服务器启动

系统 SHALL 支持启动 Phoenix 服务器以提供 Web UI。

#### Scenario: 启动本地 Phoenix 服务器

- **WHEN** 用户执行 `cinder phoenix start` 命令
- **THEN** 系统启动 Phoenix 服务器
- **AND** 服务器监听默认端口 6006
- **AND** 系统显示访问 URL

#### Scenario: Phoenix 服务器已在运行

- **WHEN** 用户执行 `cinder phoenix start` 命令
- **AND** Phoenix 服务器已经在运行
- **THEN** 系统提示服务器已在运行
- **AND** 系统显示访问 URL

#### Scenario: Phoenix 服务器启动失败

- **WHEN** 用户执行 `cinder phoenix start` 命令
- **AND** 端口 6006 已被占用
- **THEN** 系统显示错误信息
- **AND** 系统建议使用其他端口

### Requirement: Phoenix 客户端初始化

系统 SHALL 支持初始化 Phoenix 客户端以连接到 Phoenix 服务器。

#### Scenario: 初始化 Phoenix 客户端

- **WHEN** 系统启动 trace 功能
- **THEN** 系统创建 Phoenix 客户端实例
- **AND** 客户端连接到配置的 Phoenix 服务器
- **AND** 客户端验证连接成功

#### Scenario: Phoenix 客户端连接失败

- **WHEN** 系统初始化 Phoenix 客户端
- **AND** Phoenix 服务器不可用
- **THEN** 系统记录警告日志
- **AND** 系统继续执行（降级模式）
- **AND** trace 数据存储在本地

### Requirement: OpenTelemetry Tracer 初始化

系统 SHALL 支持初始化 OpenTelemetry Tracer 以导出 trace 数据到 Phoenix。

#### Scenario: 初始化 OpenTelemetry Tracer

- **WHEN** 系统启动 trace 功能
- **THEN** 系统创建 TracerProvider
- **AND** 系统创建 OTLPSpanExporter
- **AND** 系统创建 BatchSpanProcessor
- **AND** 系统设置全局 TracerProvider

#### Scenario: 配置 OpenTelemetry 资源

- **WHEN** 系统初始化 OpenTelemetry Tracer
- **THEN** 系统设置服务名称为 "cinder-cli"
- **AND** 系统设置服务版本
- **AND** 系统设置部署环境

### Requirement: Phoenix UI 访问

系统 SHALL 支持通过浏览器访问 Phoenix Web UI。

#### Scenario: 访问 Phoenix UI

- **WHEN** 用户打开浏览器访问 http://localhost:6006
- **THEN** Phoenix UI 正常显示
- **AND** UI 显示 trace 列表
- **AND** UI 支持搜索和过滤

#### Scenario: Phoenix UI 显示 trace 详情

- **WHEN** 用户在 Phoenix UI 中点击某个 trace
- **THEN** UI 显示 trace 的详细信息
- **AND** UI 显示 span 树结构
- **AND** UI 显示 LLM 调用详情

### Requirement: Phoenix 配置选项

系统 SHALL 支持通过配置文件配置 Phoenix 集成。

#### Scenario: 配置 Phoenix 启用/禁用

- **WHEN** 用户在 cinder.yaml 中设置 tracing.enabled = false
- **THEN** 系统禁用 trace 功能
- **AND** 系统不记录任何 trace 数据

#### Scenario: 配置 Phoenix 服务器地址

- **WHEN** 用户在 cinder.yaml 中设置 tracing.phoenix_endpoint
- **THEN** 系统连接到指定的 Phoenix 服务器
- **AND** trace 数据导出到远程服务器

#### Scenario: 配置 trace 采样率

- **WHEN** 用户在 cinder.yaml 中设置 tracing.sample_rate
- **THEN** 系统按照配置的采样率记录 trace
- **AND** 未被采样的请求不记录 trace
