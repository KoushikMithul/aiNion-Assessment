"""
Output formatter for orchestration results
Formats the orchestration map according to the specification
"""
from src.models import OrchestrationResult, Task


class OutputFormatter:
    """Formats orchestration results into the specified output format"""
    
    def format(self, result: OrchestrationResult) -> str:
        """Format the orchestration result into a string"""
        lines = []
        
        # Header
        lines.append("=" * 70)
        lines.append("NION ORCHESTRATION MAP")
        lines.append("=" * 70)
        lines.append(f"Message: {result.message.message_id}")
        lines.append(f"From: {result.message.sender.name} ({result.message.sender.role})")
        lines.append(f"Project: {result.message.project or 'N/A'}")
        lines.append("")
        
        # L1 Plan
        lines.append("=" * 70)
        lines.append("L1 PLAN")
        lines.append("=" * 70)
        
        for task in result.l1_plan.tasks:
            lines.append(f"[{task.task_id}] → {task.target_agent}")
            lines.append(f"Purpose: {task.purpose}")
            if task.depends_on:
                lines.append(f"Depends On: {', '.join(task.depends_on)}")
            lines.append("")
        
        # L2/L3 Execution
        lines.append("=" * 70)
        lines.append("L2/L3 EXECUTION")
        lines.append("=" * 70)
        lines.append("")
        
        for task in result.executed_tasks:
            if task.target_agent.startswith("L2:"):
                lines.extend(self._format_l2_task(task))
            elif task.target_agent.startswith("L3:") and task.is_cross_cutting:
                lines.extend(self._format_cross_cutting_task(task))
            lines.append("")
        
        lines.append("=" * 70)
        
        return "\n".join(lines)
    
    def _format_l2_task(self, task: Task) -> list:
        """Format an L2 task with its subtasks"""
        lines = []
        lines.append(f"[{task.task_id}] {task.target_agent}")
        
        for subtask in task.subtasks:
            lines.append(f"└─▶ [{subtask.task_id}] {subtask.target_agent}")
            lines.append(f"    Status: {subtask.status.value}")
            if subtask.output:
                lines.append("    Output:")
                for output_line in subtask.output:
                    lines.append(f"    • {output_line}")
        
        return lines
    
    def _format_cross_cutting_task(self, task: Task) -> list:
        """Format a cross-cutting L3 task"""
        lines = []
        lines.append(f"[{task.task_id}] {task.target_agent} (Cross-Cutting)")
        lines.append(f"Status: {task.status.value}")
        if task.output:
            lines.append("Output:")
            for output_line in task.output:
                lines.append(f"• {output_line}")
        
        return lines
