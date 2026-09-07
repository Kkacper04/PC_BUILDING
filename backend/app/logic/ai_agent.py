import os
import json
import re
import asyncio
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
from sqlalchemy.orm import Session
from sqlalchemy import select, String

from app.models.components import (
    CPU, GPU, Motherboard, RAM, PSU, Case, Storage, CPUCooler
)

AI_BASE_URL = os.getenv("AI_BASE_URL", "http://host.docker.internal:11434/v1")
AI_MODEL_NAME = os.getenv("AI_MODEL_NAME", "llama3.1")

client = AsyncOpenAI(
    base_url=AI_BASE_URL,
    api_key="local-dev-key"
)

SYSTEM_PROMPT = """You are an elite, highly professional PC Hardware Consultant. Your goal is to design optimal, custom PC builds tailored exactly to the user's budget and specific use-cases (e.g., gaming, video editing, programming).

CORE DIRECTIVES:
1. EXCLUSIVE DATABASE USAGE: You MUST use the `get_components_by_category` tool to find and select real parts from our database. NEVER invent, guess, or hallucinate component names, prices, or IDs. The IDs you put in the final JSON MUST EXACTLY MATCH the integer IDs returned by the tool.
2. STRICT COMPATIBILITY: Ensure flawless hardware compatibility. Check that the CPU socket matches the motherboard, the RAM generation (DDR4/DDR5) is supported, and the PSU has enough wattage for the chosen CPU + GPU combo.
3. PROFESSIONAL COMMUNICATION: Communicate with the user exclusively in fluent, highly professional English. Use proper markdown formatting (bolding, lists) to make your response readable and elegant. DO NOT use any emojis (like 🖥️, 🚀, etc.). Keep the tone serious and expert.
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

def execute_get_components(
    db: Session, 
    category: str, 
    max_price: Optional[float] = None,
    socket: Optional[str] = None,
    ddr_generation: Optional[str] = None,
    min_wattage: Optional[int] = None,
    min_capacity_gb: Optional[int] = None
) -> str:
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
    if max_price is not None:
        try:
            max_price = float(max_price)
            stmt = stmt.where(model.price <= max_price)
        except (ValueError, TypeError):
            pass

    if socket and hasattr(model, 'socket'):
        stmt = stmt.where(model.socket.cast(String).ilike(f"%{socket}%"))
    if ddr_generation and hasattr(model, 'ddr_generation'):
        stmt = stmt.where(model.ddr_generation.cast(String).ilike(f"%{ddr_generation}%"))
    if min_wattage and hasattr(model, 'wattage'):
        stmt = stmt.where(model.wattage >= int(min_wattage))
    if min_capacity_gb and hasattr(model, 'total_capacity_gb'):
        stmt = stmt.where(model.total_capacity_gb >= int(min_capacity_gb))
    if min_capacity_gb and hasattr(model, 'capacity_gb'):
        stmt = stmt.where(model.capacity_gb >= int(min_capacity_gb))

    stmt = stmt.order_by(model.price.asc()).limit(50)
    
    results = db.execute(stmt).scalars().all()
    
    if not results:
        return "No components found matching your criteria."
        
    lines = []
    for r in results:
        price = float(r.price) if r.price else 0
        details = []
        if category == "cpu":
            details.append(f"Socket: {r.socket.value if hasattr(r.socket, 'value') else r.socket}")
            details.append(f"TDP: {r.tdp}W")
        elif category == "gpu":
            details.append(f"VRAM: {r.vram_gb}GB")
            details.append(f"TDP: {r.tdp}W")
            details.append(f"Length: {r.length_mm}mm")
        elif category == "motherboard":
            details.append(f"Socket: {r.socket.value if hasattr(r.socket, 'value') else r.socket}")
            details.append(f"RAM: {r.ddr_generation.value if hasattr(r.ddr_generation, 'value') else r.ddr_generation}")
            details.append(f"Form: {r.form_factor.value if hasattr(r.form_factor, 'value') else r.form_factor}")
        elif category == "ram":
            details.append(f"Type: {r.ddr_generation.value if hasattr(r.ddr_generation, 'value') else r.ddr_generation}")
            details.append(f"Cap: {r.total_capacity_gb}GB")
            details.append(f"Speed: {r.speed_mhz}MHz")
        elif category == "psu":
            details.append(f"Power: {r.wattage}W")
            details.append(f"Eff: {r.efficiency_rating.value if hasattr(r.efficiency_rating, 'value') else r.efficiency_rating}")
        elif category == "case":
            details.append(f"Max GPU: {r.max_gpu_length_mm}mm")
        elif category == "cooler":
            details.append(f"Max TDP: {r.max_tdp}W")
        elif category == "storage":
            details.append(f"Cap: {r.capacity_gb}GB")
            
        detail_str = " | ".join(details)
        lines.append(f"[ID: {r.id}] {r.name} - {price} PLN - {detail_str}")
        
    return "\n".join(lines)

TOOLS: List[Any] = [
    {
        "type": "function",
        "function": {
            "name": "get_components_by_category",
            "description": "Get a list of PC components from the database by category. Use optional filters to find compatible parts (e.g. searching for AM5 motherboards after picking an AM5 CPU).",
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
                    },
                    "socket": {
                        "type": "string",
                        "description": "Optional CPU/Motherboard socket (e.g. 'AM5', 'LGA1700')"
                    },
                    "ddr_generation": {
                        "type": "string",
                        "description": "Optional RAM generation (e.g. 'DDR4', 'DDR5')"
                    },
                    "min_wattage": {
                        "type": "number",
                        "description": "Optional minimum PSU wattage (e.g. 750, 850)"
                    },
                    "min_capacity_gb": {
                        "type": "number",
                        "description": "Optional minimum capacity in GB for RAM or Storage (e.g. 32, 2000)"
                    }
                },
                "required": ["category"]
            }
        }
    }
]

MAX_TOOL_ITERATIONS = 15

async def process_chat(db: Session, messages: List[Dict[str, str]]) -> Dict[str, Any]:
    api_messages: List[Any] = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in messages:
        api_messages.append({"role": msg["role"], "content": msg["content"]})
        
    try:
        response = await client.chat.completions.create(
            model=AI_MODEL_NAME,
            messages=api_messages,
            tools=TOOLS,
            temperature=0.7,
            timeout=600.0,
        )
    except Exception as e:
        return {
            "message": f"AI service error during processing: {str(e)}",
            "suggested_build": None
        }
    
    if not response.choices:
        return {"message": "AI returned an empty response. Please try again.", "suggested_build": None}
    
    response_message = response.choices[0].message
    
    iteration = 0
    while response_message.tool_calls and iteration < MAX_TOOL_ITERATIONS:
        iteration += 1
        
        # Manually construct to avoid passing reasoning_content or other non-standard fields back
        assistant_msg = {
            "role": "assistant",
            "content": response_message.content or "",
            "tool_calls": [
                {
                    "id": getattr(t, "id", ""),
                    "type": "function",
                    "function": {
                        "name": getattr(getattr(t, "function", None), "name", ""),
                        "arguments": getattr(getattr(t, "function", None), "arguments", "{}")
                    }
                } for t in response_message.tool_calls
            ]
        }
        api_messages.append(assistant_msg)
        
        for tool_call in response_message.tool_calls:
            func = getattr(tool_call, "function", None)
            if not func:
                api_messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps({"error": "Unknown function"})
                })
                continue
                
            if func.name == "get_components_by_category":
                try:
                    args = json.loads(func.arguments)
                    cat = args.get("category")
                    max_p = args.get("max_price")
                    socket = args.get("socket")
                    ddr_gen = args.get("ddr_generation")
                    min_w = args.get("min_wattage")
                    min_cap = args.get("min_capacity_gb")
                    
                    tool_result = await asyncio.to_thread(
                        execute_get_components, db, cat, max_p, socket, ddr_gen, min_w, min_cap
                    )
                except Exception as e:
                    tool_result = json.dumps({"error": str(e)})
                    
                api_messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": func.name,
                    "content": tool_result
                })
            else:
                api_messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps({"error": f"Unknown tool: {func.name}"})
                })
                
        try:
            response = await client.chat.completions.create(
                model=AI_MODEL_NAME,
                messages=api_messages,
                tools=TOOLS,
                temperature=0.7,
                timeout=600.0,
            )
        except Exception as e:
            return {
                "message": f"AI service error during tool processing: {str(e)}",
                "suggested_build": None
            }
            
        if not response.choices:
            break
            
        response_message = response.choices[0].message

    final_content = response_message.content or ""
    
    suggested_build = None
    json_match = re.search(r'```json\s*(\{.*?\})\s*```', final_content, re.DOTALL)
    if not json_match:
        json_match = re.search(r'(\{[^{}]*"suggested_build"[^{}]*\{[^{}]*\}[^{}]*\})', final_content, re.DOTALL)
    if json_match:
        try:
            parsed = json.loads(json_match.group(1))
            if "suggested_build" in parsed:
                suggested_build = parsed["suggested_build"]
            final_content = re.sub(r'```json\s*(\{.*?\})\s*```', '', final_content, flags=re.DOTALL).strip()
        except Exception:
            pass
            
    return {
        "message": final_content,
        "suggested_build": suggested_build
    }
