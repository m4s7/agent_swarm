# MCP Integration Module
# This module is included by all agents for MCP awareness

## Available MCP Servers

All agents in this swarm have access to the following Model Context Protocol servers:

### 🧠 Memory Server
- **Command**: `npx -y @modelcontextprotocol/server-memory`
- **Purpose**: Persistent memory and knowledge management
- **Use Cases**:
  - Store important discoveries and learnings
  - Maintain context across sessions
  - Share knowledge with other agents
  - Track project state and progress

### 🌐 Puppeteer Server
- **Command**: `npx -y puppeteer-mcp-server`
- **Purpose**: Browser automation and web scraping
- **Use Cases**:
  - Automated testing of web applications
  - Data extraction from websites
  - Form automation and submission
  - Screenshot generation for documentation

### 🎨 Shadcn UI Server
- **Command**: `npx @heilgar/shadcn-ui-mcp-server`
- **Purpose**: UI component library and patterns
- **Use Cases**:
  - Access pre-built React components
  - UI/UX best practices
  - Component documentation and examples
  - Rapid prototyping with consistent design

### 🤔 Sequential Thinking Server
- **Command**: `npx -y @modelcontextprotocol/server-sequential-thinking`
- **Purpose**: Complex reasoning and problem-solving
- **Use Cases**:
  - Break down complex problems
  - Step-by-step solution development
  - Logical reasoning chains
  - Decision tree analysis

### 📚 Ref Documentation Server
- **URL**: `https://api.ref.tools/mcp?apiKey=ref-af6011e8146f630e3a14`
- **Purpose**: Technical documentation search
- **Use Cases**:
  - Find API documentation
  - Search programming references
  - Locate code examples
  - Access framework guides

### 🔍 Exa Research Server
- **Command**: `npx -y mcp-remote https://mcp.exa.ai/mcp?exaApiKey=25b94979-70a5-48af-9791-3309b92eb451`
- **Purpose**: Advanced web search and research
- **Use Cases**:
  - Company and market research
  - Technical article discovery
  - News and trend analysis
  - Academic paper retrieval

### 🎭 Playwright Server
- **Command**: `npx @playwright/mcp@latest`
- **Purpose**: Advanced browser testing framework
- **Use Cases**:
  - Cross-browser compatibility testing
  - End-to-end test automation
  - Visual regression testing
  - Performance testing

## Integration Guidelines

### For Development Tasks
1. Use **memory** MCP to store project requirements and decisions
2. Use **sequential_thinking** for architecture planning
3. Use **ref** for API documentation lookups
4. Use **exa** for researching best practices

### For Testing Tasks
1. Use **puppeteer** or **playwright** for automated testing
2. Use **memory** to track test results and patterns
3. Use **sequential_thinking** for test case design

### For UI/Frontend Tasks
1. Use **shadcn_ui** for component patterns
2. Use **playwright** for visual testing
3. Use **ref** for framework documentation

### For Research Tasks
1. Use **exa** for comprehensive web research
2. Use **ref** for technical documentation
3. Use **memory** to store findings
4. Use **sequential_thinking** for analysis

## Cross-Agent Collaboration via MCP

Agents can collaborate through MCP servers:
- Share knowledge via **memory** server
- Coordinate testing via **playwright/puppeteer**
- Share research findings via **exa** results
- Maintain project context across all agents

## Example Usage Patterns

```python
# Store discovery in memory
memory.store("project_requirements", requirements_doc)

# Research best practices
results = exa.search("futures trading microstructure analysis")

# Automate browser testing
playwright.test("trading_dashboard", test_scenarios)

# Complex reasoning
solution = sequential_thinking.analyze(problem_statement)
```