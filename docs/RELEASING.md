# 发布流程

Galileo 使用语义化版本，`0.x` 阶段的破坏性变更也必须在变更记录中明确说明。发布由主要维护者执行，不能仅凭 CI 绿色跳过人工复核。

## 1. 准备版本

1. 确认目标里程碑中的 Issue 和 PR 已分类；
2. 把 `CHANGELOG.md` 的 Unreleased 内容整理到版本标题和北京时间发布日期，并准备 `docs/releases/vX.Y.Z.md`；
3. 更新 `pyproject.toml` 中版本；
4. 若有内容格式、环境变量或 URL 变化，补齐迁移与回滚说明；
5. 在干净克隆中执行完整验证。

```powershell
python -m pip install -r requirements-dev.txt
ruff check .
ruff format --check .
pytest
python scripts/check_secrets.py
docker compose config --quiet
docker compose -f compose.release.yml config --quiet
docker compose up --build --detach --wait
Invoke-RestMethod http://localhost:8080/healthz
docker compose down
```

## 2. 创建发布提交与标签

发布提交信息使用中文，示例：

```powershell
git add --all
git commit -m "发布：v0.1.0"
git tag -s v0.1.0 -m "Galileo v0.1.0"
```

只有在明确准备发布并确认远端分支时才推送提交和标签。标签优先使用签名标签；若签名环境尚未建立，使用 annotated tag 并在发布说明中如实标注。

推送标签会触发 `Publish container images` 工作流。工作流会核对 tag 与 `pyproject.toml` 版本，并为应用和 Nginx 发布 `linux/amd64`、`linux/arm64` 镜像、SBOM 与构建来源证明。

## 3. GitHub Release

- 标题使用 `Galileo vX.Y.Z`；
- 内容基于 CHANGELOG 对应版本，不写未交付能力；
- 明确兼容范围、升级步骤、已知问题和安全修复；
- 预发布版本勾选 Pre-release；
- 等待两个 GHCR 镜像完成发布，并确认匿名拉取可用后再创建 Release；
- 发布后从干净目录按 README 再执行一次安装。

## 4. 发布后

1. 验证 Release、源码归档、tag 和 GHCR 版本标签指向同一提交；
2. 检查 CI、Dependabot 和安全页状态；
3. 更新路线图并为下一版本创建真实 Issue；
4. 观察 72 小时内的安装、兼容与安全反馈；
5. 若出现回归，优先发布补丁版本，不移动或重写已公开 tag。
