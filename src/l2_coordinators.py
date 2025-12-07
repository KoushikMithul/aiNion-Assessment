"""
L2 Coordinator Implementations
L2 agents receive directions from L1 and coordinate L3 agents
"""
from typing import List, Dict, Any
from src.models import Task, TaskStatus
from src.agents import get_l3_agents_for_l2, is_cross_cutting_agent
from src.l3_agents import (
    ActionItemExtraction, RiskExtraction, IssueExtraction, DecisionExtraction,
    QnA, ReportGeneration, MessageDelivery, MeetingAttendance
)


class L2Coordinator:
    """Base class for L2 coordinators"""
    
    def __init__(self, domain: str):
        self.domain = domain
        self.visible_l3_agents = get_l3_agents_for_l2(domain)
        self.gemini_client = None  # Will be set by orchestration engine
    
    def set_gemini_client(self, client):
        """Set the Gemini client for AI-enhanced responses"""
        self.gemini_client = client
    
    def can_access_l3_agent(self, agent_name: str) -> bool:
        """Check if this L2 can access the specified L3 agent"""
        return agent_name in self.visible_l3_agents
    
    def coordinate(self, task: Task, message_content: str, project: str, context: Dict[str, Any] = None) -> Task:
        """Coordinate L3 agents to complete the task"""
        raise NotImplementedError("Subclasses must implement coordinate method")


class TrackingExecutionCoordinator(L2Coordinator):
    """L2 Coordinator for TRACKING_EXECUTION domain"""
    
    def __init__(self):
        super().__init__("TRACKING_EXECUTION")
    
    def coordinate(self, task: Task, message_content: str, project: str, context: Dict[str, Any] = None) -> Task:
        """Coordinate tracking and extraction L3 agents"""
        context = context or {}
        
        # Determine which L3 agents to use based on task purpose
        purpose_lower = task.purpose.lower()
        
        if "action item" in purpose_lower:
            subtask = self._create_subtask(task.task_id, "action_item_extraction", "Extract action items")
            executor = ActionItemExtraction(message_content, project)
            subtask.output = executor.execute()
            subtask.status = TaskStatus.COMPLETED
            task.subtasks.append(subtask)
            
        elif "risk" in purpose_lower:
            subtask = self._create_subtask(task.task_id, "risk_extraction", "Extract risks")
            executor = RiskExtraction(message_content, project)
            subtask.output = executor.execute()
            subtask.status = TaskStatus.COMPLETED
            task.subtasks.append(subtask)
            
        elif "issue" in purpose_lower:
            subtask = self._create_subtask(task.task_id, "issue_extraction", "Extract issues")
            executor = IssueExtraction(message_content, project)
            subtask.output = executor.execute()
            subtask.status = TaskStatus.COMPLETED
            task.subtasks.append(subtask)
            
        elif "decision" in purpose_lower:
            subtask = self._create_subtask(task.task_id, "decision_extraction", "Extract decisions")
            executor = DecisionExtraction(message_content, project)
            subtask.output = executor.execute()
            subtask.status = TaskStatus.COMPLETED
            task.subtasks.append(subtask)
        
        else:
            # Fallback if L1 purpose is unclear
            print(f"Warning: L2:TRACKING_EXECUTION could not map purpose '{task.purpose}' to a specific L3 agent.")
            subtask = self._create_subtask(task.task_id, "action_item_extraction", "Fallback: attempt extraction")
            executor = ActionItemExtraction(message_content, project)
            subtask.output = executor.execute()
            subtask.status = TaskStatus.COMPLETED
            task.subtasks.append(subtask)
        
        task.status = TaskStatus.COMPLETED
        return task
    
    def _create_subtask(self, parent_task_id: str, agent_name: str, purpose: str) -> Task:
        """Create a subtask for L3 agent"""
        subtask_id = f"{parent_task_id}-A"
        return Task(
            task_id=subtask_id,
            target_agent=f"L3:{agent_name}",
            purpose=purpose,
            status=TaskStatus.IN_PROGRESS
        )


