# Codex 集成计划 Review 报告

基于 `.refs/codex` 目录下的实际 Codex 代码，对当前集成计划进行全面 review。

## 📋 执行摘要

**总体评估**: ✅ 集成计划基本合理，但需要调整部分实现细节

**关键发现**:
1. Codex CLI 提供了比预期更丰富的功能
2. App Server 的 JSON-RPC 协议比预期更完善
3. 需要调整部分架构设计以更好地利用 Codex 的能力

## 🔍 详细分析

### 1. CLI Exec 方式 ✅

**实际代码发现** (`codex-rs/exec/src/cli.rs`):

```rust
pub struct Cli {
    pub model: Option<String>,
    pub oss: bool,
    pub oss_provider: Option<String>,
    pub sandbox_mode: Option<SandboxModeCliArg>,
    pub full_auto: bool,
    pub dangerously_bypass_approvals_and_sandbox: bool,
    pub cwd: Option<PathBuf>,
    pub skip_git_repo_check: bool,
    pub add_dir: Vec<PathBuf>,
    pub ephemeral: bool,
    pub output_schema: Option<PathBuf>,
    pub json: bool,
    pub last_message_file: Option<PathBuf>,
    pub prompt: Option<String>,
}
```

**关键特性**:
- ✅ `--json` 支持 JSONL 输出
- ✅ `--output-last-message` 输出最后一条消息到文件
- ✅ `--output-schema` 支持 JSON Schema 约束输出
- ✅ `--ephemeral` 不保存会话文件
- ✅ `--full-auto` 便捷模式（on-request + workspace-write）
- ✅ `--sandbox` 支持多种沙箱模式
- ✅ `--skip-git-repo-check` 允许在非 Git 仓库运行

**对我们的影响**:
- ✅ 我们的 CodexExecExecutor 设计是正确的
- ⚠️ 需要增加对 `--output-schema` 的支持
- ⚠️ 需要增加对 `--ephemeral` 的支持
- ⚠️ 需要增加对 `--skip-git-repo-check` 的支持

**建议调整**:
```python
class CodexExecExecutor:
    def execute(self, task: Task) -> Result:
        cmd = [
            "codex", "exec",
            "--json",
            "--skip-git-repo-check",  # 新增
            "--ephemeral",  # 新增
        ]
        
        # 支持 output schema
        if task.output_schema:
            cmd.extend(["--output-schema", task.output_schema])
        
        # 支持 last message file
        if task.last_message_file:
            cmd.extend(["--output-last-message", task.last_message_file])
        
        # ... 其他参数
```

### 2. App Server 方式 ✅

**实际代码发现** (`codex-rs/app-server/README.md`):

**核心原语**:
- **Thread**: 会话，包含多个 Turn
- **Turn**: 一次对话，包含多个 Item
- **Item**: 用户输入和代理输出

**关键 API**:
```json
// 创建线程
{ "method": "thread/start", "id": 10, "params": {
    "model": "gpt-5.1-codex",
    "cwd": "/Users/me/project",
    "approvalPolicy": "never",
    "sandbox": "workspaceWrite"
} }

// 开始 turn
{ "method": "turn/start", "id": 30, "params": {
    "threadId": "thr_123",
    "input": [ { "type": "text", "text": "Run tests" } ]
} }

// 流式事件
{ "method": "turn/started", "params": { ... } }
{ "method": "item/started", "params": { ... } }
{ "method": "item/completed", "params": { ... } }
{ "method": "turn/completed", "params": { ... } }
```

**对我们的影响**:
- ✅ 我们的 CodexAppServerClient 设计是正确的
- ⚠️ 需要实现完整的 JSON-RPC 2.0 客户端
- ⚠️ 需要处理流式事件通知
- ⚠️ 需要实现审批流程（如果需要）

