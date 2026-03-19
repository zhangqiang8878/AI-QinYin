# AI亲音 - 胎教微信小程序设计文档

> 设计日期: 2026-03-17

## 项目概述

AI亲音是一款基于语音克隆技术的胎教微信小程序，核心功能是通过10秒语音样本克隆父母声音，为胎儿提供个性化的胎教内容。

### 核心价值

- **声音克隆**: 10秒样本即可克隆父母声音
- **个性化内容**: 通义千问API生成定制胎教内容
- **多音色支持**: 支持妈妈、爸爸等多种音色
- **便捷使用**: 微信小程序，随时随地使用

---

## 系统架构

### 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                      微信小程序前端                          │
└─────────────────────────────────────────────────────────────┘
                            ↓ HTTPS
┌─────────────────────────────────────────────────────────────┐
│                   阿里云服务器 (云后端)                       │
├─────────────────────────────────────────────────────────────┤
│  FastAPI服务  │  MongoDB  │  OSS存储  │  微信支付           │
└─────────────────────────────────────────────────────────────┘
          ↓ FRP隧道                      ↓ API调用
┌──────────────────────────┐    ┌─────────────────────────────┐
│  本地服务器 (16GB VRAM)  │    │      通义千问 API           │
│  vllm-omni + Qwen3-TTS   │    │      内容生成服务           │
└──────────────────────────┘    └─────────────────────────────┘
```

### 部署方案

| 服务 | 部署位置 | 说明 |
|------|----------|------|
| 微信小程序 | 微信平台 | 前端应用 |
| 业务后端 | 阿里云 | FastAPI + MongoDB |
| TTS服务 | 本地服务器 | 16GB VRAM, vllm-omni |
| FRP隧道 | 阿里云→本地 | 内网穿透，端口18001 |
| 对象存储 | 阿里云OSS | 音频文件存储 |
| 内容生成 | 云端API | 通义千问 |

---

## 数据模型

### 用户表 (users)

```python
{
    "_id": ObjectId,
    "phone": "13800138000",           # 手机号（唯一）
    "nickname": "准妈妈小王",          # 昵称
    "avatar": "https://...",          # 头像URL
    "pregnancy_weeks": 20,            # 孕周（可选）
    "created_at": datetime,
    "last_login": datetime
}
```

### 音色表 (voice_samples)

```python
{
    "_id": ObjectId,
    "user_id": ObjectId,              # 关联用户
    "voice_name": "妈妈的声音",        # 音色名称（用户自定义）
    "voice_type": "mom",              # 音色类型：mom/dad/other
    "audio_url": "https://...",       # 10秒样本音频URL
    "duration": 10.0,                 # 音频时长（秒）
    "voice_id": "voice_abc123",       # TTS服务生成的音色ID
    "is_default": false,              # 是否为默认音色
    "created_at": datetime,
    "updated_at": datetime
}
```

### 订阅表 (subscriptions)

```python
{
    "_id": ObjectId,
    "user_id": ObjectId,
    "plan_type": "monthly",           # monthly/quarterly/yearly
    "status": "active",               # active/expired/cancelled
    "total_credits": 100,             # 总点数（每月/季/年可用次数）
    "used_credits": 30,               # 已用点数
    "started_at": datetime,
    "expires_at": datetime,
    "payment_id": ObjectId            # 关联支付记录
}
```

### 支付记录表 (payments)

```python
{
    "_id": ObjectId,
    "user_id": ObjectId,
    "order_id": "ORDER_2026031712345678",  # 商户订单号（唯一）
    "transaction_id": "wx1234567890",       # 微信支付交易号
    "plan_type": "monthly",                  # 套餐类型
    "amount": 2990,                          # 支付金额（分）
    "status": "success",                     # pending/success/failed/refunded
    "payment_method": "wechat_pay",          # 支付方式
    "paid_at": datetime,                     # 支付完成时间
    "created_at": datetime,
    "raw_response": {}                       # 微信支付回调原始数据
}
```

### 生成记录表 (generated_contents)

```python
{
    "_id": ObjectId,
    "user_id": ObjectId,
    "voice_id": ObjectId,             # 使用的音色
    "content_type": "story",          # story/music/daily/knowledge
    "text_content": "...",            # 生成的文本内容
    "audio_url": "https://...",       # 生成的音频URL
    "duration": 120.5,                # 音频时长（秒）
    "created_at": datetime
}
```

---

## API设计

### 认证相关

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/auth/send-code | 发送验证码 |
| POST | /api/auth/login | 手机号验证码登录 |
| GET | /api/auth/profile | 获取用户信息 |
| PUT | /api/auth/profile | 更新用户信息 |

### 音色管理

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/voice/samples | 创建新音色 |
| GET | /api/voice/samples | 获取用户音色列表 |
| PUT | /api/voice/samples/{id} | 更新音色信息 |
| DELETE | /api/voice/samples/{id} | 删除音色 |
| PUT | /api/voice/samples/{id}/default | 设为默认音色 |

### 内容生成

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/content/generate-text | 生成文本内容 |
| POST | /api/content/synthesize | 文本转语音 |
| POST | /api/content/generate-full | 一键生成（文本+语音） |
| GET | /api/content/templates | 获取内容模板列表 |

### 历史记录

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/history | 获取生成历史 |
| GET | /api/history/{id} | 获取单条记录详情 |
| DELETE | /api/history/{id} | 删除历史记录 |

### 订阅管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/subscription/plans | 获取套餐列表 |
| POST | /api/subscription/subscribe | 创建订阅订单 |
| GET | /api/subscription/status | 获取订阅状态 |
| POST | /api/payment/create | 创建支付订单 |
| POST | /api/payment/callback | 微信支付回调 |

---

## 前端页面结构

```
pages/
├── index/              # 首页
│   └── 展示功能入口、快捷操作
├── login/              # 登录页
│   └── 手机号验证码登录
├── profile/            # 个人中心
│   └── 用户信息、订阅状态、设置
├── voice-sample/       # 声音采样
│   ├── index/          # 音色列表
│   ├── create/         # 创建音色
│   └── edit/           # 编辑音色
├── generate/           # 生成页
│   └── 内容类型选择、参数填写、音色选择
├── history/            # 历史记录
│   └── 生成内容列表
├── player/             # 播放页
│   └── 音频播放、下载
├── trial/              # 试用页
│   └── 免费试用介绍
└── purchase/           # 购买页
    └── 套餐选择、支付
```

---

## TTS服务设计

### 服务架构

```
┌─────────────────────────────────────────────────────────────┐
│                     本地服务器 (16GB VRAM)                    │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐   │
│  │              vllm-omni TTS Service                  │   │
│  │  ┌─────────────────────────────────────────────┐    │   │
│  │  │  Qwen3-TTS-12Hz-1.7B-CustomVoice Model      │    │   │
│  │  │  - Voice Cloning (10s sample)               │    │   │
│  │  │  - Multi-speaker support                    │    │   │
│  │  └─────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────┘   │
│                           ↓                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              FastAPI Gateway (Port 8001)            │   │
│  │  - /clone    创建音色                               │   │
│  │  - /synthesize  生成语音                            │   │
│  │  - /health   健康检查                               │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### TTS API

**创建音色**
```
POST /clone
Content-Type: multipart/form-data

Request:
  - audio_file: 10秒音频文件
  - voice_name: 音色名称（可选）

Response:
{
    "success": true,
    "data": {
        "voice_id": "voice_abc123",
        "duration": 10.0
    }
}
```

**生成语音**
```
POST /synthesize
Content-Type: application/json

Request:
{
    "voice_id": "voice_abc123",
    "text": "宝宝你好...",
    "speed": 1.0,
    "emotion": "gentle"
}

Response:
{
    "success": true,
    "data": {
        "audio_url": "https://oss.../output.wav",
        "duration": 15.2
    }
}
```

