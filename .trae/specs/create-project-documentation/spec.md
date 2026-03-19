# 项目说明文档 Spec

## Why
用户请求生成整个工程的说明文档，以便于理解项目架构、功能模块、部署方式和技术栈等，方便后续开发、维护和项目交接。

## What Changes
- 增加项目的 README.md 文档（位于根目录）。
- 梳理并说明后端 FastAPI 服务、微信小程序前端、TTS 服务、第三方集成（如阿里云 OSS、SMS、微信支付）的配置和使用方法。
- 整合之前生成的 `DEPLOY.md` 和其他配置说明。

## Impact
- Affected specs: 无现有规范受影响，纯文档增加。
- Affected code: 根目录增加 `README.md`。

## ADDED Requirements
### Requirement: 项目总览文档
系统需要提供一份全面的 `README.md` 文件。

#### Scenario: Success case
- **WHEN** 开发者或用户查看项目根目录
- **THEN** 可以阅读 `README.md` 并了解项目背景、技术栈、模块说明和快速启动指南。