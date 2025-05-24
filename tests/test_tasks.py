import json
import pytest
from app.models import Project, Stage, Task, SubTask, db # For verifying deletions and setup

# Helper fixture to create a project
@pytest.fixture
def project(client):
    response = client.post('/api/projects', json={'name': 'Test Project for Tasks', 'description': 'Project for task tests'})
    assert response.status_code == 201
    return response.json

# Helper fixture to create a stage
@pytest.fixture
def stage(client, project):
    project_id = project['id']
    response = client.post(f'/api/projects/{project_id}/stages', json={'name': 'Test Stage for Tasks'})
    assert response.status_code == 201
    return response.json

# POST /api/stages/<stage_id>/tasks
def test_create_task_success(client, stage):
    stage_id = stage['id']
    response = client.post(f'/api/stages/{stage_id}/tasks', json={
        'content': 'New Task Content',
        'assignee': 'testuser@example.com',
        'start_date': '2024-01-01',
        'end_date': '2024-01-10'
    })
    assert response.status_code == 201
    data = response.json
    assert data['content'] == 'New Task Content'
    assert data['stage_id'] == stage_id
    assert data['assignee'] == 'testuser@example.com'
    assert data['start_date'] == '2024-01-01'
    assert data['end_date'] == '2024-01-10'
    assert 'id' in data
    assert data['order'] == 0 # First task in stage
    # Check DB
    task = Task.query.get(data['id'])
    assert task is not None
    assert task.content == 'New Task Content'

def test_create_task_verify_order_assignment(client, stage):
    stage_id = stage['id']
    # Create first task
    response1 = client.post(f'/api/stages/{stage_id}/tasks', json={'content': 'Task One'})
    assert response1.status_code == 201
    assert response1.json['order'] == 0
    
    # Create second task
    response2 = client.post(f'/api/stages/{stage_id}/tasks', json={'content': 'Task Two'})
    assert response2.status_code == 201
    assert response2.json['order'] == 1

def test_create_task_non_existent_stage(client):
    response = client.post('/api/stages/non_existent_stage_id/tasks', json={'content': 'Task for Ghost Stage'})
    assert response.status_code == 404
    data = response.json
    assert data['error'] == 'Stage not found'

def test_create_task_missing_content(client, stage):
    stage_id = stage['id']
    response = client.post(f'/api/stages/{stage_id}/tasks', json={}) # Missing content
    assert response.status_code == 400
    data = response.json
    assert data['error'] == 'Task content (content) is required'

def test_create_task_invalid_date_formats(client, stage):
    stage_id = stage['id']
    # Invalid start_date
    response_start = client.post(f'/api/stages/{stage_id}/tasks', json={'content': 'Test', 'start_date': '01-01-2024'})
    assert response_start.status_code == 400
    assert response_start.json['error'] == 'Invalid start_date format. Use YYYY-MM-DD.'
    # Invalid end_date
    response_end = client.post(f'/api/stages/{stage_id}/tasks', json={'content': 'Test', 'end_date': '2024/01/01'})
    assert response_end.status_code == 400
    assert response_end.json['error'] == 'Invalid end_date format. Use YYYY-MM-DD.'

# PUT /api/tasks/<task_id>
def test_update_task_success(client, stage):
    stage_id = stage['id']
    # Create a task first
    task_response = client.post(f'/api/stages/{stage_id}/tasks', json={'content': 'Old Task Content', 'order': 0})
    task_id = task_response.json['id']

    # Create another stage to test moving the task
    project_id = stage['project_id']
    other_stage_response = client.post(f'/api/projects/{project_id}/stages', json={'name': 'Other Stage'})
    other_stage_id = other_stage_response.json['id']

    update_payload = {
        'content': 'Updated Task Content',
        'assignee': 'newassignee@example.com',
        'start_date': '2024-02-01',
        'end_date': '2024-02-15',
        'order': 10,
        'stage_id': other_stage_id
    }
    response = client.put(f'/api/tasks/{task_id}', json=update_payload)
    assert response.status_code == 200
    data = response.json
    assert data['content'] == 'Updated Task Content'
    assert data['assignee'] == 'newassignee@example.com'
    assert data['start_date'] == '2024-02-01'
    assert data['end_date'] == '2024-02-15'
    assert data['order'] == 10
    assert data['stage_id'] == other_stage_id
    # Check DB
    task = Task.query.get(task_id)
    assert task.content == 'Updated Task Content'
    assert task.stage_id == other_stage_id

def test_update_task_non_existent(client):
    response = client.put('/api/tasks/non_existent_task_id', json={'content': 'Trying to update ghost task'})
    assert response.status_code == 404
    data = response.json
    assert data['error'] == 'Task not found'

def test_update_task_empty_content(client, stage):
    stage_id = stage['id']
    task_response = client.post(f'/api/stages/{stage_id}/tasks', json={'content': 'Valid Task Content'})
    task_id = task_response.json['id']
    response = client.put(f'/api/tasks/{task_id}', json={'content': ''}) # Empty content
    assert response.status_code == 400
    data = response.json
    assert data['error'] == 'Task content cannot be an empty string if provided'

