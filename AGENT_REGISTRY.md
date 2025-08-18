# Agent Registry - Multi-Agent Swarm

## Total Agents: 31 (11 Original + 19 New + 1 Rust Engineer)

## 📊 Agent Categories

### 🎯 Core Development (5 agents)
| Agent | Purpose | MCP Servers | Status |
|-------|---------|-------------|--------|
| `api-designer` | API design patterns, REST/GraphQL schemas | memory, ref, sequential_thinking, exa | ✅ Active |
| `frontend-developer` | General frontend development | memory, ref, shadcn_ui, playwright, puppeteer | ✅ Active |
| `nextjs-developer` | Next.js specific development | memory, ref, shadcn_ui, playwright, puppeteer | ✅ Active |
| `websocket-engineer` | Real-time communication, WebSocket protocols | memory, ref, sequential_thinking | ✅ Active |
| `python-pro` | Python backend development | memory, ref, sequential_thinking, exa | ✅ Active |

### 🔤 Language Specialists (3 agents)
| Agent | Purpose | MCP Servers | Status |
|-------|---------|-------------|--------|
| `typescript-pro` | TypeScript development, type safety | memory, ref, sequential_thinking, exa | ✅ Active |
| `python-pro` | Python expertise (also in Core Dev) | memory, ref, sequential_thinking, exa | ✅ Active |
| `rust-engineer` | Rust systems programming, memory safety | memory, ref, sequential_thinking | ✅ Active |

### 🏗️ Infrastructure (1 agent)
| Agent | Purpose | MCP Servers | Status |
|-------|---------|-------------|--------|
| `deployment-engineer` | CI/CD, deployment automation | memory, ref, sequential_thinking, exa | ✅ Active |

### 🔒 Quality & Security (5 agents)
| Agent | Purpose | MCP Servers | Status |
|-------|---------|-------------|--------|
| `architect-reviewer` | Architecture review, system design validation | memory, sequential_thinking, ref, exa | ✅ Active |
| `code-reviewer` | Code quality, best practices enforcement | memory, ref, sequential_thinking | ✅ Active |
| `debugger` | Bug detection and resolution | memory, sequential_thinking, ref | ✅ Active |
| `qa-expert` | Test strategy and planning | memory, playwright, puppeteer, sequential_thinking | ✅ Active |
| `test-automator` | Automated test implementation | memory, playwright, puppeteer, ref | ✅ Active |

### 📊 Data & AI (5 agents)
| Agent | Purpose | MCP Servers | Status |
|-------|---------|-------------|--------|
| `ai-engineer` | AI/ML model development | memory, exa, sequential_thinking, ref | ✅ Active |
| `data-analyst` | Data analysis and visualization | memory, exa, sequential_thinking, ref | ✅ Active |
| `data-engineer` | Data pipelines, ETL processes | memory, ref, sequential_thinking, exa | ✅ Active |
| `data-scientist` | Statistical modeling, ML research | memory, exa, sequential_thinking, ref | ✅ Active |
| `postgres-pro` | PostgreSQL optimization | memory, ref, sequential_thinking | ✅ Active |

### 💰 Finance & Trading (3 agents)
| Agent | Purpose | MCP Servers | Status |
|-------|---------|-------------|--------|
| `fintech-engineer` | Financial systems, compliance | memory, ref, sequential_thinking, exa | ✅ Active |
| `futures-trading-strategist` | Futures trading strategies | memory, exa, sequential_thinking, ref | ✅ Active |
| `quant-analyst` | Quantitative analysis, modeling | memory, exa, sequential_thinking, ref | ✅ Active |

### 🛠️ Developer Experience (2 agents)
| Agent | Purpose | MCP Servers | Status |
|-------|---------|-------------|--------|
| `refactoring-specialist` | Code refactoring, optimization | memory, sequential_thinking, ref | ✅ Active |
| `tooling-engineer` | Developer tools, automation | memory, ref, sequential_thinking, exa | ✅ Active |

### 📈 Business & Product (3 agents)
| Agent | Purpose | MCP Servers | Status |
|-------|---------|-------------|--------|
| `product-manager` | Product strategy, roadmapping | memory, exa, sequential_thinking, shadcn_ui | ✅ Active |
| `prd-writer` | PRD creation with BMAD methodology | memory, exa, sequential_thinking, ref, shadcn_ui | ✅ Active |
| `ux-researcher` | User experience research | memory, exa, sequential_thinking, shadcn_ui | ✅ Active |

