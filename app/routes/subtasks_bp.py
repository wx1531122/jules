from flask import Blueprint, jsonify, request
from app import db
from app.models import SubTask, Task # Task needed for parent task validation
from sqlalchemy.exc import IntegrityError # Though not explicitly used for custom checks here, good to have for db errors
from sqlalchemy import func # For db.func.max

subtasks_api_bp = Blueprint('subtasks_api', __name__)

# POST /api/tasks/<string:parent_task_id>/subtasks - Create a new subtask for a parent task
@subtasks_api_bp.route('/tasks/<string:parent_task_id>/subtasks', methods=['POST'])
def create_subtask_for_task(parent_task_id):
    parent_task = Task.query.get(parent_task_id)
    if not parent_task:
        return jsonify({"error": "Parent task not found"}), 404

    data = request.get_json()
    if not data or not data.get('content'):
        return jsonify({"error": "Subtask content (content) is required"}), 400

    # Determine order: place new subtask at the end
    current_max_order = db.session.query(func.max(SubTask.order)).filter(SubTask.parent_task_id == parent_task_id).scalar()
    # Illustrative code uses filter_by, which is fine. My current is filter(). Sticking to current.
    
    new_order = 0
    if current_max_order is not None: # If there are existing subtasks
        new_order = current_max_order + 1
    
    # Validate 'completed' field if present - keeping my robust check
    completed_status = data.get('completed', False) # Default to False
    if not isinstance(completed_status, bool):
        return jsonify({"error": "Completed status must be a boolean"}), 400

    new_subtask = SubTask(
        content=data['content'],
        parent_task_id=parent_task_id,
        completed=completed_status, # Using validated status
        order=new_order
        # created_at and updated_at are handled by model defaults
    )
    try:
        db.session.add(new_subtask)
        db.session.commit()
        return jsonify(new_subtask.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        # Log the error e for server-side debugging
        print(f"Error creating subtask for task {parent_task_id}: {str(e)}")
        return jsonify({"error": f"Failed to create subtask: {str(e)}"}), 500

# PUT /api/subtasks/<string:subtask_id> - Update an existing subtask
@subtasks_api_bp.route('/subtasks/<string:subtask_id>', methods=['PUT'])
def update_subtask(subtask_id):
    subtask = SubTask.query.get(subtask_id)
    if not subtask:
        return jsonify({"error": "Subtask not found"}), 404

    data = request.get_json()
    if not data: # Check if request body is empty
        return jsonify({"error": "Request body cannot be empty"}), 400 # Aligned with illustrative

    if 'content' in data:
        if not data['content']: # Content cannot be set to an empty string
             return jsonify({"error": "Subtask content cannot be empty"}), 400 # Aligned
        subtask.content = data['content']
    
    if 'completed' in data:
        if not isinstance(data['completed'], bool): # Keeping robust check
            return jsonify({"error": "Completed status must be a boolean"}), 400
        subtask.completed = data['completed']
        
    if 'order' in data:
        try:
            new_order = int(data['order']) # Illustrative sets subtask.order directly, I'll use new_order then set
            subtask.order = new_order
        except ValueError:
            return jsonify({"error": "Order must be an integer"}), 400
    
    # Removed 'updated' flag logic, direct assignment is fine as per illustrative.
    # updated_at is handled by the model's onupdate
    try:
        db.session.commit()
        return jsonify(subtask.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error updating subtask {subtask_id}: {str(e)}")
        return jsonify({"error": f"Failed to update subtask: {str(e)}"}), 500

# DELETE /api/subtasks/<string:subtask_id> - Delete a subtask
@subtasks_api_bp.route('/subtasks/<string:subtask_id>', methods=['DELETE'])
def delete_subtask(subtask_id):
    subtask = SubTask.query.get(subtask_id)
    if not subtask:
        return jsonify({"error": "Subtask not found"}), 404
    try:
        db.session.delete(subtask)
        db.session.commit()
        return jsonify({"message": "SubTask successfully deleted"}), 200 # Or 204 No Content
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting subtask {subtask_id}: {str(e)}")
        return jsonify({"error": f"Failed to delete subtask: {str(e)}"}), 500
