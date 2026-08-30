import sqlite3
import json
import os
from typing import Dict, Any, List, Optional

class PersonalMCPDaemon:
    def __init__(self, db_path: str = ":memory:", sandbox_root: str = "/tmp"):
        self.db_path = db_path
        self.sandbox_root = os.path.realpath(sandbox_root)
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._init_db()
        
    def _init_db(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS memos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task TEXT NOT NULL,
                completed BOOLEAN DEFAULT 0
            )
        """)
        self.conn.commit()
            
    def validate_path(self, relative_path: str) -> str:
        target = os.path.realpath(os.path.join(self.sandbox_root, relative_path))
        if os.path.commonpath([target, self.sandbox_root]) != self.sandbox_root:
            raise PermissionError(f"Path Traversal Blocked: '{relative_path}' escapes sandbox.")
        return target

    def handle_request(self, request_str: str) -> str:
        msg = json.loads(request_str.strip())
        method = msg.get("method")
        msg_id = msg.get("id")
        params = msg.get("params", {})
        
        if method == "initialize":
            return json.dumps({
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "serverInfo": {"name": "personal-mcp-daemon", "version": "1.0.0"},
                    "capabilities": {"tools": {}, "resources": {}, "prompts": {}}
                }
            })
            
        elif method == "tools/list":
            return json.dumps({
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "tools": [
                        {"name": "save_memo", "description": "Save developer memo", "inputSchema": {"type": "object"}},
                        {"name": "search_memos", "description": "Search memos by keyword", "inputSchema": {"type": "object"}},
                        {"name": "add_todo", "description": "Add pending task", "inputSchema": {"type": "object"}}
                    ]
                }
            })
            
        elif method == "tools/call":
            tool_name = params.get("name")
            args = params.get("arguments", {})
            
            cur = self.conn.cursor()
            if tool_name == "save_memo":
                cur.execute("INSERT INTO memos (title, content, tags) VALUES (?, ?, ?)", (args["title"], args["content"], args.get("tags", "")))
                self.conn.commit()
                return json.dumps({
                    "jsonrpc": "2.0", "id": msg_id,
                    "result": {"content": [{"type": "text", "text": f"Saved memo ID: {cur.lastrowid}"}], "isError": False}
                })
            elif tool_name == "search_memos":
                cur.execute("SELECT id, title, content FROM memos WHERE title LIKE ? OR content LIKE ?", (f"%{args['keyword']}%", f"%{args['keyword']}%"))
                rows = cur.fetchall()
                return json.dumps({
                    "jsonrpc": "2.0", "id": msg_id,
                    "result": {"content": [{"type": "text", "text": json.dumps(rows)}], "isError": False}
                })
            elif tool_name == "add_todo":
                cur.execute("INSERT INTO todos (task, completed) VALUES (?, 0)", (args["task"],))
                self.conn.commit()
                return json.dumps({
                    "jsonrpc": "2.0", "id": msg_id,
                    "result": {"content": [{"type": "text", "text": f"Added todo ID: {cur.lastrowid}"}], "isError": False}
                })
            return json.dumps({"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32601, "message": f"Tool '{tool_name}' not found."}})
            
        elif method == "resources/list":
            return json.dumps({
                "jsonrpc": "2.0", "id": msg_id,
                "result": {
                    "resources": [
                        {"uri": "memo://pending-todos", "name": "Active Todos", "mimeType": "text/plain"}
                    ]
                }
            })
            
        elif method == "resources/read":
            uri = params.get("uri")
            if uri == "memo://pending-todos":
                cur = self.conn.cursor()
                cur.execute("SELECT id, task FROM todos WHERE completed = 0")
                rows = cur.fetchall()
                text = "\n".join([f"- [{r[0]}] {r[1]}" for r in rows]) if rows else "No active todos."
                return json.dumps({
                    "jsonrpc": "2.0", "id": msg_id,
                    "result": {"contents": [{"uri": uri, "mimeType": "text/plain", "text": text}]}
                })
            return json.dumps({"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32602, "message": f"Resource '{uri}' not found."}})
            
        elif method == "prompts/list":
            return json.dumps({
                "jsonrpc": "2.0", "id": msg_id,
                "result": {
                    "prompts": [
                        {"name": "standup", "description": "Generate daily standup summary", "arguments": [{"name": "git_log", "required": True}]}
                    ]
                }
            })
            
        elif method == "prompts/get":
            name = params.get("name")
            if name == "standup":
                git_log = params.get("arguments", {}).get("git_log", "No recent commits.")
                cur = self.conn.cursor()
                cur.execute("SELECT task FROM todos WHERE completed = 0")
                todos = [r[0] for r in cur.fetchall()]
                prompt_text = f"Summarize standup.\nGit Log:\n{git_log}\nActive Todos:\n" + "\n".join(todos)
                return json.dumps({
                    "jsonrpc": "2.0", "id": msg_id,
                    "result": {
                        "description": "Daily standup template",
                        "messages": [{"role": "user", "content": {"type": "text", "text": prompt_text}}]
                    }
                })
            return json.dumps({"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32601, "message": f"Prompt '{name}' not found."}})
            
        return json.dumps({"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32601, "message": "Method not supported"}})

if __name__ == "__main__":
    daemon = PersonalMCPDaemon(":memory:")
    res = daemon.handle_request('{"jsonrpc": "2.0", "id": 1, "method": "initialize"}')
    print("Init response:", res)
