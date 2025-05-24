import json
import pytest
from app.models import Project, Stage, Task, SubTask, db # For verifying deletions and setup

# Helper fixture to create a project
@pytest.fixture
def project(client):
    response = client.post('/api/projects', json={'name': 'Test Project for Subtasks', 'description': 'Project for subtask tests'})
    assert response.status_code == 201
    return response.json

# Helper fixture to create a stage
@pytest.fixture
def stage(client, project):
    project_id = project['id']
    response = client.post(f'/api/projects/{project_id}/stages', json={'name': 'Test Stage for Subtasks'})
    assert response.status_code == 201
    return response.json

# Helper fixture to create a task
@pytest.fixture
def task(client, stage):
    stage_id = stage['id']
    response = client.post(f'/api/stages/{stage_id}/tasks', json={'content': 'Test Task for Subtasks'})
    assert response.status_code == 201
    return response.json

# POST /api/tasks/<parent_task_id>/subtasks
def test_create_subtask_success(client, task):
    parent_task_id = task['id']
    response = client.post(f'/api/tasks/{parent_task_id}/subtasks', json={
        'content': 'New Subtask Content',
        'completed': True 
    })
    assert response.status_code == 201
    data = response.json
    assert data['content'] == 'New Subtask Content'
    assert data['parent_task_id'] == parent_task_id
    assert data['completed'] is True
    assert 'id' in data
    assert data['order'] == 0 # First subtask for this parent
    # Check DB
    subtask = SubTask.query.get(data['id'])
    assert subtask is not None
    assert subtask.content == 'New Subtask Content'
    assert subtask.completed is True

def test_create_subtask_defaults(client, task): # Verify order and completed default
    parent_task_id = task['id']
    response = client.post(f'/api/tasks/{parent_task_id}/subtasks', json={'content': 'Subtask with defaults'})
    assert response.status_code == 201
    data = response.json
    assert data['content'] == 'Subtask with defaults'
    assert data['completed'] is False # Default value
    assert data['order'] == 0 # First subtask

    # Create another to check order increment
    response2 = client.post(f'/api/tasks/{parent_task_id}/subtasks', json={'content': 'Second Subtask'})
    assert response2.status_code == 201
    assert response2.json['order'] == 1 

def test_create_subtask_non_existent_parent_task(client):
    response = client.post('/api/tasks/non_existent_task_id/subtasks', json={'content': 'Subtask for Ghost Task'})
    assert response.status_code == 404
    data = response.json
    assert data['error'] == 'Parent task not found'

def test_create_subtask_missing_content(client, task):
    parent_task_id = task['id']
    response = client.post(f'/api/tasks/{parent_task_id}/subtasks', json={}) # Missing content
    assert response.status_code == 400
    data = response.json
    assert data['error'] == 'Subtask content (content) is required'

def test_create_subtask_invalid_completed_type(client, task):
    parent_task_id = task['id']
    response = client.post(f'/api/tasks/{parent_task_id}/subtasks', json={'content': 'Test', 'completed': 'not-a-boolean'})
    assert response.status_code == 400
    data = response.json
    assert data['error'] == 'Completed status must be a boolean'


# PUT /api/subtasks/<subtask_id>
def test_update_subtask_success(client, task):
    parent_task_id = task['id']
    # Create a subtask first
    subtask_response = client.post(f'/api/tasks/{parent_task_id}/subtasks', json={'content': 'Old Subtask Content', 'completed': False, 'order': 0})
    subtask_id = subtask_response.json['id']

    update_payload = {
        'content': 'Updated Subtask Content',
        'completed': True,
        'order': 5
    }
    response = client.put(f'/api/subtasks/{subtask_id}', json=update_payload)
    assert response.status_code == 200
    data = response.json
    assert data['content'] == 'Updated Subtask Content'
    assert data['completed'] is True
    assert data['order'] == 5
    # Check DB
    subtask = SubTask.query.get(subtask_id)
    assert subtask.content == 'Updated Subtask Content'
    assert subtask.completed is True
    assert subtask.order == 5

