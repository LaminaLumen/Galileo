FROM nginx:1.31.0-alpine@sha256:2f07d83bf561b506400dc183b1b2003803e39efbd22451f848adaba14d28c7c7

RUN apk add --no-cache tzdata

ENV TZ=Asia/Shanghai

COPY --chown=101:101 nginx/nginx.conf /etc/nginx/nginx.conf
COPY --chown=101:101 nginx/default.conf /etc/nginx/conf.d/default.conf
COPY --chown=101:101 static /srv/static

USER 101:101

ENTRYPOINT ["nginx"]
CMD ["-g", "daemon off;"]