### 🔍 Research & Analysis (3 agents)
| Agent | Purpose | MCP Servers | Status |
|-------|---------|-------------|--------|
| `data-researcher` | Data research and insights | memory, exa, sequential_thinking, ref | ✅ Active |
| `research-analyst` | Competitive analysis, market research | memory, exa, sequential_thinking, ref | ✅ Active |
| `search-specialist` | Search optimization, information retrieval | memory, exa, ref, sequential_thinking | ✅ Active |

### 🎭 Orchestration (2 agents)
| Agent | Purpose | MCP Servers | Status |
|-------|---------|-------------|--------|
| `multi-agent-coordinator` | Workflow orchestration | memory, sequential_thinking | ✅ Active |
| `agent-organizer` | Task distribution, resource allocation | memory, sequential_thinking | ✅ Active |

## 🔌 MCP Server Usage Summary

| MCP Server | Agent Count | Primary Use Case |
|------------|-------------|------------------|
| `memory` | 30/30 | Universal - All agents use for persistence |
| `sequential_thinking` | 26/30 | Complex problem solving |
| `ref` | 23/30 | Documentation and references |
| `exa` | 16/30 | Research and web search |
| `shadcn_ui` | 5/30 | UI/UX related agents |
| `playwright` | 4/30 | Testing agents |
| `puppeteer` | 4/30 | Testing and automation |

## 🚀 Quick Start Commands

### Test All Agents
```bash
python3 .claude/test-agent-setup.py
```

### Run MCP Integration Test
```bash
python3 .claude/scripts/test-mcp-integration.py
```

### Start with Specific Agent
```bash
# Use the Task tool in Claude Code to launch specific agents
# In Claude Code, you can use:

# For development tasks
# Use Task tool with subagent_type: "typescript-pro"

# For data analysis  
# Use Task tool with subagent_type: "data-scientist"

# For architecture review
# Use Task tool with subagent_type: "architect-reviewer"

# Or use the intelligent agent selection system:
python3 .claude/demo_agent_selection.py
```

### Run Full Orchestration
```bash
python3 .claude/agents/orchestration/communication-protocol.py
```

## 📝 Adding New Agents

1. Copy agent from VoltAgent collection:
```bash
cp awesome-claude-code-subagents/categories/<category>/<agent>.md \
   .claude/agents/core/<agent>.md
```

2. Assign MCP servers:
```bash
python3 .claude/scripts/assign-mcp-new-agents.py
```

3. Update verification:
```bash
# Edit .claude/test-agent-setup.py to include new agent
```

4. Test integration:
```bash
python3 .claude/scripts/test-mcp-integration.py
```

## 🔄 Recent Updates

- **2024-08-16**: Added 19 new specialized agents
- **2024-08-16**: Integrated MCP servers across all agents
- **2024-08-16**: Implemented color-coded orchestration
- **2024-08-16**: Created automated integration scripts

## 📊 Agent Capability Matrix

| Capability | Agents Available |
|------------|-----------------|
| Frontend Development | frontend-developer, nextjs-developer, typescript-pro |
| Backend Development | python-pro, api-designer, websocket-engineer |
| Database Management | postgres-pro, data-engineer |
| Testing & QA | qa-expert, test-automator, debugger |
| Code Review | code-reviewer, architect-reviewer, refactoring-specialist |
| Data Science | data-scientist, data-analyst, ai-engineer |
| Research | research-analyst, data-researcher, search-specialist, ux-researcher |
| DevOps | deployment-engineer, tooling-engineer |
| Product Management | product-manager, prd-writer |
| Finance | fintech-engineer, futures-trading-strategist, futures-tick-data-specialist, quant-analyst |

## 🎯 Recommended Agent Teams

### Full-Stack Web Application
- `architect-reviewer` → `api-designer` → `typescript-pro` → `nextjs-developer` → `postgres-pro` → `test-automator`

### Data Pipeline
- `data-engineer` → `postgres-pro` → `data-analyst` → `data-scientist`

### Trading System
- `futures-trading-strategist` → `futures-tick-data-specialist` → `quant-analyst` → `python-pro` → `fintech-engineer` → `test-automator`

### Product Development
- `prd-writer` → `ux-researcher` → `architect-reviewer` → Development Team → `qa-expert`

---
*Last Updated: 2024-08-16*
*Total Active Agents: 30*
*MCP Integration: 100%*