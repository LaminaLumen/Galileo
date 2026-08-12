# Galileo 部署指南

本文面向通用团队和自托管环境，不假设维护者本机已有私人配置。所有示例使用 PowerShell；Linux/CI 环境可将等价变量和文件挂载转换为相应 shell 语法。

## 1. 前置条件

- Docker Engine 24+ 或 Docker Desktop；
- Docker Compose v2；
- 至少 256 MiB 可用内存；
- 若公开到互联网：已配置 DNS、可信 TLS 证书和入口防火墙；
- 运行主机与容器时区可不同，但应用配置必须明确为 IANA `Asia/Shanghai`。

## 2. 本机或反向代理后运行

```powershell
git clone https://github.com/LaminaLumen/Galileo.git
Set-Location Galileo
Copy-Item .env.example .env
docker compose up --build --detach --wait
Invoke-RestMethod http://localhost:8080/healthz
```

默认只绑定 `127.0.0.1:8080`。这适合本机预览，或由同一主机上的 Caddy、Traefik、Cloudflare Tunnel、Nginx 等可信入口继续代理。

如果入口代理和 Galileo 不在同一主机，不要直接把绑定地址改为 `0.0.0.0` 后暴露公网。应先建立私有网络、来源白名单或主机防火墙，并确认实际管理通道不会被阻断。

## 3. 配置公开站点 URL

编辑 `.env`：

```dotenv
SITE_URL=https://example.com
SITE_NAME=My Galileo
SITE_AUTHOR=Your Name
TZ=Asia/Shanghai
```

`SITE_URL` 会写入 canonical、RSS、robots.txt 和 sitemap，必须与读者实际访问地址一致，且末尾不要加 `/`。

修改后重建：

```powershell
docker compose up --build --detach --wait
```

## 4. TLS

### 推荐：在外部网关终止 TLS

让已有网关负责 ACME、证书轮换、HSTS 和公网端口；将上游指向 `http://127.0.0.1:8080`。入口至少应传递：

- `Host`；
- `X-Forwarded-For`；
- `X-Forwarded-Proto: https`。

### 可选：由项目 Nginx 终止 TLS

复制 `nginx/https.example.conf`，替换 `server_name`，把它作为容器内 `/etc/nginx/conf.d/default.conf` 只读挂载，同时把证书挂载到：

- `/run/secrets/tls.crt`；
- `/run/secrets/tls.key`。

证书和私钥不得放入仓库、Dockerfile、镜像层或 Compose 明文环境变量。HSTS 只有在确认域名及子域将长期提供 HTTPS 后才启用。

## 5. 内容更新

内容位于 `content/posts`。标准发布过程：

```powershell
ruff check .
ruff format --check .
pytest
docker compose build
docker compose up --detach --wait
```

复核：

```powershell
$health = Invoke-RestMethod https://example.com/healthz
$health
Invoke-WebRequest https://example.com/feed.xml | Select-Object StatusCode, Headers
```

`healthz.time` 必须带 `+08:00`，`timezone` 必须为 `Asia/Shanghai`。

## 6. 升级与回滚

升级前记录当前版本：

```powershell
git rev-parse HEAD
docker compose images
```

拉取并验证新版本后再切换：

```powershell
git fetch --tags
git checkout <目标版本>
docker compose build
docker compose up --detach --wait
```

若健康检查或业务复核失败，切回此前记录的提交或 tag，重新执行 `docker compose up --build --detach --wait`。内容文件也由 Git 管理；回滚应用时需确认是否同时回滚内容，避免误删已发布文章。

## 7. 日志与时间

- 应用和 Nginx 日志写入标准输出，由容器平台统一采集；
- `TZ=Asia/Shanghai` 必须显式设置，不依赖基础镜像默认值；
- 外部日志平台若强制 UTC，应在采集边界保留原始带偏移时间，并在展示层转换；
- 不要将访问日志、错误日志或容器转储提交到仓库，它们可能包含 IP、URL 参数或其他个人数据。

## 8. 生产检查清单

- [ ] 使用已审核的 tag 或固定 commit，而不是不可控浮动分支；
- [ ] `SITE_URL`、DNS、TLS 证书与 Host 一致；
- [ ] 入口只开放业务需要的端口和来源；
- [ ] 证书和密钥未进入 Git、镜像或日志；
- [ ] 应用和 Nginx 健康检查通过；
- [ ] 首页、文章、RSS、sitemap、404 均验证；
- [ ] 响应含 CSP、`X-Frame-Options`、`X-Content-Type-Options`；
- [ ] 应用、容器和日志时间均为明确的 `Asia/Shanghai` 或带 `+08:00`；
- [ ] 已记录版本、配置备份和回滚命令；
- [ ] 已配置依赖更新、安全公告和最小权限运维流程。