### FRP配置

```ini
# frpc.ini (本地服务器)
[common]
server_addr = your-frp-server.com
server_port = 7000

[tts-service]
type = tcp
local_ip = 127.0.0.1
local_port = 8001
remote_port = 18001
```

### 容错处理

| 场景 | 处理方式 |
|------|----------|
| 服务不可用 | 云后端检测健康状态，降级提示 |
| 生成超时 | 30秒超时，支持重试队列 |
| 并发限制 | 本地限制并发2-3个，超出排队 |

---

## 内容生成集成

### 内容类型

| 类型 | 名称 | 说明 |
|------|------|------|
| story | 胎教故事 | 主题式故事创作 |
| music | 音乐欣赏 | 古典音乐介绍 |
| daily | 日常对话 | 场景化对话内容 |
| knowledge | 孕期知识 | 胎儿发育科普 |

### 生成模板示例

```python
CONTENT_TEMPLATES = {
    "story": {
        "name": "胎教故事",
        "prompt_template": """请为孕{weeks}周的宝宝创作一个温馨的胎教故事。
要求：
- 主题：{theme}
- 语言温柔、节奏舒缓
- 适合朗读，时长约{duration}分钟
- 以"宝宝你好"开头""",
        "themes": ["自然", "友情", "勇气", "爱", "成长"]
    },

    "daily": {
        "name": "日常对话",
        "prompt_template": """请创作一段孕{weeks}周的妈妈与宝宝的日常对话。
场景：{scene}
要求：
- 语言自然亲切
- 包含对宝宝的关爱
- 时长约{duration}分钟""",
        "scenes": ["早晨起床", "午休时光", "晚间睡前", "户外散步"]
    }
}
```

### 生成流程

```
用户选择内容类型 → 填写参数 → Qwen生成文本 →
选择音色 → TTS合成语音 → 返回音频URL
```

---

## 商业模式

### 用户等级与权益

| 用户类型 | 音色数量 | 每日生成次数 | 有效期 |
|----------|----------|--------------|--------|
| 试用用户 | 1个 | 3次 | 7天 |
| 月度会员 | 10个 | 100次/月 | 30天 |
| 季度会员 | 10个 | 350次/季 | 90天 |
| 年度会员 | 10个 | 1500次/年 | 365天 |

### 定价方案

| 套餐 | 价格 | 说明 |
|------|------|------|
| 月度会员 | ¥29.9/月 | 适合短期体验 |
| 季度会员 | ¥69.9/季 | 性价比之选 |
| 年度会员 | ¥199.9/年 | 最优惠 |

---

## 安全设计

### 认证与授权

- 短信验证码登录，验证码有效期5分钟
- JWT Token认证，有效期7天
- 敏感操作需二次验证

### 数据安全

- 音频文件OSS私有存储，签名URL访问
- 用户数据加密存储
- API请求频率限制

### 隐私保护

- 最小化数据收集
- 用户可删除所有个人数据
- 符合微信小程序隐私规范

---

## 技术栈

| 层级 | 技术选型 |
|------|----------|
| 前端 | 微信小程序原生开发 |
| 后端框架 | FastAPI (Python 3.10+) |
| 数据库 | MongoDB 6.0 |
| TTS引擎 | vllm-omni + Qwen3-TTS |
| 内容生成 | 通义千问API |
| 对象存储 | 阿里云OSS |
| 内网穿透 | FRP |
| 部署 | 阿里云ECS + 本地服务器 |

---

## 项目文件结构

```
AI-QinYin/
├── model_cache/                    # 模型缓存（已下载）
│   ├── Qwen3-TTS-12Hz-1.7B-Base/
│   ├── Qwen3-TTS-12Hz-1.7B-CustomVoice/
│   └── Qwen3-TTS-12Hz-1.7B-VoiceDesign/
├── backend/                        # 后端服务
│   ├── app/
│   │   ├── api/                    # API路由
│   │   ├── models/                 # 数据模型
│   │   ├── services/               # 业务逻辑
│   │   ├── utils/                  # 工具函数
│   │   └── config.py               # 配置文件
│   ├── requirements.txt
│   └── main.py
├── tts-service/                    # TTS服务（本地部署）
│   ├── server.py                   # FastAPI网关
│   ├── voice_cloner.py             # 音色克隆
│   └── synthesizer.py              # 语音合成
├── miniprogram/                    # 微信小程序
│   ├── pages/                      # 页面
│   ├── components/                 # 组件
│   ├── utils/                      # 工具
│   └── app.json                    # 配置
└── docs/                           # 文档
    └── superpowers/specs/          # 设计文档
```

---

## API详细设计

### 认证相关 API

#### 发送验证码
```
POST /api/auth/send-code
Content-Type: application/json

Request:
{
    "phone": "13800138000"
}

Response (成功):
{
    "success": true,
    "data": {
        "message": "验证码已发送",
        "expires_in": 300
    }
}

Response (失败):
{
    "success": false,
    "error": {
        "code": "RATE_LIMITED",
        "message": "验证码发送过于频繁，请1分钟后重试"
    }
}
```

#### 手机号登录
```
POST /api/auth/login
Content-Type: application/json

Request:
{
    "phone": "13800138000",
    "code": "123456"
}

Response (成功):
{
    "success": true,
    "data": {
        "token": "eyJhbGciOiJIUzI1NiIs...",
        "expires_in": 604800,
        "user": {
            "id": "507f1f77bcf86cd799439011",
            "phone": "138****8000",
            "nickname": "准妈妈小王",
            "avatar": "https://...",
            "is_new_user": false
        }
    }
}

Response (失败):
{
    "success": false,
    "error": {
        "code": "INVALID_CODE",
        "message": "验证码错误或已过期"
    }
}
```

#### 获取/更新用户信息
```
GET /api/auth/profile
Authorization: Bearer <token>

Response:
{
    "success": true,
    "data": {
        "id": "507f1f77bcf86cd799439011",
        "phone": "138****8000",
        "nickname": "准妈妈小王",
        "avatar": "https://...",
        "pregnancy_weeks": 20,
        "subscription": {
            "type": "monthly",
            "status": "active",
            "remaining_credits": 70,
            "expires_at": "2026-04-17T00:00:00Z"
        }
    }
}

PUT /api/auth/profile
Authorization: Bearer <token>
Content-Type: application/json

Request:
{
    "nickname": "幸福准妈",
    "pregnancy_weeks": 21
}

Response:
{
    "success": true,
    "data": {
        "id": "507f1f77bcf86cd799439011",
        "nickname": "幸福准妈",
        "pregnancy_weeks": 21
    }
}
```

### 音色管理 API

#### 创建音色
```
POST /api/voice/samples
Authorization: Bearer <token>
Content-Type: multipart/form-data

Request:
- audio_file: 音频文件 (10秒, wav/mp3/m4a, max 5MB)
- voice_name: "妈妈的声音"
- voice_type: "mom"

Response (成功):
{
    "success": true,
    "data": {
        "id": "507f1f77bcf86cd799439012",
        "voice_name": "妈妈的声音",
        "voice_type": "mom",
        "audio_url": "https://oss.../sample.wav",
        "duration": 10.5,
        "voice_id": "voice_abc123",
        "is_default": true,
        "created_at": "2026-03-17T10:30:00Z"
    }
}

Response (失败 - 音色数量超限):
{
    "success": false,
    "error": {
        "code": "VOICE_LIMIT_EXCEEDED",
        "message": "试用用户最多创建1个音色，请升级会员"
    }
}
```

