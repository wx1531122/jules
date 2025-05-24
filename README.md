# Kanban CMS Backend API

This is a Flask-based backend API service for a Kanban Content Management System (CMS).
It provides CRUD (Create, Read, Update, Delete) operations for projects, stages, tasks, and subtasks.

## Table of Contents

- [Environment Requirements](#environment-requirements)
- [Installation & Setup](#installation--setup)
- [Running the Project](#running-the-project)
- [Running Tests](#running-tests)
- [API Interface Document](#api-interface-document)
  - [Projects](#projects)
  - [Stages](#stages)
  - [Tasks](#tasks)
  - [SubTasks](#subtasks)
  - [Test Interface](#test-interface)

## Environment Requirements

- Python 3.10 (virtual environment recommended)
- pip (Python package installer)

## Installation & Setup

1.  **Clone the Repository (if applicable)**
    ```bash
    # git clone <your-repository-url>
    # cd <repository-name> 
    ```
    (This step is for a typical Git workflow; if you have the files directly, navigate to the project root directory, likely named `backend` or similar.)

2.  **Create and Activate a Virtual Environment**
    From the project root directory:
    ```bash
    # For Windows
    python -m venv venv
    .\venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables**
    In the project root directory, create a `.env` file. You can copy `.env.example` if provided, or create it manually.
    It should contain at least the following:
    ```env
    FLASK_APP=run.py
    FLASK_ENV=development # Use 'production' for production deployments
    SECRET_KEY=your_very_strong_and_unique_secret_key # CHANGE THIS!

    # Database URLs (SQLite is used by default)
    # The actual database file will be created in the 'instance' folder.
    # For development:
    DEV_DATABASE_URL=sqlite:///kanban_dev.db 
    # For production (can be the same for SQLite, or a different DB like PostgreSQL):
    DATABASE_URL=sqlite:///kanban_prod.db
    ```
    **Important:** The `SECRET_KEY` is crucial for security (e.g., session management, signing). Generate a strong, random key and keep it secret. The default in `config.py` is for development only and should not be used in production.
    The database will be created inside an `instance` folder in your project root (e.g., `instance/kanban_dev.db`).

5.  **Initialize and Migrate Database**
    After installing dependencies and setting up the `.env` file, run the following commands from the project root directory to initialize the database and apply migrations:
    ```bash
    # Ensure your virtual environment is activated and FLASK_APP is set in .env
    
    # Initialize the migrations system (only needed once per project setup)
    # If the 'migrations' folder already exists, you can skip this command.
    flask db init
    
    # Generate the initial migration script (or subsequent migration scripts if models change)
    flask db migrate -m "Initial migration with all tables"
    
    # Apply the migration to the database (creates tables, etc.)
    flask db upgrade
    ```
    - `flask db init`: Sets up the migration environment. Only run this if the `migrations` directory doesn't exist.
    - `flask db migrate`: Generates a new migration script based on changes detected in your models (`app/models.py`).
    - `flask db upgrade`: Applies the latest migration script(s) to your database.

## Running the Project

Ensure your virtual environment is activated and you are in the project root directory.

```bash
python run.py
```

By default, the service will run at `http://0.0.0.0:5000/`.
You can test if the service is running by navigating to `http://localhost:5000/hello` in your browser or using a tool like `curl`.

## Running Tests

To run the automated tests, ensure you have `pytest` installed (it's included in `requirements.txt`).
From the project root directory:

```bash
pytest
```

## API Interface Document

All API endpoints are prefixed with `/api`. Timestamps in responses are in ISO8601 format ending with 'Z' to denote UTC (e.g., `YYYY-MM-DDTHH:MM:SS.ffffffZ`).

### Projects

#### 1. Get All Projects

-   **Method:** `GET`
-   **Endpoint:** `/api/projects`
-   **Description:** Retrieves a list of all projects, ordered by creation date (newest first).
-   **Request Body:** None
-   **Success Response (200 OK):**
    ```json
    [
        {
            "id": "project_uuid_1",
            "name": "Project Alpha",
            "description": "This is project Alpha.",
            "created_at": "2023-10-01T10:00:00.123456Z",
            "updated_at": "2023-10-01T10:05:00.654321Z"
        },
        {
            "id": "project_uuid_2",
            "name": "Project Beta",
            "description": null,
            "created_at": "2023-09-25T15:30:00.000000Z",
            "updated_at": "2023-09-25T15:30:00.000000Z"
        }
    ]
    ```
-   **Error Response (500 Internal Server Error):**
    ```json
    {
        "error": "Failed to retrieve projects due to an internal server error"
    }
    ```

#### 2. Create a New Project

-   **Method:** `POST`
-   **Endpoint:** `/api/projects`
-   **Description:** Creates a new project.
-   **Request Body:**
    ```json
    {
        "name": "New Project Name", // String, Required
        "description": "Optional project description" // String, Optional
    }
    ```
-   **Success Response (201 Created):**
    ```json
    {
        "id": "new_project_uuid",
        "name": "New Project Name",
        "description": "Optional project description",
        "created_at": "2023-10-02T12:00:00.000000Z",
        "updated_at": "2023-10-02T12:00:00.000000Z"
    }
    ```
-   **Error Responses:**
    -   `400 Bad Request` (e.g., missing `name`):
        ```json
        {
            "error": "Project name (name) is required"
        }
        ```
    -   `409 Conflict` (project name already exists):
        ```json
        {
            "error": "Project name \"New Project Name\" already exists"
        }
        ```
    -   `500 Internal Server Error`:
        ```json
        {
            "error": "Failed to create project due to an internal server error"
        }
        ```

#### 3. Get Single Project Details

-   **Method:** `GET`
-   **Endpoint:** `/api/projects/<string:project_id>`
-   **Description:** Retrieves details for a specific project, including its stages, tasks, and subtasks, all sorted by their `order` attribute.
-   **Path Parameters:**
    -   `project_id` (String): The unique ID of the project.
-   **Success Response (200 OK):**
    ```json
    {
        "id": "project_uuid",
        "name": "Project Name",
        "description": "Project description",
        "created_at": "2023-10-01T10:00:00.123456Z",
        "updated_at": "2023-10-01T10:05:00.654321Z",
        "stages": [
            {
                "id": "stage_uuid_1",
                "name": "To Do",
                "project_id": "project_uuid",
                "order": 0,
                "created_at": "2023-10-01T10:01:00.000000Z",
                "updated_at": "2023-10-01T10:01:00.000000Z",
                "tasks": [
                    {
                        "id": "task_uuid_1_1",
                        "content": "Design homepage",
                        "stage_id": "stage_uuid_1",
                        "assignee": "Alice",
                        "start_date": "2023-10-05",
                        "end_date": "2023-10-10",
                        "order": 0,
                        "created_at": "2023-10-01T10:02:00.000000Z",
                        "updated_at": "2023-10-01T10:02:00.000000Z",
                        "subtasks": [
                            {
                                "id": "subtask_uuid_1_1_1",
                                "content": "Draft wireframes",
                                "parent_task_id": "task_uuid_1_1",
                                "completed": true,
                                "order": 0,
                                "created_at": "2023-10-01T10:03:00.000000Z",
                                "updated_at": "2023-10-01T10:04:00.000000Z"
                            }
                        ]
                    }
                ]
            }
            // ... other stages sorted by order
        ]
    }
    ```
-   **Error Responses:**
    -   `404 Not Found`:
        ```json
        {
            "error": "Project not found"
        }
        ```
    -   `500 Internal Server Error`.

#### 4. Update a Project

-   **Method:** `PUT`
-   **Endpoint:** `/api/projects/<string:project_id>`
-   **Description:** Updates an existing project's information.
-   **Path Parameters:**
    -   `project_id` (String): The unique ID of the project.
-   **Request Body:**
    ```json
    {
        "name": "Updated Project Name", // String, Optional
        "description": "Updated project description" // String, Optional (can be null or empty)
    }
    ```
-   **Success Response (200 OK):**
    ```json
    {
        "id": "project_uuid",
        "name": "Updated Project Name",
        "description": "Updated project description",
        "created_at": "2023-10-01T10:00:00.123456Z",
        "updated_at": "2023-10-02T14:30:00.000000Z"
    }
    ```
-   **Error Responses:**
    -   `400 Bad Request` (e.g., request body is empty, or `name` provided as empty string):
        ```json
        {
            "error": "Request body cannot be empty. Please provide 'name' and/or 'description'."
        }
        // or
        {
            "error": "Project name cannot be an empty string if provided"
        }
        ```
    -   `404 Not Found` (project not found).
    -   `409 Conflict` (new name conflicts with another project):
        ```json
        {
            "error": "Project name \"Updated Project Name\" is already used by another project"
        }
        ```
    -   `500 Internal Server Error`.

#### 5. Delete a Project

-   **Method:** `DELETE`
-   **Endpoint:** `/api/projects/<string:project_id>`
-   **Description:** Deletes a project and all its associated stages, tasks, and subtasks.
-   **Path Parameters:**
    -   `project_id` (String): The unique ID of the project.
-   **Success Response (200 OK):**
    ```json
    {
        "message": "Project successfully deleted"
    }
    ```
-   **Error Responses:**
    -   `404 Not Found` (project not found).
    -   `500 Internal Server Error`.

### Stages

#### 1. Create a New Stage for a Project

-   **Method:** `POST`
-   **Endpoint:** `/api/projects/<string:project_id>/stages`
-   **Description:** Creates a new stage within the specified project. New stages are appended to the end of the existing stages list (highest order).
-   **Path Parameters:**
    -   `project_id` (String): The unique ID of the parent project.
-   **Request Body:**
    ```json
    {
        "name": "New Stage Name" // String, Required
    }
    ```
-   **Success Response (201 Created):**
    ```json
    {
        "id": "new_stage_uuid",
        "name": "New Stage Name",
        "project_id": "project_uuid",
        "order": 2, // Example: if there were already stages with order 0 and 1
        "created_at": "2023-10-02T15:00:00.000000Z",
        "updated_at": "2023-10-02T15:00:00.000000Z",
        "tasks": [] // Tasks list is empty on creation
    }
    ```
-   **Error Responses:**
    -   `400 Bad Request` (e.g., missing `name`):
        ```json
        {
            "error": "Stage name (name) is required"
        }
        ```
    -   `404 Not Found` (project not found).
    -   `500 Internal Server Error`.

#### 2. Update a Stage

-   **Method:** `PUT`
-   **Endpoint:** `/api/stages/<string:stage_id>`
-   **Description:** Updates an existing stage's information (name, order).
-   **Path Parameters:**
    -   `stage_id` (String): The unique ID of the stage.
-   **Request Body:**
    ```json
    {
        "name": "Updated Stage Name", // String, Optional
        "order": 1 // Integer, Optional
    }
    ```
-   **Success Response (200 OK):**
    ```json
    {
        "id": "stage_uuid",
        "name": "Updated Stage Name",
        "project_id": "project_uuid",
        "order": 1,
        "created_at": "2023-10-01T10:01:00.000000Z",
        "updated_at": "2023-10-02T16:00:00.000000Z",
        "tasks": [/* ... existing tasks ... */]
    }
    ```
-   **Error Responses:**
    -   `400 Bad Request` (e.g., request body empty, name is empty string, order not integer):
        ```json
        {
            "error": "Request body cannot be empty. Please provide 'name' and/or 'order'."
        }
        // or
        {
            "error": "Stage name cannot be an empty string if provided"
        }
        // or
        {
            "error": "Order must be an integer"
        }
        ```
    -   `404 Not Found` (stage not found).
    -   `500 Internal Server Error`.

#### 3. Delete a Stage

-   **Method:** `DELETE`
-   **Endpoint:** `/api/stages/<string:stage_id>`
-   **Description:** Deletes a stage and all its associated tasks and subtasks.
-   **Path Parameters:**
    -   `stage_id` (String): The unique ID of the stage.
-   **Success Response (200 OK):**
    ```json
    {
        "message": "Stage successfully deleted"
    }
    ```
-   **Error Responses:**
    -   `404 Not Found` (stage not found).
    -   `500 Internal Server Error`.

### Tasks

#### 1. Create a New Task for a Stage

-   **Method:** `POST`
-   **Endpoint:** `/api/stages/<string:stage_id>/tasks`
-   **Description:** Creates a new task within the specified stage. New tasks are appended to the end of the existing tasks list for that stage.
-   **Path Parameters:**
    -   `stage_id` (String): The unique ID of the parent stage.
-   **Request Body:**
    ```json
    {
        "content": "New task description", // String, Required
        "assignee": "User Name", // String, Optional
        "start_date": "YYYY-MM-DD", // String (Date format), Optional
        "end_date": "YYYY-MM-DD" // String (Date format), Optional
    }
    ```
-   **Success Response (201 Created):**
    ```json
    {
        "id": "new_task_uuid",
        "content": "New task description",
        "stage_id": "stage_uuid",
        "assignee": "User Name",
        "start_date": "2023-10-05",
        "end_date": "2023-10-10",
        "order": 1, // Example: if there was already a task with order 0
        "created_at": "2023-10-02T17:00:00.000000Z",
        "updated_at": "2023-10-02T17:00:00.000000Z",
        "subtasks": []
    }
    ```
-   **Error Responses:**
    -   `400 Bad Request` (e.g., missing `content`, invalid date format):
        ```json
        {
            "error": "Task content (content) is required"
        }
        // or
        {
            "error": "Invalid start_date format. Use YYYY-MM-DD."
        }
        ```
    -   `404 Not Found` (stage not found).
    -   `500 Internal Server Error`.

#### 2. Update a Task

-   **Method:** `PUT`
-   **Endpoint:** `/api/tasks/<string:task_id>`
-   **Description:** Updates an existing task's information (content, assignee, dates, order, or moves to a different stage).
-   **Path Parameters:**
    -   `task_id` (String): The unique ID of the task.
-   **Request Body:**
    ```json
    {
        "content": "Updated task content", // String, Optional
        "assignee": "New Assignee", // String, Optional (can be null)
        "start_date": "YYYY-MM-DD", // String (Date format), Optional (can be null)
        "end_date": "YYYY-MM-DD", // String (Date format), Optional (can be null)
        "order": 0, // Integer, Optional
        "stage_id": "new_stage_uuid" // String, Optional (to move task)
    }
    ```
-   **Success Response (200 OK):**
    ```json
    {
        "id": "task_uuid",
        "content": "Updated task content",
        "stage_id": "new_stage_uuid",
        "assignee": "New Assignee",
        "start_date": "2023-10-06",
        "end_date": "2023-10-12",
        "order": 0,
        "created_at": "2023-10-01T10:02:00.000000Z",
        "updated_at": "2023-10-02T18:00:00.000000Z",
        "subtasks": [/* ... existing subtasks ... */]
    }
    ```
-   **Error Responses:**
    -   `400 Bad Request` (e.g., empty body, empty content string, invalid date, invalid order):
        ```json
        {
            "error": "Request body cannot be empty. Please provide fields to update."
        }
        // or
        {
            "error": "Task content cannot be an empty string if provided"
        }
        ```
    -   `404 Not Found` (task not found, or target `stage_id` not found).
    -   `500 Internal Server Error`.

#### 3. Delete a Task

-   **Method:** `DELETE`
-   **Endpoint:** `/api/tasks/<string:task_id>`
-   **Description:** Deletes a task and all its associated subtasks.
-   **Path Parameters:**
    -   `task_id` (String): The unique ID of the task.
-   **Success Response (200 OK):**
    ```json
    {
        "message": "Task successfully deleted"
    }
    ```
-   **Error Responses:**
    -   `404 Not Found` (task not found).
    -   `500 Internal Server Error`.

### SubTasks

#### 1. Create a New SubTask for a Parent Task

-   **Method:** `POST`
-   **Endpoint:** `/api/tasks/<string:parent_task_id>/subtasks`
-   **Description:** Creates a new subtask under the specified parent task. New subtasks are appended to the end of the existing subtasks list for that parent.
-   **Path Parameters:**
    -   `parent_task_id` (String): The unique ID of the parent task.
-   **Request Body:**
    ```json
    {
        "content": "New subtask details", // String, Required
        "completed": false // Boolean, Optional, Defaults to false
    }
    ```
-   **Success Response (201 Created):**
    ```json
    {
        "id": "new_subtask_uuid",
        "content": "New subtask details",
        "parent_task_id": "parent_task_uuid",
        "completed": false,
        "order": 0, // Example: if this is the first subtask
        "created_at": "2023-10-02T19:00:00.000000Z",
        "updated_at": "2023-10-02T19:00:00.000000Z"
    }
    ```
-   **Error Responses:**
    -   `400 Bad Request` (e.g., missing `content`, `completed` is not boolean):
        ```json
        {
            "error": "Subtask content (content) is required"
        }
        // or
        {
            "error": "Completed status must be a boolean"
        }
        ```
    -   `404 Not Found` (parent task not found).
    -   `500 Internal Server Error`.

#### 2. Update a SubTask

-   **Method:** `PUT`
-   **Endpoint:** `/api/subtasks/<string:subtask_id>`
-   **Description:** Updates an existing subtask's information (content, completion status, order).
-   **Path Parameters:**
    -   `subtask_id` (String): The unique ID of the subtask.
-   **Request Body:**
    ```json
    {
        "content": "Updated subtask details", // String, Optional
        "completed": true, // Boolean, Optional
        "order": 1 // Integer, Optional
    }
    ```
-   **Success Response (200 OK):**
    ```json
    {
        "id": "subtask_uuid",
        "content": "Updated subtask details",
        "parent_task_id": "parent_task_uuid",
        "completed": true,
        "order": 1,
        "created_at": "2023-10-01T10:03:00.000000Z",
        "updated_at": "2023-10-02T20:00:00.000000Z"
    }
    ```
-   **Error Responses:**
    -   `400 Bad Request` (e.g., empty body, empty content string, invalid `completed`, invalid `order`):
        ```json
        {
            "error": "Request body cannot be empty"
        }
        // or
        {
            "error": "Subtask content cannot be empty"
        }
        ```
    -   `404 Not Found` (subtask not found).
    -   `500 Internal Server Error`.

#### 3. Delete a SubTask

-   **Method:** `DELETE`
-   **Endpoint:** `/api/subtasks/<string:subtask_id>`
-   **Description:** Deletes a subtask.
-   **Path Parameters:**
    -   `subtask_id` (String): The unique ID of the subtask.
-   **Success Response (200 OK):**
    ```json
    {
        "message": "SubTask successfully deleted" 
    }
    ```
-   **Error Responses:**
    -   `404 Not Found` (subtask not found).
    -   `500 Internal Server Error`.

### Test Interface

#### 1. Hello World

-   **Method:** `GET`
-   **Endpoint:** `/hello`
-   **Description:** A simple test route to check if the backend service is running.
-   **Success Response (200 OK):**
    ```text
    你好，看板后端已启动！(Hello, Kanban Backend is Running!)
    ```
