from flask import jsonify
import datetime


class ResponseBuilder:
    @staticmethod
    def success(data=None, message="Success", pagination=None, metadata=None):
        """构建成功响应"""
        return ResponseBuilder._build(
            status=200,
            message=message,
            data=data,
            pagination=pagination,
            metadata=metadata
        )

    @staticmethod
    def error(message="Error", status=400, code=None, errors=None):
        """构建错误响应"""
        return ResponseBuilder._build(
            status=status,
            message=message,
            code=code,
            errors=errors
        )

    @staticmethod
    def created(data=None, message="Resource created"):
        """资源创建成功响应"""
        return ResponseBuilder._build(
            status=201,
            message=message,
            data=data
        )

    @staticmethod
    def _build(status, message, data=None, pagination=None, metadata=None, code=None, errors=None):
        """内部构造响应方法"""
        response = {
            "status": status,
            "message": message,
            "timestamp": datetime.datetime.utcnow().isoformat() + 'Z'
        }

        # 可选字段处理
        if data is not None:
            response["data"] = data

        if pagination:
            response["pagination"] = pagination

        if metadata:
            response["metadata"] = metadata

        if code:
            response["code"] = code

        if errors:
            response["errors"] = errors

        return jsonify(response), status