#### 获取音色列表
```
GET /api/voice/samples
Authorization: Bearer <token>

Response:
{
    "success": true,
    "data": {
        "voices": [
            {
                "id": "507f1f77bcf86cd799439012",
                "voice_name": "妈妈的声音",
                "voice_type": "mom",
                "audio_url": "https://oss.../sample.wav",
                "duration": 10.5,
                "is_default": true,
                "created_at": "2026-03-17T10:30:00Z"
            }
        ],
        "total": 1,
        "limit": 10
    }
}
```

#### 更新/删除音色
```
PUT /api/voice/samples/{id}
Authorization: Bearer <token>
Content-Type: application/json

Request:
{
    "voice_name": "温柔妈妈声"
}

Response:
{
    "success": true,
    "data": {
        "id": "507f1f77bcf86cd799439012",
        "voice_name": "温柔妈妈声"
    }
}

DELETE /api/voice/samples/{id}
Authorization: Bearer <token>

Response:
{
    "success": true,
    "data": {
        "message": "音色已删除"
    }
}
```

### 内容生成 API

#### 生成文本内容
```
POST /api/content/generate-text
Authorization: Bearer <token>
Content-Type: application/json

Request:
{
    "content_type": "story",
    "params": {
        "theme": "自然",
        "duration_minutes": 3,
        "pregnancy_weeks": 20
    }
}

Response:
{
    "success": true,
    "data": {
        "text_content": "宝宝你好，今天妈妈要给你讲一个关于大自然的故事...",
        "word_count": 450,
        "estimated_duration": 180
    }
}
```

#### 文本转语音
```
POST /api/content/synthesize
Authorization: Bearer <token>
Content-Type: application/json

Request:
{
    "voice_id": "507f1f77bcf86cd799439012",
    "text": "宝宝你好...",
    "speed": 1.0,
    "emotion": "gentle"
}

Response:
{
    "success": true,
    "data": {
        "id": "507f1f77bcf86cd799439013",
        "audio_url": "https://oss.../output.wav?signature=...",
        "duration": 180.5,
        "created_at": "2026-03-17T10:35:00Z"
    }
}

Response (失败 - 点数不足):
{
    "success": false,
    "error": {
        "code": "INSUFFICIENT_CREDITS",
        "message": "本月生成次数已用完，请升级套餐"
    }
}
```

#### 一键生成
```
POST /api/content/generate-full
Authorization: Bearer <token>
Content-Type: application/json

Request:
{
    "content_type": "story",
    "voice_id": "507f1f77bcf86cd799439012",
    "params": {
        "theme": "自然",
        "duration_minutes": 3
    }
}

Response:
{
    "success": true,
    "data": {
        "id": "507f1f77bcf86cd799439013",
        "text_content": "宝宝你好...",
        "audio_url": "https://oss.../output.wav?signature=...",
        "duration": 180.5,
        "created_at": "2026-03-17T10:35:00Z"
    }
}
```

### 订阅管理 API

#### 获取套餐列表
```
GET /api/subscription/plans

Response:
{
    "success": true,
    "data": {
        "plans": [
            {
                "type": "monthly",
                "name": "月度会员",
                "price": 2990,
                "credits": 100,
                "duration_days": 30,
                "description": "适合短期体验"
            },
            {
                "type": "quarterly",
                "name": "季度会员",
                "price": 6990,
                "credits": 350,
                "duration_days": 90,
                "description": "性价比之选"
            },
            {
                "type": "yearly",
                "name": "年度会员",
                "price": 19990,
                "credits": 1500,
                "duration_days": 365,
                "description": "最优惠"
            }
        ]
    }
}
```

#### 创建订阅订单
```
POST /api/subscription/subscribe
Authorization: Bearer <token>
Content-Type: application/json

Request:
{
    "plan_type": "monthly"
}

Response:
{
    "success": true,
    "data": {
        "order_id": "ORDER_2026031712345678",
        "plan_type": "monthly",
        "amount": 2990,
        "created_at": "2026-03-17T10:40:00Z"
    }
}
```

---

## 微信支付集成

### 支付流程

```
1. 小程序调用 wx.requestPayment() 前的准备工作:
   - 后端调用微信支付统一下单API
   - 生成预支付交易会话标识(prepay_id)
   - 计算签名并返回支付参数

2. 用户完成支付后:
   - 微信服务器回调后端通知接口
   - 后端验证签名，更新订单状态
   - 更新用户订阅状态和点数
```

### 创建支付订单
```
POST /api/payment/create
Authorization: Bearer <token>
Content-Type: application/json

Request:
{
    "order_id": "ORDER_2026031712345678"
}

Response:
{
    "success": true,
    "data": {
        "timeStamp": "1710662400",
        "nonceStr": "abc123...",
        "package": "prepay_id=wx123...",
        "signType": "RSA",
        "paySign": "签名值..."
    }
}
```

### 微信支付回调
```
POST /api/payment/callback
Content-Type: application/json
Wechatpay-Signature: 签名
Wechatpay-Timestamp: 时间戳
Wechatpay-Nonce: 随机串

Request (微信服务器发送):
{
    "id": "EV-201802...",
    "create_time": "2026-03-17T10:41:00+08:00",
    "resource_type": "encrypt-resource",
    "event_type": "TRANSACTION.SUCCESS",
    "resource": {
        "algorithm": "AEAD_AES_256_GCM",
        "ciphertext": "加密内容...",
        "nonce": "随机串",
        "associated_data": "transaction"
    }
}

Response:
{
    "code": "SUCCESS",
    "message": "成功"
}
```

### 签名验证流程

```python
# 回调签名验证步骤
1. 从请求头获取:
   - Wechatpay-Signature: Base64编码的签名
   - Wechatpay-Timestamp: 时间戳
   - Wechatpay-Nonce: 随机字符串
   - Wechatpay-Serial: 平台证书序列号

2. 构造验签名串:
   签名串 = 时间戳 + "\n" + 随机串 + "\n" + 请求体 + "\n"

3. 使用微信平台公钥验证签名:
   - 从微信平台证书获取公钥
   - 使用SHA256withRSA验证签名

4. 解密回调数据:
   - 使用API v3密钥解密resource.ciphertext
   - 验证订单金额、商户号等信息
```

### 退款处理

```python
# 退款场景和处理
REFUND_RULES = {
    "within_7_days": {
        "condition": "购买7天内且未使用",
        "refund_ratio": 1.0,
        "description": "全额退款"
    },
    "within_30_days": {
        "condition": "购买30天内",
        "refund_ratio": 0.8,
        "description": "扣除已使用点数对应金额"
    },
    "after_30_days": {
        "condition": "超过30天",
        "refund_ratio": 0,
        "description": "不支持退款"
    }
}

# 退款API调用
POST https://api.mch.weixin.qq.com/v3/refund/domestic/refunds
{
    "transaction_id": "wx123...",
    "out_refund_no": "REFUND_2026031712345678",
    "amount": {
        "refund": 2990,
        "total": 2990,
        "currency": "CNY"
    },
    "reason": "用户申请退款"
}
```

---

## 短信服务集成

### 服务提供商

**阿里云短信服务 (Aliyun SMS)**

| 配置项 | 值 | 说明 |
|--------|-----|------|
| 服务商 | 阿里云 | 短信服务商 |
| SDK | alibabacloud-dysmsapi20170525 | Python SDK |
| API版本 | 2017-05-25 | 短信API版本 |
| 区域 | cn-hangzhou | 服务区域 |
| 签名名称 | AI亲音 | 已审核通过 |
| 模板CODE | SMS_123456789 | 验证码模板 |
| Endpoint | dysmsapi.aliyuncs.com | API端点 |

### 凭证配置

