#!/usr/bin/env python3
"""
Test script to verify agent setup and communication with color support
"""

import os
import json
from pathlib import Path

# Color codes for terminal output
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    ORANGE = '\033[38;5;208m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'

# Agent type to color mapping
AGENT_TYPE_COLORS = {
    'python-pro': Colors.BLUE,
    'nextjs-developer': Colors.YELLOW,
    'qa-expert': Colors.GREEN,
    'test-automator': Colors.GREEN,
    'quant-analyst': Colors.ORANGE,
    'fintech-engineer': Colors.ORANGE,
    'product-manager': Colors.MAGENTA,
    'futures-trading-strategist': Colors.ORANGE,
    'prd-writer': Colors.MAGENTA,
    'multi-agent-coordinator': Colors.RED,
    'rust-engineer': Colors.ORANGE,  # Systems programming - orange
}

def get_agent_name_colored(agent_file: str) -> str:
    """Get colored agent name from file path"""
    agent_name = Path(agent_file).stem
    color = AGENT_TYPE_COLORS.get(agent_name, Colors.RESET)
    return f"{color}{agent_name}{Colors.RESET}"

def verify_agent_files():
    """Check all required agent files are in place"""
    required_agents = [
        # Original agents
        ".claude/agents/language-specialists/python-pro.md",
        ".claude/agents/core/nextjs-developer.md",
        ".claude/agents/core/qa-expert.md",
        ".claude/agents/core/test-automator.md",
        ".claude/agents/core/quant-analyst.md",
        ".claude/agents/core/fintech-engineer.md",
        ".claude/agents/core/product-manager.md",
        ".claude/agents/custom/futures-trading-strategist.md",
        ".claude/agents/custom/futures-tick-data-specialist.md",
        ".claude/agents/custom/prd-writer.md",
        ".claude/agents/orchestration/multi-agent-coordinator.md",
        # New agents (19 additions)
        ".claude/agents/core/api-designer.md",
        ".claude/agents/core/frontend-developer.md",
        ".claude/agents/core/websocket-engineer.md",
        ".claude/agents/language-specialists/typescript-pro.md",
        ".claude/agents/core/deployment-engineer.md",
        ".claude/agents/core/architect-reviewer.md",
        ".claude/agents/core/code-reviewer.md",
        ".claude/agents/core/debugger.md",
        ".claude/agents/core/ai-engineer.md",
        ".claude/agents/core/postgres-pro.md",
        ".claude/agents/core/data-analyst.md",
        ".claude/agents/core/data-engineer.md",
        ".claude/agents/core/data-scientist.md",
        ".claude/agents/core/refactoring-specialist.md",
        ".claude/agents/core/tooling-engineer.md",
        ".claude/agents/core/ux-researcher.md",
        ".claude/agents/core/data-researcher.md",
        ".claude/agents/core/research-analyst.md",
        ".claude/agents/core/search-specialist.md",
        # Rust engineer
        ".claude/agents/language-specialists/rust-engineer.md"
    ]
    
    print(f"{Colors.CYAN}{Colors.BOLD}Verifying agent files...{Colors.RESET}")
    missing = []
    for agent_file in required_agents:
        if not Path(agent_file).exists():
            missing.append(agent_file)
            agent_name = Path(agent_file).stem
            print(f"  {Colors.RED}❌ Missing:{Colors.RESET} {get_agent_name_colored(agent_file)} ({agent_file})")
        else:
            agent_name = Path(agent_file).stem
            print(f"  {Colors.GREEN}✅ Found:{Colors.RESET} {get_agent_name_colored(agent_file)}")
    
    return len(missing) == 0

def verify_workflow_config():
    """Check workflow configuration"""
    config_file = ".claude/workflows/team-orchestration.json"
    print(f"\n{Colors.CYAN}{Colors.BOLD}Verifying workflow configuration...{Colors.RESET}")
    
    if not Path(config_file).exists():
        print(f"  {Colors.RED}❌ Missing workflow config:{Colors.RESET} {config_file}")
        return False
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        print(f"  {Colors.GREEN}✅ Valid JSON configuration{Colors.RESET}")
        print(f"  {Colors.GREEN}✅ Workflow:{Colors.RESET} {Colors.BLUE}{config['name']}{Colors.RESET}")
        print(f"  {Colors.GREEN}✅ Stages:{Colors.RESET} {Colors.YELLOW}{len(config['stages'])}{Colors.RESET}")
        return True
    except Exception as e:
        print(f"  {Colors.RED}❌ Invalid configuration:{Colors.RESET} {e}")
        return False

def create_sample_project():
    """Create a sample project structure for testing"""
    print(f"\n{Colors.CYAN}{Colors.BOLD}Creating sample project structure...{Colors.RESET}")
    
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
    
    print(f"  {Colors.GREEN}✅ Created{Colors.RESET} user_requirements.md")
    
    # Create project directories
    dirs = ["backend", "frontend", "strategies", "tests", "docs"]
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)
        print(f"  {Colors.GREEN}✅ Created{Colors.RESET} {Colors.BLUE}{dir_name}/{Colors.RESET} directory")

def main():
    print(f"{Colors.CYAN}{Colors.BOLD}{'=' * 50}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}Multi-Agent Team Setup Verification{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'=' * 50}{Colors.RESET}")
    
    # Run verification checks
    agents_ok = verify_agent_files()
    workflow_ok = verify_workflow_config()
    
    if agents_ok and workflow_ok:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✅ All checks passed! Your agent team is ready.{Colors.RESET}")
        create_sample_project()
        
        print(f"\n{Colors.CYAN}{Colors.BOLD}{'=' * 50}{Colors.RESET}")
        print(f"{Colors.YELLOW}{Colors.BOLD}Next Steps:{Colors.RESET}")
        print(f"1. Run: {Colors.BLUE}python .claude/agents/orchestration/communication-protocol.py{Colors.RESET}")
        print(f"2. Check logs in: {Colors.BLUE}.claude/logs/{Colors.RESET}")
        print(f"3. Start Claude Code with any agent from {Colors.BLUE}.claude/agents/{Colors.RESET}")
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}❌ Setup incomplete. Please check missing files.{Colors.RESET}")

if __name__ == "__main__":
    main()