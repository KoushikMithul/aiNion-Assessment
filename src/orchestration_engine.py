"""
Main Orchestration Engine
Coordinates L1, L2, and L3 layers and executes the plan
"""
from typing import Dict, Any, List
from src.models import InputMessage, Task, L1Plan, OrchestrationResult, TaskStatus
from src.l1_orchestrator import L1Orchestrator
from src.l2_coordinators import get_l2_coordinator
from src.l3_agents import KnowledgeRetrieval, Evaluation
from src.gemini_client import GeminiClient


class OrchestrationEngine:
    """Main orchestration engine that coordinates all layers"""
    
    def __init__(self):
        self.l1_orchestrator = L1Orchestrator()
        self.execution_context = {}
        self.gemini_client = GeminiClient()
    
    def process_message(self, message: InputMessage) -> OrchestrationResult:
        """Process a message through the orchestration pipeline"""
        
        # L1: Ingest and reason
        l1_plan = self.l1_orchestrator.ingest_and_reason(message)
        
        # Execute the plan
        executed_tasks = self._execute_plan(l1_plan, message)
        
        return OrchestrationResult(
            message=message,
            l1_plan=l1_plan,
            executed_tasks=executed_tasks
        )
    
    def _execute_plan(self, plan: L1Plan, message: InputMessage) -> List[Task]:
        """Execute the L1 plan by delegating to L2/L3 agents"""
        executed_tasks = []
        task_outputs = {}  # Store task outputs for dependencies
        
        for task in plan.tasks:
            # Check dependencies
            if task.depends_on:
                if not all(dep in task_outputs for dep in task.depends_on):
                    # Dependencies not met yet, skip for now
                    continue
            
            # Execute task
            executed_task = self._execute_task(task, message, task_outputs)
            executed_tasks.append(executed_task)
            task_outputs[task.task_id] = executed_task
        
        # Execute remaining tasks with dependencies
        remaining_tasks = [t for t in plan.tasks if t.task_id not in task_outputs]
        for task in remaining_tasks:
            executed_task = self._execute_task(task, message, task_outputs)
            executed_tasks.append(executed_task)
            task_outputs[task.task_id] = executed_task
        
        return executed_tasks
    
    def _execute_task(self, task: Task, message: InputMessage, task_outputs: Dict[str, Task]) -> Task:
        """Execute a single task"""
        target = task.target_agent
        
        # Build context from previous tasks
        context = self._build_context(task, task_outputs, message)
        
        if target.startswith("L2:"):
            # Delegate to L2 coordinator
            domain = target.split(":")[1]
            coordinator = get_l2_coordinator(domain)
            coordinator.set_gemini_client(self.gemini_client)  # Pass Gemini client
            return coordinator.coordinate(task, message.content, message.project, context)
            
        elif target.startswith("L3:"):
            # Execute cross-cutting L3 agent directly
            agent_name = target.split(":")[1]
            return self._execute_cross_cutting_agent(task, agent_name, message, context)
        
        return task
    
    def _execute_cross_cutting_agent(self, task: Task, agent_name: str, message: InputMessage, context: Dict[str, Any]) -> Task:
        """Execute a cross-cutting L3 agent"""
        if agent_name == "knowledge_retrieval":
            executor = KnowledgeRetrieval(message.content, message.project)
            task.output = executor.execute()
            task.status = TaskStatus.COMPLETED
            
        elif agent_name == "evaluation":
            # Get the content to evaluate from context
            content_to_evaluate = "\n".join(context.get("response", ["No content to evaluate"]))
            executor = Evaluation(content_to_evaluate)
            task.output = executor.execute()
            task.status = TaskStatus.COMPLETED
        
        return task
    
    def _build_context(self, task: Task, task_outputs: Dict[str, Task], message: InputMessage) -> Dict[str, Any]:
        """Build context from previous task outputs"""
        context = {
            "sender_name": message.sender.name,
            "source": message.source,
            "cc_list": [],
        }
        
        # Collect outputs from dependencies
        for dep_id in task.depends_on:
            if dep_id in task_outputs:
                dep_task = task_outputs[dep_id]
                
                # Store specific outputs based on task type
                if "action item" in dep_task.purpose.lower():
                    context["action_items"] = dep_task.subtasks[0].output if dep_task.subtasks else []
                elif "risk" in dep_task.purpose.lower():
                    context["risks"] = dep_task.subtasks[0].output if dep_task.subtasks else []
                elif "decision" in dep_task.purpose.lower():
                    context["decisions"] = dep_task.subtasks[0].output if dep_task.subtasks else []
                elif "knowledge" in dep_task.purpose.lower():
                    context["knowledge"] = dep_task.output
                elif "response" in dep_task.purpose.lower():
                    context["response"] = dep_task.subtasks[0].output if dep_task.subtasks else []
        
        return context
