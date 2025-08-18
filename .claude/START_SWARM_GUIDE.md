# 🚀 How to Start the Agent Swarm

## 📋 **For PRD Creation** (Your Current Need)

### **Option 1: Direct PRD Agent (Fastest)**
Use Claude Code's Task tool:
```
Task tool parameters:
- subagent_type: "prd-writer"
- description: "Create updated PRD"
- prompt: "I need to create an updated Product Requirements Document for [your project description]"
```

### **Option 2: Intelligent Agent Selection**
Let the system choose the best agents automatically:
```bash
python3 .claude/demo_agent_selection.py
```
Then enter your task, e.g.:
- "Create a comprehensive PRD for a new trading platform"
- "Update our product requirements document with new features"
- "Write a PRD using BMAD methodology for our fintech app"

### **Option 3: Research + PRD Team**
Start with research agents first, then PRD:
```bash
# Step 1: Research phase
python3 .claude/demo_agent_selection.py
# Enter: "Research market requirements for trading platform"

# Step 2: PRD creation
python3 .claude/demo_agent_selection.py  
# Enter: "Create PRD based on research findings"
```

---

## 🤖 **General Agent Selection Methods**

### **Method 1: Task Tool (Direct Agent)**
Use Claude Code's built-in Task tool with specific agents:

| Agent Type | Use Case | Example Prompt |
|------------|----------|----------------|
| `prd-writer` | Product requirements | "Create PRD for mobile app" |
| `rust-engineer` | Rust development | "Build high-performance parser in Rust" |
| `python-pro` | Python development | "Create FastAPI backend service" |
| `nextjs-developer` | Frontend development | "Build React dashboard with Next.js" |
| `data-scientist` | Data analysis | "Analyze user behavior patterns" |
| `qa-expert` | Testing strategy | "Create comprehensive test plan" |

### **Method 2: Intelligent Selection**
Let the system analyze your task and choose the best team:
```bash
python3 .claude/demo_agent_selection.py
```

**Benefits:**
- Automatically selects optimal agent combination
- Considers task complexity and requirements
- Provides confidence scoring
- Suggests workflow optimization

### **Method 3: Full Workflow Orchestration**
For complex multi-stage projects:
```bash
# Select workflow
python3 .claude/scripts/select-workflow.py

# Run orchestration  
python3 .claude/agents/orchestration/communication-protocol.py
```

---

## 📊 **Available Workflows**

### **1. Comprehensive Multi-Agent Workflow** (32 agents)
- **Best for**: Large, complex projects
- **Stages**: 10 stages from discovery to deployment
- **Agents**: All 32 specialized agents
- **Use case**: Enterprise applications, full product development

### **2. Specialized Workflows** (Coming Soon)
- **Data Science Workflow**: ML/AI projects
- **Full-Stack App Workflow**: Web applications  
- **Trading System Workflow**: Financial platforms

---

## 🎯 **Quick Start for Common Tasks**

### **Product Requirements (PRD)**
```bash
# Quick start
python3 .claude/demo_agent_selection.py
# Enter: "Create comprehensive PRD for [your product]"

# Or use Task tool directly:
# subagent_type: "prd-writer"
# prompt: "Create PRD for [description]"
```

### **Rust Development**
```bash
python3 .claude/demo_agent_selection.py
# Enter: "Build [your Rust project description]"

# System will automatically select rust-engineer
```

### **Full-Stack Web Development**
```bash
python3 .claude/demo_agent_selection.py
# Enter: "Build full-stack web application with [tech stack]"

# System will select appropriate frontend + backend team
```

### **Data Analysis**
```bash
python3 .claude/demo_agent_selection.py  
# Enter: "Analyze [your data description]"

# System will select data-scientist or data-analyst
```

---

## 🔧 **Testing & Validation**

### **Test Agent Setup**
```bash
python3 .claude/test-agent-setup.py
```

### **Test Specific Language Support**
```bash
# Test Rust support
python3 .claude/test_rust_selection.py

# Test agent selection
python3 .claude/demo_agent_selection.py
```

### **Validate Workflow Coverage**
```bash
python3 .claude/validate_workflow_agents.py
```

---

## 📝 **Agent Categories Available**

### **Core Development** (5 agents)
- `api-designer` - API design and architecture
- `frontend-developer` - General frontend development
- `nextjs-developer` - Next.js specific development
- `websocket-engineer` - Real-time communication
- `python-pro` - Python backend development

### **Language Specialists** (3 agents)
- `typescript-pro` - TypeScript expertise
- `rust-engineer` - Rust systems programming
- `python-pro` - Python specialization

### **Business & Product** (3 agents)
- `product-manager` - Product strategy and roadmapping
- `prd-writer` - PRD creation with BMAD methodology ⭐
- `ux-researcher` - User experience research

### **Quality & Security** (5 agents)
- `architect-reviewer` - Architecture validation
- `code-reviewer` - Code quality enforcement
- `debugger` - Issue diagnosis and resolution
- `qa-expert` - Test strategy and planning
- `test-automator` - Automated testing

### **Data & AI** (5 agents)
- `ai-engineer` - AI/ML development
- `data-analyst` - Data analysis and visualization
- `data-engineer` - Data pipelines and ETL
- `data-scientist` - Statistical modeling and ML
- `postgres-pro` - Database optimization

### **Finance & Trading** (4 agents)
- `fintech-engineer` - Financial systems
- `futures-trading-strategist` - Trading strategies
- `futures-tick-data-specialist` - Market data processing
- `quant-analyst` - Quantitative analysis

### **Research & Analysis** (3 agents)
- `data-researcher` - Data research and insights
- `research-analyst` - Market research and analysis
- `search-specialist` - Information retrieval

### **Infrastructure & DevOps** (3 agents)
- `deployment-engineer` - CI/CD and deployment
- `tooling-engineer` - Developer tools
- `refactoring-specialist` - Code optimization

### **Orchestration** (2 agents)
- `multi-agent-coordinator` - Workflow coordination
- `agent-organizer` - Task distribution

---

## 🎬 **Getting Started NOW**

**For your PRD creation task, the fastest path is:**

1. **Use the intelligent selection system:**
   ```bash
   python3 .claude/demo_agent_selection.py
   ```

2. **Enter your PRD task:**
   ```
   "Create an updated PRD for [describe your product/feature]"
   ```

3. **The system will:**
   - Automatically select `prd-writer` agent
   - Provide confidence scoring
   - Suggest workflow optimization
   - Route to BMAD methodology specialist

**Alternative:** Use Claude Code Task tool directly with `subagent_type: "prd-writer"`

---

*This guide reflects the correct Claude Code usage patterns - no `--agent` CLI parameters needed!*