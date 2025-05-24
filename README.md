# Kanban CMS 后端 API

这是一个基于 Flask 的看板（Kanban）内容管理系统 (CMS) 的后端 API 服务。
它提供了项目、阶段、任务和子任务的 CRUD (创建、读取、更新、删除) 操作。

## 目录

- [环境要求](#环境要求)
- [安装与设置](#安装与设置)
- [运行项目](#运行项目)
- [API接口文档](#api接口文档)
  - [项目 (Projects)](#项目-projects)
  - [阶段 (Stages)](#阶段-stages)
  - [任务 (Tasks)](#任务-tasks)
  - [子任务 (SubTasks)](#子任务-subtasks)
  - [测试接口](#测试接口)

## 环境要求

- Python 3.10 (推荐使用虚拟环境)
- pip (Python 包安装器)

## 安装与设置

1.  **克隆仓库 (如果适用)**
    ```bash
    # git clone <your-repository-url>
    # cd backend
    ```

2.  **创建并激活虚拟环境**
    ```bash
    # For Windows
    python -m venv venv
    .\venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **安装依赖**
    ```bash
    pip install -r requirements.txt
    ```

4.  **配置环境变量**
    在 `backend` 目录下创建一个 `.env` 文件 (可以复制 `.env.example` 如果有的话，或手动创建)。
    内容至少应包含：
    ```env
    # backend/.env
    FLASK_APP=run.py
    FLASK_ENV=development # 可选 'production'
    # SECRET_KEY=your_very_strong_secret_key # 强烈建议设置一个强密钥

    # 数据库URL (可选, config.py 中有默认值)
    # DEV_DATABASE_URL=sqlite:///instance/kanban_dev.db
    # DATABASE_URL=sqlite:///instance/kanban_prod.db
    ```
    `SECRET_KEY` 对于生产环境至关重要。如果未在 `.env` 中设置，`config.py` 中会有一个默认值，但强烈建议修改它。
    数据库默认使用 SQLite，文件将存储在 `backend/instance/` 目录下。

## 运行项目

确保虚拟环境已激活，并且您在 `backend` 目录下。

```bash
python run.py
```

默认情况下，服务将运行在 `http://0.0.0.0:5000/`。
您可以通过访问 `http://localhost:5000/hello` 来测试服务是否正常启动。

## API接口文档

所有 API 接口都以 `/api` 为前缀。

### 项目 (Projects)

#### 1. 获取所有项目

-   **Method:** `GET`
-   **Endpoint:** `/api/projects`
-   **Description:** 获取所有项目列表，按创建时间降序排列。
-   **Request Body:** None
-   **Success Response (200 OK):**
    ```json
    [
        {
            "id": "project_uuid_1",
            "name": "项目A",
            "description": "这是项目A的描述",
            "created_at": "YYYY-MM-DDTHH:MM:SS.ffffff",
            "updated_at": "YYYY-MM-DDTHH:MM:SS.ffffff"
        },
        {
            "id": "project_uuid_2",
            "name": "项目B",
            "description": null,
            "created_at": "YYYY-MM-DDTHH:MM:SS.ffffff",
            "updated_at": "YYYY-MM-DDTHH:MM:SS.ffffff"
        }
    ]
    ```
-   **Error Response (500 Internal Server Error):**
    ```json
    {
        "error": "服务器内部错误描述"
    }
    ```

#### 2. 创建一个新项目

-   **Method:** `POST`
-   **Endpoint:** `/api/projects`
-   **Description:** 创建一个新的项目。
-   **Request Body:**
    ```json
    {
        "name": "新项目名称", // String, 必需
        "description": "可选的项目描述" // String, 可选
    }
    ```
-   **Success Response (201 Created):**
    ```json
    {
        "id": "new_project_uuid",
        "name": "新项目名称",
        "description": "可选的项目描述",
        "created_at": "YYYY-MM-DDTHH:MM:SS.ffffff",
        "updated_at": "YYYY-MM-DDTHH:MM:SS.ffffff"
    }
    ```
-   **Error Responses:**
    -   `400 Bad Request` (例如，缺少 `name`):
        ```json
        {
            "error": "项目名称 (name) 是必需的"
        }
        ```
    -   `409 Conflict` (项目名称已存在):
        ```json
        {
            "error": "项目名称 \"新项目名称\" 已存在"
        }
        ```
    -   `500 Internal Server Error`:
        ```json
        {
            "error": "创建项目失败: 错误详情"
        }
        ```

#### 3. 获取单个项目详情

-   **Method:** `GET`
-   **Endpoint:** `/api/projects/<string:project_id>`
-   **Description:** 获取指定项目的详细信息，包括其下的所有阶段和任务。
-   **Path Parameters:**
    -   `project_id` (String): 项目的唯一ID。
-   **Success Response (200 OK):**
    ```json
    {
        "id": "project_uuid",
        "name": "项目名称",
        "description": "项目描述",
        "created_at": "YYYY-MM-DDTHH:MM:SS.ffffff",
        "updated_at": "YYYY-MM-DDTHH:MM:SS.ffffff",
        "stages": [
            {
                "id": "stage_uuid_1",
                "name": "阶段1",
                "project_id": "project_uuid",
                "order": 0,
                "created_at": "...",
                "updated_at": "...",
                "tasks": [
                    {
                        "id": "task_uuid_1_1",
                        "content": "任务1.1",
                        "stage_id": "stage_uuid_1",
                        "assignee": "张三",
                        "start_date": "YYYY-MM-DD",
                        "end_date": "YYYY-MM-DD",
                        "order": 0,
                        "created_at": "...",
                        "updated_at": "...",
                        "subtasks": [
                            {
                                "id": "subtask_uuid_1_1_1",
                                "content": "子任务1.1.1",
                                "parent_task_id": "task_uuid_1_1",
                                "completed": false,
                                "order": 0,
                                "created_at": "...",
                                "updated_at": "..."
                            }
                        ]
                    }
                ]
            }
        ]
    }
    ```
-   **Error Responses:**
    -   `404 Not Found`:
        ```json
        {
            "error": "未找到项目"
        }
        ```
    -   `500 Internal Server Error`.

#### 4. 更新一个项目

-   **Method:** `PUT`
-   **Endpoint:** `/api/projects/<string:project_id>`
-   **Description:** 更新一个已存在的项目信息。
-   **Path Parameters:**
    -   `project_id` (String): 项目的唯一ID。
-   **Request Body:**
    ```json
    {
        "name": "更新后的项目名称", // String, 可选
        "description": "更新后的项目描述" // String, 可选 (可为 null 或空字符串)
    }
    ```
-   **Success Response (200 OK):**
    ```json
    {
        "id": "project_uuid",
        "name": "更新后的项目名称",
        "description": "更新后的项目描述",
        "created_at": "...",
        "updated_at": "..."
    }
    ```
-   **Error Responses:**
    -   `400 Bad Request` (例如，请求体为空或 `name` 为空字符串):
        ```json
        {
            "error": "请求体不能为空" 
        }
        // 或
        {
            "error": "项目名称不能为空"
        }
        ```
    -   `404 Not Found`.
    -   `409 Conflict` (新名称与其他项目冲突):
        ```json
        {
            "error": "项目名称 \"更新后的项目名称\" 已被其他项目使用"
        }
        ```
    -   `500 Internal Server Error`.

#### 5. 删除一个项目

-   **Method:** `DELETE`
-   **Endpoint:** `/api/projects/<string:project_id>`
-   **Description:** 删除一个项目及其所有关联的阶段、任务和子任务。
-   **Path Parameters:**
    -   `project_id` (String): 项目的唯一ID。
-   **Success Response (200 OK):**
    ```json
    {
        "message": "项目已成功删除"
    }
    ```
    (也可能是 `204 No Content`，具体取决于实现)
-   **Error Responses:**
    -   `404 Not Found`.
    -   `500 Internal Server Error`.

### 阶段 (Stages)

#### 1. 为项目创建新阶段

-   **Method:** `POST`
-   **Endpoint:** `/api/projects/<string:project_id>/stages`
-   **Description:** 为指定的项目创建一个新的阶段。
-   **Path Parameters:**
    -   `project_id` (String): 项目的唯一ID。
-   **Request Body:**
    ```json
    {
        "name": "新阶段名称" // String, 必需
    }
    ```
-   **Success Response (201 Created):**
    ```json
    {
        "id": "new_stage_uuid",
        "name": "新阶段名称",
        "project_id": "project_uuid",
        "order": 0, // 或下一个可用的顺序值
        "created_at": "...",
        "updated_at": "..."
    }
    ```
-   **Error Responses:**
    -   `400 Bad Request` (例如，缺少 `name`):
        ```json
        {
            "error": "阶段名称 (name) 是必需的"
        }
        ```
    -   `404 Not Found` (项目未找到).
    -   `500 Internal Server Error`.

#### 2. 更新一个阶段

-   **Method:** `PUT`
-   **Endpoint:** `/api/stages/<string:stage_id>`
-   **Description:** 更新一个已存在的阶段信息 (如名称、顺序)。
-   **Path Parameters:**
    -   `stage_id` (String): 阶段的唯一ID。
-   **Request Body:**
    ```json
    {
        "name": "更新后的阶段名称", // String, 可选
        "order": 1 // Integer, 可选
    }
    ```
-   **Success Response (200 OK):**
    ```json
    {
        "id": "stage_uuid",
        "name": "更新后的阶段名称",
        "project_id": "project_uuid",
        "order": 1,
        "created_at": "...",
        "updated_at": "..."
    }
    ```
-   **Error Responses:**
    -   `400 Bad Request` (请求数据为空).
    -   `404 Not Found` (阶段未找到).
    -   `500 Internal Server Error`.

#### 3. 删除一个阶段

-   **Method:** `DELETE`
-   **Endpoint:** `/api/stages/<string:stage_id>`
-   **Description:** 删除一个阶段及其所有关联的任务和子任务。
-   **Path Parameters:**
    -   `stage_id` (String): 阶段的唯一ID。
-   **Success Response (200 OK):**
    ```json
    {
        "message": "阶段已成功删除"
    }
    ```
-   **Error Responses:**
    -   `404 Not Found` (阶段未找到).
    -   `500 Internal Server Error`.

### 任务 (Tasks)

#### 1. 为阶段创建新任务

-   **Method:** `POST`
-   **Endpoint:** `/api/stages/<string:stage_id>/tasks`
-   **Description:** 为指定的阶段创建一个新的任务。
-   **Path Parameters:**
    -   `stage_id` (String): 阶段的唯一ID。
-   **Request Body:**
    ```json
    {
        "content": "新任务的内容", // String, 必需
        "assignee": "负责人名称", // String, 可选
        "start_date": "YYYY-MM-DD", // String (Date), 可选
        "end_date": "YYYY-MM-DD" // String (Date), 可选
    }
    ```
-   **Success Response (201 Created):**
    ```json
    {
        "id": "new_task_uuid",
        "content": "新任务的内容",
        "stage_id": "stage_uuid",
        "assignee": "负责人名称",
        "start_date": "YYYY-MM-DD",
        "end_date": "YYYY-MM-DD",
        "order": 0, // 或下一个可用的顺序值
        "created_at": "...",
        "updated_at": "...",
        "subtasks": []
    }
    ```
-   **Error Responses:**
    -   `400 Bad Request` (例如，缺少 `content`):
        ```json
        {
            "error": "任务内容 (content) 是必需的"
        }
        ```
    -   `404 Not Found` (阶段未找到).
    -   `500 Internal Server Error`.

#### 2. 更新一个任务

-   **Method:** `PUT`
-   **Endpoint:** `/api/tasks/<string:task_id>`
-   **Description:** 更新一个已存在的任务信息 (内容、负责人、日期、顺序、所属阶段)。
-   **Path Parameters:**
    -   `task_id` (String): 任务的唯一ID。
-   **Request Body:**
    ```json
    {
        "content": "更新后的任务内容", // String, 可选
        "assignee": "新的负责人", // String, 可选 (可为 null)
        "start_date": "YYYY-MM-DD", // String (Date), 可选 (可为 null)
        "end_date": "YYYY-MM-DD", // String (Date), 可选 (可为 null)
        "order": 1, // Integer, 可选
        "stage_id": "new_stage_uuid" // String, 可选 (用于移动任务到不同阶段)
    }
    ```
-   **Success Response (200 OK):**
    ```json
    {
        "id": "task_uuid",
        "content": "更新后的任务内容",
        "stage_id": "new_stage_uuid", // 或原 stage_id
        "assignee": "新的负责人",
        "start_date": "YYYY-MM-DD",
        "end_date": "YYYY-MM-DD",
        "order": 1,
        "created_at": "...",
        "updated_at": "...",
        "subtasks": [/* ... */]
    }
    ```
-   **Error Responses:**
    -   `400 Bad Request` (请求数据为空).
    -   `404 Not Found` (任务或目标阶段未找到).
    -   `500 Internal Server Error`.

#### 3. 删除一个任务

-   **Method:** `DELETE`
-   **Endpoint:** `/api/tasks/<string:task_id>`
-   **Description:** 删除一个任务及其所有关联的子任务。
-   **Path Parameters:**
    -   `task_id` (String): 任务的唯一ID。
-   **Success Response (200 OK):**
    ```json
    {
        "message": "任务已成功删除"
    }
    ```
-   **Error Responses:**
    -   `404 Not Found` (任务未找到).
    -   `500 Internal Server Error`.

### 子任务 (SubTasks)

#### 1. 为父任务创建新子任务

-   **Method:** `POST`
-   **Endpoint:** `/api/tasks/<string:parent_task_id>/subtasks`
-   **Description:** 为指定的父任务创建一个新的子任务。
-   **Path Parameters:**
    -   `parent_task_id` (String): 父任务的唯一ID。
-   **Request Body:**
    ```json
    {
        "content": "新子任务的内容", // String, 必需
        "completed": false // Boolean, 可选, 默认为 false
    }
    ```
-   **Success Response (201 Created):**
    ```json
    {
        "id": "new_subtask_uuid",
        "content": "新子任务的内容",
        "parent_task_id": "parent_task_id",
        "completed": false,
        "order": 0, // 或下一个可用的顺序值
        "created_at": "...",
        "updated_at": "..."
    }
    ```
-   **Error Responses:**
    -   `400 Bad Request` (例如，缺少 `content`):
        ```json
        {
            "error": "子任务内容 (content) 是必需的"
        }
        ```
    -   `404 Not Found` (父任务未找到).
    -   `500 Internal Server Error`.

#### 2. 更新一个子任务

-   **Method:** `PUT`
-   **Endpoint:** `/api/subtasks/<string:subtask_id>`
-   **Description:** 更新一个已存在的子任务信息 (内容、完成状态、顺序)。
-   **Path Parameters:**
    -   `subtask_id` (String): 子任务的唯一ID。
-   **Request Body:**
    ```json
    {
        "content": "更新后的子任务内容", // String, 可选
        "completed": true, // Boolean, 可选
        "order": 1 // Integer, 可选
    }
    ```
-   **Success Response (200 OK):**
    ```json
    {
        "id": "subtask_uuid",
        "content": "更新后的子任务内容",
        "parent_task_id": "parent_task_id",
        "completed": true,
        "order": 1,
        "created_at": "...",
        "updated_at": "..."
    }
    ```
-   **Error Responses:**
    -   `400 Bad Request` (请求数据为空).
    -   `404 Not Found` (子任务未找到).
    -   `500 Internal Server Error`.

#### 3. 删除一个子任务

-   **Method:** `DELETE`
-   **Endpoint:** `/api/subtasks/<string:subtask_id>`
-   **Description:** 删除一个子任务。
-   **Path Parameters:**
    -   `subtask_id` (String): 子任务的唯一ID。
-   **Success Response (200 OK):**
    ```json
    {
        "message": "子任务已成功删除"
    }
    ```
-   **Error Responses:**
    -   `404 Not Found` (子任务未找到).
    -   `500 Internal Server Error`.

### 测试接口

#### 1. Hello World

-   **Method:** `GET`
-   **Endpoint:** `/hello`
-   **Description:** 一个简单的测试路由，用于检查后端服务是否正在运行。
-   **Success Response (200 OK):**
    ```text
    你好，看板后端已启动！(Hello, Kanban Backend is Running!)
    ```
