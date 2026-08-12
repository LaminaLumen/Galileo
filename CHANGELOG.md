# 变更记录

本项目遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/) 的组织方式，并计划从 `v0.1.0` 开始使用语义化版本。

## [Unreleased]

## [0.1.0] - 2026-08-12

### 新增

- 文件优先的 Markdown 内容仓库与 front matter 校验。
- 首页、文章详情、标签筛选、关于页与 404 页面。
- RSS 2.0、sitemap.xml、robots.txt 与健康检查接口。
- 中文优先的响应式观测档案视觉系统。
- CSP、权限策略、点击劫持与 MIME 嗅探防护响应头。
- 非 root Gunicorn 应用镜像与独立 Nginx Compose 服务。
- pytest、Ruff、GitHub Actions 与 Dependabot 自动化。
- GHCR `linux/amd64`、`linux/arm64` 多架构应用与 Nginx 镜像。
- 固定版本的 `compose.release.yml` 预构建镜像部署入口。
- 贡献指南、安全政策、治理说明、路线图与 Issue/PR 模板。

### 变更

- 项目从单页个人博客演示重构为可复用的自托管发布起步项目。
- HTTPS 证书改为仓库外运行时挂载，不再写入镜像。
- 默认时区显式统一为 `Asia/Shanghai`。
- 秘密扫描通过当前 Python 模块启动，兼容 Windows、venv 与 Conda 的脚本目录布局。

### 安全

- 从当前版本中移除曾提交的 Cloudflare Origin CA 证书及私钥。
- 在 `.gitignore` 与 `.dockerignore` 中阻止常见证书、私钥与本地环境文件进入版本控制和构建上下文。

[Unreleased]: https://github.com/LaminaLumen/Galileo/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/LaminaLumen/Galileo/releases/tag/v0.1.0
