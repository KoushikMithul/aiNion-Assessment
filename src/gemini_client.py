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
        
        prompt = f"""Analyze this message and identify the primary intent.

Message: "{message_content}"
Sender Role: {sender_role}
Source: {source}

Classify the intent as one of:
- status_query: Asking about current status or progress
- feasibility_query: Asking if something can be done
- decision_request: Requesting a decision or recommendation
- escalation: Urgent issue or escalation
- meeting_update: Meeting transcript or update
- general_request: General communication

Also identify:
- Has action items: yes/no
- Has risks: yes/no
- Has issues: yes/no
- Has decisions: yes/no
- Urgency level: low/medium/high

Respond ONLY with valid JSON in this exact format:
{{
  "intent": "intent_type",
  "has_action_items": true/false,
  "has_risks": true/false,
  "has_issues": true/false,
  "has_decisions": true/false,
  "urgency": "low/medium/high",
  "reasoning": "brief explanation"
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
            return self._fallback_intent_analysis(message_content)
    
    def _fallback_intent_analysis(self, content: str) -> Dict[str, Any]:
        """Fallback rule-based intent analysis when API is not available"""
        content_lower = content.lower()
        
        # Determine intent
        if "?" in content and ("status" in content_lower or "what" in content_lower):
            intent = "status_query"
        elif "?" in content and ("can we" in content_lower or "should we" in content_lower):
            intent = "feasibility_query"
        elif "decide" in content_lower or "prioritize" in content_lower:
            intent = "decision_request"
        elif "blocked" in content_lower or "urgent" in content_lower or "escalate" in content_lower or "threat" in content_lower:
            intent = "escalation"
        elif "meeting" in content_lower or "transcript" in content_lower or "demo" in content_lower:
            intent = "meeting_update"
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
        
        prompt = f"""You are Nion, an AI Program Manager. Generate a professional, gap-aware response.

Original Message: "{message_content}"

Context Available:
- Action Items: {len(context.get('action_items', []))} logged
- Risks: {len(context.get('risks', []))} identified
- Decisions: {len(context.get('decisions', []))} pending
- Project Info: {context.get('knowledge', ['Limited context'])[0] if context.get('knowledge') else 'Unknown'}

Generate a response that:
1. Acknowledges what you know
2. States what you've logged/tracked
3. Clearly identifies what information is missing
4. Is professional and concise

Response (plain text, no JSON):"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Warning: Gemini response generation error: {e}")
            return None  # Fall back to default
