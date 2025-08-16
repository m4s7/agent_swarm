#!/usr/bin/env python3
"""
Multi-Agent Communication Protocol Implementation
"""

import json
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from enum import Enum

class MessageType(Enum):
    REQUEST = "request"
    RESPONSE = "response"
    STATUS = "status"
    ERROR = "error"
    HANDOFF = "handoff"

class AgentMessage:
    def __init__(self, 
                 from_agent: str, 
                 to_agent: str, 
                 message_type: MessageType,
                 payload: Dict[str, Any],
                 correlation_id: Optional[str] = None):
        self.timestamp = datetime.now().isoformat()
        self.from_agent = from_agent
        self.to_agent = to_agent
        self.message_type = message_type
        self.payload = payload
        self.correlation_id = correlation_id or self._generate_id()
        
    def _generate_id(self) -> str:
        import uuid
        return str(uuid.uuid4())
    
    def to_json(self) -> str:
        return json.dumps({
            "timestamp": self.timestamp,
            "from": self.from_agent,
            "to": self.to_agent,
            "type": self.message_type.value,
            "payload": self.payload,
            "correlation_id": self.correlation_id
        }, indent=2)
    
    def save_to_log(self):
        log_dir = Path(".claude/logs")
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / f"messages_{datetime.now().strftime('%Y%m%d')}.jsonl"
        with open(log_file, 'a') as f:
            f.write(self.to_json() + '\n')

class AgentOrchestrator:
    def __init__(self, config_file: str):
        with open(config_file, 'r') as f:
            self.config = json.load(f)
        self.active_agents = {}
        self.message_queue = asyncio.Queue()
        
    async def execute_stage(self, stage: Dict) -> Dict[str, Any]:
        """Execute a workflow stage"""
        stage_id = stage['stage_id']
        execution = stage.get('execution', 'sequential')
        
        print(f"[Orchestrator] Starting stage: {stage['name']}")
        
        if execution == 'parallel':
            results = await self._execute_parallel(stage['agents'])
        else:
            # Check if this stage has substages or agents
            if 'substages' in stage:
                results = await self._execute_sequential(stage['substages'])
            else:
                results = await self._execute_sequential(stage['agents'])
            
        return {
            'stage_id': stage_id,
            'status': 'completed',
            'results': results
        }
    
    async def _execute_parallel(self, agents: List) -> List[Dict]:
        """Execute agents in parallel"""
        tasks = []
        for agent_config in agents:
            if isinstance(agent_config, dict):
                task = self._run_agent(
                    agent_config['agent'],
                    agent_config.get('scope', ''),
                    agent_config.get('output', '')
                )
            else:
                task = self._run_agent(agent_config, '', '')
            tasks.append(task)
        
        return await asyncio.gather(*tasks)
    
    async def _execute_sequential(self, agents: List) -> List[Dict]:
        """Execute agents sequentially"""
        results = []
        for agent_config in agents:
            if isinstance(agent_config, dict):
                result = await self._run_agent(
                    agent_config.get('agent', agent_config.get('name', '')),
                    agent_config.get('scope', ''),
                    agent_config.get('outputs', [])
                )
            else:
                result = await self._run_agent(agent_config, '', '')
            results.append(result)
        return results
    
    async def _run_agent(self, agent_name: str, scope: str, outputs: Any) -> Dict:
        """Simulate running an agent"""
        print(f"  [Agent: {agent_name}] Starting with scope: {scope}")
        
        # Log the agent activation
        msg = AgentMessage(
            from_agent="orchestrator",
            to_agent=agent_name,
            message_type=MessageType.REQUEST,
            payload={"scope": scope, "outputs": outputs}
        )
        msg.save_to_log()
        
        # Simulate agent work
        await asyncio.sleep(1)
        
        print(f"  [Agent: {agent_name}] Completed")
        
        return {
            "agent": agent_name,
            "status": "success",
            "outputs": outputs
        }
    
    async def run_workflow(self):
        """Execute the entire workflow"""
        print(f"Starting workflow: {self.config['name']}")
        
        for stage in self.config['stages']:
            result = await self.execute_stage(stage)
            print(f"Stage {result['stage_id']} completed\n")
        
        print("Workflow completed successfully!")

# Main execution
if __name__ == "__main__":
    orchestrator = AgentOrchestrator(".claude/workflows/team-orchestration.json")
    asyncio.run(orchestrator.run_workflow())