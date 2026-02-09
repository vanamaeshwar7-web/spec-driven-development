# CRUD operations
from sqlalchemy.orm import Session
from sqlalchemy import select
from .models import Task


def create_task(db: Session, title: str, description: str | None):
    task = Task(
        title=title,
        description=description,
        status="todo"
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def get_task(db: Session, task_id: int):
    return db.get(Task, task_id)


def list_tasks(db: Session, status: str | None = None, query: str | None = None):
    stmt = select(Task)

    if status:
        stmt = stmt.where(Task.status == status)

    if query:
        q = f"%{query}%"
        stmt = stmt.where(
            Task.title.ilike(q) |
            Task.description.ilike(q)
        )

    stmt = stmt.order_by(Task.created_at.desc())
    return db.scalars(stmt).all()


def update_task_status(db: Session, task_id: int, status: str):
    task = db.get(Task, task_id)
    if not task:
        return None
    task.status = status
    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task_id: int):
    task = db.get(Task, task_id)
    if not task:
        return False
    db.delete(task)
    db.commit()
    return True
