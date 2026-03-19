# TTS语音合成服务

> 本文档定义TTS语音合成服务的接口规范，遵循单一职责原则。

## 输入接口

- 音色克隆请求：用户上传音频样本创建音色
- 语音合成请求：文本内容转语音
- 健康检查：服务状态监控

## 输出接口

- 音色ID：克隆后的voice_id
- 音频URL：合成后的音频文件地址
- 服务状态：健康检查结果

---

## 服务架构

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

---

## API接口

### 创建音色

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

### 生成语音

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

### 健康检查

```
GET /health

Response:
{
    "status": "healthy",
    "model_loaded": true,
    "gpu_memory": "14.2GB/16GB"
}
```

---

## 音色克隆流程

```
用户录音(10秒) → 上传到TTS服务 → 音色特征提取 →
生成voice_id → 存储到MongoDB → 关联用户账户
```

### 音色ID格式

```
voice_{timestamp}_{random}
示例: voice_20240315_abc123
```

### 音色样本要求

| 参数 | 要求 | 说明 |
|------|------|------|
| 时长 | 10-30秒 | 推荐10秒 |
| 格式 | WAV/MP3 | 推荐16kHz采样率WAV |
| 内容 | 自然朗读 | 无背景噪音 |
| 语言 | 中文 | 支持普通话 |

---

## FRP隧道配置

```ini
# frpc.ini (本地服务器)
[common]
server_addr = your-frp-server.com
server_port = 7000
auth_token = "your-secure-token-here"

[tts-service]
type = tcp
local_ip = 127.0.0.1
local_port = 8001
remote_port = 18001
pool_count = 3
```

---

## 容错处理

| 场景 | 处理方式 |
|------|----------|
| 服务不可用 | 云后端检测健康状态，降级提示 |
| 生成超时 | 30秒超时，支持重试队列 |
| 并发限制 | 本地限制并发2-3个，超出排队 |
| GPU内存不足 | 排队等待，按顺序处理 |

---

## 云后端调用示例

```python
# backend/services/tts_client.py
import httpx
from config import settings

class TTSClient:
    def __init__(self):
        self.base_url = settings.TTS_SERVICE_URL
        self.timeout = 30.0

    async def clone_voice(self, audio_file: bytes) -> dict:
        """创建音色"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            files = {"audio_file": ("sample.wav", audio_file)}
            response = await client.post(
                f"{self.base_url}/clone",
                files=files
            )
            return response.json()

    async def synthesize(
        self,
        voice_id: str,
        text: str,
        speed: float = 1.0
    ) -> dict:
        """生成语音"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/synthesize",
                json={
                    "voice_id": voice_id,
                    "text": text,
                    "speed": speed,
                    "emotion": "gentle"
                }
            )
            return response.json()

    async def health_check(self) -> bool:
        """健康检查"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/health")
                return response.json().get("status") == "healthy"
        except Exception:
            return False
```

---

## 安全配置

### IP白名单

```python
ALLOWED_IPS = [
    "127.0.0.1",           # 本地
    "10.0.0.0/8",          # 内网
    "阿里云ECS内网IP"       # 业务服务器
]
```

### 访问控制中间件

```python
from fastapi import Request, HTTPException

@app.middleware("http")
async def ip_whitelist_middleware(request: Request, call_next):
    client_ip = request.client.host
    if not is_ip_allowed(client_ip, ALLOWED_IPS):
        raise HTTPException(status_code=403, detail="Access denied")
    return await call_next(request)
```

---

## 监控指标

| 指标 | 说明 | 告警阈值 |
|------|------|----------|
| 服务可用性 | 健康检查成功率 | < 95% |
| 响应时间 | 合成请求延迟 | > 30秒 |
| GPU利用率 | 显存使用率 | > 90% |
| 队列长度 | 等待处理请求数 | > 10 |

---

## 安全检查清单

- [ ] FRP token使用强随机字符串
- [ ] 启用TLS加密传输
- [ ] 配置IP白名单
- [ ] 限制并发请求数
- [ ] 启用请求日志审计