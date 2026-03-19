# 本地测试与调试指南

在正式部署到云端服务器之前，建议在本地环境完成完整的测试闭环，以确保各个模块（前端、后端、数据库、TTS 模型服务）协同工作正常。

本指南将指导你如何在本地（单机）运行整个 AI 亲音项目并进行测试验证。

---

## 1. 架构预览 (本地单机模式)

在本地测试时，我们不需要使用 FRP 内网穿透。架构简化如下：

```
┌─────────────────┐       ┌────────────────────────┐
│  微信开发者工具  │──────▶│   本地 FastAPI 后端    │
│  (模拟器/真机)   │       │   (localhost:8000)     │
└─────────────────┘       └─────────┬──────┬───────┘
                                    │      │
                          ┌─────────▼┐   ┌─▼────────┐
                          │ 本地 TTS  │   │ MongoDB  │
                          │ 模拟服务  │   │ & Redis  │
                          │ (:8001)  │   │ (Docker) │
                          └──────────┘   └──────────┘
```

---

## 2. 基础设施启动 (数据库)

为了不污染本地宿主机环境，推荐使用 Docker Compose 仅启动依赖数据库：

创建一个临时的用于本地开发的 `docker-compose.dev.yml` 文件（如果你不想使用全量的 `docker-compose.yml`）：

```yaml
# docker-compose.dev.yml
version: '3.8'
services:
  mongodb:
    image: mongo:6.0
    ports:
      - "27017:27017"
    environment:
      # 为了本地开发方便，可以不设置密码，或设置简单密码
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: password

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

**启动命令：**
```bash
docker-compose -f docker-compose.dev.yml up -d
```

---

## 3. TTS 模拟服务启动

如果你在本地没有足够的 GPU 资源运行真实的 `vllm-omni` 大模型，可以使用我们提供的 Mock TTS 网关进行测试。

在项目根目录下，进入（或创建）`tts-service` 目录，确保有 `server.py` 文件（见任务 5 中的模拟实现）。

**启动模拟服务：**
```bash
cd tts-service
# 如果没有安装依赖，请先执行：pip install fastapi uvicorn pydantic
uvicorn server:app --host 127.0.0.1 --port 8001 --reload
```
服务将在 `http://localhost:8001` 启动。

---

## 4. 后端 API 启动

1. **环境准备：**
   ```bash
   cd backend
   python -m venv venv
   # Windows:
   .\venv\Scripts\Activate.ps1
   # macOS/Linux:
   source venv/bin/activate
   
   pip install -r requirements.txt
   ```

2. **配置 `.env` 文件：**
   在 `backend` 目录下创建 `.env`，修改为本地开发配置：
   ```env
   # 数据库指向本地 Docker
   MONGODB_URI=mongodb://admin:password@localhost:27017/ai_qinyin?authSource=admin
   DATABASE_NAME=ai_qinyin_dev
   
   # Redis 指向本地 Docker
   REDIS_HOST=localhost
   REDIS_PORT=6379
   REDIS_DB=0
   
   # 密钥配置 (开发环境可随便写，除了需要对接真实外部服务的)
   JWT_SECRET=super-secret-local-key
   JWT_ALGORITHM=HS256
   JWT_EXPIRE_HOURS=168
   
   # TTS 服务指向本地模拟网关
   TTS_SERVICE_URL=http://localhost:8001
   
   # (可选) 如果你不需要真实发送短信和上传OSS，代码中会进入 mock 逻辑
   # SMS_ACCESS_KEY_ID=
   # OSS_ACCESS_KEY_ID=
   ```

3. **初始化数据库：**
   ```bash
   python scripts/init_db.py
   python scripts/init_subscriptions.py
   ```

4. **运行 FastAPI：**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

---

## 5. 前端小程序启动

1. 打开 **微信开发者工具**。
2. 导入 `wechat-miniprogram` 文件夹。
3. 找到 `wechat-miniprogram/app.js` 或 `wechat-miniprogram/utils/api.js`。
4. 将 API 请求的基础 URL 修改为本地后端地址：
   ```javascript
   // utils/api.js
   const API_BASE = 'http://127.0.0.1:8000/api';
   ```
5. 在微信开发者工具的右上角 **详情 -> 本地设置** 中，**勾选“不校验合法域名、web-view（业务域名）、TLS版本以及HTTPS证书”**。
   *(因为本地使用的是 HTTP 而不是 HTTPS)*

---

## 6. 测试流程验证

请按照以下顺序在微信开发者工具（或真机预览）中进行点击测试：

1. **登录注册流程：**
   - 进入“我的”页面，点击“去登录”。
   - 输入手机号（如 `13800138000`），点击获取验证码。
   - *(由于是本地 mock 模式，你可以在后端终端日志中看到生成的验证码，或者随便输入一个通过 mock 逻辑)*
   - 点击登录，应成功跳转回首页，并能在“我的”页面看到默认的积分（如 0 或 初始化送的积分）。

2. **音色管理流程：**
   - 此流程暂需配合前端直传 OSS。如果本地未配置真实 OSS AK/SK，上传环节可能会报错。
   - **调试建议：** 可以使用 Postman 直接调用 `/api/voices` 接口，手动插入一条音色数据，然后在小程序的“生成”页面验证是否能拉取到音色列表。

3. **内容生成流程：**
   - 切换到“生成”页面。
   - 走完三个步骤：选择音色 -> 选择内容类型和主题 -> 点击生成。
   - 观察后端控制台日志，确认请求是否成功发送到了本地的 TTS 模拟服务（8001 端口）。
   - 成功后应跳转到“历史”页面。

4. **历史记录与播放：**
   - 在“历史”页面下拉刷新，应该能看到刚刚生成的音频记录。
   - 点击记录进入播放详情页，验证进度条和播放按钮的状态切换（因为是 mock 的音频 URL，可能无法真正发声，但能验证 UI 逻辑）。

---

## 7. 自动化测试 (TDD 验证)

在任何代码修改后，务必运行单元测试来保证核心逻辑未被破坏。

**后端测试：**
```bash
cd backend
# 激活虚拟环境
pytest tests/ -v
```

**前端测试：**
```bash
cd wechat-miniprogram
npm test
```

## 8. 常见问题排查

- **Q: 小程序请求后端提示 "request:fail url not in domain list"**
  - **A**: 记得在微信开发者工具的本地设置中勾选“不校验合法域名”。
- **Q: 后端连接 MongoDB 失败**
  - **A**: 检查 Docker 是否正常运行，并且 `docker-compose.dev.yml` 中的账号密码与 `backend/.env` 中的 `MONGODB_URI` 匹配。
- **Q: 验证码收不到**
  - **A**: 如果没有配置阿里云真实 AK/SK，`sms_service.py` 默认会返回成功。你可以在后端的终端输出中打印出生成的验证码（开发模式下 `send_code` 接口的返回值里包含了 `code`）。