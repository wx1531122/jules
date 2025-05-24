import json
import pytest # Pytest is implicitly available but good for clarity
from app.models import Project, Stage, Task # For verifying deletions

# POST /api/projects
def test_create_project_success(client):
    response = client.post('/api/projects', json={
        'name': 'My First Project',
        'description': 'This is a test project.'
    })
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['name'] == 'My First Project'
    assert 'id' in data
    assert 'created_at' in data
    assert 'updated_at' in data
    # Check it's in the DB
    project = Project.query.get(data['id'])
    assert project is not None
    assert project.name == 'My First Project'

def test_create_project_missing_name(client):
    response = client.post('/api/projects', json={
        'description': 'This is a test project without a name.'
    })
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error'] == 'Project name (name) is required'

def test_create_project_duplicate_name(client):
    # Create a project first
    client.post('/api/projects', json={'name': 'Duplicate Test Project', 'description': 'First instance'})
    # Attempt to create another with the same name
    response = client.post('/api/projects', json={'name': 'Duplicate Test Project', 'description': 'Second instance attempt'})
    assert response.status_code == 409
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error'] == 'Project name "Duplicate Test Project" already exists'

# GET /api/projects
def test_get_projects_empty(client):
    response = client.get('/api/projects')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) == 0

def test_get_projects_multiple(client):
    p1_data = client.post('/api/projects', json={'name': 'Project Alpha', 'description': 'A'}).json
    p2_data = client.post('/api/projects', json={'name': 'Project Beta', 'description': 'B'}).json
    
    response = client.get('/api/projects')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) == 2
    # Check order (newest first by default)
    assert data[0]['name'] == 'Project Beta'
    assert data[1]['name'] == 'Project Alpha'
    assert 'stages' not in data[0] # List view should not include stages

