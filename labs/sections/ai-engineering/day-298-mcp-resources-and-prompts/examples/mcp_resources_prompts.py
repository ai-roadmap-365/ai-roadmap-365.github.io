from typing import Dict, Any, List, Optional, Callable

class MCPResourcePromptEngine:
    def __init__(self, server_name: str = "doc-server"):
        self.server_name = server_name
        self.resources: Dict[str, Dict[str, Any]] = {}
        self.prompts: Dict[str, Dict[str, Any]] = {}
        
    def register_resource(self, uri: str, name: str, mime_type: str, reader_fn: Callable[[], str]):
        self.resources[uri] = {
            "uri": uri,
            "name": name,
            "mimeType": mime_type,
            "reader": reader_fn
        }
        
    def register_prompt(self, name: str, description: str, arguments: List[Dict[str, Any]], template_fn: Callable[..., List[Dict[str, Any]]]):
        self.prompts[name] = {
            "name": name,
            "description": description,
            "arguments": arguments,
            "template": template_fn
        }
        
    def handle_request(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        params = params or {}
        
        if method == "resources/list":
            res_list = [
                {"uri": r["uri"], "name": r["name"], "mimeType": r["mimeType"]}
                for r in self.resources.values()
            ]
            return {"resources": res_list}
            
        elif method == "resources/read":
            uri = params.get("uri")
            if uri not in self.resources:
                raise ValueError(f"Resource URI not found: {uri}")
            r = self.resources[uri]
            text_content = r["reader"]()
            return {
                "contents": [
                    {"uri": uri, "mimeType": r["mimeType"], "text": text_content}
                ]
            }
            
        elif method == "prompts/list":
            p_list = [
                {"name": p["name"], "description": p["description"], "arguments": p["arguments"]}
                for p in self.prompts.values()
            ]
            return {"prompts": p_list}
            
        elif method == "prompts/get":
            name = params.get("name")
            if name not in self.prompts:
                raise ValueError(f"Prompt not found: {name}")
            p = self.prompts[name]
            args = params.get("arguments", {})
            messages = p["template"](**args)
            return {
                "description": p["description"],
                "messages": messages
            }
            
        raise ValueError(f"Unsupported method: {method}")

if __name__ == "__main__":
    engine = MCPResourcePromptEngine("doc-server")
    engine.register_resource("memo://active", "Active Note", "text/plain", lambda: "Deploying model v2")
    engine.register_prompt(
        "summarize",
        "Summarize a document",
        [{"name": "doc", "required": True}],
        lambda doc: [{"role": "user", "content": {"type": "text", "text": f"Summarize: {doc}"}}]
    )
    print("Resources:", engine.handle_request("resources/list"))
    print("Prompts:", engine.handle_request("prompts/list"))
