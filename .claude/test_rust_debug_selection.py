#!/usr/bin/env python3
"""
Test specific Rust debugging scenarios
"""

import sys
import os
sys.path.append('.claude')

from agent_selection import AgentSelector, SelectionStrategy

def test_rust_debugging_scenarios():
    """Test various strategies for Rust debugging"""
    
    print("🔧 TESTING RUST DEBUGGING SCENARIOS")
    print("=" * 50)
    
    selector = AgentSelector()
    
    debug_task = "Debug ownership and lifetime issues in complex Rust codebase"
    
    strategies = [
        SelectionStrategy.BEST_MATCH,
        SelectionStrategy.SPECIALIZED_TEAM,
        SelectionStrategy.MINIMAL_TEAM,
        SelectionStrategy.REDUNDANT_TEAM
    ]
    
    for strategy in strategies:
        print(f"\nStrategy: {strategy.value}")
        print(f"Task: {debug_task}")
        
        team = selector.select_agents(debug_task, strategy)
        all_agents = team.get_all_agents()
        
        print(f"Selected agents: {all_agents}")
        print(f"Confidence: {team.confidence:.2%}")
        
        if 'rust-engineer' in all_agents:
            print(f"✅ Rust engineer selected!")
            if 'rust-engineer' in team.primary_agents:
                print(f"   🎯 As PRIMARY agent")
            elif 'rust-engineer' in team.support_agents:
                print(f"   🔧 As SUPPORT agent")
        else:
            print(f"❌ Rust engineer NOT selected")
        
        # Show task classification
        features = selector.task_classifier.classify_task(debug_task)
        print(f"Task classification:")
        print(f"  Languages: {[l.value for l in features.languages]}")
        print(f"  Categories: {[c.value for c in features.categories]}")
        print(f"  Complexity: {features.complexity.value}")

def test_explicit_rust_debugging():
    """Test more explicit Rust debugging tasks"""
    
    print("\n\n🔍 TESTING EXPLICIT RUST DEBUGGING TASKS")
    print("=" * 50)
    
    selector = AgentSelector()
    
    rust_debug_tasks = [
        "Debug Rust ownership issues in main.rs file",
        "Fix lifetime compilation errors in Rust struct",
        "Resolve borrow checker issues in async Rust code",
        "Debug memory safety violations in unsafe Rust block",
        "Fix compilation errors in Rust cargo project"
    ]
    
    for task in rust_debug_tasks:
        print(f"\nTask: {task}")
        
        # Try BEST_MATCH strategy which should prefer language-specific agents
        team = selector.select_agents(task, SelectionStrategy.BEST_MATCH)
        all_agents = team.get_all_agents()
        
        print(f"Selected agents: {all_agents}")
        print(f"Confidence: {team.confidence:.2%}")
        
        if 'rust-engineer' in all_agents:
            print(f"✅ Rust engineer selected!")
        else:
            print(f"❌ Rust engineer NOT selected")
            
            # Show why
            features = selector.task_classifier.classify_task(task)
            print(f"  Detected languages: {[l.value for l in features.languages]}")
            print(f"  Categories: {[c.value for c in features.categories]}")

if __name__ == '__main__':
    test_rust_debugging_scenarios()
    test_explicit_rust_debugging()