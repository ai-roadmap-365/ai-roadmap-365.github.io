import sqlite3
from typing import Dict, Any, List

class PersonalMCPServer:
    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
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
            
    def save_memo(self, title: str, content: str, tags: str = "") -> str:
        cur = self.conn.cursor()
        cur.execute("INSERT INTO memos (title, content, tags) VALUES (?, ?, ?)", (title, content, tags))
        self.conn.commit()
        return f"Saved memo '{title}' with ID {cur.lastrowid}."
            
    def search_memos(self, keyword: str) -> List[Dict[str, Any]]:
        self.conn.row_factory = sqlite3.Row
        cur = self.conn.cursor()
        cur.execute("SELECT id, title, content, tags FROM memos WHERE title LIKE ? OR content LIKE ?", (f"%{keyword}%", f"%{keyword}%"))
        rows = cur.fetchall()
        return [dict(r) for r in rows]
            
    def add_todo(self, task: str) -> str:
        cur = self.conn.cursor()
        cur.execute("INSERT INTO todos (task, completed) VALUES (?, 0)", (task,))
        self.conn.commit()
        return f"Added todo '{task}' with ID {cur.lastrowid}."
            
    def get_pending_todos_resource(self) -> str:
        cur = self.conn.cursor()
        cur.execute("SELECT id, task FROM todos WHERE completed = 0")
        rows = cur.fetchall()
        if not rows:
            return "No pending todos."
        return "\n".join([f"- [{r[0]}] {r[1]}" for r in rows])
            
    def generate_standup_prompt(self, recent_commits: str) -> List[Dict[str, Any]]:
        pending = self.get_pending_todos_resource()
        prompt_text = (
            "Please generate a concise 3-part daily standup report using the following data:\n\n"
            f"### Recent Git Commits:\n{recent_commits}\n\n"
            f"### Active Pending Todos:\n{pending}\n\n"
            "Format with sections: **1. Completed Yesterday**, **2. Planned Today**, **3. Blockers**."
        )
        return [{"role": "user", "content": {"type": "text", "text": prompt_text}}]

if __name__ == "__main__":
    server = PersonalMCPServer(":memory:")
    print(server.save_memo("Test Memo", "Discussing MCP architecture", "mcp,architecture"))
    print(server.add_todo("Write test suite for personal server"))
    print("Search:", server.search_memos("architecture"))
    print("Resource:", server.get_pending_todos_resource())
    print("Prompt:", server.generate_standup_prompt("feat: initial commit"))
