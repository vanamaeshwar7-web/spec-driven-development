# Pydantic schemas
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, Literal

TaskStatus = Literal["todo", "in_progress", "done"]


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)

    def model_post_init(self, __context):
        self.title = self.title.strip()
        if self.description is not None:
            self.description = self.description.strip()


class TaskUpdateStatus(BaseModel):
    status: TaskStatus


class TaskOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: TaskStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
