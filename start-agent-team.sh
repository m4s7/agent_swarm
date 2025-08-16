#!/bin/bash

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
ORANGE='\033[38;5;208m'
BOLD='\033[1m'
RESET='\033[0m'

echo -e "${CYAN}${BOLD}=====================================${RESET}"
echo -e "${CYAN}${BOLD}Starting Multi-Agent Development Team${RESET}"
echo -e "${CYAN}${BOLD}=====================================${RESET}"

# Verify setup
echo -e "\n${YELLOW}Verifying installation...${RESET}"
python3 .claude/test-agent-setup.py

if [ $? -ne 0 ]; then
    echo -e "${RED}${BOLD}✗ Setup verification failed. Please complete setup first.${RESET}"
    exit 1
fi

echo ""
echo -e "${GREEN}${BOLD}Available Agents:${RESET}"
echo -e "${GREEN}-----------------${RESET}"
echo -e "1. ${MAGENTA}prd-writer${RESET} - Create product requirements"
echo -e "2. ${BLUE}python-pro${RESET} - Python backend development"
echo -e "3. ${YELLOW}nextjs-developer${RESET} - Next.js frontend development"
echo -e "4. ${ORANGE}futures-trading-strategist${RESET} - Trading strategy development"
echo -e "5. ${GREEN}qa-expert${RESET} - Test planning and strategy"
echo -e "6. ${GREEN}test-automator${RESET} - Automated test implementation"
echo -e "7. ${RED}multi-agent-coordinator${RESET} - Orchestrate all agents"

echo ""
echo -e "${CYAN}${BOLD}To start with a specific agent:${RESET}"
echo -e "  claude --agent .claude/agents/custom/prd-writer.md"

echo ""
echo -e "${CYAN}${BOLD}To run the full workflow:${RESET}"
echo -e "  python .claude/agents/orchestration/communication-protocol.py"

echo ""
echo -e "${GREEN}${BOLD}✓ Agent team ready for deployment!${RESET}"