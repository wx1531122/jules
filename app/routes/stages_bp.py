from flask import Blueprint, jsonify, request
from app import db
from app.models import Stage, Project # Task model is not directly used here
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func # For db.func.max

stages_api_bp = Blueprint('stages_api', __name__)

# POST /api/projects/<string:project_id>/stages - Create a new stage for a project
@stages_api_bp.route('/projects/<string:project_id>/stages', methods=['POST'])
def create_stage_for_project(project_id):
    project = Project.query.get(project_id)
    if not project:
        return jsonify({"error": "Project not found"}), 404

    data = request.get_json()
    if not data or not data.get('name'):
        return jsonify({"error": "Stage name (name) is required"}), 400

    # Determine order: place new stage at the end
    # Query for the maximum 'order' value among stages for this project.
    # func.max(Stage.order) returns None if there are no stages, so handle that.
    current_max_order = db.session.query(func.max(Stage.order)).filter(Stage.project_id == project_id).scalar()
    
    new_order = 0
    if current_max_order is not None: # If there are existing stages
        new_order = current_max_order + 1
    
    new_stage = Stage(
        name=data['name'],
        project_id=project_id,
        order=new_order
        # created_at and updated_at are handled by model defaults
    )
    try:
        db.session.add(new_stage)
        db.session.commit()
        # Serialize without tasks for this specific response as per common practice for creation
        return jsonify(new_stage.to_dict(include_tasks=False)), 201 
    except Exception as e:
        db.session.rollback()
        # Log the error e for server-side debugging
        print(f"Error creating stage for project {project_id}: {str(e)}")
        return jsonify({"error": "Failed to create stage due to an internal server error"}), 500

# PUT /api/stages/<string:stage_id> - Update an existing stage
@stages_api_bp.route('/stages/<string:stage_id>', methods=['PUT'])
def update_stage(stage_id):
    stage = Stage.query.get(stage_id)
    if not stage:
        return jsonify({"error": "Stage not found"}), 404

    data = request.get_json()
    if not data: # Check if request body is empty
        return jsonify({"error": "Request body cannot be empty. Please provide 'name' and/or 'order'."}), 400

    updated = False
    if 'name' in data:
        if not data['name']: # Name cannot be set to an empty string
             return jsonify({"error": "Stage name cannot be an empty string if provided"}), 400
        stage.name = data['name']
        updated = True
    
    if 'order' in data:
        try:
            new_order = int(data['order'])
            # Add validation for negative order if necessary, e.g. if new_order < 0: return error
            stage.order = new_order
            updated = True
            # Note: This simple order update doesn't automatically re-order other stages.
            # If a full re-ordering (maintaining contiguous, unique order) is needed,
            # that logic would be significantly more complex and involve querying other stages
            # for the same project and potentially shifting them.
        except ValueError:
            return jsonify({"error": "Order must be an integer"}), 400
    
    if not updated:
        # If data was provided, but 'name' or 'order' were not present or not valid for update.
        # Or, we could return 200 OK with current representation if no valid fields for update were passed.
        # For now, let's assume if data is present, it must contain at least one updatable field.
        # If 'name' and 'order' are not in data, it means no intended update to these fields.
        # It's not strictly an error if the state doesn't change, updated_at will still change.
        pass # Proceed to commit, updated_at will be handled by model

    # updated_at is handled by the model's onupdate
    try:
        db.session.commit()
        return jsonify(stage.to_dict(include_tasks=True)), 200 # Show tasks after update
    except Exception as e:
        db.session.rollback()
        print(f"Error updating stage {stage_id}: {str(e)}")
        return jsonify({"error": "Failed to update stage due to an internal server error"}), 500

# DELETE /api/stages/<string:stage_id> - Delete a stage
@stages_api_bp.route('/stages/<string:stage_id>', methods=['DELETE'])
def delete_stage(stage_id):
    stage = Stage.query.get(stage_id)
    if not stage:
        return jsonify({"error": "Stage not found"}), 404
    try:
        db.session.delete(stage) # Cascade delete should handle related tasks
        db.session.commit()
        return jsonify({"message": "Stage successfully deleted"}), 200 # Or 204 No Content
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting stage {stage_id}: {str(e)}")
        return jsonify({"error": "Failed to delete stage due to an internal server error"}), 500
