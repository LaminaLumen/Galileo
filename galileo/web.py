"""Galileo 的公开 Web 路由。"""

from __future__ import annotations

from collections import Counter
from datetime import datetime
from email.utils import format_datetime
from xml.etree import ElementTree

from flask import Blueprint, Response, abort, current_app, jsonify, render_template, request

from galileo.content import ContentRepository

site = Blueprint("site", __name__)


def _repository() -> ContentRepository:
    return current_app.extensions["content_repository"]


def _show_drafts() -> bool:
    return bool(current_app.config["SHOW_DRAFTS"])


@site.get("/")
def index():
    posts = _repository().list_posts(include_drafts=_show_drafts())
    selected_tag = request.args.get("tag", "").strip()
    if selected_tag:
        posts = [post for post in posts if selected_tag in post.tags]

    tag_counts = Counter(
        tag for post in _repository().list_posts(include_drafts=_show_drafts()) for tag in post.tags
    )
    featured = next((post for post in posts if post.featured), None)
    return render_template(
        "index.html",
        posts=posts,
        featured=featured,
        tag_counts=tag_counts.most_common(),
        selected_tag=selected_tag,
    )


@site.get("/posts/<slug>/")
def post_detail(slug: str):
    post = _repository().get_post(slug, include_drafts=_show_drafts())
    if post is None:
        abort(404)
    return render_template("post.html", post=post)


@site.get("/about/")
def about():
    return render_template("about.html")


@site.get("/healthz")
def health():
    timezone = _repository().timezone
    return jsonify(
        status="ok",
        service="galileo",
        time=datetime.now(timezone).isoformat(),
        timezone=current_app.config["TIMEZONE"],
    )


@site.get("/feed.xml")
def feed():
    posts = _repository().list_posts(include_drafts=False)[:20]
    base_url = current_app.config["SITE_URL"]
    rss = ElementTree.Element("rss", version="2.0")
    channel = ElementTree.SubElement(rss, "channel")
    ElementTree.SubElement(channel, "title").text = current_app.config["SITE_NAME"]
    ElementTree.SubElement(channel, "link").text = base_url
    ElementTree.SubElement(channel, "description").text = current_app.config["SITE_DESCRIPTION"]
    ElementTree.SubElement(channel, "language").text = "zh-CN"
    if posts:
        ElementTree.SubElement(channel, "lastBuildDate").text = format_datetime(
            posts[0].published_at
        )

    for post in posts:
        url = f"{base_url}/posts/{post.slug}/"
        item = ElementTree.SubElement(channel, "item")
        ElementTree.SubElement(item, "title").text = post.title
        ElementTree.SubElement(item, "link").text = url
        ElementTree.SubElement(item, "guid", isPermaLink="true").text = url
        ElementTree.SubElement(item, "description").text = post.summary
        ElementTree.SubElement(item, "pubDate").text = format_datetime(post.published_at)

    xml = ElementTree.tostring(rss, encoding="utf-8", xml_declaration=True)
    return Response(xml, content_type="application/rss+xml; charset=utf-8")


@site.get("/sitemap.xml")
def sitemap():
    base_url = current_app.config["SITE_URL"]
    namespace = "http://www.sitemaps.org/schemas/sitemap/0.9"
    ElementTree.register_namespace("", namespace)
    urlset = ElementTree.Element(f"{{{namespace}}}urlset")
    entries = [(base_url + "/", None), (base_url + "/about/", None)]
    entries.extend(
        (f"{base_url}/posts/{post.slug}/", post.published_at.date().isoformat())
        for post in _repository().list_posts(include_drafts=False)
    )
    for location, modified in entries:
        url = ElementTree.SubElement(urlset, f"{{{namespace}}}url")
        ElementTree.SubElement(url, f"{{{namespace}}}loc").text = location
        if modified:
            ElementTree.SubElement(url, f"{{{namespace}}}lastmod").text = modified
    xml = ElementTree.tostring(urlset, encoding="utf-8", xml_declaration=True)
    return Response(xml, content_type="application/xml; charset=utf-8")


@site.get("/robots.txt")
def robots():
    body = f"User-agent: *\nAllow: /\nSitemap: {current_app.config['SITE_URL']}/sitemap.xml\n"
    return Response(body, content_type="text/plain; charset=utf-8")
