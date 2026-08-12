from __future__ import annotations

from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

from galileo.content import ContentError, ContentRepository


def test_list_posts_hides_drafts_and_preserves_shanghai_timezone(content_dir: Path):
    repository = ContentRepository(content_dir, timezone=ZoneInfo("Asia/Shanghai"))

    posts = repository.list_posts()

    assert [post.slug for post in posts] == ["hello-galileo"]
    assert posts[0].published_at.utcoffset().total_seconds() == 8 * 60 * 60
    assert posts[0].tags == ("测试", "开放网络")
    assert posts[0].featured is True
    assert posts[0].reading_minutes == 1
    assert "<strong>加粗内容</strong>" in posts[0].body_html


def test_get_post_can_include_drafts_explicitly(content_dir: Path):
    repository = ContentRepository(content_dir, timezone=ZoneInfo("Asia/Shanghai"))

    assert repository.get_post("draft-note") is None
    assert repository.get_post("draft-note", include_drafts=True).draft is True
    assert repository.get_post("../draft-note", include_drafts=True) is None


@pytest.mark.parametrize(
    ("filename", "text", "message"),
    [
        ("Bad Name.md", "---\ntitle: x\n---\nbody", "文件名仅允许"),
        ("missing-date.md", "---\ntitle: x\nsummary: y\n---\nbody", "缺少必填字段"),
        (
            "naive-time.md",
            "---\ntitle: x\nsummary: y\ndate: 2026-08-12T09:00:00\n---\nbody",
            "必须包含时区偏移",
        ),
        ("broken.md", "title: x\nbody", "必须以 --- 开始"),
    ],
)
def test_invalid_content_fails_with_actionable_error(
    tmp_path: Path, filename: str, text: str, message: str
):
    content_dir = tmp_path / "posts"
    content_dir.mkdir()
    (content_dir / filename).write_text(text, encoding="utf-8")
    repository = ContentRepository(content_dir, timezone=ZoneInfo("Asia/Shanghai"))

    with pytest.raises(ContentError, match=message):
        repository.list_posts(include_drafts=True)


def test_markdown_escapes_raw_html(tmp_path: Path):
    content_dir = tmp_path / "posts"
    content_dir.mkdir()
    (content_dir / "safe-post.md").write_text(
        """---
title: "安全正文"
summary: "验证原始 HTML 不会注入页面。"
date: "2026-08-12T09:00:00+08:00"
---

<script>alert('unsafe')</script>
""",
        encoding="utf-8",
    )
    repository = ContentRepository(content_dir, timezone=ZoneInfo("Asia/Shanghai"))

    html = repository.list_posts()[0].body_html

    assert "<script>" not in html
    assert "&lt;script&gt;" in html
