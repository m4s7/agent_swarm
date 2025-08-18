When you need another specialized agent from VoltAgent's collection:

## Quick Addition Process

### 1. Browse Available Agents
```bash
# List all agent categories
ls awesome-claude-code-subagents/categories/

# Find specific agent type (example: database specialist)
find awesome-claude-code-subagents -name "*database*.md"
find awesome-claude-code-subagents -name "*sql*.md"
```

### 2. Copy Agent to Your Project
```bash
# Example: Adding database architect
cp awesome-claude-code-subagents/categories/03-backend-systems/database-architect.md \
   .claude/agents/core/database-architect.md
```

### 3. Update Orchestration Config
Add the new agent to `.claude/workflows/team-orchestration.json`:
```json
{
  "stage_id": "database_design",
  "name": "Database Architecture",
  "agents": ["database-architect"],
  "outputs": ["schema.sql", "migration_plan.md"]
}
```

### 4. Create Integration Message
If the agent needs to communicate with existing agents, add to the appropriate stage:
```json
{
  "agent": "database-architect",
  "scope": "schema_design",
  "dependencies": ["backend_design.md"],
  "output": "database_schema.sql"
}
```

### 5. Test Integration
```bash
# Verify the agent file
cat .claude/agents/core/database-architect.md | head -20

# Update verification script
echo '".claude/agents/core/database-architect.md"' >> .claude/test-agent-setup.py

# Run verification
python3 .claude/test-agent-setup.py
```

**Pro tip**: Keep a `agent-registry.txt` file listing all added agents and their purposes for quick reference.