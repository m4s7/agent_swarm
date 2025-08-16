#!/usr/bin/env python3
"""
Script to update all agents with MCP server awareness
"""

import os
from pathlib import Path
import re

# MCP server assignments for different agent types
AGENT_MCP_MAPPING = {
    'python-pro.md': {
        'servers': ['memory', 'ref', 'sequential_thinking', 'exa'],
        'focus': 'Backend development and API design'
    },
    'nextjs-developer.md': {
        'servers': ['memory', 'ref', 'shadcn_ui', 'playwright', 'puppeteer'],
        'focus': 'Frontend development and UI testing'
    },
    'qa-expert.md': {
        'servers': ['memory', 'playwright', 'puppeteer', 'sequential_thinking'],
        'focus': 'Test strategy and quality assurance'
    },
    'test-automator.md': {
        'servers': ['memory', 'playwright', 'puppeteer', 'ref'],
        'focus': 'Automated testing and CI/CD'
    },
    'quant-analyst.md': {
        'servers': ['memory', 'exa', 'sequential_thinking', 'ref'],
        'focus': 'Quantitative analysis and modeling'
    },
    'fintech-engineer.md': {
        'servers': ['memory', 'ref', 'sequential_thinking', 'exa'],
        'focus': 'Financial systems and compliance'
    },
    'product-manager.md': {
        'servers': ['memory', 'exa', 'sequential_thinking', 'shadcn_ui'],
        'focus': 'Product strategy and user research'
    },
    'multi-agent-coordinator.md': {
        'servers': ['memory', 'sequential_thinking'],
        'focus': 'Agent orchestration and workflow management'
    },
    'agent-organizer.md': {
        'servers': ['memory', 'sequential_thinking'],
        'focus': 'Task distribution and resource allocation'
    }
}

def add_mcp_section(content, agent_name, mcp_config):
    """Add MCP awareness section to agent content"""
    
    # Check if MCP section already exists
    if "## MCP Server Integration" in content:
        print(f"  ⚠️  {agent_name} already has MCP section, skipping...")
        return content
    
    servers = mcp_config['servers']
    focus = mcp_config['focus']
    
    mcp_section = f"""

## MCP Server Integration

This agent is MCP-aware and can leverage the following servers:

### Available MCP Servers
{', '.join([f'`{s}`' for s in servers])}

### Primary Focus
{focus}

### MCP Usage Patterns
"""
    
    # Add specific usage for each server
    if 'memory' in servers:
        mcp_section += """
- **Memory**: Store and retrieve project context, maintain state across sessions"""
    
    if 'ref' in servers:
        mcp_section += """
- **Ref**: Access technical documentation, API references, and code examples"""
    
    if 'exa' in servers:
        mcp_section += """
- **Exa**: Perform deep research, find best practices, analyze trends"""
    
    if 'sequential_thinking' in servers:
        mcp_section += """
- **Sequential Thinking**: Break down complex problems, design solutions step-by-step"""
    
    if 'shadcn_ui' in servers:
        mcp_section += """
- **Shadcn UI**: Access UI components, design patterns, and styling guidelines"""
    
    if 'playwright' in servers:
        mcp_section += """
- **Playwright**: Automate browser testing, E2E scenarios, visual regression"""
    
    if 'puppeteer' in servers:
        mcp_section += """
- **Puppeteer**: Web scraping, form automation, screenshot generation"""
    
    mcp_section += """

### Integration Note
All MCP servers are automatically available. Reference `../shared/mcp-integration.md` for detailed usage.
"""
    
    # Add to end of content
    return content + mcp_section

def update_agent_file(file_path, mcp_config):
    """Update a single agent file with MCP awareness"""
    
    agent_name = Path(file_path).name
    print(f"Updating {agent_name}...")
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Add MCP section
        updated_content = add_mcp_section(content, agent_name, mcp_config)
        
        # Update YAML frontmatter if present
        if updated_content.startswith('---'):
            # Find the end of frontmatter
            end_match = re.search(r'\n---\n', updated_content[3:])
            if end_match:
                frontmatter_end = end_match.start() + 3
                frontmatter = updated_content[:frontmatter_end]
                
                # Add MCP servers to frontmatter if not present
                if 'mcp_servers:' not in frontmatter:
                    servers_line = f"mcp_servers: [{', '.join(mcp_config['servers'])}]\n"
                    includes_line = "includes: [../shared/mcp-integration.md]\n"
                    updated_content = frontmatter + servers_line + includes_line + updated_content[frontmatter_end:]
        
        with open(file_path, 'w') as f:
            f.write(updated_content)
        
        print(f"  ✅ Updated successfully")
        return True
        
    except Exception as e:
        print(f"  ❌ Error updating {agent_name}: {e}")
        return False

def main():
    """Update all agents with MCP awareness"""
    
    print("=" * 50)
    print("Updating Agents with MCP Server Awareness")
    print("=" * 50)
    
    # Update core agents
    core_dir = Path(".claude/agents/core")
    updated_count = 0
    
    for agent_file, mcp_config in AGENT_MCP_MAPPING.items():
        file_path = core_dir / agent_file
        if file_path.exists():
            if update_agent_file(file_path, mcp_config):
                updated_count += 1
        else:
            print(f"  ⚠️  {agent_file} not found")
    
    # Update orchestration agents
    orch_dir = Path(".claude/agents/orchestration")
    for agent_file in ['multi-agent-coordinator.md', 'agent-organizer.md']:
        if agent_file in AGENT_MCP_MAPPING:
            file_path = orch_dir / agent_file
            if file_path.exists():
                if update_agent_file(file_path, AGENT_MCP_MAPPING[agent_file]):
                    updated_count += 1
    
    print("\n" + "=" * 50)
    print(f"✅ Updated {updated_count} agents with MCP awareness")
    print("=" * 50)

if __name__ == "__main__":
    main()