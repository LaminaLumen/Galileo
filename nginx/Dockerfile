FROM nginx:1.31.7-alpine@sha256:892bb2152464f0c5d8972593a5f5afaf8054552580b699d95f8ff4af08c2d33d

RUN apk add --no-cache tzdata

ENV TZ=Asia/Shanghai

COPY --chown=101:101 nginx/nginx.conf /etc/nginx/nginx.conf
COPY --chown=101:101 nginx/default.conf /etc/nginx/conf.d/default.conf
COPY --chown=101:101 static /srv/static

USER 101:101

ENTRYPOINT ["nginx"]
CMD ["-g", "daemon off;"]