```python
# config/sms.py
from dataclasses import dataclass
from alibabacloud_credentials.client import Client as CredentialClient
from alibabacloud_credentials.models import Config as CredentialConfig

@dataclass
class SMSConfig:
    """短信服务配置"""
    access_key_id: str          # 从环境变量 ALIBABA_CLOUD_ACCESS_KEY_ID
    access_key_secret: str      # 从环境变量 ALIBABA_CLOUD_ACCESS_KEY_SECRET
    sign_name: str = "AI亲音"
    template_code: str = "SMS_123456789"
    region_id: str = "cn-hangzhou"
    endpoint: str = "dysmsapi.aliyuncs.com"

    @classmethod
    def from_env(cls) -> "SMSConfig":
        """从环境变量加载配置"""
        import os
        return cls(
            access_key_id=os.getenv("ALIBABA_CLOUD_ACCESS_KEY_ID", ""),
            access_key_secret=os.getenv("ALIBABA_CLOUD_ACCESS_KEY_SECRET", ""),
        )
```

### 短信模板

```
模板名称: 胎教小程序验证码
模板内容: 您的验证码为${code}，有效期5分钟，请勿泄露给他人。
模板CODE: SMS_123456789
申请说明: 用于小程序用户手机号验证
```

### 完整实现代码

```python
# services/sms_service.py
import json
import random
import logging
from datetime import datetime, timedelta
from typing import Optional, Tuple
from dataclasses import dataclass

from alibabacloud_dysmsapi20170525.client import Client
from alibabacloud_dysmsapi20170525 import models as sms_models
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_tea_util.client import Client as UtilClient

logger = logging.getLogger(__name__)


@dataclass
class SMSResult:
    """短信发送结果"""
    success: bool
    request_id: Optional[str] = None
    biz_id: Optional[str] = None  # 发送回执ID，可用于查询发送状态
    code: Optional[str] = None
    message: Optional[str] = None
    error_detail: Optional[str] = None


@dataclass
class RateLimitResult:
    """频率限制检查结果"""
    allowed: bool
    retry_after: int = 0  # 秒
    reason: str = ""


class SMSService:
    """阿里云短信服务"""

    # 频率限制配置
    RATE_LIMITS = {
        "per_minute": 1,    # 每分钟最多1条
        "per_hour": 5,      # 每小时最多5条
        "per_day": 10,      # 每天最多10条
    }

    # 错误码映射
    ERROR_CODES = {
        "OK": "请求成功",
        "isp.RAM_PERMISSION_DENY": "RAM权限不足",
        "isv.OUT_OF_SERVICE": "业务停机",
        "isv.PRODUCT_UN_SUBSCRIPT": "未开通云通信产品",
        "isv.PRODUCT_UNSUBSCRIBE": "产品未开通",
        "isv.ACCOUNT_NOT_EXISTS": "账户不存在",
        "isv.ACCOUNT_ABNORMAL": "账户异常",
        "isv.SMS_TEMPLATE_ILLEGAL": "模板不合法",
        "isv.SMS_SIGNATURE_ILLEGAL": "签名不合法",
        "isv.INVALID_PARAMETERS": "参数异常",
        "isv.MOBILE_NUMBER_ILLEGAL": "手机号码格式错误",
        "isv.MOBILE_COUNT_OVER_LIMIT": "手机号码数量超过限制",
        "isv.TEMPLATE_MISSING_PARAMETERS": "模板缺少变量",
        "isv.BUSINESS_LIMIT_CONTROL": "业务限流",
        "isv.INVALID_JSON_PARAM": "JSON参数不合法",
        "isv.AMOUNT_NOT_ENOUGH": "账户余额不足",
        "isv.TEMPLATE_JSON_PARSE_ERROR": "模板变量解析错误",
        "isv.SIGN_NAME_ILLEGAL": "签名不合法",
        "isv.SIGN_NAME_DURING_AUDIT": "签名审核中",
        "isv.SIGN_NAME_UNAUDITED": "签名未通过审核",
        "isv.SIGN_NAME_NOT_EXISTS": "签名不存在",
        "isv.TEMPLATE_NOT_EXISTS": "模板不存在",
        "isv.TEMPLATE_UNAUDITED": "模板未通过审核",
        "isv.TEMPLATE_DURING_AUDIT": "模板审核中",
        "isv.BLACK_KEY_CONTROL_LIMIT": "黑名单管控",
        "isv.DOMESTIC_NUMBER_NOT_SUPPORTED": "不支持国内号码",
    }

    def __init__(self, config: "SMSConfig"):
        """初始化短信客户端"""
        self.config = config
        self.sign_name = config.sign_name
        self.template_code = config.template_code

        # 创建OpenAPI配置
        openapi_config = open_api_models.Config(
            access_key_id=config.access_key_id,
            access_key_secret=config.access_key_secret,
        )
        openapi_config.endpoint = config.endpoint
        openapi_config.region_id = config.region_id

        # 创建客户端
        self.client = Client(openapi_config)
        self.runtime = util_models.RuntimeOptions(
            connect_timeout=5000,    # 连接超时 5秒
            read_timeout=10000,      # 读取超时 10秒
            max_attempts=3,          # 最大重试次数
            autoretry=True,          # 自动重试
        )

    def generate_code(self) -> str:
        """生成6位验证码"""
        return str(random.randint(100000, 999999))

    def validate_phone(self, phone: str) -> bool:
        """验证手机号格式"""
        import re
        pattern = r'^1[3-9]\d{9}$'
        return bool(re.match(pattern, phone))

    async def check_rate_limit(self, phone: str, redis_client) -> RateLimitResult:
        """检查发送频率限制"""
        now = datetime.utcnow()
        minute_key = f"sms:limit:{phone}:minute:{now.strftime('%Y%m%d%H%M')}"
        hour_key = f"sms:limit:{phone}:hour:{now.strftime('%Y%m%d%H')}"
        day_key = f"sms:limit:{phone}:day:{now.strftime('%Y%m%d')}"

        # 检查每分钟限制
        minute_count = await redis_client.get(minute_key)
        if minute_count and int(minute_count) >= self.RATE_LIMITS["per_minute"]:
            return RateLimitResult(
                allowed=False,
                retry_after=60,
                reason="发送过于频繁，请1分钟后再试"
            )

        # 检查每小时限制
        hour_count = await redis_client.get(hour_key)
        if hour_count and int(hour_count) >= self.RATE_LIMITS["per_hour"]:
            return RateLimitResult(
                allowed=False,
                retry_after=3600,
                reason="每小时最多发送5条验证码"
            )

        # 检查每天限制
        day_count = await redis_client.get(day_key)
        if day_count and int(day_count) >= self.RATE_LIMITS["per_day"]:
            return RateLimitResult(
                allowed=False,
                retry_after=86400,
                reason="每天最多发送10条验证码"
            )

        return RateLimitResult(allowed=True)

    async def increment_rate_limit(self, phone: str, redis_client):
        """增加发送计数"""
        now = datetime.utcnow()

        # 每分钟计数
        minute_key = f"sms:limit:{phone}:minute:{now.strftime('%Y%m%d%H%M')}"
        await redis_client.incr(minute_key)
        await redis_client.expire(minute_key, 60)

        # 每小时计数
        hour_key = f"sms:limit:{phone}:hour:{now.strftime('%Y%m%d%H')}"
        await redis_client.incr(hour_key)
        await redis_client.expire(hour_key, 3600)

        # 每天计数
        day_key = f"sms:limit:{phone}:day:{now.strftime('%Y%m%d')}"
        await redis_client.incr(day_key)
        await redis_client.expire(day_key, 86400)

    async def send_verification_code(
        self,
        phone: str,
        code: str,
        redis_client=None
    ) -> SMSResult:
        """发送验证码短信

        Args:
            phone: 手机号码
            code: 验证码
            redis_client: Redis客户端（用于频率限制）

        Returns:
            SMSResult: 发送结果
        """
        # 验证手机号格式
        if not self.validate_phone(phone):
            return SMSResult(
                success=False,
                code="INVALID_PHONE",
                message="手机号码格式错误"
            )

        # 检查频率限制
        if redis_client:
            rate_result = await self.check_rate_limit(phone, redis_client)
            if not rate_result.allowed:
                return SMSResult(
                    success=False,
                    code="RATE_LIMITED",
                    message=rate_result.reason,
                    error_detail=f"retry_after: {rate_result.retry_after}s"
                )

        try:
            # 构建请求
            request = sms_models.SendSmsRequest(
                phone_numbers=phone,
                sign_name=self.sign_name,
                template_code=self.template_code,
                template_param=json.dumps({"code": code})
            )

            # 发送请求
            response = self.client.send_sms_with_options(request, self.runtime)

            # 解析响应
            body = response.body

            if body.code == "OK":
                logger.info(
                    "SMS sent successfully",
                    extra={
                        "phone": phone[:3] + "****" + phone[-4:],
                        "request_id": body.request_id,
                        "biz_id": body.biz_id
                    }
                )

                # 增加发送计数
                if redis_client:
                    await self.increment_rate_limit(phone, redis_client)

                return SMSResult(
                    success=True,
                    request_id=body.request_id,
                    biz_id=body.biz_id,
                    code=body.code,
                    message="发送成功"
                )
            else:
                error_msg = self.ERROR_CODES.get(body.code, body.message)
                logger.warning(
                    "SMS send failed",
                    extra={
                        "phone": phone[:3] + "****" + phone[-4:],
                        "code": body.code,
                        "message": error_msg
                    }
                )
                return SMSResult(
                    success=False,
                    request_id=body.request_id,
                    code=body.code,
                    message=error_msg,
                    error_detail=body.message
                )

        except Exception as e:
            logger.error(
                "SMS send exception",
                extra={
                    "phone": phone[:3] + "****" + phone[-4:],
                    "error": str(e)
                },
                exc_info=True
            )
            return SMSResult(
                success=False,
                code="EXCEPTION",
                message="短信发送异常",
                error_detail=str(e)
            )

    async def query_send_status(
        self,
        phone: str,
        biz_id: str
    ) -> dict:
        """查询短信发送状态

        Args:
            phone: 手机号码
            biz_id: 发送回执ID

        Returns:
            dict: 发送状态信息
        """
        try:
            request = sms_models.QuerySendDetailsRequest(
                phone_number=phone,
                biz_id=biz_id,
                send_date=datetime.now().strftime("%Y%m%d"),
                page_size=10,
                current_page=1
            )

            response = self.client.query_send_details_with_options(request, self.runtime)

            if response.body.code == "OK":
                return {
                    "success": True,
                    "total_count": response.body.total_count,
                    "details": [
                        {
                            "phone": item.phone_num,
                            "send_status": item.send_status,  # 1-等待回执 2-发送成功 3-发送失败
                            "err_code": item.err_code,
                            "template": item.template_code,
                            "content": item.content,
                            "send_time": item.send_date,
                        }
                        for item in (response.body.sms_send_detail_ons or [])
                    ]
                }

            return {
                "success": False,
                "code": response.body.code,
                "message": response.body.message
            }

        except Exception as e:
            logger.error(f"Query SMS status failed: {e}")
            return {"success": False, "error": str(e)}


class VerificationCodeManager:
    """验证码管理器"""

    CODE_EXPIRY = 300  # 验证码有效期 5分钟

    def __init__(self, redis_client, sms_service: SMSService):
        self.redis = redis_client
        self.sms = sms_service

    def _get_code_key(self, phone: str) -> str:
        """获取验证码存储key"""
        return f"sms:code:{phone}"

    async def send_and_store(self, phone: str) -> Tuple[bool, str]:
        """发送验证码并存储"""
        # 生成验证码
        code = self.sms.generate_code()

        # 发送短信
        result = await self.sms.send_verification_code(phone, code, self.redis)

        if result.success:
            # 存储验证码到Redis
            key = self._get_code_key(phone)
            await self.redis.setex(key, self.CODE_EXPIRY, code)

            return True, "验证码已发送"

        return False, result.message or "发送失败"

    async def verify(self, phone: str, code: str) -> Tuple[bool, str]:
        """验证验证码"""
        key = self._get_code_key(phone)
        stored_code = await self.redis.get(key)

        if not stored_code:
            return False, "验证码已过期，请重新获取"

        if stored_code.decode() != code:
            return False, "验证码错误"

        # 验证成功后删除验证码（一次性使用）
        await self.redis.delete(key)

        return True, "验证成功"

    async def get_remaining_time(self, phone: str) -> int:
        """获取验证码剩余有效时间"""
        key = self._get_code_key(phone)
        ttl = await self.redis.ttl(key)
        return max(0, ttl)
```

