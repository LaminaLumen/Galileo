import functools
from flask import Flask, request, Response, render_template, jsonify
from utils.response_util import ResponseBuilder

app = Flask(
    __name__,
    template_folder='templates',
    static_folder='templates/static',
)


def standard_response(func):
    """将视图函数包装为标准化响应的装饰器"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            # 执行原函数
            result = func(*args, **kwargs)

            # 处理返回的数据
            if isinstance(result, tuple):
                data, meta = result
            else:
                data, meta = result, None

            # 构建成功响应
            return ResponseBuilder.success(data=data, metadata=meta)

        except Exception as e:
            # 处理捕获异常
            app.logger.exception("Unhandled exception")
            return ResponseBuilder.error(
                message="Internal server error",
                status=500,
                code="INTERNAL_SERVER_ERROR",
            )

    return wrapper


@app.route('/', methods=['GET'])
def homePage():
    return render_template('index2.html')


if __name__ == '__main__':
    # host = '0.0.0.0'时，表示监听所有地址，包括本机地址和外网地址
    app.run(host='0.0.0.0', port=5000)
