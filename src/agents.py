"""
Agent registry and configuration
"""
from typing import Dict, List, Set
from enum import Enum


class L3Agent(str, Enum):
    # TRACKING_EXECUTION L3 Agents
    ACTION_ITEM_EXTRACTION = "action_item_extraction"
    ACTION_ITEM_VALIDATION = "action_item_validation"
    ACTION_ITEM_TRACKING = "action_item_tracking"
    RISK_EXTRACTION = "risk_extraction"
    RISK_TRACKING = "risk_tracking"
    ISSUE_EXTRACTION = "issue_extraction"
    ISSUE_TRACKING = "issue_tracking"
    DECISION_EXTRACTION = "decision_extraction"
    DECISION_TRACKING = "decision_tracking"
    
    # COMMUNICATION_COLLABORATION L3 Agents
    QNA = "qna"
    REPORT_GENERATION = "report_generation"
    MESSAGE_DELIVERY = "message_delivery"
    MEETING_ATTENDANCE = "meeting_attendance"
    
    # LEARNING_IMPROVEMENT L3 Agents
    INSTRUCTION_LED_LEARNING = "instruction_led_learning"


class CrossCuttingAgent(str, Enum):
    KNOWLEDGE_RETRIEVAL = "knowledge_retrieval"
    EVALUATION = "evaluation"


# L2 to L3 Agent Mapping (Visibility Rules)
L2_TO_L3_MAPPING: Dict[str, List[str]] = {
    "TRACKING_EXECUTION": [
        L3Agent.ACTION_ITEM_EXTRACTION.value,
        L3Agent.ACTION_ITEM_VALIDATION.value,
        L3Agent.ACTION_ITEM_TRACKING.value,
        L3Agent.RISK_EXTRACTION.value,
        L3Agent.RISK_TRACKING.value,
        L3Agent.ISSUE_EXTRACTION.value,
        L3Agent.ISSUE_TRACKING.value,
        L3Agent.DECISION_EXTRACTION.value,
        L3Agent.DECISION_TRACKING.value,
    ],
    "COMMUNICATION_COLLABORATION": [
        L3Agent.QNA.value,
        L3Agent.REPORT_GENERATION.value,
        L3Agent.MESSAGE_DELIVERY.value,
        L3Agent.MEETING_ATTENDANCE.value,
    ],
    "LEARNING_IMPROVEMENT": [
        L3Agent.INSTRUCTION_LED_LEARNING.value,
    ],
}


# Cross-Cutting Agents accessible by all layers
CROSS_CUTTING_AGENTS: List[str] = [
    CrossCuttingAgent.KNOWLEDGE_RETRIEVAL.value,
    CrossCuttingAgent.EVALUATION.value,
]


# L1 can see L2 domains and Cross-Cutting agents
L1_VISIBLE_AGENTS: List[str] = [
    "L2:TRACKING_EXECUTION",
    "L2:COMMUNICATION_COLLABORATION",
    "L2:LEARNING_IMPROVEMENT",
] + [f"L3:{agent}" for agent in CROSS_CUTTING_AGENTS]


def get_l3_agents_for_l2(l2_domain: str) -> List[str]:
    """Get L3 agents visible to a specific L2 domain"""
    return L2_TO_L3_MAPPING.get(l2_domain, []) + CROSS_CUTTING_AGENTS


def is_cross_cutting_agent(agent_name: str) -> bool:
    """Check if an agent is a cross-cutting agent"""
    return agent_name in CROSS_CUTTING_AGENTS