### 发送限制规则

| 限制类型 | 规则 | 存储方式 | 过期时间 |
|----------|------|----------|----------|
| 单手机号每分钟 | 最多1条 | Redis Key | 60秒 |
| 单手机号每小时 | 最多5条 | Redis Key | 1小时 |
| 单手机号每天 | 最多10条 | Redis Key | 24小时 |
| 验证码有效期 | 5分钟 | Redis Key | 300秒 |
| 重发间隔 | 60秒 | - | - |

### 错误处理策略

| 错误类型 | 处理方式 | 用户提示 |
|----------|----------|----------|
| 手机号格式错误 | 直接拒绝 | "请输入正确的手机号" |
| 频率限制 | 拒绝并提示等待时间 | "发送过于频繁，请X分钟后再试" |
| 账户余额不足 | 告警通知管理员 | "服务暂时不可用，请稍后重试" |
| 模板/签名问题 | 记录日志，告警 | "服务暂时不可用" |
| 网络超时 | 自动重试(最多3次) | "发送失败，请重试" |
| 黑名单管控 | 记录日志 | "该号码暂时无法接收验证码" |

### 监控与告警

```python
# 监控指标
METRICS = {
    "sms_send_total": "短信发送总数",
    "sms_send_success": "发送成功数",
    "sms_send_failed": "发送失败数",
    "sms_send_latency": "发送延迟",
    "sms_rate_limit_hits": "频率限制触发次数",
    "sms_balance_warning": "余额不足告警",
}

# Prometheus指标示例
from prometheus_client import Counter, Histogram

sms_send_total = Counter(
    'sms_send_total',
    'Total SMS messages sent',
    ['status', 'error_code']
)

sms_send_latency = Histogram(
    'sms_send_latency_seconds',
    'SMS send latency in seconds'
)
```

### 安全建议

1. **凭证管理**
   - AccessKey使用RAM子账号，仅授予短信权限
   - 定期轮换AccessKey（建议每季度）
   - 生产环境使用环境变量或密钥管理服务

2. **敏感信息保护**
   - 日志中手机号脱敏（如：138****1234）
   - 验证码不在日志中明文记录

3. **频率限制防护**
   - 服务端强制频率限制，不依赖阿里云限制
   - 异常高频请求触发风控告警

4. **签名模板管理**
   - 定期检查签名/模板状态
   - 审核失败及时处理

---

## FRP安全配置

### 服务端配置 (frps.ini - 阿里云)

```ini
[common]
bind_port = 7000
# 认证token
auth_token = "your-secure-token-here"

# 启用TLS加密
tls_only = true
tls_cert_file = /etc/frp/server.crt
tls_key_file = /etc/frp/server.key

# 允许的端口范围
allow_ports = 18001

# 日志配置
log_file = /var/log/frps.log
log_level = info

# 最大连接数
max_pool_count = 5
```

### 客户端配置 (frpc.ini - 本地服务器)

