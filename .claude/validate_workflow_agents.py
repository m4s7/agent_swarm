#!/usr/bin/env python3
"""
Validation script to ensure all 32 agents are referenced in team-orchestration.json
"""

import json
from pathlib import Path

def validate_workflow_coverage():
    """Validate that all agents are covered in the workflow"""
    
    # Load the workflow configuration
    workflow_path = Path(".claude/workflows/team-orchestration.json")
    with open(workflow_path) as f:
        workflow = json.load(f)
    
    # Extract all agent references from the workflow
    workflow_agents = set()
    
    # Get agents from stages
    for stage in workflow["stages"]:
        if "agents" in stage:
            for agent_config in stage["agents"]:
                if isinstance(agent_config, str):
                    workflow_agents.add(agent_config)
                elif isinstance(agent_config, dict) and "agent" in agent_config:
                    workflow_agents.add(agent_config["agent"])
    
    # Get agents from registry
    registry_agents = set()
    for category, agents in workflow["agent_registry"].items():
        registry_agents.update(agents)
    
    # Get agents from collaboration patterns
    collab_agents = set()
    for team, agents in workflow["collaboration_patterns"].items():
        collab_agents.update(agents)
    
    # All expected agents from the agent registry
    expected_agents = {
        # Core Development (5)
        "api-designer", "frontend-developer", "nextjs-developer", 
        "websocket-engineer", "python-pro",
        
        # Language Specialists (3)
        "typescript-pro", "rust-engineer",
        # python-pro already counted
        
        # Infrastructure (1)
        "deployment-engineer",
        
        # Quality & Security (5)
        "architect-reviewer", "code-reviewer", "debugger", 
        "qa-expert", "test-automator",
        
        # Data & AI (5)
        "ai-engineer", "data-analyst", "data-engineer", 
        "data-scientist", "postgres-pro",
        
        # Finance & Trading (4)
        "fintech-engineer", "futures-trading-strategist", 
        "futures-tick-data-specialist", "quant-analyst",
        
        # Developer Experience (2)
        "refactoring-specialist", "tooling-engineer",
        
        # Business & Product (3)
        "product-manager", "prd-writer", "ux-researcher",
        
        # Research & Analysis (3)
        "data-researcher", "research-analyst", "search-specialist",
        
        # Orchestration (2)
        "multi-agent-coordinator", "agent-organizer"
    }
    
    print("🔍 WORKFLOW AGENT COVERAGE VALIDATION")
    print("=" * 50)
    
    print(f"\n📊 Summary:")
    print(f"  Expected agents: {len(expected_agents)}")
    print(f"  Workflow stages agents: {len(workflow_agents)}")
    print(f"  Registry agents: {len(registry_agents)}")
    print(f"  Collaboration agents: {len(collab_agents)}")
    
    # Check coverage
    missing_from_stages = expected_agents - workflow_agents
    missing_from_registry = expected_agents - registry_agents
    missing_from_collab = expected_agents - collab_agents
    
    print(f"\n✅ Coverage Analysis:")
    print(f"  Stages coverage: {len(workflow_agents)}/{len(expected_agents)} agents")
    print(f"  Registry coverage: {len(registry_agents)}/{len(expected_agents)} agents")
    print(f"  Collaboration coverage: {len(collab_agents)}/{len(expected_agents)} agents")
    
    if missing_from_stages:
        print(f"\n⚠️  Missing from workflow stages: {sorted(missing_from_stages)}")
    else:
        print(f"\n✅ All agents referenced in workflow stages!")
    
    if missing_from_registry:
        print(f"\n⚠️  Missing from agent registry: {sorted(missing_from_registry)}")
    else:
        print(f"\n✅ All agents in agent registry!")
    
    if missing_from_collab:
        print(f"\n⚠️  Missing from collaboration patterns: {sorted(missing_from_collab)}")
    else:
        print(f"\n✅ All agents in collaboration patterns!")
    
    # Additional validation
    extra_in_workflow = workflow_agents - expected_agents
    if extra_in_workflow:
        print(f"\n⚠️  Unexpected agents in workflow: {sorted(extra_in_workflow)}")
    
    # Detailed stage breakdown
    print(f"\n📋 Stage-by-stage agent usage:")
    for stage in workflow["stages"]:
        stage_agents = []
        if "agents" in stage:
            for agent_config in stage["agents"]:
                if isinstance(agent_config, str):
                    stage_agents.append(agent_config)
                elif isinstance(agent_config, dict) and "agent" in agent_config:
                    stage_agents.append(agent_config["agent"])
        
        print(f"  {stage['stage_id']}: {len(stage_agents)} agents - {stage_agents}")
    
    # Validate JSON structure
    print(f"\n🔧 JSON Structure Validation:")
    required_fields = ["name", "version", "orchestrator", "stages", "agent_registry"]
    for field in required_fields:
        if field in workflow:
            print(f"  ✅ {field}: present")
        else:
            print(f"  ❌ {field}: missing")
    
    print(f"\n🎯 Total agents referenced: {len(workflow_agents | registry_agents | collab_agents)}")
    
    success = (not missing_from_stages and not missing_from_registry and 
               len(expected_agents) == len(workflow_agents))
    
    if success:
        print(f"\n🎉 VALIDATION SUCCESSFUL! All 32 agents properly referenced.")
    else:
        print(f"\n❌ VALIDATION FAILED! Some agents missing or incorrectly referenced.")
    
    return success

if __name__ == "__main__":
    validate_workflow_coverage()