import os
import json
import re
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.components import (
    CPU, GPU, Motherboard, RAM, PSU, Case, Storage, CPUCooler
)

AI_BASE_URL = os.getenv("AI_BASE_URL", "http://host.docker.internal:11434/v1")
AI_MODEL_NAME = os.getenv("AI_MODEL_NAME", "llama3.1")

client = AsyncOpenAI(
    base_url=AI_BASE_URL,
    api_key=" local-dev-key" #sth random 
)

SYSTEM_PROMPT = """You are an elite, highly professional PC Hardware Consultant. Your goal is to design optimal, custom PC builds tailored exactly to the user's budget and specific use-cases (e.g., gaming, video editing, programming).

CORE DIRECTIVES:
1. EXCLUSIVE DATABASE USAGE: You MUST use the `get_components_by_category` tool to find and select real parts from our database. NEVER invent, guess, or hallucinate component names, prices, or IDs.
2. STRICT COMPATIBILITY: Ensure flawless hardware compatibility. Check that the CPU socket matches the motherboard, the RAM generation (DDR4/DDR5) is supported, and the PSU has enough wattage for the chosen CPU + GPU combo.
3. PROFESSIONAL COMMUNICATION: Communicate with the user exclusively in fluent, highly professional English. Use proper markdown formatting (bolding, lists) to make your response readable and elegant. 
4. JUSTIFICATION: Briefly but technically explain WHY you chose these specific parts and how they maximize the performance-to-price ratio for the user's budget.

Available component categories for your tool: cpu, gpu, motherboard, ram, psu, case, cooler, storage.

OUTPUT FORMAT:
First, write your professional response to the user. Then, at the very end of your message, you MUST append a JSON block containing the exact database IDs of the selected components. Format this JSON strictly as follows:

```json
{
  "suggested_build": {
    "cpu": 12,
    "gpu": 45,
    "motherboard": 3,
    "ram": 16,
    "psu": 22,
    "case": 1,
    "cooler": 5,
    "storage": 9
  }
}
```
"""

def execute_get_components(db: Session, category: str, max_price: Optional[float] = None) -> str:
    category = category.lower()
    model_map = {
        "cpu": CPU,
        "gpu": GPU,
        "motherboard": Motherboard,
        "ram": RAM,
        "psu": PSU,
        "case": Case,
        "cooler": CPUCooler,
        "storage": Storage
    }
    
    if category not in model_map:
        return json.dumps({"error": f"Invalid category: {category}"})
        
    model = model_map[category]
    stmt = select(model)
    if max_price:
        stmt = stmt.where(model.price <= max_price)
    stmt = stmt.order_by(model.price.desc()).limit(15)
    
    results = db.execute(stmt).scalars().all()
    
    components = []
    for r in results:
        comp = {
            "id": r.id,
            "name": r.name,
            "price": float(r.price)
        }
        if category == "cpu":
            comp["socket"] = r.socket
            comp["tdp"] = r.tdp
        elif category == "gpu":
            comp["vram_gb"] = r.vram_gb
        elif category == "motherboard":
            comp["socket"] = r.socket
            comp["form_factor"] = r.form_factor
            
        components.append(comp)
        
    return json.dumps(components)

TOOLS: List[Any] = [
    {
        "type": "function",
        "function": {
            "name": "get_components_by_category",
            "description": "Get a list of PC components from the database by category.",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Must be one of: cpu, gpu, motherboard, ram, psu, case, cooler, storage"
                    },
                    "max_price": {
                        "type": "number",
                        "description": "The maximum price in PLN"
                    }
                },
                "required": ["category"]
            }
        }
    }
]

async def process_chat(db: Session, messages: List[Dict[str, str]]) -> Dict[str, Any]:
    # Prepare messages
    api_messages: List[Any] = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in messages:
        api_messages.append({"role": msg["role"], "content": msg["content"]})
        
    # Call LLM
    response = await client.chat.completions.create(
        model=AI_MODEL_NAME,
        messages=api_messages,
        tools=TOOLS,
        temperature=0.7
    )
    
    response_message = response.choices[0].message
    
    # Handle tool calls if any
    while response_message.tool_calls:
        api_messages.append(response_message.model_dump(exclude_none=True))
        
        for tool_call in response_message.tool_calls:
            # Use getattr or type ignore to bypass Pylance union issues
            func = getattr(tool_call, "function", None)
            if not func:
                continue
                
            if func.name == "get_components_by_category":
                try:
                    args = json.loads(func.arguments)
                    cat = args.get("category")
                    max_p = args.get("max_price")
                    tool_result = execute_get_components(db, cat, max_p)
                except Exception as e:
                    tool_result = json.dumps({"error": str(e)})
                    
                api_messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": func.name,
                    "content": tool_result
                })
                
        # Call LLM again with tool results
        response = await client.chat.completions.create(
            model=AI_MODEL_NAME,
            messages=api_messages,
            tools=TOOLS,
            temperature=0.7
        )
        response_message = response.choices[0].message

    final_content = response_message.content or ""
    
    # Extract JSON block if present
    suggested_build = None
    json_match = re.search(r'```json\s*(\{.*?\})\s*```', final_content, re.DOTALL)
    if json_match:
        try:
            parsed = json.loads(json_match.group(1))
            if "suggested_build" in parsed:
                suggested_build = parsed["suggested_build"]
            # Clean up the message by removing the JSON block so the user doesn't see it
            final_content = re.sub(r'```json\s*(\{.*?\})\s*```', '', final_content, flags=re.DOTALL).strip()
        except Exception:
            pass
            
    return {
        "message": final_content,
        "suggested_build": suggested_build
    }
