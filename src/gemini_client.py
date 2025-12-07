"""
Gemini AI Integration for enhanced L1 reasoning
"""
import os
import json
from typing import Dict, Any
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()


class GeminiClient:
    """Client for Google Gemini API"""
    
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("Warning: GOOGLE_API_KEY not found in environment variables.")
            print("The system will use rule-based reasoning instead of AI-enhanced reasoning.")
            self.model = None
        else:
            try:
                genai.configure(api_key=api_key)
                # Use the latest available Gemini model
                self.model = genai.GenerativeModel('models/gemini-2.0-flash')
                print("✅ Gemini AI initialized successfully!")
            except Exception as e:
                print(f"Warning: Error configuring Gemini API: {e}")
                print("The system will use rule-based reasoning instead of AI-enhanced reasoning.")
                self.model = None
    
    def analyze_intent(self, message_content: str, sender_role: str, source: str) -> Dict[str, Any]:
        """Use Gemini to analyze message intent"""
        if not self.model:
            return self._fallback_intent_analysis(message_content)
        
        prompt = f"""You are Nion, an expert AI Technical Program Manager. Analyze the following project message with high precision.

Message: "{message_content}"
Sender Role: {sender_role}
Source: {source}

### Instructions
1. **Classify Intent**: Choose exactly one of the following:
   - `status_query`: Asking about progress, dates, or specific feature states.
   - `feasibility_query`: Asking if a feature/change is possible within constraints.
   - `decision_request`: Asking for a choice between options or a go/no-go.
   - `escalation`: High-stress communication, legal threats, or angry stakeholders.
   - `meeting_update`: Transcript, minutes, or summary of a discussion.
   - `general_request`: Generic communication not fitting the above.

2. **Assess Urgency**:
   - `high`: Legal threats, production downtime, angry client, or immediate blockers.
   - `medium`: Scope changes, tight deadlines, or important questions.
   - `low`: General info sharing or non-time-sensitive items.

3. **Identify Flags**:
   - `has_action_items`: Explicit requests to perform a task.
   - `has_risks`: Mentions of delays, scope creep, budget issues, or blockers.
   - `has_issues`: Mentions of bugs, failures, or broken processes.
   - `has_decisions`: Questions requiring a choice or approval.

Respond ONLY with valid JSON in this exact format:
{{
  "intent": "intent_type",
  "has_action_items": true/false,
  "has_risks": true/false,
  "has_issues": true/false,
  "has_decisions": true/false,
  "urgency": "low/medium/high",
  "reasoning": "Explain clearly why you classified the urgency and flags this way."
}}"""
        
        try:
            response = self.model.generate_content(prompt)
            # Extract JSON from response
            response_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            result = json.loads(response_text)
            return result
        except Exception as e:
            print(f"Warning: Gemini API error: {e}")
            print("Falling back to rule-based reasoning...")
            return self._fallback_intent_analysis(message_content, source)
    
    def _fallback_intent_analysis(self, content: str, source: str = "") -> Dict[str, Any]:
        """Fallback rule-based intent analysis when API is not available"""
        content_lower = content.lower()
        source_lower = source.lower() if source else ""
        
        # Determine intent (check meeting first before escalation keywords)
        if source_lower == "meeting" or "meeting" in content_lower or "transcript" in content_lower or "demo" in content_lower:
            intent = "meeting_update"
        elif "?" in content and ("status" in content_lower or "what" in content_lower):
            intent = "status_query"
        elif "?" in content and ("can we" in content_lower or "should we" in content_lower):
            intent = "feasibility_query"
        elif "decide" in content_lower or "prioritize" in content_lower:
            intent = "decision_request"
        elif "blocked" in content_lower or "urgent" in content_lower or "escalate" in content_lower or "threat" in content_lower:
            intent = "escalation"
        else:
            intent = "general_request"
        
        return {
            "intent": intent,
            "has_action_items": any(kw in content_lower for kw in ["add", "create", "implement", "fix"]),
            "has_risks": any(kw in content_lower for kw in ["risk", "concern", "timeline", "deadline"]),
            "has_issues": any(kw in content_lower for kw in ["blocked", "down", "bug", "issue", "problem"]),
            "has_decisions": any(kw in content_lower for kw in ["decide", "should", "prioritize", "choose"]),
            "urgency": "high" if intent == "escalation" else "medium" if "?" in content else "low",
            "reasoning": "Rule-based analysis (API not configured)"
        }
    
    def enhance_response(self, context: Dict[str, Any], message_content: str) -> str:
        """Use Gemini to generate more natural responses"""
        if not self.model:
            return None  # Use default response generation
        
        # Helper to format list items into strings
        def format_list(items):
            if not items:
                return "None"
            return "\n  - ".join([str(item) for item in items])

        # Prepare context strings
        knowledge_info = format_list(context.get('knowledge', []))
        action_items_info = format_list(context.get('action_items', []))
        risks_info = format_list(context.get('risks', []))
        decisions_info = format_list(context.get('decisions', []))
        
        prompt = f"""You are Nion, an advanced AI Program Manager. 
Generate a professional, structured, and gap-aware response using the following EXACT format:

Original Message: "{message_content}"

### Context Available
- **Project Info**: 
  {knowledge_info}
- **Action Items**: 
  {action_items_info}
- **Risks**: 
  {risks_info}
- **Decisions**: 
  {decisions_info}

### Response Format (REQUIRED STRUCTURE)
Generate your response in this exact format:

[Opening acknowledgment of the request]

WHAT I KNOW:
• [List specific project data: timeline, progress, capacity, team members, etc.]
• [Include all relevant information from project context]
• [Be specific with dates, percentages, and names]

WHAT I'VE LOGGED:
• [List action items with their details and flags]
• [List risks with likelihood and impact]
• [List decisions with status]
• [Be concrete about what has been tracked]

WHAT I NEED:
• [List specific missing information needed to answer fully]
• [Mention specific people who should provide input]
• [Be clear about why this information is needed]

[Closing statement explaining how the missing info will help]

### Guidelines
1. Keep the three sections clearly separated with the exact headers above
2. Use bullet points (•) for all items
3. Be specific with data (dates, percentages, names)
4. Make "WHAT I NEED" actionable and specific
5. Professional, concise tone

Response (plain text, no JSON):"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Warning: Gemini response generation error: {e}")
            return None  # Fall back to default
