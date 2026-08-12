# 贡献指南

感谢你帮助 Galileo 成为更可靠的个人发布起点。项目欢迎代码、文档、设计、测试、自托管反馈和可复现的问题报告。

参与即表示你同意遵守 [社区行为准则](CODE_OF_CONDUCT.md)。安全漏洞请不要创建公开 Issue，改按 [安全政策](SECURITY.md) 报告。

## 开始之前

1. 搜索现有 Issue 与 Pull Request，避免重复工作。
2. Bug 修复可直接提交；新功能、依赖、内容格式或安全边界变更应先创建提案 Issue。
3. 选择范围小、可独立验证的变更。不要在同一 PR 混入无关重构。
4. 不要提交真实密钥、证书、访问令牌、个人数据或生产日志。

## 本地环境

Windows PowerShell：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
```

运行验证：

```powershell
ruff check .
ruff format --check .
pytest
python scripts/check_secrets.py
```

启动开发服务器：

```powershell
python app.py
```

## 代码与内容约定

- Python 最低版本为 3.11，使用 Ruff 管理格式与基础静态检查。
- 代码注释和项目文档以中文为主；公共协议和生态术语可保留英文。
- 时间必须带时区；项目内部和面向用户默认使用 IANA `Asia/Shanghai`。
- 内容 slug 只使用小写字母、数字和单个连字符。
- Markdown 原始 HTML 保持关闭，除非先完成威胁模型和隔离设计评审。
- 新增依赖必须说明必要性、许可证、维护状态和可替代方案。
- 用户可见行为应有测试；Bug 修复应先写能复现问题的测试。
- 前端变化需在桌面与移动宽度下验证键盘导航、对比度和无横向溢出。

## Pull Request 清单

- [ ] PR 只包含一个清晰目标；
- [ ] 测试与静态检查通过；
- [ ] 用户可见变化同步更新 README、文档或 CHANGELOG；
- [ ] 未提交凭据、个人数据或生成产物；
- [ ] 破坏性变更说明迁移和回滚方法；
- [ ] UI 变化提供前后截图或可复现预览步骤。

维护者通常会在 7 天内完成首次分类或回复。早期项目可能由一名维护者处理，请允许合理等待时间。
