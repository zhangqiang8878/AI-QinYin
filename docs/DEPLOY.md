# AI亲音部署文档

## 系统架构

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   微信小程序     │────▶│   云端后端API     │◀────│   FRP服务端      │
│  (微信服务器)    │     │  (FastAPI+MongoDB)│     │  (frps)         │
└─────────────────┘     └──────────────────┘     └────────┬────────┘
                                                          │
                                                          │ 公网:18001
                                                          │
                                                  ┌───────┴────────┐
                                                  │   FRP客户端    │
                                                  │    (frpc)      │
                                                  └───────┬────────┘
                                                          │
                                                  ┌───────┴────────┐
                                                  │   TTS服务      │
                                                  │ (vllm-omni)    │
                                                  │    :8001       │
                                                  └────────────────┘
```

## 部署步骤

### 1. 云端服务器部署

#### 1.1 安装Docker和Docker Compose

```bash
curl -fsSL https://get.docker.com | sh
```

#### 1.2 部署MongoDB和Redis

```yaml
# docker-compose.yml
version: '3.8'
services:
  mongodb:
    image: mongo:6.0
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: your-password

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  mongodb_data:
  redis_data:
```

#### 1.3 部署后端API

我们提供了 `docker-compose.yml` 来一键启动 MongoDB、Redis 和 FastAPI 后端服务。

```bash
# 在项目根目录下执行
docker-compose up -d --build
```

或者如果您只想单独部署后端服务，可以使用以下命令：

```bash
cd backend
docker build -t ai-qinyin-backend .
docker run -d \
  --name ai-qinyin-backend \
  --env-file .env \
  -p 8000:8000 \
  -v $(pwd)/logs:/app/logs \
  ai-qinyin-backend
```

#### 1.4 部署FRP服务端

```bash
cd frp
./frps -c frps.ini
```

### 2. 本地TTS服务器部署

#### 2.1 安装vllm-omni

```bash
# 安装依赖
pip install vllm-omni

# 下载模型 (约3.5GB)
python -c "from huggingface_hub import snapshot_download; snapshot_download('Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice')"
```

#### 2.2 启动TTS服务

```bash
cd tts-service
python server.py
```

#### 2.3 启动FRP客户端

```bash
cd frp
./frpc -c frpc.ini
```

### 3. 微信小程序部署

#### 3.1 配置域名

在微信公众平台配置服务器域名：
- request合法域名: `https://your-api-domain.com`
- uploadFile合法域名: `https://your-oss-bucket.oss-cn-beijing.aliyuncs.com`

#### 3.2 上传代码

使用微信开发者工具上传代码并提交审核。

## 配置检查清单

- [ ] MongoDB已启动且可访问
- [ ] Redis已启动且可访问
- [ ] 后端API环境变量已配置
  - `MONGODB_URI=mongodb://admin:password@localhost:27017/ai_qinyin`
  - `JWT_SECRET=your_secret_key`
- [ ] 阿里云SMS密钥已配置
- [ ] 阿里云OSS密钥已配置
- [ ] 微信支付密钥已配置
- [ ] FRP服务端已启动
- [ ] TTS服务已启动
- [ ] FRP客户端已连接
- [ ] 微信小程序服务器域名已配置
- [ ] 微信小程序AppID已配置

## 监控与维护

### 日志查看

```bash
# 后端日志
docker logs -f ai-qinyin-backend

# TTS服务日志
tail -f tts-service/server.log

# FRP日志
tail -f frp/frps.log
```

### 数据库备份

```bash
# MongoDB备份
docker exec mongodb mongodump --out /backup/$(date +%Y%m%d)
```

## 故障排查

### TTS服务连接失败

1. 检查FRP客户端是否连接: `cat frp/frpc.log`
2. 检查后端TTS_SERVICE_URL配置
3. 检查云端服务器防火墙是否放行18001端口

### 支付回调失败

1. 检查WECHAT_NOTIFY_URL配置
2. 检查微信支付证书配置
3. 查看后端支付日志

### 短信发送失败

1. 检查阿里云SMS密钥配置
2. 检查短信签名和模板是否审核通过
3. 检查发送频率限制