# GET /api/projects/<id>
def test_get_project_by_id_success(client):
    # Create a project
    create_response = client.post('/api/projects', json={'name': 'Specific Project', 'description': 'Details here'})
    project_id = json.loads(create_response.data)['id']

    # Add a stage and a task to test nesting
    stage_resp = client.post(f'/api/projects/{project_id}/stages', json={'name': 'To Do'})
    assert stage_resp.status_code == 201
    stage_id = stage_resp.json['id']
    
    task_resp = client.post(f'/api/stages/{stage_id}/tasks', json={'content': 'Test Task 1'})
    assert task_resp.status_code == 201
    task_id = task_resp.json['id']

    # Retrieve the project
    response = client.get(f'/api/projects/{project_id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['id'] == project_id
    assert data['name'] == 'Specific Project'
    assert 'stages' in data
    assert len(data['stages']) == 1
    assert data['stages'][0]['name'] == 'To Do'
    assert 'tasks' in data['stages'][0]
    assert len(data['stages'][0]['tasks']) == 1
    assert data['stages'][0]['tasks'][0]['content'] == 'Test Task 1'

def test_get_project_by_id_not_found(client):
    response = client.get('/api/projects/non_existent_uuid')
    assert response.status_code == 404
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error'] == 'Project not found'

# PUT /api/projects/<id>
def test_update_project_success(client):
    create_response = client.post('/api/projects', json={'name': 'Old Name', 'description': 'Old Desc'})
    project_id = json.loads(create_response.data)['id']

    update_payload = {'name': 'New Name', 'description': 'New Desc'}
    response = client.put(f'/api/projects/{project_id}', json=update_payload)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['name'] == 'New Name'
    assert data['description'] == 'New Desc'
    assert data['id'] == project_id
    # Verify updated_at changed (tricky to test exact value, but should be different from created_at)
    assert data['updated_at'] != data['created_at'] # Assuming they are not identical immediately after creation

def test_update_project_not_found(client):
    response = client.put('/api/projects/non_existent_uuid', json={'name': 'Trying to update'})
    assert response.status_code == 404
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error'] == 'Project not found'

def test_update_project_empty_name(client):
    create_response = client.post('/api/projects', json={'name': 'Valid Name', 'description': 'Desc'})
    project_id = json.loads(create_response.data)['id']
    
    response = client.put(f'/api/projects/{project_id}', json={'name': ''}) # Empty name
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error'] == 'Project name cannot be an empty string if provided'

def test_update_project_conflicting_name(client):
    p1 = client.post('/api/projects', json={'name': 'Project One', 'description': 'Desc1'}).json
    p2 = client.post('/api/projects', json={'name': 'Project Two', 'description': 'Desc2'}).json
    
    # Try to update P2's name to P1's name
    response = client.put(f'/api/projects/{p2["id"]}', json={'name': 'Project One'})
    assert response.status_code == 409
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error'] == 'Project name "Project One" is already used by another project'

# DELETE /api/projects/<id>
def test_delete_project_success(client):
    create_response = client.post('/api/projects', json={'name': 'To Be Deleted', 'description': 'Desc'})
    project_id = json.loads(create_response.data)['id']

    # Add a stage and task to check cascade delete
    stage_resp = client.post(f'/api/projects/{project_id}/stages', json={'name': 'Stage in Deleted Project'})
    stage_id = stage_resp.json['id']
    task_resp = client.post(f'/api/stages/{stage_id}/tasks', json={'content': 'Task in Deleted Stage'})
    task_id = task_resp.json['id']

    delete_response = client.delete(f'/api/projects/{project_id}')
    assert delete_response.status_code == 200 # or 204
    data = json.loads(delete_response.data)
    assert data['message'] == 'Project successfully deleted'

    # Verify it's gone from DB
    assert Project.query.get(project_id) is None
    assert Stage.query.get(stage_id) is None
    assert Task.query.get(task_id) is None
    
    # Verify it's not returned by GET
    get_response = client.get(f'/api/projects/{project_id}')
    assert get_response.status_code == 404

def test_delete_project_not_found(client):
    response = client.delete('/api/projects/non_existent_uuid')
    assert response.status_code == 404
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error'] == 'Project not found'

# Test partial updates for PUT
def test_update_project_partial_name_only(client):
    create_response = client.post('/api/projects', json={'name': 'Original Name', 'description': 'Original Description'})
    project_id = json.loads(create_response.data)['id']

    update_payload = {'name': 'Updated Name Only'}
    response = client.put(f'/api/projects/{project_id}', json=update_payload)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['name'] == 'Updated Name Only'
    assert data['description'] == 'Original Description' # Description should remain unchanged

def test_update_project_partial_description_only(client):
    create_response = client.post('/api/projects', json={'name': 'Original Name', 'description': 'Original Description'})
    project_id = json.loads(create_response.data)['id']

    update_payload = {'description': 'Updated Description Only'}
    response = client.put(f'/api/projects/{project_id}', json=update_payload)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['name'] == 'Original Name' # Name should remain unchanged
    assert data['description'] == 'Updated Description Only'

def test_update_project_no_change_data(client):
    # Create a project
    create_resp = client.post('/api/projects', json={'name': 'No Change Project', 'description': 'Desc'})
    project_id = create_resp.json['id']
    original_updated_at = create_resp.json['updated_at']

    # PUT request with the same data
    # Note: The API currently updates `updated_at` even if field values are the same.
    # This test checks that behavior. If `updated_at` should only change on actual data modification,
    # the API logic would need adjustment.
    response = client.put(f'/api/projects/{project_id}', json={
        'name': 'No Change Project',
        'description': 'Desc'
    })
    assert response.status_code == 200
    data = response.json
    assert data['name'] == 'No Change Project'
    assert data['description'] == 'Desc'
    # Depending on DB precision and speed, this might or might not be different.
    # For a robust test, one might need to mock datetime or check that it's greater.
    # For now, we'll assume it gets updated.
    assert data['updated_at'] >= original_updated_at # Should be same or newer

def test_update_project_empty_json(client):
    create_response = client.post('/api/projects', json={'name': 'Test Project', 'description': 'Desc'})
    project_id = json.loads(create_response.data)['id']
    
    response = client.put(f'/api/projects/{project_id}', json={}) # Empty JSON
    assert response.status_code == 400 # As per projects_bp.py logic
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error'] == "Request body cannot be empty. Please provide 'name' and/or 'description'."

def test_get_project_with_empty_stages_and_tasks(client):
    # Create a project
    create_response = client.post('/api/projects', json={'name': 'Empty Project', 'description': 'No stages yet'})
    project_id = json.loads(create_response.data)['id']

    # Retrieve the project
    response = client.get(f'/api/projects/{project_id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['id'] == project_id
    assert data['name'] == 'Empty Project'
    assert 'stages' in data
    assert isinstance(data['stages'], list)
    assert len(data['stages']) == 0 # Should be an empty list
    
def test_get_project_with_stages_but_empty_tasks(client):
    # Create a project
    create_response = client.post('/api/projects', json={'name': 'Project With Empty Stage', 'description': 'Stage has no tasks'})
    project_id = json.loads(create_response.data)['id']
    
    # Add a stage
    stage_resp = client.post(f'/api/projects/{project_id}/stages', json={'name': 'Empty Stage'})
    assert stage_resp.status_code == 201

    # Retrieve the project
    response = client.get(f'/api/projects/{project_id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['id'] == project_id
    assert data['name'] == 'Project With Empty Stage'
    assert 'stages' in data
    assert len(data['stages']) == 1
    stage_data = data['stages'][0]
    assert stage_data['name'] == 'Empty Stage'
    assert 'tasks' in stage_data
    assert isinstance(stage_data['tasks'], list)
    assert len(stage_data['tasks']) == 0 # Tasks list should be empty
