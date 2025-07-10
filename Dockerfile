# 使用官方 Python 基础镜像
FROM python:3.10-slim

# 安装Nginx
RUN apt-get update && \
    apt-get install -y nginx && \
    rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /flaskapp

# 复制依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# ======== Nginx配置 ========
# 1. 删除默认配置
RUN rm /etc/nginx/sites-enabled/default

# 2. 复制自定义配置
COPY config/nginx_flaskapp.conf /etc/nginx/sites-available/
RUN ln -s /etc/nginx/sites-available/nginx_flaskapp.conf /etc/nginx/sites-enabled/

# 3. 日志重定向
RUN ln -sf /dev/stdout /var/log/nginx/access.log && \
    ln -sf /dev/stderr /var/log/nginx/error.log

# ======== 启动设置 ========
# 复制启动脚本
COPY start.sh /start.sh
RUN chmod +x /start.sh

# 暴露Nginx端口（根据DNS图片，Cloudflare需连接此端口）
EXPOSE 80

# 使用启动脚本
CMD ["/start.sh"]