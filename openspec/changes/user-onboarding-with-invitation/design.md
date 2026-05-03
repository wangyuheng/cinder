## Context

当前系统架构：
- **前端**: Next.js Web Dashboard，提供仪表盘、执行监控、决策管理等功能
- **后端**: FastAPI 服务器，提供 REST API
- **数据存储**: 文件系统（soul.md、soul.meta.yaml）
- **认证**: 无认证机制，任何人都可以访问所有功能

现有 SOUL 系统：
- CLI 工具（question_guide.py）实现完整的 6 题心理测评问卷
- Web 界面仅有简单的 4 个滑块配置（风险容忍度、结构化程度、细节关注度、沟通风格）
- 问卷结果生成 soul.md（人类可读）和 soul.meta.yaml（机器可读）
- 包含 13 个特质维度和决策画像

约束条件：
- 必须保持向后兼容，现有 CLI 功能不受影响
- 需要支持单机部署，避免引入复杂的外部依赖
- 数据存储应轻量级，适合个人使用场景
- 用户体验应流畅，避免过多的验证步骤

利益相关者：
- 终端用户：期望获得流畅的引导流程和个性化体验
- 系统管理员：需要控制用户访问，管理邀请码
- 开发者：需要清晰的架构和可维护的代码

## Goals / Non-Goals

**Goals:**
- 实现完整的用户引导流程：邀请码验证 → 信息收集 → SOUL 问卷 → 系统使用
- 提供基于邀请码的访问控制机制
- 将 CLI 中的 SOUL 问卷移植到 Web 界面
- 实现轻量级的用户会话管理
- 确保用户数据安全存储

**Non-Goals:**
- 不实现完整的用户认证系统（如 OAuth、JWT）
- 不实现多租户或权限管理
- 不实现云端同步或远程数据存储
- 不修改现有的 CLI 问卷功能
- 不实现复杂的邀请码生成算法

## Decisions

### 1. 数据存储方案：SQLite

**决定**: 使用 SQLite 作为数据存储方案。

**理由**:
- 轻量级，无需额外服务，适合单机部署
- Python 内置支持，无需额外依赖
- 支持事务和并发读取
- 便于查询和数据分析
- 与现有的决策日志存储方案一致

**数据模型**:
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    created_at TEXT NOT NULL,
    soul_path TEXT,
    onboarding_completed BOOLEAN DEFAULT FALSE
);

