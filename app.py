"""Galileo 的本地开发入口与 WSGI 入口。"""

from __future__ import annotations

import os

from galileo import create_app

app = create_app()


if __name__ == "__main__":
    app.run(
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "5000")),
        debug=os.getenv("FLASK_DEBUG", "0") == "1",
    )
