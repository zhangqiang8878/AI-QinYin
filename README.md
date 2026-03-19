# AI亲音 - 胎教音频克隆与生成微信小程序

AI亲音是一款面向孕妈的胎教微信小程序。用户只需上传短至10秒的音频样本（如准爸爸的声音），即可利用前沿的大模型语音克隆技术（TTS），生成具有专属音色的胎教故事、日常对话和胎教音乐，为宝宝带来个性化的陪伴体验。

## ✨ 核心特性

- **声音克隆 (Voice Cloning)**：基于 vllm-omni 和 Qwen3-TTS 技术，快速克隆上传的音频音色。
- **内容生成 (Content Generation)**：提供胎教故事、胎教音乐、古典诗词等多种内容的文本生成与语音合成。
- **微信小程序端 (Mini Program)**：原生微信小程序开发，支持音频播放、历史记录查看、个人中心及订阅管理。
- **订阅与支付 (Subscription & Payment)**：集成微信支付（JSAPI），支持月度、季度、年度套餐及点数充值。
- **云端存储 (Cloud Storage)**：集成阿里云 OSS 服务，安全可靠地存储生成的音频文件。
- **验证码登录 (SMS Auth)**：集成阿里云 SMS 服务，支持手机号快捷登录与注册。

## 🏗️ 系统架构

本项目采用前后端分离架构，配合本地高性能 GPU 节点提供大模型推理服务：

- **前端**：微信小程序原生开发 (WXML/WXSS/JS)。
- **后端**：FastAPI 构建 RESTful API，提供高并发的异步接口。
- **数据库**：MongoDB (Motor 异步驱动) 作为核心数据库；Redis 用于短信验证码和频率限流。
- **大模型节点**：部署于本地或带 GPU 的独立服务器，运行基于 vllm-omni 的 TTS 接口。
- **内网穿透**：通过 FRP (Fast Reverse Proxy) 将本地 TTS 节点的接口安全暴露给云端 FastAPI 服务调用。

详情请参考：[部署与架构文档 (docs/DEPLOY.md)](./docs/DEPLOY.md)

## 📁 目录结构

```text
AI-QinYin-Gemini/
├── backend/                  # FastAPI 后端服务
│   ├── app/                  # 核心应用代码
│   │   ├── api/              # API 路由 (auth, users, voices, contents, payments 等)
│   │   ├── models/           # MongoDB 集合的数据模型 (Pydantic)
│   │   ├── services/         # 第三方服务集成 (OSS, SMS, WeChat Pay, TTS Client)
│   │   └── utils/            # 工具类 (JWT Auth 等)
│   ├── scripts/              # 数据库初始化及环境验证脚本
│   └── tests/                # 单元测试 (pytest)
├── wechat-miniprogram/       # 微信小程序前端
│   ├── pages/                # 小程序页面 (index, generate, history, profile, login, audio 等)
│   ├── utils/                # 小程序工具类 (API 请求封装等)
│   └── tests/                # 小程序端测试 (jest + miniprogram-simulate)
├── frp/                      # FRP 内网穿透配置 (frps.ini, frpc.ini)
├── docs/                     # 项目文档 (包含 DEPLOY.md)
└── .trae/                    # 项目 Spec 设计和规划文档
```

## 🚀 快速启动

### 1. 环境准备

- Python 3.10+
- Node.js (用于运行小程序端测试)
- MongoDB 6.0+
- Redis 7.0+
- 微信开发者工具

### 2. 后端服务启动

1. 进入后端目录并安装依赖：
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

2. 配置环境变量：
   将 `backend/.env.example` 复制为 `backend/.env`，并填入相应的密钥（MongoDB, Redis, 阿里云 SMS/OSS, 微信支付等）。
   > 可以使用验证脚本检查配置是否正确：`python backend/scripts/validate_env.py backend/.env`

3. 初始化数据库索引和基础数据：
   ```bash
   python backend/scripts/init_db.py
   python backend/scripts/init_subscriptions.py
   ```

4. 启动 FastAPI 服务：
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### 3. 微信小程序启动

1. 打开 **微信开发者工具**。
2. 选择 **导入项目**，目录选择项目根目录下的 `wechat-miniprogram` 文件夹。
3. 填入你自己的微信小程序 AppID。
4. 在 `wechat-miniprogram/app.js` 或 `utils/api.js` 中修改后端的 `API_BASE` 地址为你的本地或服务器地址。
5. 编译运行。

### 4. 测试与验证

**后端单元测试：**
```bash
cd backend
pytest tests/ -v
```

**前端单元测试：**
```bash
cd wechat-miniprogram
npm install
npm test
```

## 📖 相关文档

- [系统部署指南](./docs/DEPLOY.md)
- [API 接口设计规范](./docs/specs/03-API设计/API接口文档.md)
- [数据库模型设计](./docs/specs/02-数据模型/数据模型.md)
- [微信支付与订阅服务说明](./docs/specs/04-服务设计/wechat-payment/微信支付服务.md)

---
*本项目规划与开发受 AI 辅助工具支持，相关执行记录保存在 `.trae/` 和 `docs/superpowers/` 目录下。*