"""
Core data models for the Nion Orchestration Engine
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from enum import Enum


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class AgentType(str, Enum):
    L1_ORCHESTRATOR = "L1"
    L2_COORDINATOR = "L2"
    L3_AGENT = "L3"


class L2Domain(str, Enum):
    TRACKING_EXECUTION = "TRACKING_EXECUTION"
    COMMUNICATION_COLLABORATION = "COMMUNICATION_COLLABORATION"
    LEARNING_IMPROVEMENT = "LEARNING_IMPROVEMENT"


class Sender(BaseModel):
    name: str
    role: str


class InputMessage(BaseModel):
    message_id: str
    source: str
    sender: Sender
    content: str
    project: Optional[str] = None


class Task(BaseModel):
    task_id: str
    target_agent: str  # L2:DOMAIN or L3:agent_name
    purpose: str
    depends_on: List[str] = []
    status: TaskStatus = TaskStatus.PENDING
    output: Optional[List[str]] = None
    subtasks: List['Task'] = []
    is_cross_cutting: bool = False


class L1Plan(BaseModel):
    message: InputMessage
    tasks: List[Task]


class OrchestrationResult(BaseModel):
    message: InputMessage
    l1_plan: L1Plan
    executed_tasks: List[Task]
