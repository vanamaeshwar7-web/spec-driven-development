# Application entry point
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .db import Base, engine, get_db
from . import crud, schemas

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Task Manager API",
    version="1.0.0"
)


@app.post("/tasks", response_model=schemas.TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(payload: schemas.TaskCreate, db: Session = Depends(get_db)):
    if not payload.title.strip():
        raise HTTPException(status_code=422, detail="title cannot be blank")
    return crud.create_task(db, payload.title, payload.description)


@app.get("/tasks", response_model=list[schemas.TaskOut])
def list_tasks(
    status: schemas.TaskStatus | None = None,
    query: str | None = None,
    db: Session = Depends(get_db)
):
    return crud.list_tasks(db, status=status, query=query)


@app.get("/tasks/{task_id}", response_model=schemas.TaskOut)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = crud.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="task not found")
    return task


@app.patch("/tasks/{task_id}", response_model=schemas.TaskOut)
def update_task_status(
    task_id: int,
    payload: schemas.TaskUpdateStatus,
    db: Session = Depends(get_db)
):
    task = crud.update_task_status(db, task_id, payload.status)
    if not task:
        raise HTTPException(status_code=404, detail="task not found")
    return task


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    ok = crud.delete_task(db, task_id)
    if not ok:
        raise HTTPException(status_code=404, detail="task not found")
    return None