CREATE TABLE invitation_codes (
    code TEXT PRIMARY KEY,
    is_single_use BOOLEAN NOT NULL,
    used_count INTEGER DEFAULT 0,
    max_uses INTEGER,
    created_at TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE user_sessions (
    session_id TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL,
    created_at TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE questionnaire_answers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    question_key TEXT NOT NULL,
    choice TEXT NOT NULL,
    reason TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

**替代方案**:
- 纯文件存储（JSON/YAML）：查询效率低，不便于管理多用户
- PostgreSQL/MySQL：过于重量级，增加部署复杂度

### 2. 会话管理：基于 Cookie 的简单会话

**决定**: 使用基于 Cookie 的简单会话机制，不实现完整的认证系统。

**实现**:
- 用户完成引导流程后，生成唯一的 session_id（UUID）
- session_id 存储在 HttpOnly Cookie 中
- 会话有效期：7 天（可配置）
- 每次请求时验证 session_id 是否有效

**理由**:
- 实现简单，无需复杂的认证流程
- 满足基本的访问控制需求
- 适合单机部署场景
- 用户体验好，无需频繁登录

**替代方案**:
- JWT Token：过于复杂，需要处理刷新和撤销
- Session + Redis：需要额外服务，增加部署复杂度

### 3. 邀请码机制：配置文件 + 数据库混合

**决定**: 邀请码存储在配置文件中，使用状态存储在数据库中。

**实现**:
```yaml
# ~/.cinder/invitations.yaml
codes:
  - code: "WELCOME2024"
    is_single_use: false
    max_uses: 100
    description: "2024年通用邀请码"
  
  - code: "BETA-TESTER"
    is_single_use: true
    description: "Beta测试专用"
```

**理由**:
- 配置文件便于管理员手动管理邀请码
- 数据库记录使用状态，支持查询和统计
- 分离配置和状态，便于维护

**替代方案**:
- 纯数据库存储：不便于手动管理
- 纯配置文件：难以追踪使用状态

### 4. 问卷流程：单页逐题展示

**决定**: 采用单页逐题展示方式，类似 CLI 的交互体验。

**实现**:
- 每次显示一个问题，用户选择后进入下一题
- 显示进度指示器（问题 1/6）
- 支持返回修改上一题
- 可选填写原因
- 支持保存进度，用户可以中途离开

**理由**:
- 与 CLI 体验一致，降低学习成本
- 每个问题获得充分关注，提高答案质量
- 避免长表单带来的认知负担
- 支持进度保存，提升用户体验

**替代方案**:
- 单页长表单：所有问题在一个页面，用户可能快速填写，降低答案质量
- 多步骤向导：增加页面跳转复杂度

### 5. API 设计：RESTful 风格

**决定**: 采用 RESTful API 设计风格。

**端点设计**:
```
POST   /api/invitations/validate     - 验证邀请码
POST   /api/users                    - 创建用户
GET    /api/users/me                 - 获取当前用户信息
POST   /api/soul/questionnaire       - 提交问卷答案
GET    /api/soul/questionnaire       - 获取问卷问题
GET    /api/soul/questionnaire/progress - 获取问卷进度
DELETE /api/soul/questionnaire/progress - 清除问卷进度
```

**理由**:
- 符合 REST 规范，易于理解和使用
- 与现有 API 风格一致
- 便于前端调用和测试

### 6. 前端路由守卫：中间件模式

**决定**: 使用 Next.js 中间件实现路由守卫。

**实现**:
```typescript
// middleware.ts
export function middleware(request: NextRequest) {
  const sessionId = request.cookies.get('session_id');
  const path = request.nextUrl.pathname;
  
  // 公开路径
  if (path.startsWith('/onboarding')) {
    return NextResponse.next();
  }
  
  // 需要认证的路径
  if (!sessionId) {
    return NextResponse.redirect('/onboarding/invitation');
  }
  
  // 验证会话和引导状态
  // ...
}
```

**理由**:
- Next.js 原生支持，无需额外依赖
- 集中管理访问控制逻辑
- 便于扩展和维护

## Risks / Trade-offs

### 风险 1: SQLite 并发写入限制

**风险描述**: SQLite 在高并发写入场景下可能出现锁定问题。

**缓解措施**:
- 使用 WAL 模式提升并发性能
- 设置合理的超时时间
- 实现重试机制
- 单机部署场景下并发压力较小，风险可控

### 风险 2: 会话安全性

**风险描述**: 简单的 Cookie 会话可能被劫持或伪造。

**缓解措施**:
- 使用 HttpOnly 和 Secure 标志
- 设置合理的过期时间
- session_id 使用 UUID v4，难以猜测
- 绑定客户端 IP（可选）
- 未来可升级为 JWT + 签名

### 风险 3: 邀请码泄露

**风险描述**: 邀请码可能被泄露，导致未授权用户访问。

**缓解措施**:
- 支持单次使用的邀请码
- 支持设置最大使用次数
- 支持手动禁用邀请码
- 记录邀请码使用日志，便于审计

### 风险 4: 问卷完成率低

**风险描述**: 用户可能在中途放弃问卷，导致引导流程未完成。

**缓解措施**:
- 实现进度保存功能，用户可以稍后继续
- 显示进度指示器，让用户了解完成进度
- 优化问题设计，确保简洁明了
- 提供"稍后完成"选项，允许用户先浏览系统

### 风险 5: 向后兼容性

**风险描述**: 新的用户系统可能影响现有功能。

**缓解措施**:
- 现有 API 保持兼容，仅新增端点
- CLI 功能不受影响
- 已有的 soul.meta.yaml 文件可继续使用
- 提供数据迁移工具，将现有用户数据导入数据库

## Migration Plan

### 阶段 1: 数据库初始化（v1.0.0）
1. 创建 SQLite 数据库和表结构
2. 实现数据库访问层（DAO）
3. 编写数据库迁移脚本

### 阶段 2: 后端 API 实现（v1.1.0）
1. 实现邀请码验证 API
2. 实现用户管理 API
3. 实现问卷相关 API
4. 实现会话管理中间件

### 阶段 3: 前端引导流程（v1.2.0）
1. 实现邀请码验证页面
2. 实现用户信息填写页面
3. 实现问卷页面（逐题展示）
4. 实现路由守卫

### 阶段 4: 集成和测试（v1.3.0）
1. 端到端测试引导流程
2. 性能测试和优化
3. 安全测试
4. 文档编写

### 回滚策略
- 保留原有的 soul.md 和 soul.meta.yaml 文件
- 数据库文件独立存储，删除即可回滚
- 配置文件支持开关新功能
- 前端路由守卫可通过配置禁用

## Open Questions

1. **邀请码生成策略**
   - 是否需要实现自动生成邀请码的功能？
   - 邀请码的格式规范是什么？（长度、字符集）
   - 是否需要支持邀请码分组或标签？

2. **问卷答案的可修改性**
   - 用户是否可以重新填写问卷？
   - 如果可以，是否需要保留历史记录？
   - 修改问卷后，如何更新 soul 画像？

3. **多设备访问**
   - 用户是否可以在多个设备上同时登录？
   - 如何处理会话冲突？
   - 是否需要实现设备管理功能？

4. **数据导出和备份**
   - 是否需要提供用户数据导出功能？
   - 如何备份用户数据？
   - 是否需要实现数据恢复功能？

5. **性能优化**
   - 当用户量增长时，SQLite 是否需要迁移到更强大的数据库？
   - 是否需要实现缓存机制？
   - 如何优化问卷页面的加载速度？