def test_update_subtask_non_existent(client):
    response = client.put('/api/subtasks/non_existent_subtask_id', json={'content': 'Trying to update ghost subtask'})
    assert response.status_code == 404
    data = response.json
    assert data['error'] == 'Subtask not found'

def test_update_subtask_empty_content(client, task):
    parent_task_id = task['id']
    subtask_response = client.post(f'/api/tasks/{parent_task_id}/subtasks', json={'content': 'Valid Subtask Content'})
    subtask_id = subtask_response.json['id']
    response = client.put(f'/api/subtasks/{subtask_id}', json={'content': ''}) # Empty content
    assert response.status_code == 400
    data = response.json
    assert data['error'] == 'Subtask content cannot be empty' # Matches illustrative code for subtasks_bp

def test_update_subtask_invalid_completed_status(client, task):
    parent_task_id = task['id']
    subtask_response = client.post(f'/api/tasks/{parent_task_id}/subtasks', json={'content': 'Subtask for completed update test'})
    subtask_id = subtask_response.json['id']
    response = client.put(f'/api/subtasks/{subtask_id}', json={'completed': 'not-a-boolean'})
    assert response.status_code == 400
    data = response.json
    assert data['error'] == 'Completed status must be a boolean'

def test_update_subtask_invalid_order(client, task):
    parent_task_id = task['id']
    subtask_response = client.post(f'/api/tasks/{parent_task_id}/subtasks', json={'content': 'Subtask for order update test'})
    subtask_id = subtask_response.json['id']
    response = client.put(f'/api/subtasks/{subtask_id}', json={'order': 'not-an-integer'})
    assert response.status_code == 400
    data = response.json
    assert data['error'] == 'Order must be an integer'

# DELETE /api/subtasks/<subtask_id>
def test_delete_subtask_success(client, task, app): # app fixture for db context
    parent_task_id = task['id']
    # Create a subtask
    subtask_resp = client.post(f'/api/tasks/{parent_task_id}/subtasks', json={'content': 'Subtask To Be Deleted'})
    subtask_id = subtask_resp.json['id']

    delete_response = client.delete(f'/api/subtasks/{subtask_id}')
    assert delete_response.status_code == 200
    data = delete_response.json
    assert data['message'] == 'SubTask successfully deleted'

    # Verify it's gone from DB
    with app.app_context():
        assert SubTask.query.get(subtask_id) is None

def test_delete_subtask_non_existent(client):
    response = client.delete('/api/subtasks/non_existent_subtask_id')
    assert response.status_code == 404
    data = response.json
    assert data['error'] == 'Subtask not found'

def test_update_subtask_partial_updates(client, task):
    parent_task_id = task['id']
    subtask_resp = client.post(f'/api/tasks/{parent_task_id}/subtasks', json={
        'content': 'Initial SubContent', 
        'completed': False,
        'order': 1
    })
    subtask_id = subtask_resp.json['id']

    # Update only content
    res_content = client.put(f'/api/subtasks/{subtask_id}', json={'content': 'Updated SubContent Only'})
    assert res_content.status_code == 200
    assert res_content.json['content'] == 'Updated SubContent Only'
    assert res_content.json['completed'] is False # Should remain

    # Update only completed status
    res_completed = client.put(f'/api/subtasks/{subtask_id}', json={'completed': True})
    assert res_completed.status_code == 200
    assert res_completed.json['completed'] is True
    assert res_completed.json['content'] == 'Updated SubContent Only' # Should remain

    # Update only order
    res_order = client.put(f'/api/subtasks/{subtask_id}', json={'order': 5})
    assert res_order.status_code == 200
    assert res_order.json['order'] == 5

def test_update_subtask_empty_json(client, task):
    parent_task_id = task['id']
    subtask_response = client.post(f'/api/tasks/{parent_task_id}/subtasks', json={'content': 'Subtask For Empty JSON Update'})
    subtask_id = subtask_response.json['id']
    
    response = client.put(f'/api/subtasks/{subtask_id}', json={})
    assert response.status_code == 400 # As per subtasks_bp.py logic
    data = response.json
    assert data['error'] == "Request body cannot be empty" # Matches illustrative code for subtasks_bp
