# FRP内网穿透配置

> 本文档定义FRP内网穿透服务的配置规范，遵循单一职责原则。

## 输入接口

- TTS服务请求：云后端通过FRP隧道调用本地TTS服务
- 健康检查：服务状态监控

## 输出接口

- TTS服务响应：音色克隆、语音合成结果
- 连接状态：FRP隧道连接状态

---

## 架构说明

```
┌─────────────────┐     FRP隧道      ┌─────────────────┐
│   阿里云服务器   │ ←──────────────→ │   本地服务器    │
│   (FRP Server)  │                  │   (FRP Client)  │
│   端口: 7000    │                  │                 │
│                 │                  │  TTS Service    │
│  远程端口:18001 │ ←──────────────→ │  本地端口:8001  │
└─────────────────┘                  └─────────────────┘
```

---

## 服务端配置 (frps.ini - 阿里云)

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

---

## 客户端配置 (frpc.ini - 本地服务器)

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

---

## IP白名单配置

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

---

## 安全检查清单

- [ ] FRP token使用强随机字符串 (32位+)
- [ ] 启用TLS加密传输
- [ ] 限制远程端口范围
- [ ] 配置连接池大小限制
- [ ] 启用日志审计
- [ ] 定期更新token (建议每季度)

---

## 连接状态监控

```python
# 健康检查接口
@app.get("/health")
async def health_check():
    try:
        # 检查FRP隧道连通性
        response = await tts_client.ping()
        return {"status": "healthy", "tts_connection": "ok"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
```

---

## 容错处理

| 场景 | 处理方式 |
|------|----------|
| 服务不可用 | 云后端检测健康状态，降级提示 |
| 生成超时 | 30秒超时，支持重试队列 |
| 并发限制 | 本地限制并发2-3个，超出排队 |