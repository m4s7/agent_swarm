#!/bin/bash

echo "Starting Multi-Agent Development Team"
echo "====================================="

# Verify setup
echo "Verifying installation..."
python3 .claude/test-agent-setup.py

if [ $? -ne 0 ]; then
    echo "Setup verification failed. Please complete setup first."
    exit 1
fi

echo ""
echo "Available Agents:"
echo "-----------------"
echo "1. prd-writer - Create product requirements"
echo "2. python-pro - Python backend development"
echo "3. nextjs-developer - Next.js frontend development"
echo "4. futures-trading-strategist - Trading strategy development"
echo "5. qa-expert - Test planning and strategy"
echo "6. test-automator - Automated test implementation"
echo "7. multi-agent-coordinator - Orchestrate all agents"

echo ""
echo "To start with a specific agent:"
echo "  claude --agent .claude/agents/custom/prd-writer.md"

echo ""
echo "To run the full workflow:"
echo "  python .claude/agents/orchestration/communication-protocol.py"

echo ""
echo "Agent team ready for deployment!"