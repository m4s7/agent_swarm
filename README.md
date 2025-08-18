# Multi-Agent Development Team

## Architecture
- **Framework**: VoltAgent awesome-claude-code-subagents (git submodule)
- **Templates**: BMAD-METHOD integration (git submodule)
- **Orchestration**: Multi-agent coordinator with parallel execution
- **Communication**: JSON-based message protocol with logging

## Team Composition
**Total: 31 Specialized Agents** across 10 categories
- Core Development (5 agents)
- Language Specialists (2 agents) 
- Infrastructure (1 agent)
- Quality & Security (5 agents)
- Data & AI (5 agents)
- Finance & Trading (4 agents)
- Developer Experience (2 agents)
- Business & Product (3 agents)
- Research & Analysis (3 agents)
- Orchestration (2 agents)

See [AGENT_REGISTRY.md](AGENT_REGISTRY.md) for complete list

## Quick Start
```bash
# Initialize submodules (first time setup)
git submodule update --init --recursive

# Verify setup (30 agents)
./start-agent-team.sh

# Choose a workflow for your project
python .claude/scripts/select-workflow.py

# Run with specific workflow
python .claude/agents/orchestration/communication-protocol.py .claude/workflows/team-orchestration.json

# Or use an individual agent
claude --agent .claude/agents/language-specialists/typescript-pro.md
```

## Available Workflows

| Workflow | Agents | Stages | Best For |
|----------|--------|--------|-----------|
| **Original Team** | 10 | 4 | Simple projects, prototypes |
| **Enhanced Team** | 30 | 9 | Enterprise projects |
| **Data Science** | 7 | 5 | ML/AI projects |
| **Full-Stack App** | 14 | 7 | Web applications |

### Workflow Selection
```bash
# Interactive workflow selector
python .claude/scripts/select-workflow.py

# Compare all workflows
python .claude/scripts/select-workflow.py --compare

# View workflow details
python .claude/scripts/select-workflow.py --details 2
```

## Submodule Management
```bash
# Update submodules to latest versions
git submodule update --remote

# Clone repository with submodules
git clone --recursive <repository-url>
```

## Project Structure
```
.claude/
├── agents/
│   ├── core/          # VoltAgent base agents
│   ├── custom/        # Customized agents
│   └── orchestration/ # Coordination agents
├── workflows/         # Orchestration configs
├── templates/         # BMAD templates
├── artifacts/         # Agent outputs
└── logs/             # Communication logs
```