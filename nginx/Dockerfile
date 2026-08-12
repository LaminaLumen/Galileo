FROM nginx:1.30.3-alpine@sha256:0d3b80406a13a767339fbe2f41406d6c7da727ab89cf8fae399e81f780f814d1

RUN apk add --no-cache tzdata

ENV TZ=Asia/Shanghai

COPY --chown=101:101 nginx/nginx.conf /etc/nginx/nginx.conf
COPY --chown=101:101 nginx/default.conf /etc/nginx/conf.d/default.conf
COPY --chown=101:101 static /srv/static

USER 101:101

ENTRYPOINT ["nginx"]
CMD ["-g", "daemon off;"]
