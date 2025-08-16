#!/usr/bin/env python3
"""
Test script to verify MCP integration in agents
"""

import os
import re
from pathlib import Path
from typing import Dict, List

# Colors for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

def check_agent_mcp_integration(file_path: Path) -> Dict:
    """Check if an agent has proper MCP integration"""
    
    agent_name = file_path.stem
    results = {
        'name': agent_name,
        'has_mcp_section': False,
        'has_mcp_servers': False,
        'has_includes': False,
        'servers': [],
        'status': 'not_integrated'
    }
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Check for MCP section
        if "MCP Server" in content or "mcp_servers:" in content:
            results['has_mcp_section'] = True
        
        # Extract MCP servers from frontmatter
        mcp_match = re.search(r'mcp_servers:\s*\[(.*?)\]', content)
        if mcp_match:
            results['has_mcp_servers'] = True
            servers_str = mcp_match.group(1)
            results['servers'] = [s.strip() for s in servers_str.split(',')]
        
        # Check for includes
        if "includes:" in content and "mcp-integration.md" in content:
            results['has_includes'] = True
        
        # Determine overall status
        if results['has_mcp_section'] or results['has_mcp_servers']:
            if results['has_mcp_servers'] and results['servers']:
                results['status'] = 'fully_integrated'
            else:
                results['status'] = 'partially_integrated'
        
    except Exception as e:
        results['status'] = 'error'
        results['error'] = str(e)
    
    return results

def print_agent_status(result: Dict):
    """Print formatted status for an agent"""
    
    name = result['name']
    status = result['status']
    
    # Choose color based on status
    if status == 'fully_integrated':
        status_color = Colors.GREEN
        status_symbol = '✅'
    elif status == 'partially_integrated':
        status_color = Colors.YELLOW
        status_symbol = '⚠️'
    else:
        status_color = Colors.RED
        status_symbol = '❌'
    
    print(f"  {status_symbol} {status_color}{name}{Colors.RESET}")
    
    if result['servers']:
        servers_str = ', '.join([f"{Colors.CYAN}{s}{Colors.RESET}" for s in result['servers']])
        print(f"     MCP Servers: {servers_str}")
    
    if status == 'partially_integrated':
        missing = []
        if not result['has_mcp_servers']:
            missing.append("MCP servers in frontmatter")
        if not result['has_includes']:
            missing.append("includes reference")
        if missing:
            print(f"     {Colors.YELLOW}Missing: {', '.join(missing)}{Colors.RESET}")

def main():
    """Test MCP integration across all agents"""
    
    print(f"{Colors.CYAN}{Colors.BOLD}{'=' * 60}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}MCP Integration Test Report{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'=' * 60}{Colors.RESET}\n")
    
    # Test directories
    test_dirs = [
        (".claude/agents/core", "Core Agents"),
        (".claude/agents/custom", "Custom Agents"),
        (".claude/agents/orchestration", "Orchestration Agents")
    ]
    
    total_agents = 0
    fully_integrated = 0
    partially_integrated = 0
    not_integrated = 0
    
    for dir_path, category in test_dirs:
        agent_dir = Path(dir_path)
        if not agent_dir.exists():
            continue
        
        print(f"{Colors.BLUE}{Colors.BOLD}{category}:{Colors.RESET}")
        
        for agent_file in sorted(agent_dir.glob("*.md")):
            result = check_agent_mcp_integration(agent_file)
            print_agent_status(result)
            
            total_agents += 1
            if result['status'] == 'fully_integrated':
                fully_integrated += 1
            elif result['status'] == 'partially_integrated':
                partially_integrated += 1
            else:
                not_integrated += 1
        
        print()
    
    # Print summary
    print(f"{Colors.CYAN}{Colors.BOLD}{'=' * 60}{Colors.RESET}")
    print(f"{Colors.BOLD}Summary:{Colors.RESET}")
    print(f"  Total Agents: {Colors.BLUE}{total_agents}{Colors.RESET}")
    print(f"  Fully Integrated: {Colors.GREEN}{fully_integrated}{Colors.RESET}")
    print(f"  Partially Integrated: {Colors.YELLOW}{partially_integrated}{Colors.RESET}")
    print(f"  Not Integrated: {Colors.RED}{not_integrated}{Colors.RESET}")
    
    # Overall status
    if fully_integrated == total_agents:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✅ All agents are MCP-aware!{Colors.RESET}")
    elif fully_integrated > 0:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠️  MCP integration in progress{Colors.RESET}")
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}❌ MCP integration needed{Colors.RESET}")
    
    print(f"{Colors.CYAN}{Colors.BOLD}{'=' * 60}{Colors.RESET}")
    
    # Print available MCP servers reference
    print(f"\n{Colors.BOLD}Available MCP Servers:{Colors.RESET}")
    servers = [
        ("memory", "Persistent knowledge management"),
        ("puppeteer", "Browser automation"),
        ("shadcn_ui", "UI components library"),
        ("sequential_thinking", "Complex reasoning"),
        ("ref", "Documentation search"),
        ("exa", "Web research"),
        ("playwright", "Advanced testing")
    ]
    
    for server, desc in servers:
        print(f"  • {Colors.CYAN}{server}{Colors.RESET}: {desc}")

if __name__ == "__main__":
    main()