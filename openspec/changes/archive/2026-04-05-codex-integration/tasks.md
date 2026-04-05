## 阶段 1: 基础集成（高优先级）

### 1. 基础设施和配置

- [x] 1.1 添加 Codex 配置项到 cinder.yaml 配置文件
- [x] 1.2 扩展 Config 类以支持 Codex 配置加载
- [x] 1.3 创建 Codex 配置验证逻辑
- [x] 1.4 添加 Codex CLI 可用性检查工具

### 2. CodexExecExecutor 实现（增强版）

- [x] 2.1 创建 CodexExecExecutor 基类和接口
- [x] 2.2 实现 `codex exec` 命令构建逻辑（支持所有 CLI 参数）
- [x] 2.3 实现 subprocess 执行和输出捕获
- [x] 2.4 实现 JSONL 输出解析逻辑
- [x] 2.5 实现错误处理和异常类（CodexNotInstalledError, CodexTimeoutError 等）
- [x] 2.6 实现超时控制和进程终止
- [x] 2.7 实现 sandbox mode 和 approval policy 支持
- [x] 2.8 实现 `--skip-git-repo-check` 支持
- [x] 2.9 实现 `--ephemeral` 支持
- [x] 2.10 实现 `--full-auto` 便捷模式支持
- [x] 2.11 实现 `--output-schema` 支持
- [x] 2.12 为 CodexExecExecutor 编写单元测试

### 3. CodexIntegrationManager 实现

- [x] 3.1 创建 CodexIntegrationManager 主类
- [x] 3.2 实现简化的执行器选择逻辑（优先 exec）
- [x] 3.3 实现 Soul profile 上下文构建
- [x] 3.4 实现决策上下文传递
- [x] 3.5 实现执行器初始化和生命周期管理
- [x] 3.6 实现结果统一化逻辑
- [x] 3.7 实现降级机制（fallback to CodeGenerator）
- [x] 3.8 实现配置管理和验证
- [x] 3.9 为 CodexIntegrationManager 编写单元测试

### 4. Worker Agent 集成

- [x] 4.1 修改 Worker Agent 以支持执行器选择
- [x] 4.2 在 Worker Agent 中集成 CodexIntegrationManager
- [x] 4.3 实现 Generate 阶段的执行器选择逻辑
- [x] 4.4 实现上下文传递到 CodexIntegrationManager
- [x] 4.5 实现执行器降级和错误处理
- [x] 4.6 更新 Worker Agent 的配置加载逻辑
- [x] 4.7 为 Worker Agent 集成编写集成测试

### 5. 错误处理和日志

- [x] 5.1 创建自定义异常类（CodexError, CodexNotInstalledError 等）
- [x] 5.2 实现详细的错误消息和用户指导
- [x] 5.3 添加 Codex 相关的日志记录
- [x] 5.4 实现错误上报和监控点
- [x] 5.5 编写错误处理测试用例

### 6. 文档和示例

- [x] 6.1 编写 Codex 集成用户指南
- [x] 6.2 编写 Codex CLI 安装和配置文档
- [x] 6.3 创建配置示例文件
- [x] 6.4 编写故障排除指南
- [x] 6.5 更新项目 README 添加 Codex 集成说明

### 7. 测试和验证

- [x] 7.1 编写 CodexExecExecutor 集成测试
- [x] 7.2 编写端到端测试（Decision Agent → Worker Agent → Codex）
- [x] 7.3 编写降级机制测试
- [x] 7.4 编写性能和超时测试
- [x] 7.5 进行手动测试验证

### 8. 部署和发布

- [x] 8.1 更新 CHANGELOG.md
- [x] 8.2 更新版本号
- [x] 8.3 创建迁移指南（如果需要）
- [x] 8.4 准备发布说明
- [x] 8.5 执行发布流程

## 阶段 2: 高级集成（中优先级）

### 9. CodexAppServerClient 实现

- [ ] 9.1 创建 CodexAppServerClient 基类
- [ ] 9.2 实现 App Server 进程启动和管理
- [ ] 9.3 实现完整的 JSON-RPC 2.0 客户端
- [ ] 9.4 实现 stdio 传输层通信
- [ ] 9.5 实现初始化握手（initialize + initialized）
- [ ] 9.6 实现线程创建、恢复和管理
- [ ] 9.7 实现事件流处理和监听
- [ ] 9.8 实现双向通信和请求-响应映射
- [ ] 9.9 实现 App Server 生命周期管理（启动、停止、重启）
- [ ] 9.10 为 CodexAppServerClient 编写单元测试
- [ ] 9.11 编写 CodexAppServerClient 集成测试

### 10. 高级功能

- [ ] 10.1 实现会话持久化支持
- [ ] 10.2 实现流式事件通知
- [ ] 10.3 实现审批流程（如果需要）
- [ ] 10.4 实现多线程管理
- [ ] 10.5 编写高级功能测试

## 阶段 3: 扩展功能（低优先级，可选）

### 11. MCP 集成

- [ ] 11.1 评估 MCP 集成的必要性
- [ ] 11.2 实现 CodexMCPBridge（如果需要）
- [ ] 11.3 连接外部 MCP servers（如果需要）
- [ ] 11.4 扩展 Codex 的能力（如果需要）
- [ ] 11.5 编写 MCP 集成文档（如果需要）

### 12. 其他扩展

- [ ] 12.1 实现自定义工具注册（如果需要）
- [ ] 12.2 实现并行任务执行（如果需要）
- [ ] 12.3 实现 Codex 性能优化（如果需要）
- [ ] 12.4 其他高级功能（根据需求添加）