**建议调整**:
```python
class CodexAppServerClient:
    def __init__(self):
        # 启动 App Server
        self.process = subprocess.Popen(
            ["codex", "app-server", "--listen", "stdio://"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE
        )
        
        # 初始化连接
        self._send_request("initialize", {
            "clientInfo": {
                "name": "cinder",
                "title": "Cinder Codex Integration",
                "version": "0.1.0"
            }
        })
        
        # 发送 initialized 通知
        self._send_notification("initialized", {})
    
    def create_thread(self, cwd: str, model: str) -> str:
        result = self._send_request("thread/start", {
            "cwd": cwd,
            "model": model,
            "approvalPolicy": "never",
            "sandbox": "workspaceWrite"
        })
        return result["thread"]["id"]
    
    def run_turn(self, thread_id: str, prompt: str):
        # 发送 turn/start 请求
        self._send_request("turn/start", {
            "threadId": thread_id,
            "input": [{"type": "text", "text": prompt}]
        })
        
        # 监听事件流
        for event in self._read_events():
            if event["method"] == "turn/completed":
                break
            yield event
```

### 3. MCP 方式 ⚠️

**实际代码发现**:
- MCP Server 实现相对简单
- 主要用于将 Codex 作为工具暴露给其他客户端
- 对于我们的用例，可能不是最佳选择

**对我们的影响**:
- ⚠️ MCP 方式可能不是我们需要的
- ✅ 我们应该优先实现 exec 和 app-server 方式
- ❌ 可以暂时不实现 MCP 方式

**建议调整**:
- 将 MCP 集成从高优先级降低到可选
- 专注于 exec 和 app-server 两种方式

### 4. 上下文传递 ✅

**实际代码发现**:
Codex 支持 AGENTS.md 文件来传递项目级指导：

```
~/.codex/AGENTS.md - 个人全局指导
项目根目录/AGENTS.md - 项目级指导
```

**对我们的影响**:
- ✅ 我们可以通过 AGENTS.md 传递 Soul profile
- ⚠️ 需要动态生成 AGENTS.md 文件
- ⚠️ 或者在任务描述中嵌入上下文

**建议调整**:
```python
class CodexIntegrationManager:
    def build_task_prompt(self, task: Task, context: dict) -> str:
        soul = self.soul_meta
        
        # 方案 1: 在任务描述中嵌入上下文
        prompt = f"""
# 上下文信息

## 用户性格特征
- 风险偏好：{soul['traits']['risk_tolerance']}
- 沟通风格：{soul['traits']['communication_style']}

## 任务理解
- 目标类型：{context.get('goal_type')}
- 关键功能：{context.get('key_features')}

# 任务描述
{task.description}
"""
        return prompt
    
    def generate_agents_md(self, soul_meta: dict) -> str:
        # 方案 2: 生成 AGENTS.md 文件
        return f"""
# Cinder Agent 指导

## 用户偏好
- 风险偏好：{soul_meta['traits']['risk_tolerance']}
- 沟通风格：{soul_meta['traits']['communication_style']}

## 决策规则
- {soul_meta['preferences']}
"""
```

### 5. 沙箱和审批 ✅

**实际代码发现**:
Codex 有完善的沙箱和审批系统：

**沙箱模式**:
- `read-only`: 只读
- `workspace-write`: 工作区可写
- `danger-full-access`: 完全访问

**审批策略**:
- `never`: 从不审批
- `on-request`: 每次都审批
- `on-failure`: 失败时审批
- `untrusted`: 不信任模式

**对我们的影响**:
- ✅ 我们需要配置合适的沙箱模式
- ✅ 我们需要处理审批流程（如果使用 app-server）
- ⚠️ 对于自动化执行，建议使用 `never` 审批策略

**建议调整**:
```yaml
# cinder.yaml
codex_integration:
  enabled: true
  default_executor: "exec"
  
  exec:
    model: "gpt-5.4"
    sandbox_mode: "workspace-write"
    approval_policy: "never"  # 自动化执行，不审批
    skip_git_repo_check: true
    ephemeral: true
  
  app_server:
    sandbox: "workspaceWrite"
    approvalPolicy: "never"
```

## 📊 架构调整建议

### 调整 1: 简化执行器选择逻辑

**原计划**: 根据任务复杂度选择 exec 或 app-server

**建议调整**: 优先使用 exec，仅在需要会话持久化时使用 app-server

```python
class CodexIntegrationManager:
    def select_executor(self, task: Task) -> str:
        # 简单任务：使用 exec
        if not task.needs_context_persistence:
            return "exec"
        
        # 需要会话持久化：使用 app-server
        return "app_server"
```

### 调整 2: 增强 CodexExecExecutor 功能

