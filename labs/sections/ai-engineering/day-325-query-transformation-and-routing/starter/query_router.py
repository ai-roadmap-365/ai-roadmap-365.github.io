from typing import Dict, Any, List, Optional

class QueryTransformRouter:
    def __init__(self):
        self.routes = {
            "sql": ["sales", "revenue", "count", "average", "total", "users", "metrics"],
            "vector_rag": ["how", "configure", "troubleshoot", "guide", "policy", "documentation"],
            "direct_llm": ["hello", "hi", "who are you", "tell me a joke", "thanks"]
        }
        
    def classify_and_route(self, query: str) -> str:
        q_lower = query.lower().strip()
        
        for kw in self.routes["direct_llm"]:
            if q_lower.startswith(kw) or q_lower == kw:
                return "DIRECT_LLM_BYPASS"
                
        for kw in self.routes["sql"]:
            if kw in q_lower:
                return "TEXT2SQL_DATABASE"
                
        return "VECTOR_RAG"

    def generate_hyde_document(self, query: str) -> str:
        return f"Technical Documentation: Regarding '{query}', the standard procedure involves verifying configuration settings, ensuring security permissions, and applying system updates."

    def expand_query(self, query: str) -> List[str]:
        return [
            query,
            f"how to resolve {query}",
            f"{query} technical documentation and troubleshooting steps",
            f"best practices for {query}"
        ]

if __name__ == "__main__":
    router = QueryTransformRouter()
    print("Route:", router.classify_and_route("Total sales in Q3"))
    print("HyDE:", router.generate_hyde_document("Fix 502 Bad Gateway"))
    print("Expanded:", router.expand_query("Postgres vacuum"))
