import hashlib
import json
import time
from typing import Dict, Any, Callable, Optional, List, Tuple

class ToolDefinition:
    def __init__(self, name: str, description: str, schema: Dict[str, Any], func: Callable, is_mutating: bool = False):
        self.name = name
        self.description = description
        self.schema = schema
        self.func = func
        self.is_mutating = is_mutating

class ProductionToolRegistry:
    def __init__(self, cache_ttl_seconds: int = 300):
        self.tools: Dict[str, ToolDefinition] = {}
        self.idempotency_cache: Dict[str, Dict[str, Any]] = {}
        self.cache_ttl = cache_ttl_seconds
        
    def register(self, tool: ToolDefinition):
        self.tools[tool.name] = tool
        
    def get_schemas(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": t.name,
                "description": t.description,
                "parameters": t.schema
            }
            for t in self.tools.values()
        ]
        
    def validate_and_coerce(self, tool: ToolDefinition, args: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], str]:
        schema = tool.schema
        properties = schema.get("properties", {})
        required = schema.get("required", [])
        
        # Check required fields
        for req in required:
            if req not in args:
                return False, {}, f"Missing required parameter: '{req}'"
                
        coerced = {}
        for k, v in args.items():
            if k not in properties:
                continue # strip unknown parameters
            target_type = properties[k].get("type")
            try:
                if target_type == "integer":
                    coerced[k] = int(v)
                elif target_type == "number":
                    coerced[k] = float(v)
                elif target_type == "boolean":
                    if isinstance(v, str):
                        coerced[k] = v.lower() in ("true", "1", "yes")
                    else:
                        coerced[k] = bool(v)
                elif target_type == "string":
                    coerced[k] = str(v)
                else:
                    coerced[k] = v
            except (ValueError, TypeError) as err:
                return False, {}, f"Type coercion failed for parameter '{k}': expected {target_type}, got {type(v).__name__}"
                
        return True, coerced, "OK"
        
    def execute(self, tool_name: str, raw_args: Dict[str, Any], idempotency_key: Optional[str] = None) -> Dict[str, Any]:
        if tool_name not in self.tools:
            return {"success": False, "error": f"Tool '{tool_name}' not registered."}
            
        tool = self.tools[tool_name]
        valid, clean_args, err_msg = self.validate_and_coerce(tool, raw_args)
        if not valid:
            return {"success": False, "error": err_msg}
            
        # Idempotency Check for Mutating Actions
        if tool.is_mutating:
            if not idempotency_key:
                canon_str = f"{tool_name}:{json.dumps(clean_args, sort_keys=True)}"
                idempotency_key = hashlib.sha256(canon_str.encode()).hexdigest()
                
            now = time.time()
            if idempotency_key in self.idempotency_cache:
                cached = self.idempotency_cache[idempotency_key]
                if now - cached["timestamp"] < self.cache_ttl:
                    return {"success": True, "result": cached["result"], "cached": True}
                    
        try:
            res = tool.func(**clean_args)
            if tool.is_mutating and idempotency_key:
                self.idempotency_cache[idempotency_key] = {"result": res, "timestamp": time.time()}
            return {"success": True, "result": res, "cached": False}
        except Exception as e:
            return {"success": False, "error": f"Execution error in {tool_name}: {str(e)}"}