```ini
[common]
server_addr = your-frp-server.com
server_port = 7000
auth_token = "your-secure-token-here"

# 启用TLS
tls_enable = true

# 心跳配置
heartbeat_interval = 30
heartbeat_timeout = 90

[tts-service]
type = tcp
local_ip = 127.0.0.1
local_port = 8001
remote_port = 18001

# 连接池
pool_count = 3
```

### IP白名单配置

```python
# 云后端访问控制
ALLOWED_IPS = [
    "127.0.0.1",           # 本地
    "10.0.0.0/8",          # 内网
    "阿里云ECS内网IP"       # 业务服务器
]

# TTS服务访问控制中间件
@app.middleware("http")
async def ip_whitelist_middleware(request: Request, call_next):
    client_ip = request.client.host
    if not is_ip_allowed(client_ip, ALLOWED_IPS):
        raise HTTPException(status_code=403, detail="Access denied")
    return await call_next(request)
```

### 安全检查清单

- [ ] FRP token使用强随机字符串 (32位+)
- [ ] 启用TLS加密传输
- [ ] 限制远程端口范围
- [ ] 配置连接池大小限制
- [ ] 启用日志审计
- [ ] 定期更新token (建议每季度)

---

## 音色ID生命周期管理

### 生命周期状态

```
创建 → 活跃 → 过期/删除
  ↓      ↓        ↓
存储   使用中    清理
```

### 详细流程

| 阶段 | 操作 | 说明 |
|------|------|------|
| **创建** | 用户上传样本 → TTS服务生成voice_id → 存储到MongoDB | voice_id格式: `voice_{timestamp}_{random}` |
| **存储** | voice_id存储在voice_samples集合 | 关联user_id，标记is_default |
| **使用** | 每次合成时查询voice_id有效性 | 检查用户权限、点数余额 |
| **过期** | 用户订阅过期后，音色保留但无法使用 | 提示续费后可继续使用 |
| **删除** | 用户主动删除或账号注销时 | 调用TTS服务清理接口 |

### Voice ID清理机制

```python
class VoiceLifecycleManager:
    """音色生命周期管理器"""

    async def create_voice(self, user_id: str, audio_file: UploadFile) -> dict:
        """创建音色"""
        # 1. 调用TTS服务克隆音色
        voice_id = await self.tts_client.clone_voice(audio_file)

        # 2. 存储到数据库
        voice_sample = VoiceSample(
            user_id=user_id,
            voice_id=voice_id,
            audio_url=await self.upload_to_oss(audio_file),
            created_at=datetime.utcnow()
        )
        await self.db.voice_samples.insert_one(voice_sample.dict())

        return voice_sample

    async def delete_voice(self, voice_id: str, user_id: str) -> bool:
        """删除音色"""
        # 1. 验证所有权
        voice = await self.db.voice_samples.find_one({
            "voice_id": voice_id,
            "user_id": user_id
        })
        if not voice:
            raise VoiceNotFoundError()

        # 2. 删除OSS音频文件
        await self.oss_client.delete(voice["audio_url"])

        # 3. 通知TTS服务清理
        await self.tts_client.delete_voice(voice_id)

        # 4. 删除数据库记录
        await self.db.voice_samples.delete_one({"voice_id": voice_id})

        return True

    async def cleanup_expired_voices(self):
        """定时清理任务 - 清理已注销用户的音色"""
        # 查找已注销用户
        deleted_users = await self.db.users.find(
            {"status": "deleted"},
            {"_id": 1}
        ).to_list(None)

        for user in deleted_users:
            voices = await self.db.voice_samples.find(
                {"user_id": user["_id"]}
            ).to_list(None)

            for voice in voices:
                await self.delete_voice(voice["voice_id"], user["_id"])
```

### Voice ID过期策略

| 用户状态 | 音色状态 | 可用性 |
|----------|----------|--------|
| 试用期过期 | 保留 | 不可用，提示续费 |
| 订阅过期 | 保留 | 不可用，提示续费 |
| 主动删除 | 删除 | 立即失效 |
| 账号注销 | 删除 | 清理所有数据 |

---

## 音频存储工作流

### 完整流程

```
┌─────────────────┐
│  用户上传音频   │
│  (样本/生成)    │
└────────┬────────┘
         ↓
┌─────────────────┐
│  云后端接收     │
│  临时存储       │
└────────┬────────┘
         ↓
┌─────────────────┐
│  上传至OSS      │
│  (私有Bucket)   │
└────────┬────────┘
         ↓
┌─────────────────┐
│  生成签名URL    │
│  (有效期1小时)  │
└────────┬────────┘
         ↓
┌─────────────────┐
│  返回给前端     │
└─────────────────┘
```

### TTS生成音频存储流程

```python
class AudioStorageService:
    """音频存储服务"""

    def __init__(self, oss_client, tts_client):
        self.oss = oss_client
        self.tts = tts_client
        self.bucket = "ai-qinyin-audio"

    async def store_voice_sample(self, audio_file: UploadFile, user_id: str) -> str:
        """存储用户上传的语音样本"""
        # 1. 生成存储路径
        object_key = f"samples/{user_id}/{uuid.uuid4()}.wav"

        # 2. 上传到OSS (私有读写)
        await self.oss.put_object(
            bucket=self.bucket,
            key=object_key,
            data=await audio_file.read(),
            acl="private"
        )

        # 3. 返回OSS URL
        return f"https://{self.bucket}.oss-cn-hangzhou.aliyuncs.com/{object_key}"

    async def store_generated_audio(
        self,
        voice_id: str,
        text: str,
        user_id: str
    ) -> dict:
        """存储生成的音频"""
        # 1. 调用TTS服务生成音频
        audio_data = await self.tts.synthesize(voice_id, text)

        # 2. 生成本地临时文件
        temp_path = f"/tmp/{uuid.uuid4()}.wav"
        with open(temp_path, "wb") as f:
            f.write(audio_data)

        # 3. 上传到OSS
        object_key = f"generated/{user_id}/{datetime.utcnow().strftime('%Y%m%d')}/{uuid.uuid4()}.wav"
        await self.oss.put_object_from_file(
            bucket=self.bucket,
            key=object_key,
            file_path=temp_path,
            acl="private"
        )

        # 4. 清理临时文件
        os.remove(temp_path)

        # 5. 生成签名URL (1小时有效)
        signed_url = self.oss.generate_presigned_url(
            bucket=self.bucket,
            key=object_key,
            expires=3600
        )

        return {
            "oss_url": f"oss://{self.bucket}/{object_key}",
            "signed_url": signed_url,
            "duration": self._get_audio_duration(audio_data)
        }

    def get_signed_url(self, oss_url: str, expires: int = 3600) -> str:
        """获取签名访问URL"""
        # 解析OSS路径
        _, _, key = oss_url.partition(f"{self.bucket}/")

        return self.oss.generate_presigned_url(
            bucket=self.bucket,
            key=key,
            expires=expires
        )
```

### OSS Bucket配置

```python
# OSS存储桶配置
OSS_CONFIG = {
    "bucket_name": "ai-qinyin-audio",
    "region": "cn-hangzhou",
    "storage_class": "Standard",
    "acl": "private",
    "lifecycle_rules": [
        {
            "id": "delete-old-generated",
            "prefix": "generated/",
            "status": "Enabled",
            "expiration_days": 90  # 生成音频保留90天
        },
        {
            "id": "archive-old-samples",
            "prefix": "samples/",
            "status": "Enabled",
            "transition_to_ia_days": 180,  # 180天后转低频存储
            "expiration_days": 365  # 1年后删除
        }
    ]
}
```

---

## 术语一致性说明

### 点数与生成次数

> **说明**: 本系统使用"点数"(credits)作为统一的计量单位，每次音频生成消耗1点数。