**新增功能**:
1. 支持 `--output-schema`
2. 支持 `--ephemeral`
3. 支持 `--skip-git-repo-check`
4. 支持 `--full-auto` 便捷模式
5. 支持流式输出解析

### 调整 3: 实现完整的 JSON-RPC 客户端

**关键功能**:
1. 初始化握手（initialize + initialized）
2. 请求-响应映射
3. 事件流处理
4. 错误处理

### 调整 4: 降低 MCP 优先级

**原因**:
- MCP 主要用于将 Codex 暴露给其他客户端
- 对于我们的用例，exec 和 app-server 更合适
- 可以作为未来的扩展功能

## 🎯 更新后的实施优先级

### 阶段 1: 基础集成（高优先级）
1. ✅ 实现 CodexExecExecutor（增强版）
2. ✅ 实现上下文传递机制
3. ✅ 实现配置管理
4. ✅ 实现错误处理和降级

### 阶段 2: 高级集成（中优先级）
1. ⚠️ 实现 CodexAppServerClient
2. ⚠️ 实现 JSON-RPC 客户端
3. ⚠️ 实现事件流处理

### 阶段 3: 扩展功能（低优先级）
1. ❌ MCP 集成（可选）
2. ❌ 自定义工具注册（可选）

## 📝 具体代码调整建议

### 1. CodexExecExecutor 调整

```python
class CodexExecExecutor:
    def execute(self, task: Task) -> Result:
        cmd = [
            "codex", "exec",
            "--json",
            "--skip-git-repo-check",
            "--ephemeral",
        ]
        
        # 模型配置
        if task.model:
            cmd.extend(["--model", task.model])
        
        # 沙箱配置
        if task.sandbox_mode:
            cmd.extend(["--sandbox", task.sandbox_mode])
        
        # 便捷模式
        if task.full_auto:
            cmd.append("--full-auto")
        
        # 输出 schema
        if task.output_schema:
            schema_file = self._write_schema_file(task.output_schema)
            cmd.extend(["--output-schema", schema_file])
        
        # 工作目录
        if task.cwd:
            cmd.extend(["--cd", task.cwd])
        
        # 任务描述
        cmd.append(task.description)
        
        # 执行
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=task.timeout
        )
        
        # 解析 JSONL 输出
        return self._parse_jsonl_output(result.stdout)
```

### 2. CodexAppServerClient 调整

```python
class CodexAppServerClient:
    def __init__(self):
        # 启动 App Server
        self.process = subprocess.Popen(
            ["codex", "app-server", "--listen", "stdio://"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1  # 行缓冲
        )
        
        self.request_id = 0
        self.pending_requests = {}
        
        # 初始化
        self._initialize()
    
    def _initialize(self):
        # 发送 initialize 请求
        result = self._send_request("initialize", {
            "clientInfo": {
                "name": "cinder",
                "title": "Cinder Codex Integration",
                "version": "0.1.0"
            },
            "capabilities": {
                "experimentalApi": False
            }
        })
        
        # 发送 initialized 通知
        self._send_notification("initialized", {})
    
    def _send_request(self, method: str, params: dict) -> dict:
        self.request_id += 1
        request = {
            "jsonrpc": "2.0",
            "method": method,
            "id": self.request_id,
            "params": params
        }
        
        # 发送请求
        self.process.stdin.write(json.dumps(request) + "\n")
        self.process.stdin.flush()
        
        # 读取响应
        response_line = self.process.stdout.readline()
        response = json.loads(response_line)
        
        if "error" in response:
            raise CodexAppServerError(response["error"])
        
        return response.get("result", {})
    
    def _send_notification(self, method: str, params: dict):
        notification = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params
        }
        
        self.process.stdin.write(json.dumps(notification) + "\n")
        self.process.stdin.flush()
```

## ✅ 结论

**总体评估**: 集成计划基本合理，但需要根据实际代码调整部分实现细节。

**主要调整**:
1. 增强 CodexExecExecutor 功能
2. 实现完整的 JSON-RPC 客户端
3. 降低 MCP 集成优先级
4. 简化执行器选择逻辑

**下一步行动**:
1. 更新 proposal.md 和 design.md
2. 更新 tasks.md 中的任务列表
3. 开始实施阶段 1 的任务
