from flask import Blueprint, jsonify, request
from app import db
from app.models import Task, Stage # SubTask model is not directly used here but its instances are handled by Task's to_dict
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func # For db.func.max
from datetime import datetime # For date parsing

tasks_api_bp = Blueprint('tasks_api', __name__)

# Helper for date parsing
def parse_date_string(date_str):
    if date_str is None:
        return None
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except (ValueError, TypeError): # Catch TypeError if date_str is not string-like (e.g. int)
        return 'error' # Signal error for caller to handle

# POST /api/stages/<string:stage_id>/tasks - Create a new task for a stage
@tasks_api_bp.route('/stages/<string:stage_id>/tasks', methods=['POST'])
def create_task_for_stage(stage_id):
    stage = Stage.query.get(stage_id)
    if not stage:
        return jsonify({"error": "Stage not found"}), 404

    data = request.get_json()
    if not data or not data.get('content'):
        return jsonify({"error": "Task content (content) is required"}), 400

    start_date_obj = parse_date_string(data.get('start_date'))
    if start_date_obj == 'error':
        return jsonify({"error": "Invalid start_date format. Use YYYY-MM-DD."}), 400
    
    end_date_obj = parse_date_string(data.get('end_date'))
    if end_date_obj == 'error':
        return jsonify({"error": "Invalid end_date format. Use YYYY-MM-DD."}), 400

    # Determine order: place new task at the end of the stage
    current_max_order = db.session.query(func.max(Task.order)).filter(Task.stage_id == stage_id).scalar()
    
    new_order = 0
    if current_max_order is not None: # If there are existing tasks in this stage
        new_order = current_max_order + 1
    
    new_task = Task(
        content=data['content'],
        stage_id=stage_id,
        assignee=data.get('assignee'),
        start_date=start_date_obj,
        end_date=end_date_obj,
        order=new_order
        # created_at and updated_at are handled by model defaults
    )
    try:
        db.session.add(new_task)
        db.session.commit()
        # Serialize with subtasks (will be empty list for new task)
        return jsonify(new_task.to_dict(include_subtasks=True)), 201 
    except Exception as e:
        db.session.rollback()
        # Log the error e for server-side debugging
        print(f"Error creating task for stage {stage_id}: {str(e)}")
        return jsonify({"error": f"Failed to create task: {str(e)}"}), 500

# PUT /api/tasks/<string:task_id> - Update an existing task
@tasks_api_bp.route('/tasks/<string:task_id>', methods=['PUT'])
def update_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404

    data = request.get_json()
    if not data: # Check if request body is empty
        return jsonify({"error": "Request body cannot be empty. Please provide fields to update."}), 400

    updated = False # Track if any attribute was actually changed

    if 'content' in data:
        if not data['content']: # Content cannot be set to an empty string
             return jsonify({"error": "Task content cannot be an empty string if provided"}), 400
        task.content = data['content']
        updated = True
    
    if 'assignee' in data: # Allows setting assignee to null or a new string
        task.assignee = data.get('assignee')
        updated = True

    if 'start_date' in data:
        start_date_obj = parse_date_string(data.get('start_date'))
        if start_date_obj == 'error':
            return jsonify({"error": "Invalid start_date format. Use YYYY-MM-DD."}), 400
        task.start_date = start_date_obj
        updated = True

    if 'end_date' in data:
        end_date_obj = parse_date_string(data.get('end_date'))
        if end_date_obj == 'error':
            return jsonify({"error": "Invalid end_date format. Use YYYY-MM-DD."}), 400
        task.end_date = end_date_obj
        updated = True
        
    if 'order' in data:
        try:
            new_order = int(data['order'])
            # Add validation for negative order if necessary
            # if new_order < 0: return jsonify({"error": "Order cannot be negative"}), 400
            task.order = new_order
            updated = True
        except ValueError:
            return jsonify({"error": "Order must be an integer"}), 400

    if 'stage_id' in data and data['stage_id'] != task.stage_id:
        target_stage_id = data['stage_id']
        target_stage = Stage.query.get(target_stage_id)
        if not target_stage:
            return jsonify({"error": f"Target stage with id {target_stage_id} not found"}), 404
        task.stage_id = target_stage_id
        updated = True
        # If 'order' is not also part of this request when moving stages, its current 'order' value
        # is maintained, which might lead to order conflicts or non-sequential order in the new stage.
        # The subtask description implies 'order' would be part of the request if re-ordering is desired.
        # A more robust solution might re-calculate order (e.g., append to end) if not specified.

    if not updated and data: # Data was provided but no recognized fields were changed
        # This could return the current task representation or a specific message.
        # For now, we proceed, only 'updated_at' will change.
        pass

    # updated_at is handled by the model's onupdate
    try:
        db.session.commit()
        return jsonify(task.to_dict(include_subtasks=True)), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error updating task {task_id}: {str(e)}")
        return jsonify({"error": f"Failed to update task: {str(e)}"}), 500

# DELETE /api/tasks/<string:task_id> - Delete a task
@tasks_api_bp.route('/tasks/<string:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    try:
        db.session.delete(task) # Cascade delete should handle related subtasks
        db.session.commit()
        return jsonify({"message": "Task successfully deleted"}), 200 # Or 204 No Content
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting task {task_id}: {str(e)}")
        return jsonify({"error": f"Failed to delete task: {str(e)}"}), 500
