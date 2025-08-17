#!/usr/bin/env python3
"""
Assign MCP servers to newly integrated agents
"""

import os
from pathlib import Path
import re

# MCP assignments for new agents
NEW_AGENT_MCP_MAPPING = {
    # Core Development
    'api-designer.md': {
        'servers': ['memory', 'ref', 'sequential_thinking', 'exa'],
        'focus': 'API design and documentation'
    },
    'frontend-developer.md': {
        'servers': ['memory', 'ref', 'shadcn_ui', 'playwright', 'puppeteer'],
        'focus': 'Frontend development and UI implementation'
    },
    'websocket-engineer.md': {
        'servers': ['memory', 'ref', 'sequential_thinking'],
        'focus': 'Real-time communication and WebSocket protocols'
    },
    
    # Language Specialists
    'typescript-pro.md': {
        'servers': ['memory', 'ref', 'sequential_thinking', 'exa'],
        'focus': 'TypeScript development and type safety'
    },
    
    # Infrastructure
    'deployment-engineer.md': {
        'servers': ['memory', 'ref', 'sequential_thinking', 'exa'],
        'focus': 'Deployment automation and CI/CD'
    },
    
    # Quality & Security
    'architect-reviewer.md': {
        'servers': ['memory', 'sequential_thinking', 'ref', 'exa'],
        'focus': 'Architecture review and system design'
    },
    'code-reviewer.md': {
        'servers': ['memory', 'ref', 'sequential_thinking'],
        'focus': 'Code quality and best practices'
    },
    'debugger.md': {
        'servers': ['memory', 'sequential_thinking', 'ref'],
        'focus': 'Bug detection and resolution'
    },
    
    # Data & AI
    'ai-engineer.md': {
        'servers': ['memory', 'exa', 'sequential_thinking', 'ref'],
        'focus': 'AI/ML model development and deployment'
    },
    'postgres-pro.md': {
        'servers': ['memory', 'ref', 'sequential_thinking'],
        'focus': 'PostgreSQL optimization and management'
    },
    'data-analyst.md': {
        'servers': ['memory', 'exa', 'sequential_thinking', 'ref'],
        'focus': 'Data analysis and visualization'
    },
    'data-engineer.md': {
        'servers': ['memory', 'ref', 'sequential_thinking', 'exa'],
        'focus': 'Data pipeline and ETL development'
    },
    'data-scientist.md': {
        'servers': ['memory', 'exa', 'sequential_thinking', 'ref'],
        'focus': 'Statistical modeling and ML research'
    },
    
    # Developer Experience
    'refactoring-specialist.md': {
        'servers': ['memory', 'sequential_thinking', 'ref'],
        'focus': 'Code refactoring and optimization'
    },
    'tooling-engineer.md': {
        'servers': ['memory', 'ref', 'sequential_thinking', 'exa'],
        'focus': 'Developer tools and automation'
    },
    
    # Business & Product
    'ux-researcher.md': {
        'servers': ['memory', 'exa', 'sequential_thinking', 'shadcn_ui'],
        'focus': 'User experience research and testing'
    },
    
    # Research & Analysis
    'data-researcher.md': {
        'servers': ['memory', 'exa', 'sequential_thinking', 'ref'],
        'focus': 'Data research and insights'
    },
    'research-analyst.md': {
        'servers': ['memory', 'exa', 'sequential_thinking', 'ref'],
        'focus': 'Research and competitive analysis'
    },
    'search-specialist.md': {
        'servers': ['memory', 'exa', 'ref', 'sequential_thinking'],
        'focus': 'Search optimization and information retrieval'
    },
    
    # Custom Agents
    'futures-tick-data-specialist.md': {
        'servers': ['memory', 'exa', 'sequential_thinking', 'ref'],
        'focus': 'Level 1 & Level 2 tick data processing and microstructure analysis'
    }
}

def add_mcp_to_agent(file_path, agent_name, mcp_config):
    """Add MCP configuration to agent file"""
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Check if already has MCP
        if 'mcp_servers:' in content or 'MCP Server' in content:
            print(f"  ⚠️  {agent_name} already has MCP config")
            return False
        
        servers = mcp_config['servers']
        focus = mcp_config['focus']
        
        # Create MCP section
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
        
        # Add MCP servers to frontmatter if YAML exists
        if content.startswith('---'):
            end_match = re.search(r'\n---\n', content[3:])
            if end_match:
                frontmatter_end = end_match.start() + 3
                frontmatter = content[:frontmatter_end]
                rest = content[frontmatter_end + 4:]
                
                # Add MCP servers line before closing ---
                servers_line = f"mcp_servers: [{', '.join(servers)}]\n"
                includes_line = "includes: [../shared/mcp-integration.md]\n"
                new_frontmatter = frontmatter + servers_line + includes_line + "---\n"
                
                content = new_frontmatter + rest
        
        # Add MCP section at the end
        content = content + mcp_section
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        print(f"  ✅ {agent_name}: {', '.join(servers)}")
        return True
        
    except Exception as e:
        print(f"  ❌ Error processing {agent_name}: {e}")
        return False

def main():
    print("=" * 60)
    print("Assigning MCP Servers to New Agents")
    print("=" * 60)
    
    core_dir = Path(".claude/agents/core")
    custom_dir = Path(".claude/agents/custom")
    success_count = 0
    
    for agent_file, mcp_config in NEW_AGENT_MCP_MAPPING.items():
        # Check core directory first
        file_path = core_dir / agent_file
        if file_path.exists():
            if add_mcp_to_agent(file_path, agent_file, mcp_config):
                success_count += 1
        else:
            # Check custom directory
            file_path = custom_dir / agent_file
            if file_path.exists():
                if add_mcp_to_agent(file_path, agent_file, mcp_config):
                    success_count += 1
            else:
                print(f"  ⚠️  {agent_file} not found")
    
    print("\n" + "=" * 60)
    print(f"✅ Successfully updated {success_count} agents with MCP servers")
    print("=" * 60)

if __name__ == "__main__":
    main()