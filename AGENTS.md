# Galileo 协作约定

- 项目定位：中文优先、隐私友好的自托管个人发布起步项目；核心价值是文件可迁移、默认最小数据流和单人可维护。
- Python 最低版本为 3.11，采用 Flask 应用工厂；公开路由位于 `galileo/web.py`，内容解析位于 `galileo/content.py`。
- 文章位于 `content/posts/*.md`；slug 只用小写字母、数字和连字符，时间必须带偏移并统一展示为 IANA `Asia/Shanghai`。
- Markdown 原始 HTML 默认关闭。除非先完成威胁模型与隔离评审，不得放开脚本或任意 HTML。
- 默认页面不得引入第三方字体、追踪器、外部图片或遥测；新增外部数据流必须在文档中说明用途、去向和关闭方式。
- 证书、私钥、令牌和真实环境配置不得进入 Git 或镜像；TLS 秘密只允许运行时只读挂载。
- 容器基线：应用使用 UID/GID 10001，Nginx 使用 UID/GID 101；保持只读根文件系统、`no-new-privileges` 和本机默认绑定。
- 代码注释和项目文档以中文为主，仅为复杂逻辑、关键边界和外部约束添加注释。
- 变更前后执行：`ruff check .`、`ruff format --check .`、`pytest`、`python scripts/check_secrets.py`；涉及容器时再执行 `docker compose config --quiet` 和完整健康检查。
- 用户可见行为、内容格式、环境变量或部署方式变化时，同步更新 README、相关文档与 CHANGELOG。
