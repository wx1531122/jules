from flask import Blueprint, jsonify, request
from app import db
from app.models import Project # Stage, Task, SubTask are not directly used here but available via Project relationships
from sqlalchemy.exc import IntegrityError
from sqlalchemy import desc # For ordering
from datetime import datetime, timezone

projects_api_bp = Blueprint('projects_api', __name__)

# POST /api/projects - Create a new project
@projects_api_bp.route('/projects', methods=['POST'])
def create_project():
    data = request.get_json()
    if not data or not data.get('name'):
        return jsonify({"error": "Project name (name) is required"}), 400

    # Check if project name already exists
    if Project.query.filter_by(name=data['name']).first():
        return jsonify({"error": f"Project name \"{data['name']}\" already exists"}), 409

    new_project = Project(
        name=data['name'],
        description=data.get('description')
        # created_at and updated_at are handled by model defaults
    )
    try:
        db.session.add(new_project)
        db.session.commit()
        return jsonify(new_project.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        # Log the error e for server-side debugging
        print(f"Error creating project: {str(e)}")
        return jsonify({"error": "Failed to create project due to an internal server error"}), 500

# GET /api/projects - Retrieve all projects
@projects_api_bp.route('/projects', methods=['GET'])
def get_projects():
    try:
        projects = Project.query.order_by(desc(Project.created_at)).all()
        # Serialize without stages for the list view
        return jsonify([project.to_dict(include_stages=False) for project in projects]), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error fetching projects: {str(e)}")
        return jsonify({"error": "Failed to retrieve projects due to an internal server error"}), 500

# GET /api/projects/<string:project_id> - Retrieve a single project by ID
@projects_api_bp.route('/projects/<string:project_id>', methods=['GET'])
def get_project(project_id):
    try:
        project = Project.query.get(project_id)
        if not project:
            return jsonify({"error": "Project not found"}), 404
        # Serialize with stages and their tasks/subtasks
        return jsonify(project.to_dict(include_stages=True)), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error fetching project {project_id}: {str(e)}")
        return jsonify({"error": "Failed to retrieve project due to an internal server error"}), 500

# PUT /api/projects/<string:project_id> - Update an existing project
@projects_api_bp.route('/projects/<string:project_id>', methods=['PUT'])
def update_project(project_id):
    project = Project.query.get(project_id)
    if not project:
        return jsonify({"error": "Project not found"}), 404

    data = request.get_json()
    if not data: # Check if request body is empty
        return jsonify({"error": "Request body cannot be empty. Please provide 'name' and/or 'description'."}), 400

    # Validate name: if provided, it cannot be empty string.
    if 'name' in data and not data['name']:
        return jsonify({"error": "Project name cannot be an empty string if provided"}), 400
    
    # Check for name conflict if name is being changed
    if 'name' in data and data['name'] != project.name:
        if Project.query.filter(Project.name == data['name'], Project.id != project_id).first():
            return jsonify({"error": f"Project name \"{data['name']}\" is already used by another project"}), 409
        project.name = data['name']
    
    # Update description if provided (allows setting it to null or empty)
    if 'description' in data:
        project.description = data.get('description')
    
    # No specific fields to update means bad request, or could be idempotent 200 OK if nothing changed.
    # For this implementation, if only 'id' or other non-updatable fields are passed, it's not an error,
    # but nothing changes other than 'updated_at'.
    # If 'name' and 'description' are not in data, it means no intended update to these fields.
    if 'name' not in data and 'description' not in data:
        # Check if any other keys were provided. If only known keys, it's fine. If unknown keys, could be an error.
        # For simplicity, if no known fields are to be updated, we can return a message or the current project.
        # However, the model's onupdate for updated_at will trigger if we commit.
        # Let's ensure at least one field is intended for update or it's an empty JSON.
        # The earlier check `if not data:` handles empty JSON. If data exists but doesn't contain 'name' or 'description',
        # it could be an attempt to update other fields, which is not supported here.
        # For now, we proceed, and only `updated_at` might change.
        pass


    # updated_at is handled by the model's onupdate
    try:
        db.session.commit()
        return jsonify(project.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error updating project {project_id}: {str(e)}")
        return jsonify({"error": "Failed to update project due to an internal server error"}), 500

# DELETE /api/projects/<string:project_id> - Delete a project
@projects_api_bp.route('/projects/<string:project_id>', methods=['DELETE'])
def delete_project(project_id):
    project = Project.query.get(project_id)
    if not project:
        return jsonify({"error": "Project not found"}), 404
    try:
        db.session.delete(project) # Cascade delete should handle related items
        db.session.commit()
        return jsonify({"message": "Project successfully deleted"}), 200 # Or 204 No Content
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting project {project_id}: {str(e)}")
        return jsonify({"error": "Failed to delete project due to an internal server error"}), 500
