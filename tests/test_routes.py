from __future__ import annotations

from xml.etree import ElementTree


def test_home_lists_public_posts_and_filters_by_tag(client):
    response = client.get("/")

    assert response.status_code == 200
    assert "你好，Galileo" in response.text
    assert "尚未发布" not in response.text
    assert "把自己的坐标" in response.text

    filtered = client.get("/?tag=不存在")
    assert filtered.status_code == 200
    assert "暂时没有匹配" in filtered.text


def test_home_supports_a_repository_without_featured_post(app, content_dir):
    featured_path = content_dir / "hello-galileo.md"
    featured_path.write_text(
        featured_path.read_text(encoding="utf-8").replace("featured: true", "featured: false"),
        encoding="utf-8",
    )

    response = app.test_client().get("/")

    assert response.status_code == 200
    assert "你好，Galileo" in response.text


def test_post_about_and_404_routes(client):
    post = client.get("/posts/hello-galileo/")
    about = client.get("/about/")
    missing = client.get("/posts/not-found/")

    assert post.status_code == 200
    assert "<strong>加粗内容</strong>" in post.text
    assert about.status_code == 200
    assert "文件优先" in about.text
    assert missing.status_code == 404
    assert "SIGNAL LOST" in missing.text


def test_health_uses_explicit_timezone(client):
    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json["status"] == "ok"
    assert response.json["timezone"] == "Asia/Shanghai"
    assert response.json["time"].endswith("+08:00")


def test_feed_and_sitemap_publish_canonical_urls(client):
    feed = client.get("/feed.xml")
    sitemap = client.get("/sitemap.xml")

    assert feed.status_code == 200
    assert feed.mimetype == "application/rss+xml"
    feed_root = ElementTree.fromstring(feed.data)
    assert feed_root.findtext("./channel/title") == "Galileo"
    assert feed_root.findtext("./channel/item/link") == (
        "https://galileo.example/posts/hello-galileo/"
    )

    assert sitemap.status_code == 200
    sitemap_root = ElementTree.fromstring(sitemap.data)
    locations = [element.text for element in sitemap_root.findall("{*}url/{*}loc")]
    assert "https://galileo.example/posts/hello-galileo/" in locations


def test_robots_and_security_headers(client):
    robots = client.get("/robots.txt")
    response = client.get("/")

    assert "Sitemap: https://galileo.example/sitemap.xml" in robots.text
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Permissions-Policy"] == ("camera=(), geolocation=(), microphone=()")
    assert "script-src 'self'" in response.headers["Content-Security-Policy"]
    assert "frame-ancestors 'none'" in response.headers["Content-Security-Policy"]


def test_static_assets_are_cacheable(client):
    response = client.get("/static/favicon.svg")

    assert response.status_code == 200
    assert response.headers["Cache-Control"] == "public, max-age=604800"
