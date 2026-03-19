# API接口文档

> 本文档定义AI亲音胎教微信小程序的所有API接口规范。

## 输入接口

- HTTP请求：微信小程序前端发起的HTTPS请求
- 微信回调：微信支付通知、小程序事件

## 输出接口

- JSON响应：统一的API响应格式
- 文件下载：OSS签名URL

---

## 响应格式规范

### 成功响应
```json
{
    "success": true,
    "data": { ... }
}
```

### 错误响应
```json
{
    "success": false,
    "error": {
        "code": "ERROR_CODE",
        "message": "错误描述"
    }
}
```

---

## 认证相关 API

### 发送验证码

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

### 手机号登录

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

### 获取用户信息

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
```

### 更新用户信息

```
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

---

## 音色管理 API

### 创建音色

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

### 获取音色列表

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

### 更新音色

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
```

### 删除音色

```
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

### 设为默认音色

```
PUT /api/voice/samples/{id}/default
Authorization: Bearer <token>

Response:
{
    "success": true,
    "data": {
        "message": "已设为默认音色"
    }
}
```

---

## 内容生成 API

### 生成文本内容

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

### 文本转语音

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

### 一键生成

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

### 获取内容模板

```
GET /api/content/templates
Authorization: Bearer <token>

Response:
{
    "success": true,
    "data": {
        "templates": [
            {
                "type": "story",
                "name": "胎教故事",
                "themes": ["自然", "友情", "勇气", "爱", "成长"]
            },
            {
                "type": "daily",
                "name": "日常对话",
                "scenes": ["早晨起床", "午休时光", "晚间睡前", "户外散步"]
            }
        ]
    }
}
```

---

## 历史记录 API

### 获取生成历史

```
GET /api/history
Authorization: Bearer <token>
Query: ?page=1&limit=20

Response:
{
    "success": true,
    "data": {
        "items": [...],
        "total": 50,
        "page": 1,
        "limit": 20
    }
}
```

### 获取单条记录详情

```
GET /api/history/{id}
Authorization: Bearer <token>

Response:
{
    "success": true,
    "data": {
        "id": "507f1f77bcf86cd799439013",
        "voice_id": "507f1f77bcf86cd799439012",
        "content_type": "story",
        "text_content": "宝宝你好...",
        "audio_url": "https://oss.../output.wav?signature=...",
        "duration": 180.5,
        "created_at": "2026-03-17T10:35:00Z"
    }
}
```

### 删除历史记录

```
DELETE /api/history/{id}
Authorization: Bearer <token>

Response:
{
    "success": true,
    "data": {
        "message": "记录已删除"
    }
}
```

---

## 订阅管理 API

### 获取套餐列表

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

### 创建订阅订单

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

### 获取订阅状态

```
GET /api/subscription/status
Authorization: Bearer <token>

Response:
{
    "success": true,
    "data": {
        "type": "monthly",
        "status": "active",
        "total_credits": 100,
        "used_credits": 30,
        "remaining_credits": 70,
        "expires_at": "2026-04-17T00:00:00Z"
    }
}
```

---

## 支付 API

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

---

## API路由汇总

| 模块 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 认证 | POST | /api/auth/send-code | 发送验证码 |
| 认证 | POST | /api/auth/login | 手机号验证码登录 |
| 认证 | GET | /api/auth/profile | 获取用户信息 |
| 认证 | PUT | /api/auth/profile | 更新用户信息 |
| 音色 | POST | /api/voice/samples | 创建新音色 |
| 音色 | GET | /api/voice/samples | 获取用户音色列表 |
| 音色 | PUT | /api/voice/samples/{id} | 更新音色信息 |
| 音色 | DELETE | /api/voice/samples/{id} | 删除音色 |
| 音色 | PUT | /api/voice/samples/{id}/default | 设为默认音色 |
| 内容 | POST | /api/content/generate-text | 生成文本内容 |
| 内容 | POST | /api/content/synthesize | 文本转语音 |
| 内容 | POST | /api/content/generate-full | 一键生成（文本+语音） |
| 内容 | GET | /api/content/templates | 获取内容模板列表 |
| 历史 | GET | /api/history | 获取生成历史 |
| 历史 | GET | /api/history/{id} | 获取单条记录详情 |
| 历史 | DELETE | /api/history/{id} | 删除历史记录 |
| 订阅 | GET | /api/subscription/plans | 获取套餐列表 |
| 订阅 | POST | /api/subscription/subscribe | 创建订阅订单 |
| 订阅 | GET | /api/subscription/status | 获取订阅状态 |
| 支付 | POST | /api/payment/create | 创建支付订单 |
| 支付 | POST | /api/payment/callback | 微信支付回调 |