| 套餐类型 | 总点数 | 有效期 | 说明 |
|----------|--------|--------|------|
| 试用用户 | 3点数 | 7天 | 免费试用 |
| 月度会员 | 100点数 | 30天 | 约3次/天 |
| 季度会员 | 350点数 | 90天 | 约4次/天 |
| 年度会员 | 1500点数 | 365天 | 约4次/天 |

### 数据库字段命名

```python
# 统一使用 credits 相关命名
{
    "total_credits": 100,      # 总点数 (不是 total_generations)
    "used_credits": 30,        # 已用点数 (不是 used_generations)
    "remaining_credits": 70    # 剩余点数 (API响应中使用)
}
```

### API响应格式

```python
# 正确的API响应格式
{
    "success": true,
    "data": {
        "subscription": {
            "type": "monthly",
            "total_credits": 100,
            "used_credits": 30,
            "remaining_credits": 70  # 计算值: total - used
        }
    }
}
```

---

## 试用用户转化流程

### 试用期生命周期

```
注册 → 7天试用期 → 转化/过期
  ↓        ↓            ↓
3点数   使用/引导     升级/流失
```

### 详细转化流程

| 阶段 | 触发条件 | 系统行为 | 用户提示 |
|------|----------|----------|----------|
| **注册** | 完成手机验证 | 自动激活7天试用，授予3点数 | "恭喜获得7天免费试用" |
| **使用中** | 每次生成 | 扣减点数，显示剩余 | "本次消耗1点数，剩余2点数" |
| **点数用尽** | 剩余0点数 | 阻止生成，显示升级弹窗 | "试用点数已用完，升级会员继续使用" |
| **即将过期** | 剩余1-2天 | 小程序模板消息提醒 | "试用即将到期，升级享更多权益" |
| **已过期** | 试用结束 | 标记过期，保留音色 | "试用期已结束，升级恢复使用" |

### 转化引导策略

```python
# 转化引导配置
CONVERSION_STRATEGY = {
    "point_exhausted": {
        "trigger": "used_credits >= total_credits",
        "action": "show_upgrade_modal",
        "modal_content": {
            "title": "试用点数已用完",
            "benefits": ["100+月生成次数", "10个专属音色", "优先客服支持"],
            "recommended_plan": "quarterly"
        }
    },
    "expiring_soon": {
        "trigger": "expires_at - now <= 2 days",
        "action": "send_template_message",
        "message_type": "trial_expiring"
    },
    "expired": {
        "trigger": "now >= expires_at",
        "action": ["mark_expired", "block_generation"],
        "fallback": "show_renewal_page"
    }
}
```

### 升级引导弹窗

```
┌────────────────────────────────────┐
│     试用点数已用完                  │
│                                    │
│  升级会员，享受更多权益：           │
│  ✓ 100+月生成次数                  │
│  ✓ 10个专属音色                    │
│  ✓ 优先客服支持                    │
│                                    │
│  ┌─────────┐ ┌─────────────────┐  │
│  │ 月度 ¥29.9 │ │ 季度 ¥69.9 (推荐) │  │
│  └─────────┘ └─────────────────┘  │
│                                    │
│        [ 暂不升级 ]                 │
└────────────────────────────────────┘
```

---

## MongoDB索引设计

### 用户表索引 (users)

```javascript
// 唯一索引
db.users.createIndex({ "phone": 1 }, { unique: true })

// 查询优化索引
db.users.createIndex({ "created_at": -1 })
db.users.createIndex({ "last_login": -1 })
```

### 音色表索引 (voice_samples)

```javascript
// 用户ID索引 (高频查询)
db.voice_samples.createIndex({ "user_id": 1 })

// 复合索引：用户+默认音色
db.voice_samples.createIndex({ "user_id": 1, "is_default": 1 })

// 创建时间索引 (历史查询)
db.voice_samples.createIndex({ "created_at": -1 })
```

### 订阅表索引 (subscriptions)

```javascript
// 用户ID索引
db.subscriptions.createIndex({ "user_id": 1 })

// 复合索引：用户+状态 (订阅状态查询)
db.subscriptions.createIndex({ "user_id": 1, "status": 1 })

// 过期时间索引 (定时任务扫描过期订阅)
db.subscriptions.createIndex({ "expires_at": 1, "status": 1 })
```

### 支付记录表索引 (payments)

```javascript
// 用户ID索引
db.payments.createIndex({ "user_id": 1 })

// 订单号唯一索引
db.payments.createIndex({ "order_id": 1 }, { unique: true })

// 微信交易号索引 (回调查询)
db.payments.createIndex({ "transaction_id": 1 })

// 创建时间索引
db.payments.createIndex({ "created_at": -1 })
```

### 生成记录表索引 (generated_contents)

```javascript
// 用户ID索引
db.generated_contents.createIndex({ "user_id": 1 })

// 复合索引：用户+创建时间 (历史记录分页)
db.generated_contents.createIndex({ "user_id": 1, "created_at": -1 })

// 音色ID索引 (查看音色使用情况)
db.generated_contents.createIndex({ "voice_id": 1 })
```

### 索引创建脚本

```python
# backend/scripts/create_indexes.py
from pymongo import MongoClient
from backend.config import settings

def create_all_indexes():
    client = MongoClient(settings.MONGODB_URI)
    db = client[settings.DATABASE_NAME]

    indexes = {
        "users": [
            ([("phone", 1)], {"unique": True}),
            ([("created_at", -1)], {}),
            ([("last_login", -1)], {}),
        ],
        "voice_samples": [
            ([("user_id", 1)], {}),
            ([("user_id", 1), ("is_default", 1)], {}),
            ([("created_at", -1)], {}),
        ],
        "subscriptions": [
            ([("user_id", 1)], {}),
            ([("user_id", 1), ("status", 1)], {}),
            ([("expires_at", 1), ("status", 1)], {}),
        ],
        "payments": [
            ([("user_id", 1)], {}),
            ([("order_id", 1)], {"unique": True}),
            ([("transaction_id", 1)], {}),
            ([("created_at", -1)], {}),
        ],
        "generated_contents": [
            ([("user_id", 1)], {}),
            ([("user_id", 1), ("created_at", -1)], {}),
            ([("voice_id", 1)], {}),
        ],
    }

    for collection, index_list in indexes.items():
        for keys, options in index_list:
            db[collection].create_index(keys, **options)
            print(f"Created index on {collection}: {keys}")

if __name__ == "__main__":
    create_all_indexes()
```

---

## 微信小程序特定配置

### app.json 配置

```json
{
  "pages": [
    "pages/index/index",
    "pages/login/login",
    "pages/profile/profile",
    "pages/voice-sample/index",
    "pages/voice-sample/create",
    "pages/voice-sample/edit",
    "pages/generate/generate",
    "pages/history/history",
    "pages/player/player",
    "pages/trial/trial",
    "pages/purchase/purchase"
  ],
  "window": {
    "navigationBarTitleText": "AI亲音",
    "navigationBarBackgroundColor": "#FFB6C1",
    "navigationBarTextStyle": "white",
    "backgroundColor": "#FFF5F5",
    "backgroundTextStyle": "dark"
  },
  "tabBar": {
    "color": "#999999",
    "selectedColor": "#FF69B4",
    "backgroundColor": "#FFFFFF",
    "borderStyle": "white",
    "list": [
      {
        "pagePath": "pages/index/index",
        "text": "首页",
        "iconPath": "assets/icons/home.png",
        "selectedIconPath": "assets/icons/home-active.png"
      },
      {
        "pagePath": "pages/generate/generate",
        "text": "生成",
        "iconPath": "assets/icons/create.png",
        "selectedIconPath": "assets/icons/create-active.png"
      },
      {
        "pagePath": "pages/history/history",
        "text": "历史",
        "iconPath": "assets/icons/history.png",
        "selectedIconPath": "assets/icons/history-active.png"
      },
      {
        "pagePath": "pages/profile/profile",
        "text": "我的",
        "iconPath": "assets/icons/profile.png",
        "selectedIconPath": "assets/icons/profile-active.png"
      }
    ]
  },
  "requiredPrivateInfos": [
    "chooseAddress",
    "chooseLocation"
  ],
  "permission": {
    "scope.record": {
      "desc": "用于录制您的声音样本，创建专属音色"
    }
  },
  "plugins": {}
}
```

