"""
Flask Application Entrypoint for Secure Task Management API.
Author: Dhiopatty Alexander (0110225006)
"""

import os
from flask import Flask, request, jsonify
from .models import TaskPriority
from .services import TaskService, UserService
from .utils import setup_logger, format_response, validate_required_fields

logger = setup_logger("app")


def create_app() -> Flask:
    """Application factory for Flask app."""
    app = Flask(__name__)
    app.config["ENV_NAME"] = os.getenv("APP_ENV", "production")

    task_service = TaskService()
    user_service = UserService()

    @app.route("/health", methods=["GET"])
    def health_check():
        """Health check endpoint for monitoring."""
        return jsonify({
            "status": "healthy",
            "service": "secure-task-api",
            "version": "1.0.0",
            "environment": app.config["ENV_NAME"]
        }), 200

    @app.route("/api/v1/auth/register", methods=["POST"])
    def register():
        """Register a new user account."""
        data = request.get_json(silent=True) or {}
        valid, msg = validate_required_fields(data, ["username", "email", "password"])
        if not valid:
            res, code = format_response(False, message=msg, status_code=400)
            return jsonify(res), code

        try:
            user = user_service.register_user(
                username=data["username"],
                email=data["email"],
                password=data["password"],
                role=data.get("role", "developer")
            )
            res, code = format_response(True, data=user.to_dict(), message="User registered successfully.", status_code=201)
            return jsonify(res), code
        except ValueError as err:
            res, code = format_response(False, message=str(err), status_code=400)
            return jsonify(res), code

    @app.route("/api/v1/auth/login", methods=["POST"])
    def login():
        """Authenticate user credentials."""
        data = request.get_json(silent=True) or {}
        valid, msg = validate_required_fields(data, ["username", "password"])
        if not valid:
            res, code = format_response(False, message=msg, status_code=400)
            return jsonify(res), code

        user = user_service.authenticate(data["username"], data["password"])
        if not user:
            res, code = format_response(False, message="Invalid credentials.", status_code=401)
            return jsonify(res), code

        res, code = format_response(True, data=user.to_dict(), message="Authentication successful.")
        return jsonify(res), code

    @app.route("/api/v1/tasks", methods=["GET"])
    def get_tasks():
        """Fetch list of tasks with optional status filter."""
        status_filter = request.args.get("status")
        tasks = task_service.list_tasks(status=status_filter)
        res, code = format_response(True, data={"tasks": tasks, "count": len(tasks)})
        return jsonify(res), code

    @app.route("/api/v1/tasks", methods=["POST"])
    def create_task():
        """Create a new task."""
        data = request.get_json(silent=True) or {}
        valid, msg = validate_required_fields(data, ["title", "description"])
        if not valid:
            res, code = format_response(False, message=msg, status_code=400)
            return jsonify(res), code

        try:
            task = task_service.create_task(
                title=data["title"],
                description=data["description"],
                priority=data.get("priority", "medium"),
                assigned_to=data.get("assigned_to")
            )
            res, code = format_response(True, data=task.to_dict(), message="Task created successfully.", status_code=201)
            return jsonify(res), code
        except (ValueError, KeyError) as err:
            res, code = format_response(False, message=str(err), status_code=400)
            return jsonify(res), code

    @app.route("/api/v1/tasks/<task_id>", methods=["GET"])
    def get_task(task_id: str):
        """Fetch single task by ID."""
        task = task_service.get_task(task_id)
        if not task:
            res, code = format_response(False, message="Task not found.", status_code=404)
            return jsonify(res), code

        res, code = format_response(True, data=task.to_dict())
        return jsonify(res), code

    @app.route("/api/v1/tasks/<task_id>/status", methods=["PUT"])
    def update_task_status(task_id: str):
        """Update task workflow status."""
        data = request.get_json(silent=True) or {}
        valid, msg = validate_required_fields(data, ["status"])
        if not valid:
            res, code = format_response(False, message=msg, status_code=400)
            return jsonify(res), code

        try:
            task = task_service.update_task_status(task_id, data["status"])
            res, code = format_response(True, data=task.to_dict(), message="Task status updated.")
            return jsonify(res), code
        except KeyError:
            res, code = format_response(False, message="Task not found.", status_code=404)
            return jsonify(res), code
        except ValueError as err:
            res, code = format_response(False, message=str(err), status_code=400)
            return jsonify(res), code

    @app.route("/api/v1/tasks/<task_id>", methods=["DELETE"])
    def delete_task(task_id: str):
        """Delete task by ID."""
        success = task_service.delete_task(task_id)
        if not success:
            res, code = format_response(False, message="Task not found.", status_code=404)
            return jsonify(res), code

        res, code = format_response(True, message=f"Task {task_id} deleted successfully.")
        return jsonify(res), code

    @app.errorhandler(404)
    def not_found(e):
        res, code = format_response(False, message="Resource not found.", status_code=404)
        return jsonify(res), code

    @app.errorhandler(500)
    def internal_error(e):
        res, code = format_response(False, message="An internal error occurred.", status_code=500)
        return jsonify(res), code

    return app


if __name__ == "__main__":
    app_instance = create_app()
    # Explicit port and debug configuration for development
    app_instance.run(host="127.0.0.1", port=5000, debug=False)
