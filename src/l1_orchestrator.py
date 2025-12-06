"""
L1 Orchestrator - The main reasoning and planning layer
Ingests messages, analyzes intent, identifies gaps, and creates execution plans
"""
from typing import List, Dict, Any
from src.models import InputMessage, Task, L1Plan, TaskStatus
from src.agents import L1_VISIBLE_AGENTS, is_cross_cutting_agent
from src.gemini_client import GeminiClient


class L1Orchestrator:
    """L1 Orchestrator - Reasons about intent and generates plans"""
    
    def __init__(self):
        self.task_counter = 0
        self.gemini_client = GeminiClient()
    
    def ingest_and_reason(self, message: InputMessage) -> L1Plan:
        """
        Ingest message and perform reasoning:
        1. Parse and understand message
        2. Identify intent
        3. Detect gaps
        4. Select strategy
        5. Generate plan
        """
        self.task_counter = 0
        
        # Use Gemini AI to analyze intent
        analysis = self.gemini_client.analyze_intent(
            message.content,
            message.sender.role,
            message.source
        )
        
        intent = analysis.get("intent", "general_request")
        print(f"\n[L1 Reasoning] Intent: {intent} | Urgency: {analysis.get('urgency', 'medium')}")
        print(f"[L1 Reasoning] {analysis.get('reasoning', 'No reasoning provided')}\n")
        
        # Generate plan based on intent
        tasks = self._generate_plan(message, intent)
        
        return L1Plan(message=message, tasks=tasks)
    

    
    def _generate_plan(self, message: InputMessage, intent: str) -> List[Task]:
        """Generate execution plan based on intent"""
        tasks = []
        
        if intent == "status_query":
            tasks = self._plan_status_query(message)
        elif intent == "feasibility_query":
            tasks = self._plan_feasibility_query(message)
        elif intent == "decision_request":
            tasks = self._plan_decision_request(message)
        elif intent == "escalation":
            tasks = self._plan_escalation(message)
        elif intent == "meeting_update":
            tasks = self._plan_meeting_update(message)
        else:
            tasks = self._plan_general_request(message)
        
        return tasks
    
    def _plan_status_query(self, message: InputMessage) -> List[Task]:
        """Plan for status query intent"""
        tasks = []
        
        # Retrieve context
        tasks.append(self._create_task(
            "L3:knowledge_retrieval",
            "Retrieve project context and current status",
            is_cross_cutting=True
        ))
        
        # Check for any tracked items
        tasks.append(self._create_task(
            "L2:TRACKING_EXECUTION",
            "Retrieve tracked action items and status"
        ))
        
        # Formulate response
        tasks.append(self._create_task(
            "L2:COMMUNICATION_COLLABORATION",
            "Formulate status response",
            depends_on=[tasks[0].task_id, tasks[1].task_id]
        ))
        
        # Send response
        tasks.append(self._create_task(
            "L2:COMMUNICATION_COLLABORATION",
            "Send response to sender",
            depends_on=[tasks[2].task_id]
        ))
        
        return tasks
    
    def _plan_feasibility_query(self, message: InputMessage) -> List[Task]:
        """Plan for feasibility query intent"""
        tasks = []
        
        # Extract action items
        tasks.append(self._create_task(
            "L2:TRACKING_EXECUTION",
            "Extract action items from request"
        ))
        
        # Extract risks
        tasks.append(self._create_task(
            "L2:TRACKING_EXECUTION",
            "Extract risks from request"
        ))
        
        # Extract decision needed
        tasks.append(self._create_task(
            "L2:TRACKING_EXECUTION",
            "Extract decision needed"
        ))
        
        # Retrieve context
        tasks.append(self._create_task(
            "L3:knowledge_retrieval",
            "Retrieve project context and timeline",
            is_cross_cutting=True
        ))
        
        # Formulate gap-aware response
        tasks.append(self._create_task(
            "L2:COMMUNICATION_COLLABORATION",
            "Formulate gap-aware response",
            depends_on=[tasks[0].task_id, tasks[1].task_id, tasks[2].task_id, tasks[3].task_id]
        ))
        
        # Evaluate response
        tasks.append(self._create_task(
            "L3:evaluation",
            "Evaluate response before sending",
            depends_on=[tasks[4].task_id],
            is_cross_cutting=True
        ))
        
        # Send response
        tasks.append(self._create_task(
            "L2:COMMUNICATION_COLLABORATION",
            "Send response to sender",
            depends_on=[tasks[5].task_id]
        ))
        
        return tasks
    
    def _plan_decision_request(self, message: InputMessage) -> List[Task]:
        """Plan for decision request intent"""
        tasks = []
        
        # Extract decision
        tasks.append(self._create_task(
            "L2:TRACKING_EXECUTION",
            "Extract decision from request"
        ))
        
        # Extract relevant context
        tasks.append(self._create_task(
            "L3:knowledge_retrieval",
            "Retrieve relevant context for decision",
            is_cross_cutting=True
        ))
        
        # Formulate response with decision framework
        tasks.append(self._create_task(
            "L2:COMMUNICATION_COLLABORATION",
            "Formulate decision framework response",
            depends_on=[tasks[0].task_id, tasks[1].task_id]
        ))
        
        # Send response
        tasks.append(self._create_task(
            "L2:COMMUNICATION_COLLABORATION",
            "Send response to sender",
            depends_on=[tasks[2].task_id]
        ))
        
        return tasks
    
    def _plan_escalation(self, message: InputMessage) -> List[Task]:
        """Plan for urgent escalation intent"""
        tasks = []
        
        # Extract issues
        tasks.append(self._create_task(
            "L2:TRACKING_EXECUTION",
            "Extract issues from escalation"
        ))
        
        # Extract risks
        tasks.append(self._create_task(
            "L2:TRACKING_EXECUTION",
            "Extract risks from escalation"
        ))
        
        # Retrieve context
        tasks.append(self._create_task(
            "L3:knowledge_retrieval",
            "Retrieve escalation context",
            is_cross_cutting=True
        ))
        
        # Formulate urgent response
        tasks.append(self._create_task(
            "L2:COMMUNICATION_COLLABORATION",
            "Formulate urgent response with action plan",
            depends_on=[tasks[0].task_id, tasks[1].task_id, tasks[2].task_id]
        ))
        
        # Send response immediately
        tasks.append(self._create_task(
            "L2:COMMUNICATION_COLLABORATION",
            "Send urgent response to sender",
            depends_on=[tasks[3].task_id]
        ))
        
        return tasks
    
    def _plan_meeting_update(self, message: InputMessage) -> List[Task]:
        """Plan for meeting update/transcript intent"""
        tasks = []
        
        # Process meeting content
        tasks.append(self._create_task(
            "L2:COMMUNICATION_COLLABORATION",
            "Process meeting transcript"
        ))
        
        # Extract action items
        tasks.append(self._create_task(
            "L2:TRACKING_EXECUTION",
            "Extract action items from meeting"
        ))
        
        # Extract issues
        tasks.append(self._create_task(
            "L2:TRACKING_EXECUTION",
            "Extract issues from meeting"
        ))
        
        # Extract decisions
        tasks.append(self._create_task(
            "L2:TRACKING_EXECUTION",
            "Extract decisions from meeting"
        ))
        
        # Generate meeting summary
        tasks.append(self._create_task(
            "L2:COMMUNICATION_COLLABORATION",
            "Generate meeting summary report",
            depends_on=[tasks[0].task_id, tasks[1].task_id, tasks[2].task_id, tasks[3].task_id]
        ))
        
        return tasks
    
    def _plan_general_request(self, message: InputMessage) -> List[Task]:
        """Plan for general request intent"""
        tasks = []
        
        # Extract any action items
        tasks.append(self._create_task(
            "L2:TRACKING_EXECUTION",
            "Extract action items from message"
        ))
        
        # Retrieve context
        tasks.append(self._create_task(
            "L3:knowledge_retrieval",
            "Retrieve project context",
            is_cross_cutting=True
        ))
        
        # Formulate acknowledgment response
        tasks.append(self._create_task(
            "L2:COMMUNICATION_COLLABORATION",
            "Formulate acknowledgment response",
            depends_on=[tasks[0].task_id, tasks[1].task_id]
        ))
        
        return tasks
    
    def _create_task(self, target: str, purpose: str, depends_on: List[str] = None, is_cross_cutting: bool = False) -> Task:
        """Create a task with auto-incrementing ID"""
        self.task_counter += 1
        task_id = f"TASK-{self.task_counter:03d}"
        
        return Task(
            task_id=task_id,
            target_agent=target,
            purpose=purpose,
            depends_on=depends_on or [],
            is_cross_cutting=is_cross_cutting
        )
