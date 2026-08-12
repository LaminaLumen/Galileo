"""Galileo 应用工厂。"""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from flask import Flask, render_template, request

from galileo.content import ContentRepository
from galileo.web import site

PROJECT_ROOT = Path(
    os.getenv("GALILEO_ROOT", str(Path(__file__).resolve().parent.parent))
).resolve()
DEFAULT_TIMEZONE = "Asia/Shanghai"


def _env_flag(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def create_app(test_config: dict | None = None) -> Flask:
    """创建 Galileo Flask 应用。

    `test_config` 仅用于测试或嵌入式部署覆盖，不会写入磁盘。
    """

    app = Flask(
        __name__,
        template_folder=str(PROJECT_ROOT / "templates"),
        static_folder=str(PROJECT_ROOT / "static"),
        static_url_path="/static",
    )
    app.config.from_mapping(
        SITE_NAME=os.getenv("SITE_NAME", "Galileo"),
        SITE_TAGLINE=os.getenv("SITE_TAGLINE", "把自己的坐标，写回开放网络"),
        SITE_DESCRIPTION=os.getenv(
            "SITE_DESCRIPTION",
            "中文优先、隐私友好的自托管个人发布起步项目。",
        ),
        SITE_AUTHOR=os.getenv("SITE_AUTHOR", "LaminaLumen"),
        SITE_URL=os.getenv("SITE_URL", "http://localhost:8080").rstrip("/"),
        GITHUB_URL=os.getenv("GITHUB_URL", "https://github.com/LaminaLumen/Galileo"),
        CONTENT_DIR=os.getenv("CONTENT_DIR", str(PROJECT_ROOT / "content" / "posts")),
        TIMEZONE=os.getenv("TZ", DEFAULT_TIMEZONE),
        SHOW_DRAFTS=_env_flag("SHOW_DRAFTS"),
        JSON_SORT_KEYS=False,
    )
    if test_config:
        app.config.update(test_config)

    try:
        timezone = ZoneInfo(app.config["TIMEZONE"])
    except ZoneInfoNotFoundError as exc:
        raise RuntimeError(f"未知时区 {app.config['TIMEZONE']!r}，请使用 IANA 时区名称。") from exc

    app.extensions["content_repository"] = ContentRepository(
        Path(app.config["CONTENT_DIR"]),
        timezone=timezone,
    )
    app.register_blueprint(site)

    @app.context_processor
    def inject_site_context() -> dict:
        now = datetime.now(timezone)
        return {
            "site": {
                "name": app.config["SITE_NAME"],
                "tagline": app.config["SITE_TAGLINE"],
                "description": app.config["SITE_DESCRIPTION"],
                "author": app.config["SITE_AUTHOR"],
                "url": app.config["SITE_URL"],
                "github_url": app.config["GITHUB_URL"],
            },
            "current_year": now.year,
        }

    @app.after_request
    def apply_security_headers(response):
        """为应用直连和反向代理场景提供一致的基础安全头。"""

        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault(
            "Permissions-Policy", "camera=(), geolocation=(), microphone=()"
        )
        response.headers.setdefault("Cross-Origin-Opener-Policy", "same-origin")
        response.headers.setdefault(
            "Content-Security-Policy",
            "; ".join(
                (
                    "default-src 'self'",
                    "base-uri 'none'",
                    "connect-src 'self'",
                    "font-src 'self'",
                    "form-action 'self'",
                    "frame-ancestors 'none'",
                    "img-src 'self' data:",
                    "object-src 'none'",
                    "script-src 'self'",
                    "style-src 'self'",
                )
            ),
        )
        if request.path.startswith("/static/"):
            response.headers["Cache-Control"] = "public, max-age=604800"
        return response

    @app.errorhandler(404)
    def not_found(_error):
        return render_template("404.html"), 404

    return app
