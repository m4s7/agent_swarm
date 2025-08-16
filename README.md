# Multi-Agent Development Team

## Architecture
- **Framework**: VoltAgent awesome-claude-code-subagents (git submodule)
- **Templates**: BMAD-METHOD integration (git submodule)
- **Orchestration**: Multi-agent coordinator with parallel execution
- **Communication**: JSON-based message protocol with logging

## Team Composition
1. **PRD Writer** - Enhanced with BMAD templates
2. **Python Expert** - Backend and API development
3. **Next.js Expert** - Frontend and UI development
4. **Futures Trading Strategist** - Custom financial expert
5. **QA Expert** - Test strategy and planning
6. **Test Automator** - Automated test implementation
7. **Multi-Agent Coordinator** - Team orchestration

## Quick Start
```bash
# Initialize submodules (first time setup)
git submodule update --init --recursive

# Verify setup
./start-agent-team.sh

# Start with PRD creation
claude --agent .claude/agents/custom/prd-writer.md

# Run full workflow
python .claude/agents/orchestration/communication-protocol.py
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