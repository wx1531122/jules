import json
import pytest
from app.models import Project, Stage, Task, SubTask, db # For verifying deletions and setup

# Helper fixture to create a project
@pytest.fixture
def project(client):
    response = client.post('/api/projects', json={'name': 'Test Project for Stages', 'description': 'Project for stage tests'})
    assert response.status_code == 201
    return response.json

# POST /api/projects/<project_id>/stages
def test_create_stage_success(client, project):
    project_id = project['id']
    response = client.post(f'/api/projects/{project_id}/stages', json={'name': 'New Stage'})
    assert response.status_code == 201
    data = response.json
    assert data['name'] == 'New Stage'
    assert data['project_id'] == project_id
    assert 'id' in data
    assert data['order'] == 0 # First stage should have order 0
    # Check DB
    stage = Stage.query.get(data['id'])
    assert stage is not None
    assert stage.name == 'New Stage'

def test_create_stage_verify_order_assignment(client, project):
    project_id = project['id']
    # Create first stage
    response1 = client.post(f'/api/projects/{project_id}/stages', json={'name': 'Stage One'})
    assert response1.status_code == 201
    assert response1.json['order'] == 0
    
    # Create second stage
    response2 = client.post(f'/api/projects/{project_id}/stages', json={'name': 'Stage Two'})
    assert response2.status_code == 201
    assert response2.json['order'] == 1

    # Create third stage
    response3 = client.post(f'/api/projects/{project_id}/stages', json={'name': 'Stage Three'})
    assert response3.status_code == 201
    assert response3.json['order'] == 2

def test_create_stage_non_existent_project(client):
    response = client.post('/api/projects/non_existent_project_id/stages', json={'name': 'Stage for Ghost Project'})
    assert response.status_code == 404
    data = response.json
    assert data['error'] == 'Project not found'

def test_create_stage_missing_name(client, project):
    project_id = project['id']
    response = client.post(f'/api/projects/{project_id}/stages', json={}) # Missing name
    assert response.status_code == 400
    data = response.json
    assert data['error'] == 'Stage name (name) is required'

# PUT /api/stages/<stage_id>
def test_update_stage_success(client, project):
    project_id = project['id']
    # Create a stage first
    stage_response = client.post(f'/api/projects/{project_id}/stages', json={'name': 'Old Stage Name', 'order': 0})
    stage_id = stage_response.json['id']

    update_payload = {'name': 'Updated Stage Name', 'order': 10}
    response = client.put(f'/api/stages/{stage_id}', json=update_payload)
    assert response.status_code == 200
    data = response.json
    assert data['name'] == 'Updated Stage Name'
    assert data['order'] == 10
    assert data['id'] == stage_id
    # Check DB
    stage = Stage.query.get(stage_id)
    assert stage.name == 'Updated Stage Name'
    assert stage.order == 10

def test_update_stage_non_existent(client):
    response = client.put('/api/stages/non_existent_stage_id', json={'name': 'Trying to update ghost stage'})
    assert response.status_code == 404
    data = response.json
    assert data['error'] == 'Stage not found'

def test_update_stage_empty_name(client, project):
    project_id = project['id']
    stage_response = client.post(f'/api/projects/{project_id}/stages', json={'name': 'Valid Stage Name'})
    stage_id = stage_response.json['id']

    response = client.put(f'/api/stages/{stage_id}', json={'name': ''}) # Empty name
    assert response.status_code == 400
    data = response.json
    assert data['error'] == 'Stage name cannot be an empty string if provided'

def test_update_stage_invalid_order(client, project):
    project_id = project['id']
    stage_response = client.post(f'/api/projects/{project_id}/stages', json={'name': 'Stage for Order Test'})
    stage_id = stage_response.json['id']

    response = client.put(f'/api/stages/{stage_id}', json={'order': 'not-an-integer'})
    assert response.status_code == 400
    data = response.json
    assert data['error'] == 'Order must be an integer'

# DELETE /api/stages/<stage_id>
def test_delete_stage_success(client, project, app): # app fixture to use db.session
    project_id = project['id']
    # Create a stage
    stage_resp = client.post(f'/api/projects/{project_id}/stages', json={'name': 'Stage To Be Deleted'})
    stage_id = stage_resp.json['id']
    
    # Create a task in that stage
    task_resp = client.post(f'/api/stages/{stage_id}/tasks', json={'content': 'Task in deleted stage'})
    task_id = task_resp.json['id']

    # Create a subtask in that task
    sub_task_resp = client.post(f'/api/tasks/{task_id}/subtasks', json={'content': 'Subtask in deleted task'})
    sub_task_id = sub_task_resp.json['id']

    delete_response = client.delete(f'/api/stages/{stage_id}')
    assert delete_response.status_code == 200
    data = delete_response.json
    assert data['message'] == 'Stage successfully deleted'

    # Verify it's gone from DB along with its tasks and subtasks
    with app.app_context(): # Need app context for DB operations
        assert Stage.query.get(stage_id) is None
        assert Task.query.get(task_id) is None
        assert SubTask.query.get(sub_task_id) is None

def test_delete_stage_non_existent(client):
    response = client.delete('/api/stages/non_existent_stage_id')
    assert response.status_code == 404
    data = response.json
    assert data['error'] == 'Stage not found'

def test_update_stage_partial_name_only(client, project):
    project_id = project['id']
    stage_response = client.post(f'/api/projects/{project_id}/stages', json={'name': 'Original Stage Name', 'order': 1})
    stage_id = stage_response.json['id']

    response = client.put(f'/api/stages/{stage_id}', json={'name': 'New Stage Name Only'})
    assert response.status_code == 200
    data = response.json
    assert data['name'] == 'New Stage Name Only'
    assert data['order'] == 1 # Order should remain unchanged

def test_update_stage_partial_order_only(client, project):
    project_id = project['id']
    stage_response = client.post(f'/api/projects/{project_id}/stages', json={'name': 'Stage For Order Update', 'order': 5})
    stage_id = stage_response.json['id']

    response = client.put(f'/api/stages/{stage_id}', json={'order': 15})
    assert response.status_code == 200
    data = response.json
    assert data['name'] == 'Stage For Order Update' # Name should remain unchanged
    assert data['order'] == 15

def test_update_stage_empty_json(client, project):
    project_id = project['id']
    stage_response = client.post(f'/api/projects/{project_id}/stages', json={'name': 'Stage For Empty JSON Update'})
    stage_id = stage_response.json['id']
    
    response = client.put(f'/api/stages/{stage_id}', json={})
    assert response.status_code == 400
    data = response.json
    assert data['error'] == "Request body cannot be empty. Please provide 'name' and/or 'order'."
