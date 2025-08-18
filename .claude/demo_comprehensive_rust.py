#!/usr/bin/env python3
"""
Comprehensive demo of Rust support in the agent selection system
"""

import sys
import os
sys.path.append('.claude')

from agent_selection import AgentSelector, SelectionStrategy

def main():
    """Comprehensive Rust support demonstration"""
    
    print("🦀" * 30)
    print(" COMPREHENSIVE RUST SUPPORT DEMO")
    print("🦀" * 30)
    
    selector = AgentSelector()
    
    # Comprehensive Rust scenarios
    scenarios = [
        {
            'task': 'Build a high-performance HTTP server with async Rust and tokio',
            'expected_primary': 'rust-engineer',
            'strategy': SelectionStrategy.BEST_MATCH
        },
        {
            'task': 'Create WebAssembly module with wasm-bindgen for React frontend',
            'expected_primary': 'rust-engineer',
            'strategy': SelectionStrategy.SPECIALIZED_TEAM
        },
        {
            'task': 'Debug memory leak in unsafe Rust FFI code',
            'expected_primary': 'rust-engineer', 
            'strategy': SelectionStrategy.BEST_MATCH
        },
        {
            'task': 'Optimize Rust structs for zero-allocation JSON parsing with serde',
            'expected_primary': 'rust-engineer',
            'strategy': SelectionStrategy.BEST_MATCH
        },
        {
            'task': 'Implement distributed microservice in Rust with gRPC and tonic',
            'expected_primary': 'rust-engineer',
            'strategy': SelectionStrategy.SPECIALIZED_TEAM
        },
        {
            'task': 'Create embedded Rust firmware for ARM microcontroller with no_std',
            'expected_primary': 'rust-engineer',
            'strategy': SelectionStrategy.BEST_MATCH
        },
        {
            'task': 'Build CLI application with clap argument parsing in Rust',
            'expected_primary': 'rust-engineer',
            'strategy': SelectionStrategy.BEST_MATCH
        },
        {
            'task': 'Integrate Rust computation engine with Python data pipeline',
            'expected_primary': 'rust-engineer',
            'strategy': SelectionStrategy.SPECIALIZED_TEAM
        }
    ]
    
    success_count = 0
    total_count = len(scenarios)
    
    for i, scenario in enumerate(scenarios, 1):
        task = scenario['task']
        expected = scenario['expected_primary']
        strategy = scenario['strategy']
        
        print(f"\n{'='*60}")
        print(f"Scenario {i}: {task}")
        print(f"Strategy: {strategy.value}")
        print(f"Expected primary: {expected}")
        print("-" * 60)
        
        # Get agent selection
        team = selector.select_agents(task, strategy)
        features = selector.task_classifier.classify_task(task)
        
        # Check results
        if expected in team.primary_agents:
            print(f"✅ SUCCESS: {expected} selected as primary")
            success_count += 1
        elif expected in team.get_all_agents():
            print(f"⚠️  PARTIAL: {expected} selected but not as primary")
            print(f"   Primary: {team.primary_agents}")
            success_count += 0.5
        else:
            print(f"❌ FAILED: {expected} not selected")
            print(f"   Selected: {team.get_all_agents()}")
        
        # Show details
        print(f"Team composition:")
        print(f"  Primary: {team.primary_agents}")
        if team.support_agents:
            print(f"  Support: {team.support_agents}")
        if team.review_agents:
            print(f"  Review: {team.review_agents}")
        
        print(f"Classification:")
        print(f"  Languages: {[l.value for l in features.languages]}")
        print(f"  Categories: {[c.value for c in features.categories]}")
        print(f"  Complexity: {features.complexity.value}")
        print(f"  Confidence: {team.confidence:.1%}")
    
    print(f"\n{'='*60}")
    print(f"FINAL RESULTS")
    print(f"{'='*60}")
    print(f"Success Rate: {success_count}/{total_count} = {success_count/total_count:.1%}")
    
    if success_count/total_count >= 0.8:
        print(f"🎉 EXCELLENT: Rust support is working very well!")
    elif success_count/total_count >= 0.6:
        print(f"✅ GOOD: Rust support is working well with room for improvement")
    else:
        print(f"⚠️  NEEDS WORK: Rust support needs improvement")
    
    print(f"\n🦀 Rust language support includes:")
    print(f"✅ Comprehensive pattern recognition (.rs files, cargo, rustc, etc.)")
    print(f"✅ Rust-specific keywords (fn, let, mut, impl, trait, etc.)")
    print(f"✅ Framework detection (tokio, serde, wasm-bindgen, etc.)")
    print(f"✅ Agent capability matching (rust-engineer with debugging support)")
    print(f"✅ Multi-strategy selection (best match, specialized teams, etc.)")
    print(f"✅ Integration with existing workflow orchestration")
    
    print(f"\n🚀 Ready to use! Try:")
    print(f"python3 .claude/demo_agent_selection.py")
    print(f"# Then enter a Rust-related task")
    print(f"\n# Or use Claude Code Task tool with:")
    print(f"# subagent_type: 'rust-engineer'")
    print(f"# prompt: 'Your Rust development task'")

if __name__ == '__main__':
    main()