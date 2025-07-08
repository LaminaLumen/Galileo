# 使用官方 Python 基础镜像
FROM python:3.10-slim

# 设置工作目录
WORKDIR /flaskapp

# 复制依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 暴露应用端口（根据实际修改）
EXPOSE 5000

# 启动命令（根据实际修改）
# 或使用 gunicorn 等
CMD ["python", "FlaskApp.py"]