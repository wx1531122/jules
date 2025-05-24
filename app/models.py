import uuid
from datetime import datetime, timezone
from app import db # Import db instance from app top-level __init__.py

# Helper for default UUID generation
def generate_uuid():
    return str(uuid.uuid4())

class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    stages = db.relationship('Stage', backref='project', lazy=True, cascade="all, delete-orphan")

    def to_dict(self, include_stages=False):
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() + 'Z',
            'updated_at': self.updated_at.isoformat() + 'Z'
        }
        if include_stages:
            data['stages'] = sorted([stage.to_dict(include_tasks=True) for stage in self.stages], key=lambda s: s['order'])
        return data

class Stage(db.Model):
    __tablename__ = 'stages'
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    name = db.Column(db.String(100), nullable=False)
    project_id = db.Column(db.String(36), db.ForeignKey('projects.id'), nullable=False)
    order = db.Column(db.Integer, nullable=False, default=0) # Default order, will need logic to set correctly
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    tasks = db.relationship('Task', backref='stage', lazy=True, cascade="all, delete-orphan")

    def to_dict(self, include_tasks=False):
        data = {
            'id': self.id,
            'name': self.name,
            'project_id': self.project_id,
            'order': self.order,
            'created_at': self.created_at.isoformat() + 'Z',
            'updated_at': self.updated_at.isoformat() + 'Z'
        }
        if include_tasks:
            data['tasks'] = sorted([task.to_dict(include_subtasks=True) for task in self.tasks], key=lambda t: t['order'])
        return data

class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    content = db.Column(db.Text, nullable=False)
    stage_id = db.Column(db.String(36), db.ForeignKey('stages.id'), nullable=False)
    assignee = db.Column(db.String(100), nullable=True)
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    order = db.Column(db.Integer, nullable=False, default=0) # Default order
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    subtasks = db.relationship('SubTask', backref='parent_task', lazy=True, cascade="all, delete-orphan")

    def to_dict(self, include_subtasks=False):
        data = {
            'id': self.id,
            'content': self.content,
            'stage_id': self.stage_id,
            'assignee': self.assignee,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'order': self.order,
            'created_at': self.created_at.isoformat() + 'Z',
            'updated_at': self.updated_at.isoformat() + 'Z'
        }
        if include_subtasks:
            data['subtasks'] = sorted([subtask.to_dict() for subtask in self.subtasks], key=lambda s: s['order'])
        return data

class SubTask(db.Model):
    __tablename__ = 'subtasks'
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    content = db.Column(db.Text, nullable=False)
    parent_task_id = db.Column(db.String(36), db.ForeignKey('tasks.id'), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    order = db.Column(db.Integer, nullable=False, default=0) # Default order
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'parent_task_id': self.parent_task_id,
            'completed': self.completed,
            'order': self.order,
            'created_at': self.created_at.isoformat() + 'Z',
            'updated_at': self.updated_at.isoformat() + 'Z'
        }
