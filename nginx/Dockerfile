FROM nginx:1.31.5-alpine@sha256:72ba65eb42c10344912a84ff42408db7d34f2feb642204570ab8fc5ffd29f1d3

RUN apk add --no-cache tzdata

ENV TZ=Asia/Shanghai

COPY --chown=101:101 nginx/nginx.conf /etc/nginx/nginx.conf
COPY --chown=101:101 nginx/default.conf /etc/nginx/conf.d/default.conf
COPY --chown=101:101 static /srv/static

USER 101:101

ENTRYPOINT ["nginx"]
CMD ["-g", "daemon off;"]
