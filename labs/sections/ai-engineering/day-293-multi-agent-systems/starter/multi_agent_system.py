from typing import Dict, Any, List, Optional
import time

class AgentMessage:
    def __init__(self, sender: str, recipient: str, content: str, msg_type: str):
        self.sender = sender
        self.recipient = recipient
        self.content = content
        self.msg_type = msg_type
        self.timestamp = time.time()

class MessageBus:
    def __init__(self):
        self.history: List[AgentMessage] = []
        
    def send(self, msg: AgentMessage):
        self.history.append(msg)
        
    def get_messages_for(self, recipient: str) -> List[AgentMessage]:
        return [m for m in self.history if m.recipient in (recipient, "BROADCAST")]

class MultiAgentSupervisorSystem:
    def __init__(self, max_rounds: int = 5):
        self.bus = MessageBus()
        self.max_rounds = max_rounds
        
    def _researcher_turn(self, task: str) -> str:
        if "revenue" in task.lower():
            return "Q3 Revenue reached $12.4 Billion (+14% YoY)."
        return "Researched records: data verified."
        
    def _critic_turn(self, draft: str) -> str:
        if "12.4 Billion" in draft:
            return "PASS: Facts are verified and grounded."
        return "REVISE: Missing specific revenue numbers."
        
    def _supervisor_turn(self, goal: str, round_num: int) -> Dict[str, Any]:
        if round_num == 1:
            self.bus.send(AgentMessage("supervisor", "researcher", f"Find financial data for: {goal}", "TASK_DISPATCH"))
            return {"action": "DELEGATE", "target": "researcher"}
            
        elif round_num == 2:
            res_msgs = self.bus.get_messages_for("supervisor")
            latest_res = res_msgs[-1].content if res_msgs else ""
            self.bus.send(AgentMessage("supervisor", "critic", latest_res, "AUDIT_REQUEST"))
            return {"action": "DELEGATE", "target": "critic"}
            
        elif round_num == 3:
            critic_msgs = [m for m in self.bus.history if m.sender == "critic"]
            critique = critic_msgs[-1].content if critic_msgs else ""
            
            if "PASS" in critique:
                final_text = "Executive Summary: Q3 Revenue reached $12.4 Billion (+14% YoY) with 100% verified compliance."
                self.bus.send(AgentMessage("supervisor", "USER", final_text, "FINAL_ANSWER"))
                return {"action": "COMPLETE", "final_answer": final_text}
            else:
                return {"action": "RETRY", "reason": critique}
                
        return {"action": "COMPLETE", "final_answer": "Task finalized."}
        
    def run(self, goal: str) -> Dict[str, Any]:
        for r in range(1, self.max_rounds + 1):
            decision = self._supervisor_turn(goal, r)
            if decision["action"] == "DELEGATE":
                target = decision["target"]
                if target == "researcher":
                    msgs = self.bus.get_messages_for("researcher")
                    res = self._researcher_turn(msgs[-1].content)
                    self.bus.send(AgentMessage("researcher", "supervisor", res, "TASK_RESULT"))
                elif target == "critic":
                    msgs = [m for m in self.bus.history if m.recipient == "critic"]
                    crit = self._critic_turn(msgs[-1].content)
                    self.bus.send(AgentMessage("critic", "supervisor", crit, "AUDIT_RESULT"))
            elif decision["action"] == "COMPLETE":
                return {
                    "status": "SUCCESS",
                    "rounds": r,
                    "final_answer": decision["final_answer"],
                    "message_count": len(self.bus.history)
                }
        return {"status": "MAX_ROUNDS_EXCEEDED", "rounds": self.max_rounds}
