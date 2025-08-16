#!/bin/bash

# Integration script for 19 new agents from VoltAgent collection
# Color definitions
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
RESET='\033[0m'

echo -e "${BLUE}========================================${RESET}"
echo -e "${BLUE}Integrating 19 New Agents${RESET}"
echo -e "${BLUE}========================================${RESET}"

# Core Development Agents
echo -e "\n${YELLOW}Copying Core Development Agents...${RESET}"
cp awesome-claude-code-subagents/categories/01-core-development/api-designer.md .claude/agents/core/
cp awesome-claude-code-subagents/categories/01-core-development/frontend-developer.md .claude/agents/core/
cp awesome-claude-code-subagents/categories/01-core-development/websocket-engineer.md .claude/agents/core/

# Language Specialists
echo -e "${YELLOW}Copying Language Specialists...${RESET}"
cp awesome-claude-code-subagents/categories/02-language-specialists/typescript-pro.md .claude/agents/core/

# Infrastructure
echo -e "${YELLOW}Copying Infrastructure Agents...${RESET}"
cp awesome-claude-code-subagents/categories/03-infrastructure/deployment-engineer.md .claude/agents/core/

# Quality & Security
echo -e "${YELLOW}Copying Quality & Security Agents...${RESET}"
cp awesome-claude-code-subagents/categories/04-quality-security/architect-reviewer.md .claude/agents/core/
cp awesome-claude-code-subagents/categories/04-quality-security/code-reviewer.md .claude/agents/core/
cp awesome-claude-code-subagents/categories/04-quality-security/debugger.md .claude/agents/core/

# Data & AI
echo -e "${YELLOW}Copying Data & AI Agents...${RESET}"
cp awesome-claude-code-subagents/categories/05-data-ai/ai-engineer.md .claude/agents/core/
cp awesome-claude-code-subagents/categories/05-data-ai/postgres-pro.md .claude/agents/core/
cp awesome-claude-code-subagents/categories/05-data-ai/data-analyst.md .claude/agents/core/
cp awesome-claude-code-subagents/categories/05-data-ai/data-engineer.md .claude/agents/core/
cp awesome-claude-code-subagents/categories/05-data-ai/data-scientist.md .claude/agents/core/

# Developer Experience
echo -e "${YELLOW}Copying Developer Experience Agents...${RESET}"
cp awesome-claude-code-subagents/categories/06-developer-experience/refactoring-specialist.md .claude/agents/core/
cp awesome-claude-code-subagents/categories/06-developer-experience/tooling-engineer.md .claude/agents/core/

# Business & Product
echo -e "${YELLOW}Copying Business & Product Agents...${RESET}"
cp awesome-claude-code-subagents/categories/08-business-product/ux-researcher.md .claude/agents/core/

# Research & Analysis
echo -e "${YELLOW}Copying Research & Analysis Agents...${RESET}"
cp awesome-claude-code-subagents/categories/10-research-analysis/data-researcher.md .claude/agents/core/
cp awesome-claude-code-subagents/categories/10-research-analysis/research-analyst.md .claude/agents/core/
cp awesome-claude-code-subagents/categories/10-research-analysis/search-specialist.md .claude/agents/core/

echo -e "\n${GREEN}✓ Successfully copied 19 agents!${RESET}"

# Count total agents
TOTAL_AGENTS=$(ls -1 .claude/agents/core/*.md | wc -l)
echo -e "${BLUE}Total agents in core: ${TOTAL_AGENTS}${RESET}"