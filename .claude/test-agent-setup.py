#!/usr/bin/env python3
"""
Test script to verify agent setup and communication
"""

import os
import json
from pathlib import Path

def verify_agent_files():
    """Check all required agent files are in place"""
    required_agents = [
        ".claude/agents/core/python-pro.md",
        ".claude/agents/core/nextjs-developer.md",
        ".claude/agents/core/qa-expert.md",
        ".claude/agents/core/test-automator.md",
        ".claude/agents/core/quant-analyst.md",
        ".claude/agents/core/fintech-engineer.md",
        ".claude/agents/core/product-manager.md",
        ".claude/agents/custom/futures-trading-strategist.md",
        ".claude/agents/custom/prd-writer.md",
        ".claude/agents/orchestration/multi-agent-coordinator.md"
    ]
    
    print("Verifying agent files...")
    missing = []
    for agent_file in required_agents:
        if not Path(agent_file).exists():
            missing.append(agent_file)
            print(f"  ❌ Missing: {agent_file}")
        else:
            print(f"  ✅ Found: {agent_file}")
    
    return len(missing) == 0

def verify_workflow_config():
    """Check workflow configuration"""
    config_file = ".claude/workflows/team-orchestration.json"
    print(f"\nVerifying workflow configuration...")
    
    if not Path(config_file).exists():
        print(f"  ❌ Missing workflow config: {config_file}")
        return False
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        print(f"  ✅ Valid JSON configuration")
        print(f"  ✅ Workflow: {config['name']}")
        print(f"  ✅ Stages: {len(config['stages'])}")
        return True
    except Exception as e:
        print(f"  ❌ Invalid configuration: {e}")
        return False

def create_sample_project():
    """Create a sample project structure for testing"""
    print("\nCreating sample project structure...")
    
    # Create sample requirements file
    requirements = """
# Trading Platform Requirements

## Overview
Build a futures trading platform with automated strategy execution

## Core Features
1. Real-time market data ingestion
2. Strategy backtesting framework
3. Risk management dashboard
4. Automated order execution

## Technical Stack
- Backend: Python (FastAPI)
- Frontend: Next.js 14
- Database: PostgreSQL + TimescaleDB
- Message Queue: Redis
"""
    
    with open("user_requirements.md", "w") as f:
        f.write(requirements)
    
    print("  ✅ Created user_requirements.md")
    
    # Create project directories
    dirs = ["backend", "frontend", "strategies", "tests", "docs"]
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)
        print(f"  ✅ Created {dir_name}/ directory")

def main():
    print("=" * 50)
    print("Multi-Agent Team Setup Verification")
    print("=" * 50)
    
    # Run verification checks
    agents_ok = verify_agent_files()
    workflow_ok = verify_workflow_config()
    
    if agents_ok and workflow_ok:
        print("\n✅ All checks passed! Your agent team is ready.")
        create_sample_project()
        
        print("\n" + "=" * 50)
        print("Next Steps:")
        print("1. Run: python .claude/agents/orchestration/communication-protocol.py")
        print("2. Check logs in: .claude/logs/")
        print("3. Start Claude Code with any agent from .claude/agents/")
    else:
        print("\n❌ Setup incomplete. Please check missing files.")

if __name__ == "__main__":
    main()