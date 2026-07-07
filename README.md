# 迅捷后台管理系统 (Xunjie Admin Dashboard)

这是一个基于 **FastAPI (Python)** 后端和 **Vue 3 + Vite** 前端构建的现代化、高性能后台管理系统开发模板。

---

## 📂 项目结构说明

整个项目采用前后端分离的架构：

```text
xunjie/
├── app/                  # 后端 FastAPI 应用程序目录
│   ├── api/              # API 接口路由层 (类似于 Controller)
│   │   └── v1/           # API 版本 1 (endpoints 对应接口控制器)
│   ├── core/             # 核心配置模块 (配置加载、数据库初始化、安全工具)
│   │   ├── config.py     # 动态配置载入模块
│   │   ├── database.py   # SQLAlchemy 异步连接池与会话管理
│   │   └── security.py   # 密码哈希与校验工具
│   ├── crud/             # 数据库增删改查业务 (DAO / Repository 层)
│   │   └── user.py       # 用户表数据库操作
│   ├── services/         # 核心业务服务层 (Service 层)
│   │   └── auth_service.py # 鉴权与数据初始化种子服务
│   ├── models/           # 数据库 ORM 模型定义目录 (Entity)
│   │   └── user.py       # 用户 ORM 模型
│   ├── schemas/          # Pydantic 数据校验与序列化模式目录 (DTO)
│   │   └── user.py       # 用户 Pydantic 数据规范
│   └── main.py           # FastAPI 实例初始化、应用生命周期与全局中间件配置
├── web/                  # 前端 Vue 3 + TypeScript 应用程序目录
│   ├── src/              # 前端源码
│   │   ├── api/          # 接口请求层
│   │   ├── components/   # 公共组件
│   │   ├── layout/       # 基础布局页面
│   │   ├── router/       # Vue Router 路由配置
│   │   ├── store/        # Pinia 状态管理
│   │   └── views/        # 各业务页面组件 (login, dashboard 等)
│   ├── index.html        # 前端入口 HTML
│   ├── vite.config.ts    # Vite 配置文件
│   └── package.json      # 前端依赖配置
├── .env                  # 当前生效的私有配置文件 (已在 .gitignore 中忽略，请勿提交)
├── .env.dev              # 开发环境配置文件模板 (已配置好本地 MySQL, 开启热重载等)
├── .env.prod             # 生产环境配置文件模板 (已配置好 0.0.0.0, 关闭热重载, 生产密钥提示)
├── .env.example          # 全局环境变量字段参考模板
├── requirements.txt      # 后端依赖项声明文件
└── run.py                # 后端应用本地启动入口脚本
```

---

## ⚙️ 配置文件与环境划分 (Docker 友好)

为了支持本地开发和生产部署，项目提供了两套预设的配置文件模板：

1. **开发环境 (`.env.dev`)**：预设连接本地 `localhost` 数据库，开启 `RELOAD=True` 热重载，配置了 `127.0.0.1` 本地运行地址。
2. **生产环境 (`.env.prod`)**：关闭代码热重载，绑定 `0.0.0.0`（允许 Docker 外部访问端口），提供生成安全 `SECRET_KEY` 的提示和生产数据库占位符。

> **本地开发使用说明**：直接复制 `.env.dev` 命名为 `.env` 即可：
> ```bash
> cp .env.dev .env
> ```

---

## ⚙️ 外部配置覆盖机制

项目启动时会读取以下优先级递增的配置源（后者覆盖前者）：
1. 本地 `.env`（默认加载，用于本地调试）
2. 项目根目录下的 `config.env`（存在时将覆盖 `.env`）
3. 环境变量 `CONFIG_PATH` 所指向的绝对路径文件（最优先，用于部署容器时挂载外部配置文件）
4. 系统环境变量（如系统原生环境变量 `DATABASE_URL`，具有最高优先级）

### 1. 配置参数列表

在 `.env` 或 `config.env` 中支持配置以下核心参数：

| 参数名称 | 默认值/示例 | 说明 |
| :--- | :--- | :--- |
| `PROJECT_NAME` | `迅捷后台管理系统` | 系统名称 |
| `API_V1_STR` | `/api/v1` | 接口前缀路径 |
| `SECRET_KEY` | `supersecretkeyreplaceinproduction` | JWT 加密密钥（生产环境必须替换） |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `10080` | JWT Token 有效期（分钟） |
| `DATABASE_URL` | `mysql+aiomysql://root:666666@localhost:3306/fast_db` | 数据库连接字符串，支持异步 MySQL (`aiomysql`) |
| `ALGORITHM` | `HS256` | JWT 签发签名算法 |
| `CAPTCHA_POLICY` | `0` | 验证码校验策略：`0`-从不开启；`1`-始终开启；`2`-智能阶梯触发 |
| `CAPTCHA_MAX_FAILURES` | `1` | 密码错误最大重试次数，触发验证码阈值（用于策略 2） |
| `CAPTCHA_IP_LIMIT_PERIOD` | `10` | IP 请求统计时间窗口（秒，用于策略 2） |
| `CAPTCHA_IP_LIMIT_COUNT` | `5` | 时间窗口内同 IP 最大登录请求次数，触发验证码阈值（用于策略 2） |
| `BACKEND_CORS_ORIGINS` | `http://localhost,http://localhost:5173,http://localhost:8000` | 跨域允许的来源列表（支持逗号分隔或 JSON 数组） |
| `HOST` | `127.0.0.1` | 本地服务监听地址（Docker 部署时设为 `0.0.0.0`） |
| `PORT` | `8000` | 本地服务监听端口 |
| `RELOAD` | `True` | 是否开启热重载（生产/Docker 环境建议为 `False`） |


