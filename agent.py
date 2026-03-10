"""
BI Agent - Uses Groq LLM to interpret natural language queries and route to analytics
"""

import json
import re
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from typing import Optional

from analyzer import DataAnalyzer

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL   = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are a sharp senior business intelligence analyst. You help founders get fast, accurate answers from their Monday.com sales pipeline (Deals) and operations (Work Orders) data.

To answer a question you MUST first call a function by responding with ONLY a raw JSON object — no markdown, no backticks, no explanation. Just the JSON.

Format:
{"function": "<name>", "args": {}}

Available functions:
- pipeline_overview
- pipeline_by_sector        args: {"sector": "optional string"}
- quarterly_pipeline        args: {"quarter": 1-4, "year": 2025}
- won_lost_analysis
- top_deals                 args: {"n": 10, "sector": "optional"}
- work_order_overview
- work_order_by_sector
- operational_health
- sector_360                args: {"sector": "optional string"}
- data_quality_report

After you receive the function result (prefixed with FUNCTION_RESULT:), write a clear, founder-friendly analysis with specific numbers and insights. Never output raw JSON to the user."""


class BIAgent:
    def __init__(self, groq_api_key: str, analyzer: DataAnalyzer):
        self.api_key  = groq_api_key
        self.analyzer = analyzer
        self.conversation_history = []

    def reset_conversation(self):
        self.conversation_history = []

    def _llm(self, messages: list) -> str:
        resp = requests.post(
            GROQ_API_URL,
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            json={"model": GROQ_MODEL, "messages": messages, "temperature": 0.2, "max_tokens": 2048},
            timeout=60,
            verify=False,
        )
        if not resp.ok:
            raise ConnectionError(f"Groq {resp.status_code}: {resp.text[:300]}")
        return resp.json()["choices"][0]["message"]["content"].strip()

    def _extract_function_call(self, text: str) -> Optional[tuple]:
        """Try every possible way to find a JSON function call in the text."""
        # 1. Whole response is JSON
        try:
            obj = json.loads(text.strip())
            if "function" in obj:
                return obj["function"], obj.get("args", {})
        except Exception:
            pass

        # 2. JSON inside ```json ... ``` or ``` ... ```
        for m in re.finditer(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL):
            try:
                obj = json.loads(m.group(1))
                if "function" in obj:
                    return obj["function"], obj.get("args", {})
            except Exception:
                pass

        # 3. Any {...} block that contains "function"
        for m in re.finditer(r'\{[^{}]*"function"[^{}]*\}', text, re.DOTALL):
            try:
                obj = json.loads(m.group(0))
                if "function" in obj:
                    return obj["function"], obj.get("args", {})
            except Exception:
                pass

        # 4. Loose key-value extraction as last resort
        fn_match = re.search(r'"function"\s*:\s*"([^"]+)"', text)
        if fn_match:
            args = {}
            args_match = re.search(r'"args"\s*:\s*(\{[^}]*\})', text)
            if args_match:
                try:
                    args = json.loads(args_match.group(1))
                except Exception:
                    pass
            return fn_match.group(1), args

        return None

    def _call_function(self, function_name: str, args: dict) -> str:
        try:
            if function_name == "pipeline_overview":
                result = self.analyzer.pipeline_overview()
            elif function_name == "pipeline_by_sector":
                result = self.analyzer.pipeline_by_sector(args.get("sector"))
            elif function_name == "quarterly_pipeline":
                result = self.analyzer.quarterly_pipeline(args.get("quarter"), args.get("year"))
            elif function_name == "won_lost_analysis":
                result = self.analyzer.won_lost_analysis()
            elif function_name == "top_deals":
                result = self.analyzer.top_deals(n=args.get("n", 10), sector=args.get("sector"))
            elif function_name == "work_order_overview":
                result = self.analyzer.work_order_overview()
            elif function_name == "work_order_by_sector":
                result = self.analyzer.work_order_by_sector()
            elif function_name == "operational_health":
                result = self.analyzer.operational_health()
            elif function_name == "sector_360":
                result = self.analyzer.sector_360(args.get("sector"))
            elif function_name == "data_quality_report":
                result = self.analyzer.data_quality_report()
            else:
                result = {"error": f"Unknown function: {function_name}"}
            return json.dumps(result, indent=2, default=str)
        except Exception as e:
            return json.dumps({"error": str(e)})

    def chat(self, user_message: str) -> str:
        self.conversation_history.append({"role": "user", "content": user_message})

        for round_num in range(4):
            messages = [{"role": "system", "content": SYSTEM_PROMPT}] + self.conversation_history
            raw = self._llm(messages)

            func_call = self._extract_function_call(raw)

            if func_call:
                func_name, func_args = func_call
                func_result = self._call_function(func_name, func_args)

                # Add the function exchange to history
                self.conversation_history.append({"role": "assistant", "content": raw})
                self.conversation_history.append({
                    "role": "user",
                    "content": f"FUNCTION_RESULT: {func_result}\n\nNow write a clear, founder-friendly analysis based on this data. No JSON, no code — just insights."
                })
                # Loop to get final narrative response
                continue
            else:
                # No function call — this is the final answer
                self.conversation_history.append({"role": "assistant", "content": raw})
                return raw

        # Safety fallback if loop exhausts
        fallback = "I retrieved the data but had trouble formatting the response. Please try asking again."
        self.conversation_history.append({"role": "assistant", "content": fallback})
        return fallback

    def generate_leadership_brief(self) -> str:
        return self.chat(
            "Generate a comprehensive leadership update brief covering pipeline health, "
            "current quarter outlook, top deals, operational status, and key risks."
        )
