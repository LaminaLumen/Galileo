---
title: "从 Markdown 到公开 URL：一条可复现的部署路径"
summary: "Galileo 把应用与入口代理拆成两个小容器，开发环境一条命令即可启动；生产环境通过显式挂载证书完成 HTTPS。"
date: "2026-08-08T14:00:00+08:00"
tags: ["Docker", "部署", "Flask"]
featured: false
draft: false
---

一个起步项目是否真的可复用，不取决于截图有多漂亮，而取决于陌生人能否按照文档，在干净环境里得到相同结果。

Galileo 提供两条路径：本地 Python 适合写作和调试，Docker Compose 适合接近生产的运行方式。

## 本地预览

在 PowerShell 中创建虚拟环境并安装开发依赖：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python app.py
```

访问 `http://127.0.0.1:5000` 即可预览。修改 `content/posts` 下的 Markdown 后刷新页面，无需执行构建步骤。

## 容器运行

安装 Docker Desktop 后执行：

```powershell
docker compose up --build
```

默认入口是 `http://localhost:8080`。应用容器使用非 root 用户运行，Nginx 只负责转发和静态资源缓存。`/healthz` 可用于编排系统的健康检查。

## HTTPS 和证书

项目不会提供任何真实证书，也不会把私钥复制进镜像。生产部署应由外部网关终止 TLS，或者把证书以只读卷挂载到 Nginx 容器，并启用示例 HTTPS 配置。

无论选择哪种方式，证书轮换都不应该要求重新构建应用镜像。运行时秘密和可公开源码之间，必须始终存在清晰边界。

## 可复现比“在我机器上可用”更重要

自动测试会检查内容解析、页面路由、RSS、站点地图和安全响应头；持续集成会在多个 Python 版本上重复这些验证。部署文档则只描述项目通用前提，不依赖维护者本机的私人路径或已有环境。

这条路径不追求隐藏所有细节，而是让每个细节都能被复核。
