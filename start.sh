#!/bin/bash
# 启动Flask应用后台运行
python FlaskApp.py &

# 启动Nginx前台运行（保持容器不退出）
nginx -g 'daemon off;'