FROM nginx:1.31.3-alpine@sha256:4a73073bd557c65b759505da037898b61f1be6cbcc3c2c3aeac22d2a470c1752

RUN apk add --no-cache tzdata

ENV TZ=Asia/Shanghai

COPY --chown=101:101 nginx/nginx.conf /etc/nginx/nginx.conf
COPY --chown=101:101 nginx/default.conf /etc/nginx/conf.d/default.conf
COPY --chown=101:101 static /srv/static

USER 101:101

ENTRYPOINT ["nginx"]
CMD ["-g", "daemon off;"]
