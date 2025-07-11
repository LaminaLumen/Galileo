# ⬇️⬇️⬇️ 关键修改点 ⬇️⬇️⬇️
# 使用官方 Python 基础镜像
FROM python:3.10-slim

# 安装依赖
RUN apt-get update && \
    apt-get install -y --no-install-recommends nginx-light && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /flaskapp

# 先复制启动脚本 👇 确保在根目录！
COPY ./start.sh /start.sh
RUN chmod +x /start.sh

# 复制证书文件
COPY ./nginx/certs/galileoblog.pem /etc/nginx/ssl/
COPY ./nginx/certs/galileoblog.key /etc/nginx/ssl/
RUN chmod 400 /etc/nginx/ssl/galileoblog.key

# 复制依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件（注意排除证书目录）
COPY . /flaskapp

# 以下保持原有配置...
RUN mkdir -p /var/www/certbot /etc/nginx/ssl
COPY nginx/flaskapp.conf /etc/nginx/conf.d/default.conf
RUN ln -sf /dev/stderr /var/log/nginx/error.log && \
    sed -i '/pid /d' /etc/nginx/nginx.conf

# 暴露端口
EXPOSE 80 443

# 启动容器
CMD ["/start.sh"]