"""从带有轻量 front matter 的 Markdown 文件加载文章。"""

from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from markdown_it import MarkdownIt

SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
WORDS_PER_MINUTE = 260


class ContentError(ValueError):
    """内容文件格式不合法。"""


@dataclass(frozen=True, slots=True)
class Post:
    slug: str
    title: str
    summary: str
    published_at: datetime
    tags: tuple[str, ...]
    featured: bool
    draft: bool
    body_markdown: str
    body_html: str
    reading_minutes: int
    source_path: Path

    @property
    def published_date(self) -> str:
        return self.published_at.strftime("%Y年%m月%d日")

    @property
    def published_iso(self) -> str:
        return self.published_at.isoformat()


def _parse_scalar(value: str):
    value = value.strip()
    if not value:
        return ""
    if value[0] in {'"', "'", "[", "{"}:
        try:
            return json.loads(value.replace("'", '"'))
        except json.JSONDecodeError as exc:
            raise ContentError(f"无法解析 front matter 值：{value}") from exc
    return value


def _parse_front_matter(text: str, source: Path) -> tuple[dict, str]:
    normalized = text.replace("\r\n", "\n")
    lines = normalized.split("\n")
    if not lines or lines[0].strip() != "---":
        raise ContentError(f"{source}: 文件必须以 --- 开始 front matter")

    try:
        end_index = next(
            index for index, line in enumerate(lines[1:], start=1) if line.strip() == "---"
        )
    except StopIteration as exc:
        raise ContentError(f"{source}: front matter 缺少结束标记 ---") from exc

    metadata: dict[str, object] = {}
    for line_number, line in enumerate(lines[1:end_index], start=2):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        key, separator, value = stripped.partition(":")
        if not separator or not key.strip():
            raise ContentError(f"{source}:{line_number}: 需要使用 key: value 格式")
        metadata[key.strip()] = _parse_scalar(value)

    body = "\n".join(lines[end_index + 1 :]).strip()
    if not body:
        raise ContentError(f"{source}: 正文不能为空")
    return metadata, body


def _parse_bool(value: object, *, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    normalized = str(value).strip().lower()
    if normalized in {"true", "1", "yes", "on"}:
        return True
    if normalized in {"false", "0", "no", "off"}:
        return False
    raise ContentError(f"布尔值必须是 true 或 false，实际为 {value!r}")


def _parse_tags(value: object) -> tuple[str, ...]:
    if value is None or value == "":
        return ()
    values = value if isinstance(value, list) else str(value).split(",")
    tags = tuple(dict.fromkeys(str(item).strip() for item in values if str(item).strip()))
    if len(tags) > 8:
        raise ContentError("每篇文章最多设置 8 个标签")
    return tags


class ContentRepository:
    """小型文件内容仓库；每次请求重新读取，便于无构建预览。"""

    def __init__(self, content_dir: Path, *, timezone: ZoneInfo):
        self.content_dir = content_dir
        self.timezone = timezone
        self._markdown = MarkdownIt(
            "commonmark",
            {"html": False, "linkify": True, "typographer": True},
        )

    def list_posts(self, *, include_drafts: bool = False) -> list[Post]:
        if not self.content_dir.exists():
            return []
        posts = [self._load_path(path) for path in self.content_dir.glob("*.md")]
        visible = posts if include_drafts else [post for post in posts if not post.draft]
        return sorted(visible, key=lambda post: post.published_at, reverse=True)

    def get_post(self, slug: str, *, include_drafts: bool = False) -> Post | None:
        if not SLUG_PATTERN.fullmatch(slug):
            return None
        path = self.content_dir / f"{slug}.md"
        if not path.is_file():
            return None
        post = self._load_path(path)
        if post.draft and not include_drafts:
            return None
        return post

    def _load_path(self, path: Path) -> Post:
        slug = path.stem
        if not SLUG_PATTERN.fullmatch(slug):
            raise ContentError(f"{path}: 文件名仅允许小写字母、数字和单个连字符")

        metadata, body = _parse_front_matter(path.read_text(encoding="utf-8"), path)
        missing = [key for key in ("title", "summary", "date") if not metadata.get(key)]
        if missing:
            raise ContentError(f"{path}: 缺少必填字段 {', '.join(missing)}")

        try:
            published_at = datetime.fromisoformat(str(metadata["date"]).replace("Z", "+00:00"))
        except ValueError as exc:
            raise ContentError(f"{path}: date 必须是 ISO 8601 时间") from exc
        if published_at.tzinfo is None:
            raise ContentError(f"{path}: date 必须包含时区偏移，例如 +08:00")
        published_at = published_at.astimezone(self.timezone)

        title = str(metadata["title"]).strip()
        summary = str(metadata["summary"]).strip()
        if len(title) > 120:
            raise ContentError(f"{path}: title 不能超过 120 个字符")
        if len(summary) > 240:
            raise ContentError(f"{path}: summary 不能超过 240 个字符")

        text_units = len(re.sub(r"\s+", "", body))
        reading_minutes = max(1, math.ceil(text_units / WORDS_PER_MINUTE))
        return Post(
            slug=slug,
            title=title,
            summary=summary,
            published_at=published_at,
            tags=_parse_tags(metadata.get("tags")),
            featured=_parse_bool(metadata.get("featured")),
            draft=_parse_bool(metadata.get("draft")),
            body_markdown=body,
            body_html=self._markdown.render(body),
            reading_minutes=reading_minutes,
            source_path=path,
        )