### 隐私政策与用户协议

**隐私保护指引内容要点:**

```
1. 信息收集
   - 手机号码（用于登录验证）
   - 音频样本（用于音色克隆）
   - 孕周信息（用于个性化内容生成）

2. 信息使用
   - 手机号仅用于登录验证，不会用于营销
   - 音频样本仅用于生成音色，不会用于其他用途
   - 用户可以随时删除自己的音色和生成内容

3. 信息存储
   - 服务器位于中国大陆
   - 音频文件加密存储
   - 支持用户数据删除

4. 信息共享
   - 未经用户同意，不会向第三方共享
   - 仅与必要的服务提供商共享（如支付、短信）
```

### 用户协议要点

```
1. 服务内容
   - 声音克隆服务
   - 文本生成服务
   - 音频合成服务

2. 用户义务
   - 提供真实信息
   - 不使用他人声音进行克隆
   - 不生成违法违规内容

3. 知识产权
   - 生成内容的知识产权归用户所有
   - 平台保留服务相关知识产权

4. 免责声明
   - 不对生成内容的准确性负责
   - 不对因不可抗力导致的服务中断负责
```

### 隐私授权弹窗配置

```json
// 小程序首页显示
{
  "title": "AI亲音隐私保护指引",
  "content": "在使用服务前，我们需要获取您的授权：\n\n• 手机号：用于登录验证\n• 麦克风：用于录制声音样本\n• 存储：用于保存生成的音频",
  "confirmText": "同意并继续",
  "cancelText": "不同意"
}
```

---

## API密钥管理策略

### 密钥分类

| 密钥类型 | 用途 | 存储方式 | 轮换周期 |
|----------|------|----------|----------|
| 通义千问API Key | 文本生成 | 环境变量 | 90天 |
| 阿里云OSS AccessKey | 对象存储 | 环境变量 | 90天 |
| 阿里云SMS AccessKey | 短信服务 | 环境变量 | 90天 |
| 微信支付商户密钥 | 支付签名 | 密钥管理服务 | 180天 |
| JWT Secret | Token签名 | 环境变量 | 30天 |
| MongoDB连接串 | 数据库连接 | 环境变量 | 按需 |
| FRP Token | 内网穿透 | 配置文件 | 90天 |

### 密钥存储配置

```python
# backend/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # 通义千问
    QWEN_API_KEY: str
    QWEN_API_URL: str = "https://dashscope.aliyuncs.com/api/v1"

    # 阿里云OSS
    OSS_ACCESS_KEY_ID: str
    OSS_ACCESS_KEY_SECRET: str
    OSS_BUCKET: str = "ai-qinyin-audio"
    OSS_REGION: str = "cn-hangzhou"

    # 阿里云短信
    SMS_ACCESS_KEY_ID: str
    SMS_ACCESS_KEY_SECRET: str
    SMS_SIGN_NAME: str = "AI亲音"
    SMS_TEMPLATE_CODE: str

    # 微信支付
    WECHAT_MCH_ID: str
    WECHAT_API_V3_KEY: str
    WECHAT_SERIAL_NO: str
    WECHAT_PRIVATE_KEY: str  # PEM格式私钥路径

    # JWT
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_HOURS: int = 168  # 7天

    # MongoDB
    MONGODB_URI: str
    DATABASE_NAME: str = "ai_qinyin"

    # FRP
    FRP_TOKEN: str
    TTS_SERVICE_URL: str = "http://localhost:18001"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
```

### 密钥轮换流程

```python
# scripts/rotate_secrets.py
import os
import secrets
from datetime import datetime, timedelta

class SecretRotator:
    """密钥轮换管理器"""

    def __init__(self):
        self.rotation_log = "logs/secret_rotation.log"

    def generate_jwt_secret(self) -> str:
        """生成新的JWT密钥"""
        return secrets.token_urlsafe(64)

    def rotate_jwt_secret(self, new_secret: str):
        """轮换JWT密钥"""
        # 1. 更新环境变量文件
        self.update_env_file("JWT_SECRET", new_secret)

        # 2. 记录轮换日志
        self.log_rotation("JWT_SECRET", datetime.utcnow())

        # 3. 通知服务重启
        self.notify_restart()

    def update_env_file(self, key: str, value: str):
        """更新.env文件"""
        env_path = ".env"

        with open(env_path, "r") as f:
            lines = f.readlines()

        with open(env_path, "w") as f:
            for line in lines:
                if line.startswith(f"{key}="):
                    f.write(f"{key}={value}\n")
                else:
                    f.write(line)

    def log_rotation(self, key: str, timestamp: datetime):
        """记录轮换日志"""
        with open(self.rotation_log, "a") as f:
            f.write(f"{timestamp.isoformat()}: Rotated {key}\n")

    def check_rotation_due(self) -> dict:
        """检查是否需要轮换"""
        due_keys = []

        # 检查JWT密钥
        jwt_last_rotation = self.get_last_rotation("JWT_SECRET")
        if jwt_last_rotation < datetime.utcnow() - timedelta(days=30):
            due_keys.append("JWT_SECRET")

        return {"due_for_rotation": due_keys}
```

### 密钥安全检查

```python
# scripts/check_secrets.py
import re

def check_secrets_security():
    """密钥安全检查"""

    issues = []

    # 1. 检查密钥长度
    if len(settings.JWT_SECRET) < 32:
        issues.append("JWT_SECRET长度不足，建议至少32字符")

    # 2. 检查是否使用默认值
    default_patterns = [
        "changeme",
        "secret",
        "password",
        "123456",
        "test"
    ]
    for key, value in settings.dict().items():
        if any(pattern in value.lower() for pattern in default_patterns):
            issues.append(f"{key}使用了不安全的默认值")

    # 3. 检查是否有密钥泄露
    # 扫描git历史中的敏感信息

    return {
        "check_time": datetime.utcnow().isoformat(),
        "issues": issues,
        "status": "PASS" if not issues else "FAIL"
    }
```

### 环境变量模板

```bash
# .env.example (提交到git)
# 通义千问
QWEN_API_KEY=your_qwen_api_key_here

# 阿里云OSS
OSS_ACCESS_KEY_ID=your_access_key_id
OSS_ACCESS_KEY_SECRET=your_access_key_secret
OSS_BUCKET=ai-qinyin-audio
OSS_REGION=cn-hangzhou

# 阿里云短信
SMS_ACCESS_KEY_ID=your_sms_access_key_id
SMS_ACCESS_KEY_SECRET=your_sms_access_key_secret
SMS_SIGN_NAME=AI亲音
SMS_TEMPLATE_CODE=SMS_123456789

# 微信支付
WECHAT_MCH_ID=your_mch_id
WECHAT_API_V3_KEY=your_api_v3_key
WECHAT_SERIAL_NO=your_serial_no
WECHAT_PRIVATE_KEY=/path/to/private_key.pem

# JWT
JWT_SECRET=your_jwt_secret_here_min_32_chars

# MongoDB
MONGODB_URI=mongodb://localhost:27017/ai_qinyin
DATABASE_NAME=ai_qinyin

# FRP
FRP_TOKEN=your_frp_token_here
TTS_SERVICE_URL=http://localhost:18001
```

---

## 下一步

1. 编写详细实现计划
2. 搭建项目基础结构
3. 实现核心功能模块
4. 测试与部署