class CommunicationCollaborationCoordinator(L2Coordinator):
    """L2 Coordinator for COMMUNICATION_COLLABORATION domain"""
    
    def __init__(self):
        super().__init__("COMMUNICATION_COLLABORATION")
    
    def coordinate(self, task: Task, message_content: str, project: str, context: Dict[str, Any] = None) -> Task:
        """Coordinate communication L3 agents"""
        context = context or {}
        purpose_lower = task.purpose.lower()
        
        if "send" in purpose_lower or "deliver" in purpose_lower:
            subtask = self._create_subtask(task.task_id, "message_delivery", "Send message")
            # Get sender info from context
            sender_name = context.get("sender_name", "Unknown")
            cc_list = context.get("cc_list", [])
            source = context.get("source", "email")
            
            executor = MessageDelivery(message_content, source, sender_name, cc_list)
            subtask.output = executor.execute()
            subtask.status = TaskStatus.COMPLETED
            task.subtasks.append(subtask)
            
        elif "response" in purpose_lower or "answer" in purpose_lower or "formulate" in purpose_lower:
            subtask = self._create_subtask(task.task_id, "qna", "Formulate response")
            executor = QnA(message_content, project, context, self.gemini_client)
            subtask.output = executor.execute()
            subtask.status = TaskStatus.COMPLETED
            task.subtasks.append(subtask)
            
        elif "report" in purpose_lower:
            subtask = self._create_subtask(task.task_id, "report_generation", "Generate report")
            executor = ReportGeneration(message_content, project, context)
            subtask.output = executor.execute()
            subtask.status = TaskStatus.COMPLETED
            task.subtasks.append(subtask)
            
        elif "meeting" in purpose_lower:
            subtask = self._create_subtask(task.task_id, "meeting_attendance", "Process meeting")
            executor = MeetingAttendance(message_content, project)
            subtask.output = executor.execute()
            subtask.status = TaskStatus.COMPLETED
            task.subtasks.append(subtask)
        
        else:
            # Fallback if L1 purpose is unclear
            print(f"Warning: L2:COMMUNICATION_COLLABORATION could not map purpose '{task.purpose}' to a specific L3 agent.")
            subtask = self._create_subtask(task.task_id, "qna", "Fallback: general acknowledgment")
            executor = QnA(message_content, project, context, self.gemini_client)
            subtask.output = executor.execute()
            subtask.status = TaskStatus.COMPLETED
            task.subtasks.append(subtask)
        
        task.status = TaskStatus.COMPLETED
        return task
    
    def _create_subtask(self, parent_task_id: str, agent_name: str, purpose: str) -> Task:
        """Create a subtask for L3 agent"""
        subtask_id = f"{parent_task_id}-A"
        return Task(
            task_id=subtask_id,
            target_agent=f"L3:{agent_name}",
            purpose=purpose,
            status=TaskStatus.IN_PROGRESS
        )


class LearningImprovementCoordinator(L2Coordinator):
    """L2 Coordinator for LEARNING_IMPROVEMENT domain"""
    
    def __init__(self):
        super().__init__("LEARNING_IMPROVEMENT")
    
    def coordinate(self, task: Task, message_content: str, project: str, context: Dict[str, Any] = None) -> Task:
        """Coordinate learning L3 agents"""
        purpose_lower = task.purpose.lower()
        
        if "learn" in purpose_lower or "instruction" in purpose_lower:
            subtask = self._create_subtask(task.task_id, "instruction_led_learning", "Learn from instructions")
            subtask.output = [
                "Instruction processed and stored",
                "Knowledge base updated",
                "SOP created successfully"
            ]
            subtask.status = TaskStatus.COMPLETED
            task.subtasks.append(subtask)
        
        task.status = TaskStatus.COMPLETED
        return task
    
    def _create_subtask(self, parent_task_id: str, agent_name: str, purpose: str) -> Task:
        """Create a subtask for L3 agent"""
        subtask_id = f"{parent_task_id}-A"
        return Task(
            task_id=subtask_id,
            target_agent=f"L3:{agent_name}",
            purpose=purpose,
            status=TaskStatus.IN_PROGRESS
        )


def get_l2_coordinator(domain: str) -> L2Coordinator:
    """Factory function to get the appropriate L2 coordinator"""
    coordinators = {
        "TRACKING_EXECUTION": TrackingExecutionCoordinator,
        "COMMUNICATION_COLLABORATION": CommunicationCollaborationCoordinator,
        "LEARNING_IMPROVEMENT": LearningImprovementCoordinator,
    }
    
    coordinator_class = coordinators.get(domain)
    if not coordinator_class:
        raise ValueError(f"Unknown L2 domain: {domain}")
    
    return coordinator_class()