def test_update_task_invalid_date_formats(client, stage):
    stage_id = stage['id']
    task_response = client.post(f'/api/stages/{stage_id}/tasks', json={'content': 'Task for date update test'})
    task_id = task_response.json['id']
    # Invalid start_date
    response_start = client.put(f'/api/tasks/{task_id}', json={'start_date': 'bad-date'})
    assert response_start.status_code == 400
    assert response_start.json['error'] == 'Invalid start_date format. Use YYYY-MM-DD.'
    # Invalid end_date
    response_end = client.put(f'/api/tasks/{task_id}', json={'end_date': '12/31/2024'})
    assert response_end.status_code == 400
    assert response_end.json['error'] == 'Invalid end_date format. Use YYYY-MM-DD.'

def test_update_task_invalid_order(client, stage):
    stage_id = stage['id']
    task_response = client.post(f'/api/stages/{stage_id}/tasks', json={'content': 'Task for order update test'})
    task_id = task_response.json['id']
    response = client.put(f'/api/tasks/{task_id}', json={'order': 'not-an-integer'})
    assert response.status_code == 400
    data = response.json
    assert data['error'] == 'Order must be an integer'

def test_update_task_moving_to_non_existent_stage(client, stage):
    stage_id = stage['id']
    task_response = client.post(f'/api/stages/{stage_id}/tasks', json={'content': 'Task to be moved'})
    task_id = task_response.json['id']
    response = client.put(f'/api/tasks/{task_id}', json={'stage_id': 'non_existent_stage_id_for_move'})
    assert response.status_code == 404 # This is the stage_id check
    data = response.json
    assert data['error'] == 'Target stage with id non_existent_stage_id_for_move not found'

# DELETE /api/tasks/<task_id>
def test_delete_task_success(client, stage, app): # app fixture for db context
    stage_id = stage['id']
    # Create a task
    task_resp = client.post(f'/api/stages/{stage_id}/tasks', json={'content': 'Task To Be Deleted'})
    task_id = task_resp.json['id']
    
    # Create a subtask in that task
    sub_task_resp = client.post(f'/api/tasks/{task_id}/subtasks', json={'content': 'Subtask in deleted task'})
    sub_task_id = sub_task_resp.json['id']

    delete_response = client.delete(f'/api/tasks/{task_id}')
    assert delete_response.status_code == 200
    data = delete_response.json
    assert data['message'] == 'Task successfully deleted'

    # Verify it's gone from DB along with its subtasks
    with app.app_context():
        assert Task.query.get(task_id) is None
        assert SubTask.query.get(sub_task_id) is None

def test_delete_task_non_existent(client):
    response = client.delete('/api/tasks/non_existent_task_id')
    assert response.status_code == 404
    data = response.json
    assert data['error'] == 'Task not found'

def test_update_task_partial_updates(client, stage):
    stage_id = stage['id']
    task_resp = client.post(f'/api/stages/{stage_id}/tasks', json={
        'content': 'Initial Content', 
        'assignee': 'user1', 
        'start_date': '2023-01-01',
        'order': 1
    })
    task_id = task_resp.json['id']

    # Update only content
    res_content = client.put(f'/api/tasks/{task_id}', json={'content': 'Updated Content Only'})
    assert res_content.status_code == 200
    assert res_content.json['content'] == 'Updated Content Only'
    assert res_content.json['assignee'] == 'user1' # Should remain

    # Update only assignee
    res_assignee = client.put(f'/api/tasks/{task_id}', json={'assignee': 'user2'})
    assert res_assignee.status_code == 200
    assert res_assignee.json['assignee'] == 'user2'
    assert res_assignee.json['content'] == 'Updated Content Only' # Should remain from previous update

    # Update only order
    res_order = client.put(f'/api/tasks/{task_id}', json={'order': 5})
    assert res_order.status_code == 200
    assert res_order.json['order'] == 5

def test_update_task_empty_json(client, stage):
    stage_id = stage['id']
    task_response = client.post(f'/api/stages/{stage_id}/tasks', json={'content': 'Task For Empty JSON Update'})
    task_id = task_response.json['id']
    
    response = client.put(f'/api/tasks/{task_id}', json={})
    assert response.status_code == 400
    data = response.json
    assert data['error'] == "Request body cannot be empty. Please provide fields to update."

def test_create_task_minimal_payload(client, stage):
    stage_id = stage['id']
    response = client.post(f'/api/stages/{stage_id}/tasks', json={'content': 'Minimal Task'})
    assert response.status_code == 201
    data = response.json
    assert data['content'] == 'Minimal Task'
    assert data['stage_id'] == stage_id
    assert data['assignee'] is None
    assert data['start_date'] is None
    assert data['end_date'] is None
    assert data['order'] == 0 # Assuming it's the first task
    assert data['subtasks'] == [] # Should have empty subtasks list by default
    
    # Check DB
    task = Task.query.get(data['id'])
    assert task is not None
    assert task.content == 'Minimal Task'
    assert task.assignee is None
    assert task.start_date is None
    assert task.end_date is None
