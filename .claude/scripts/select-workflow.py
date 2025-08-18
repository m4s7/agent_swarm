#!/usr/bin/env python3
"""
Workflow selector - Choose the right orchestration for your project
"""

import json
import sys
from pathlib import Path
from typing import Dict, List

# Colors for output
class Colors:
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

# Available workflows
WORKFLOWS = {
    "1": {
        "file": "team-orchestration.json",
        "name": "Original Team Workflow",
        "description": "Basic workflow with core agents",
        "agents": 32,
        "best_for": "Simple projects, quick prototypes"
    },
    "2": {
        "file": "enhanced-team-orchestration.json",
        "name": "Enhanced Team Workflow",
        "description": "Complete workflow with all 30 agents",
        "agents": 30,
        "best_for": "Complex enterprise projects"
    },
    "3": {
        "file": "data-science-workflow.json",
        "name": "Data Science Workflow",
        "description": "Specialized for ML/AI projects",
        "agents": 7,
        "best_for": "Data analysis, ML model development"
    },
    "4": {
        "file": "fullstack-app-workflow.json",
        "name": "Full-Stack App Workflow",
        "description": "Web application development",
        "agents": 14,
        "best_for": "Web apps, SaaS products"
    }
}

def load_workflow(workflow_file: str) -> Dict:
    """Load a workflow configuration"""
    workflow_path = Path(f".claude/workflows/{workflow_file}")
    if not workflow_path.exists():
        print(f"{Colors.YELLOW}⚠️  Workflow file not found: {workflow_file}{Colors.RESET}")
        return None
    
    with open(workflow_path, 'r') as f:
        return json.load(f)

def display_workflow_details(workflow_data: Dict):
    """Display detailed information about a workflow"""
    print(f"\n{Colors.CYAN}{Colors.BOLD}Workflow: {workflow_data['name']}{Colors.RESET}")
    print(f"Version: {workflow_data.get('version', 'N/A')}")
    print(f"Orchestrator: {workflow_data.get('orchestrator', 'multi-agent-coordinator')}")
    
    if 'description' in workflow_data:
        print(f"Description: {workflow_data['description']}")
    
    print(f"\n{Colors.GREEN}Stages:{Colors.RESET}")
    for i, stage in enumerate(workflow_data['stages'], 1):
        print(f"  {i}. {stage['name']} (ID: {stage['stage_id']})")
        
        # Show agents in this stage
        if 'agents' in stage:
            if isinstance(stage['agents'], list):
                if isinstance(stage['agents'][0], dict):
                    agents = [a['agent'] for a in stage['agents']]
                else:
                    agents = stage['agents']
                print(f"     Agents: {Colors.BLUE}{', '.join(agents)}{Colors.RESET}")
        
        if 'substages' in stage:
            for substage in stage['substages']:
                agent = substage.get('agent', 'N/A')
                print(f"     - {substage['name']}: {Colors.BLUE}{agent}{Colors.RESET}")

def compare_workflows():
    """Compare all available workflows"""
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*60}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}Workflow Comparison{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'='*60}{Colors.RESET}\n")
    
    for key, info in WORKFLOWS.items():
        workflow_data = load_workflow(info['file'])
        if workflow_data:
            stage_count = len(workflow_data.get('stages', []))
            print(f"{Colors.GREEN}{key}. {info['name']}{Colors.RESET}")
            print(f"   File: {info['file']}")
            print(f"   Stages: {stage_count}")
            print(f"   Agent Count: {info['agents']}")
            print(f"   Best For: {Colors.YELLOW}{info['best_for']}{Colors.RESET}")
            print(f"   Description: {info['description']}")
            print()

def update_active_workflow(workflow_file: str):
    """Update the active workflow symlink"""
    workflows_dir = Path(".claude/workflows")
    active_link = workflows_dir / "active-workflow.json"
    
    # Remove existing symlink if it exists
    if active_link.exists() or active_link.is_symlink():
        active_link.unlink()
    
    # Create new symlink
    target = workflows_dir / workflow_file
    if target.exists():
        active_link.symlink_to(target.name)
        print(f"{Colors.GREEN}✅ Active workflow set to: {workflow_file}{Colors.RESET}")
        return True
    else:
        print(f"{Colors.YELLOW}⚠️  Workflow file not found: {workflow_file}{Colors.RESET}")
        return False

def main():
    print(f"{Colors.CYAN}{Colors.BOLD}{'='*60}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}Workflow Selector{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'='*60}{Colors.RESET}")
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--compare":
            compare_workflows()
            return
        elif sys.argv[1] == "--details":
            if len(sys.argv) > 2:
                workflow_key = sys.argv[2]
                if workflow_key in WORKFLOWS:
                    workflow_data = load_workflow(WORKFLOWS[workflow_key]['file'])
                    if workflow_data:
                        display_workflow_details(workflow_data)
                else:
                    print(f"{Colors.YELLOW}Invalid workflow key: {workflow_key}{Colors.RESET}")
            else:
                print("Usage: select-workflow.py --details <workflow_number>")
            return
    
    # Display available workflows
    print(f"\n{Colors.GREEN}Available Workflows:{Colors.RESET}\n")
    for key, info in WORKFLOWS.items():
        print(f"{Colors.BOLD}{key}.{Colors.RESET} {Colors.BLUE}{info['name']}{Colors.RESET}")
        print(f"   {info['description']}")
        print(f"   Best for: {Colors.YELLOW}{info['best_for']}{Colors.RESET}")
        print()
    
    # Get user selection
    choice = input(f"{Colors.CYAN}Select workflow (1-{len(WORKFLOWS)}) or 'q' to quit: {Colors.RESET}")
    
    if choice.lower() == 'q':
        print("Exiting...")
        return
    
    if choice in WORKFLOWS:
        workflow_info = WORKFLOWS[choice]
        print(f"\n{Colors.GREEN}Selected: {workflow_info['name']}{Colors.RESET}")
        
        # Load and display workflow details
        workflow_data = load_workflow(workflow_info['file'])
        if workflow_data:
            display_workflow_details(workflow_data)
            
            # Ask if user wants to set as active
            set_active = input(f"\n{Colors.CYAN}Set as active workflow? (y/n): {Colors.RESET}")
            if set_active.lower() == 'y':
                update_active_workflow(workflow_info['file'])
                print(f"\n{Colors.GREEN}To run: python .claude/agents/orchestration/communication-protocol.py{Colors.RESET}")
                print(f"{Colors.CYAN}Or use Claude Code Task tool with appropriate agent types{Colors.RESET}")
    else:
        print(f"{Colors.YELLOW}Invalid selection{Colors.RESET}")

if __name__ == "__main__":
    main()