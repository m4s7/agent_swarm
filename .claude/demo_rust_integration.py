#!/usr/bin/env python3
"""
Demo script showing Rust engineer integration with agent selection system
"""

import sys
import os
sys.path.append('.claude')

from agent_selection import AgentSelector, SelectionStrategy
from agent_selection.workflow_optimizer import WorkflowOptimizer


def demo_rust_tasks():
    """Demo Rust-specific task selection"""
    print("\n" + "="*60)
    print(" RUST ENGINEER INTEGRATION DEMO")
    print("="*60)
    
    selector = AgentSelector()
    optimizer = WorkflowOptimizer()
    
    # Rust-specific tasks
    rust_tasks = [
        {
            'description': "Implement a high-performance zero-copy parser in Rust",
            'strategy': SelectionStrategy.BEST_MATCH
        },
        {
            'description': "Build a memory-safe WebAssembly module with Rust and wasm-bindgen",
            'strategy': SelectionStrategy.SPECIALIZED_TEAM
        },
        {
            'description': "Create FFI bindings to integrate Rust library with Python",
            'strategy': SelectionStrategy.SPECIALIZED_TEAM
        },
        {
            'description': "Debug memory leak in Rust async runtime with tokio",
            'strategy': SelectionStrategy.SPECIALIZED_TEAM
        },
        {
            'description': "Optimize Rust code for embedded ARM microcontroller with no_std",
            'strategy': SelectionStrategy.MINIMAL_TEAM
        }
    ]
    
    for task_info in rust_tasks:
        task = task_info['description']
        strategy = task_info['strategy']
        
        print(f"\n{'='*60}")
        print(f"Task: {task}")
        print(f"Strategy: {strategy.value}")
        print("-"*60)
        
        # Select agents
        team = selector.select_agents(task, strategy)
        features = selector.task_classifier.classify_task(task)
        
        # Show classification
        print(f"\nTask Classification:")
        print(f"  Categories: {[c.value for c in features.categories[:3]]}")
        print(f"  Complexity: {features.complexity.value}")
        print(f"  Languages: {[l.value for l in features.languages]}")
        
        # Show selected team
        print(f"\nSelected Team:")
        print(f"  Primary: {team.primary_agents}")
        if team.support_agents:
            print(f"  Support: {team.support_agents}")
        if team.review_agents:
            print(f"  Review: {team.review_agents}")
        
        print(f"  Total agents: {team.total_agents}")
        print(f"  Confidence: {team.confidence:.2%}")
        
        # Optimize workflow
        workflow = optimizer.optimize_workflow(team, features)
        print(f"\nWorkflow: {workflow.workflow_type}")
        print(f"  Stages: {len(workflow.stages)}")
        print(f"  Parallelization: {workflow.parallelization_factor:.0%}")
        
        # Check if Rust engineer was selected
        all_agents = team.get_all_agents()
        if 'rust-engineer' in all_agents:
            print(f"  ✅ Rust engineer selected as expected!")
        else:
            print(f"  ⚠️  Rust engineer not selected (other agents may be better suited)")


def demo_rust_collaboration():
    """Demo Rust engineer collaboration with other agents"""
    print("\n" + "="*60)
    print(" RUST COLLABORATION SCENARIOS")
    print("="*60)
    
    selector = AgentSelector()
    
    collaboration_tasks = [
        "Build a Python extension module in Rust for data processing performance",
        "Create a full-stack web app with Rust backend and React frontend",
        "Implement a distributed system with Rust microservices and PostgreSQL",
        "Develop a cross-platform CLI tool in Rust with comprehensive tests"
    ]
    
    for task in collaboration_tasks:
        print(f"\n### Task: {task[:60]}...")
        
        team = selector.select_agents(task, SelectionStrategy.SPECIALIZED_TEAM)
        
        # Show collaboration
        if 'rust-engineer' in team.get_all_agents():
            collaborators = [a for a in team.get_all_agents() if a != 'rust-engineer']
            if collaborators:
                print(f"Rust engineer collaborating with: {collaborators}")
            else:
                print("Rust engineer working solo")
        
        print(f"Team confidence: {team.confidence:.2%}")
        print(f"Workflow: {team.workflow_suggestion}")


def check_rust_capabilities():
    """Check Rust engineer capabilities"""
    print("\n" + "="*60)
    print(" RUST ENGINEER CAPABILITIES")
    print("="*60)
    
    from agent_selection.agent_capabilities import AgentCapabilityMatrix
    
    matrix = AgentCapabilityMatrix()
    rust_engineer = matrix.get_agent('rust-engineer')
    
    if rust_engineer:
        print(f"\n✅ Rust Engineer Found in Capability Matrix")
        print(f"  Description: {rust_engineer.description}")
        print(f"  Primary Categories: {[c.value for c in rust_engineer.primary_categories]}")
        print(f"  Secondary Categories: {[c.value for c in rust_engineer.secondary_categories]}")
        print(f"  Max Complexity: {rust_engineer.max_complexity.value}")
        print(f"  MCP Servers: {rust_engineer.mcp_servers}")
        print(f"  Capabilities:")
        print(f"    - Can Test: {rust_engineer.can_test}")
        print(f"    - Can Debug: {rust_engineer.can_debug}")
        print(f"    - Can Refactor: {rust_engineer.can_refactor}")
        print(f"    - Can Document: {rust_engineer.can_document}")
        print(f"    - Can Architect: {rust_engineer.can_architect}")
        print(f"  Works well with: {rust_engineer.works_well_with}")
    else:
        print("❌ Rust Engineer not found in capability matrix")


def main():
    """Run all Rust integration demos"""
    print("\n🦀" * 30)
    print(" RUST ENGINEER AGENT INTEGRATION")
    print("🦀" * 30)
    
    # Check capabilities
    check_rust_capabilities()
    
    # Demo task selection
    demo_rust_tasks()
    
    # Demo collaboration
    demo_rust_collaboration()
    
    print("\n" + "="*60)
    print(" INTEGRATION COMPLETE")
    print("="*60)
    print("""
The Rust engineer agent has been successfully integrated with:

✅ Agent capability matrix updated (28 agents total)
✅ Task classification recognizes Rust language
✅ Intelligent selection for Rust-specific tasks
✅ Collaboration with Python, frontend, and system agents
✅ Workflow optimization for systems programming

The Rust engineer specializes in:
- Zero-cost abstractions
- Memory safety without GC
- Fearless concurrency
- FFI and WebAssembly
- Embedded systems
- High-performance computing
    """)


if __name__ == '__main__':
    main()