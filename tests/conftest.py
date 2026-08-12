from __future__ import annotations

from pathlib import Path

import pytest

from galileo import create_app


@pytest.fixture
def content_dir(tmp_path: Path) -> Path:
    directory = tmp_path / "posts"
    directory.mkdir()
    (directory / "hello-galileo.md").write_text(
        """---
title: "你好，Galileo"
summary: "一篇用于自动验证的公开文章。"
date: "2026-08-12T09:30:00+08:00"
tags: ["测试", "开放网络"]
featured: true
draft: false
---

这里是正文，包含 **加粗内容** 和 [项目链接](https://example.com)。
""",
        encoding="utf-8",
    )
    (directory / "draft-note.md").write_text(
        """---
title: "尚未发布"
summary: "这篇文章不应出现在默认列表。"
date: "2026-08-13T10:00:00+08:00"
tags: ["草稿"]
featured: false
draft: true
---

草稿正文。
""",
        encoding="utf-8",
    )
    return directory


@pytest.fixture
def app(content_dir: Path):
    return create_app(
        {
            "TESTING": True,
            "CONTENT_DIR": str(content_dir),
            "SITE_URL": "https://galileo.example",
            "SHOW_DRAFTS": False,
        }
    )


@pytest.fixture
def client(app):
    return app.test_client()