### 2. Docker 环境下如何进行配置替换

#### 方法 A：通过挂载外部 `.env` 文件 (推荐)
无需重新构建镜像，只需将您的外部配置文件挂载至容器内的特定路径，并通过设置 `CONFIG_PATH` 告诉容器读取它。

```bash
docker run -d \
  -p 8000:8000 \
  -v /opt/xunjie/my_config.env:/app/config.env \
  -e CONFIG_PATH=/app/config.env \
  --name xunjie-backend \
  xunjie-backend-image
```

#### 方法 B：通过 -e 参数直接覆盖
如果只需要修改数据库连接地址，也可以直接在启动命令中通过环境变量指定：

```bash
docker run -d \
  -p 8000:8000 \
  -e DATABASE_URL="mysql+aiomysql://user:pwd@prod-mysql:3306/fast_db" \
  -e HOST="0.0.0.0" \
  -e RELOAD="False" \
  --name xunjie-backend \
  xunjie-backend-image
```

---

## 🚀 本地开发与运行指南

### 1. 后端 (FastAPI)

1. **创建并激活虚拟环境**：
   ```bash
   python -m venv .venv
   # Windows
   .\.venv\Scripts\activate
   # Linux/macOS
   source .venv/bin/activate
   ```
2. **安装依赖**：
   ```bash
   pip install -r requirements.txt
   ```
3. **数据库准备**：
   请在您的本地 MySQL 中创建名为 `fast_db` 的数据库，并配置 `.env` 中的 `DATABASE_URL`。
4. **启动服务**：
   ```bash
   python run.py
   ```
   后端服务启动后，可以通过访问 [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) 查看 Swagger 交互式 API 文档。

### 2. 前端 (Vue 3 + Vite)

1. **进入前端目录**：
   ```bash
   cd web
   ```
2. **安装依赖**：
   ```bash
   npm install
   ```
3. **启动开发服务器**：
   ```bash
   npm run dev
   ```
    前端服务将启动在 [http://localhost:5173](http://localhost:5173)。

---

## 🔒 AJ-Captcha 验证码安全策略与联调协议

系统引入了行业标准的交互式滑块验证码（AJ-Captcha 协议规范），具备渐进式阶梯激活策略，由后端登录接口统一裁决并驱动前端交互。

### 1. 验证码交互接口
*   **获取验证码** (`POST /api/v1/captcha/get`)：
    *   请求体：`{"captchaType": "blockPuzzle"}`
    *   返回：大图/小图的 Base64 编码、临时追踪 `token` 以及用于前端加密的 16 位 AES `secretKey`。
*   **校验验证码** (`POST /api/v1/captcha/check`)：
    *   请求体：`{"captchaType": "blockPuzzle", "token": "...", "pointJson": "AES加密后的滑动X/Y坐标"}`
    *   返回：`{"repCode": "0000", "repMsg": "success"}`，表明校验通过，将该 `token` 在后端标记为已通过验证。

### 2. 状态码驱动交互流程
登录流程以**状态码 428 (Precondition Required)** 为核心驱动：

1.  **提交登录**：前端发送 `/api/v1/auth/login` 请求（参数：`username`, `password`）。
2.  **后端裁决**：
    *   如果策略判定**不需要**验证码：直接验证密码并返回 JWT Token（200 OK）。
    *   如果策略判定**需要**验证码（或提交的验证凭证缺失/失效）：
        *   返回 **HTTP 428** 状态码，响应体为：
            ```json
            {
              "code": 42801,
              "message": "需要验证码验证",
              "data": null
            }
            ```
3.  **前端响应**：前端拦截到 HTTP 428 且 `code` 为 `42801` 时，主动弹出滑块验证码弹窗。
4.  **人机校验**：用户完成滑动，前端先调用 `/captcha/check` 校验通过，拿到标记为 verified 的 `token`。
5.  **重新提交**：前端将 `token`（或 `token---encryptedPointJson`）作为 `captchaVerification` 参数加入登录请求中重新发送，后端消费该 Token 后完成登录。

### 3. 三种策略说明
*   **策略 0（从不开启）**：登录不进行任何验证码拦截，直接比对密码。
*   **策略 1（始终开启）**：无论如何，第一次登录请求就会被拦截并返回 428，前端必须先弹验证码。
*   **策略 2（智能触发/阶梯触发 - 生产推荐）**：
    *   正常情况下登录直接通过。
    *   一旦该账号**密码输错 1 次**（阈值由 `CAPTCHA_MAX_FAILURES` 配置），或者**同 IP 请求太频繁**（10 秒内请求达 5 次，由 `CAPTCHA_IP_LIMIT_COUNT` 配置），后续的登录请求就会被立刻拦截（返回 428），要求进行滑块验证。
    *   一旦登录成功，该账号和该 IP 的失败记录会自动清空，恢复正常流程。
