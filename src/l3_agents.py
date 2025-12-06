"""
L3 Agent Implementations
Each L3 agent executes specific tasks and returns structured output
"""
import random
from typing import List, Dict, Any
from datetime import datetime, timedelta


# Mock project database for consistent knowledge retrieval
PROJECT_DB = {
    "PRJ-ALPHA": {
        "release_date": "Dec 15, 2025",
        "code_freeze": "Dec 10, 2025",
        "days_remaining": 9,
        "progress": 70,
        "capacity": 85,
        "eng_manager": "Alex Kim",
        "tech_lead": "David Park"
    },
    "PRJ-BETA": {
        "release_date": "Jan 10, 2026",
        "code_freeze": "Jan 5, 2026",
        "days_remaining": 35,
        "progress": 65,
        "capacity": 80,
        "eng_manager": "Sarah Johnson",
        "tech_lead": "Emily Zhang"
    },
    "PRJ-GAMMA": {
        "release_date": "Jan 20, 2026",
        "code_freeze": "Jan 15, 2026",
        "days_remaining": 45,
        "progress": 55,
        "capacity": 75,
        "eng_manager": "Mike Chen",
        "tech_lead": "Robert Liu"
    },
    "PRJ-DELTA": {
        "release_date": "Feb 1, 2026",
        "code_freeze": "Jan 25, 2026",
        "days_remaining": 57,
        "progress": 40,
        "capacity": 70,
        "eng_manager": "Lisa Wong",
        "tech_lead": "James Park"
    }
}


class L3AgentExecutor:
    """Base class for L3 agent execution"""
    
    def __init__(self, message_content: str, project: str = None):
        self.message_content = message_content
        self.project = project
    
    def generate_random_date(self, days_ahead: int = 30) -> str:
        """Generate a random future date"""
        future_date = datetime.now() + timedelta(days=random.randint(1, days_ahead))
        return future_date.strftime("%b %d")


class ActionItemExtraction(L3AgentExecutor):
    """Extracts action items from message content"""
    
    def execute(self) -> List[str]:
        # Simulate extraction with dummy data
        action_items = []
        counter = 1
        
        keywords = ["add", "create", "implement", "evaluate", "fix", "update", "review", "test"]
        for keyword in keywords:
            if keyword in self.message_content.lower():
                action_items.append(
                    f"AI-{counter:03d}: \"Extract from message: {keyword} related task\"\n"
                    f"      Owner: ? | Due: ? | Flags: [MISSING_OWNER, MISSING_DUE_DATE]"
                )
                counter += 1
        
        if not action_items:
            action_items.append(
                f"AI-001: \"Follow up on message content\"\n"
                f"      Owner: ? | Due: ? | Flags: [MISSING_OWNER, MISSING_DUE_DATE]"
            )
        
        return action_items


class RiskExtraction(L3AgentExecutor):
    """Extracts risks from message content"""
    
    def execute(self) -> List[str]:
        risks = []
        counter = 1
        
        # Identify risk patterns
        risk_keywords = {
            "timeline": ("HIGH", "HIGH"),
            "deadline": ("HIGH", "HIGH"),
            "blocked": ("HIGH", "HIGH"),
            "urgent": ("MEDIUM", "HIGH"),
            "threat": ("HIGH", "HIGH"),
            "bug": ("MEDIUM", "MEDIUM"),
            "issue": ("MEDIUM", "MEDIUM"),
            "scope": ("MEDIUM", "MEDIUM"),
        }
        
        for keyword, (likelihood, impact) in risk_keywords.items():
            if keyword in self.message_content.lower():
                risks.append(
                    f"RISK-{counter:03d}: \"Identified: {keyword} concern in message\"\n"
                    f"      Likelihood: {likelihood} | Impact: {impact}"
                )
                counter += 1
        
        if not risks:
            risks.append(
                f"RISK-001: \"Potential communication gap or unclear requirements\"\n"
                f"      Likelihood: LOW | Impact: MEDIUM"
            )
        
        return risks


class IssueExtraction(L3AgentExecutor):
    """Extracts issues from message content"""
    
    def execute(self) -> List[str]:
        issues = []
        counter = 1
        
        issue_keywords = ["blocked", "down", "bug", "error", "problem", "issue", "broken"]
        for keyword in issue_keywords:
            if keyword in self.message_content.lower():
                issues.append(
                    f"ISSUE-{counter:03d}: \"{keyword.capitalize()} identified in message\"\n"
                    f"      Severity: {'CRITICAL' if keyword in ['down', 'blocked', 'broken'] else 'HIGH'} | Status: OPEN"
                )
                counter += 1
        
        if not issues:
            return ["No critical issues identified"]
        
        return issues


class DecisionExtraction(L3AgentExecutor):
    """Extracts decisions from message content"""
    
    def execute(self) -> List[str]:
        decisions = []
        counter = 1
        
        decision_keywords = ["should we", "can we", "decide", "prioritize", "choose", "approve"]
        for keyword in decision_keywords:
            if keyword in self.message_content.lower():
                decisions.append(
                    f"DEC-{counter:03d}: \"Decision needed: {keyword} scenario\"\n"
                    f"      Decision Maker: ? | Status: PENDING"
                )
                counter += 1
        
        if not decisions:
            decisions.append("No explicit decisions identified")
        
        return decisions


class KnowledgeRetrieval(L3AgentExecutor):
    """Retrieves context from knowledge base"""
    
    def execute(self) -> List[str]:
        # Check if project exists in mock database
        if self.project and self.project in PROJECT_DB:
            data = PROJECT_DB[self.project]
            return [
                f"Project: {self.project}",
                f"Current Release Date: {data['release_date']}",
                f"Days Remaining: {data['days_remaining']}",
                f"Code Freeze: {data['code_freeze']}",
                f"Current Progress: {data['progress']}%",
                f"Team Capacity: {data['capacity']}% utilized",
                f"Engineering Manager: {data['eng_manager']}",
                f"Tech Lead: {data['tech_lead']}",
            ]
        elif self.project:
            # Project not in database, generate random data
            return [
                f"Project: {self.project}",
                f"Current Release Date: {self.generate_random_date(30)}",
                f"Days Remaining: {random.randint(10, 30)}",
                f"Code Freeze: {self.generate_random_date(20)}",
                f"Current Progress: {random.randint(60, 90)}%",
                f"Team Capacity: {random.randint(70, 95)}% utilized",
                f"Engineering Manager: {random.choice(['Alex Kim', 'Sarah Johnson', 'Mike Chen'])}",
                f"Tech Lead: {random.choice(['David Park', 'Emily Zhang', 'Robert Liu'])}",
            ]
        else:
            return [
                "No project context available",
                "Unable to retrieve specific project details"
            ]


class QnA(L3AgentExecutor):
    """Formulates responses to questions"""
    
    def __init__(self, message_content: str, project: str, context: Dict[str, Any] = None, gemini_client=None):
        super().__init__(message_content, project)
        self.context = context or {}
        self.gemini_client = gemini_client
    
    def execute(self) -> List[str]:
        # Try to use Gemini for enhanced response
        if self.gemini_client:
            try:
                enhanced_response = self.gemini_client.enhance_response(self.context, self.message_content)
                if enhanced_response:
                    return [f'Response: "{enhanced_response}"']
            except Exception as e:
                print(f"Warning: Could not generate enhanced response: {e}")
        
        # Build gap-aware response (fallback)
        response_parts = []
        
        if "?" in self.message_content:
            response_parts.append("Response: \"Regarding your question:")
            response_parts.append("")
            response_parts.append("  WHAT I KNOW:")
            
            if self.context.get("knowledge"):
                for item in self.context["knowledge"][:4]:
                    response_parts.append(f"  • {item}")
            else:
                response_parts.append("  • Limited project context available")
            
            response_parts.append("")
            response_parts.append("  WHAT I'VE LOGGED:")
            
            if self.context.get("action_items"):
                response_parts.append(f"  • {len(self.context['action_items'])} action items logged")
            if self.context.get("risks"):
                response_parts.append(f"  • {len(self.context['risks'])} risks flagged")
            if self.context.get("decisions"):
                response_parts.append(f"  • {len(self.context['decisions'])} decisions pending")
            
            response_parts.append("")
            response_parts.append("  WHAT I NEED:")
            response_parts.append("  • Additional context from relevant stakeholders")
            response_parts.append("  • Clarification on specific requirements or constraints")
            response_parts.append("")
            response_parts.append("  I will provide a more complete answer once I have the above information.\"")
        else:
            response_parts.append("Response: \"Message acknowledged and processed.\"")
        
        return response_parts


class Evaluation(L3AgentExecutor):
    """Validates outputs before delivery"""
    
    def __init__(self, content_to_evaluate: str):
        super().__init__(content_to_evaluate)
    
    def execute(self) -> List[str]:
        # Simulate evaluation checks
        return [
            "Relevance: PASS",
            "Accuracy: PASS",
            "Tone: PASS",
            "Gaps Acknowledged: PASS",
            "Result: APPROVED"
        ]


class MessageDelivery(L3AgentExecutor):
    """Sends messages via appropriate channels"""
    
    def __init__(self, message_content: str, source: str, recipient: str, cc_list: List[str] = None):
        super().__init__(message_content)
        self.source = source
        self.recipient = recipient
        self.cc_list = cc_list or []
    
    def execute(self) -> List[str]:
        result = [
            f"Channel: {self.source}",
            f"Recipient: {self.recipient}",
        ]
        
        if self.cc_list:
            result.append(f"CC: {', '.join(self.cc_list)}")
        
        result.append("Delivery Status: SENT")
        
        return result


class ReportGeneration(L3AgentExecutor):
    """Generates formatted reports"""
    
    def execute(self) -> List[str]:
        return [
            "Report Type: Status Summary",
            "Format: Structured text",
            "Sections: Overview, Action Items, Risks, Next Steps",
            "Status: Generated successfully"
        ]


class MeetingAttendance(L3AgentExecutor):
    """Processes meeting transcripts"""
    
    def execute(self) -> List[str]:
        return [
            "Meeting transcript processed",
            "Participants identified: 4",
            "Key topics extracted: 3",
            "Minutes generated successfully"
        ]
