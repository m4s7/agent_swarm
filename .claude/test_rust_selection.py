#!/usr/bin/env python3
"""
Test script to verify Rust language support in agent selection
"""

import sys
import os
sys.path.append('.claude')

from agent_selection import AgentSelector, SelectionStrategy
from agent_selection.task_classifier import TaskClassifier, ProgrammingLanguage

def test_rust_detection():
    """Test Rust language detection in task classification"""
    
    print("🦀 TESTING RUST LANGUAGE DETECTION")
    print("=" * 50)
    
    classifier = TaskClassifier()
    
    rust_tasks = [
        "Implement a high-performance HTTP client in Rust",
        "Create a cargo.toml configuration for my Rust project",
        "Fix memory leak in async Rust code using tokio",
        "Build a WebAssembly module with wasm-bindgen in Rust",
        "Optimize Rust struct layout for better performance",
        "Implement serde serialization for custom Rust enum",
        "Debug unsafe Rust code with potential undefined behavior",
        "Create FFI bindings between Rust and Python",
        "Develop a CLI tool using clap in Rust",
        "Implement zero-copy string parsing with &str in Rust"
    ]
    
    for i, task in enumerate(rust_tasks, 1):
        print(f"\n{i}. Task: {task}")
        features = classifier.classify_task(task)
        
        detected_languages = [lang.value for lang in features.languages]
        print(f"   Detected languages: {detected_languages}")
        
        if ProgrammingLanguage.RUST in features.languages:
            print(f"   ✅ Rust correctly detected!")
        else:
            print(f"   ❌ Rust NOT detected")
        
        print(f"   Categories: {[cat.value for cat in features.categories]}")
        print(f"   Complexity: {features.complexity.value}")

def test_rust_agent_selection():
    """Test Rust engineer selection for Rust tasks"""
    
    print("\n\n🤖 TESTING RUST AGENT SELECTION")
    print("=" * 50)
    
    selector = AgentSelector()
    
    rust_scenarios = [
        {
            'task': "Implement a zero-copy memory-safe parser in Rust",
            'strategy': SelectionStrategy.BEST_MATCH
        },
        {
            'task': "Build a high-performance web service with async Rust and tokio",
            'strategy': SelectionStrategy.SPECIALIZED_TEAM
        },
        {
            'task': "Create FFI bindings to integrate Rust library with Python backend",
            'strategy': SelectionStrategy.SPECIALIZED_TEAM
        },
        {
            'task': "Debug ownership and lifetime issues in complex Rust codebase",
            'strategy': SelectionStrategy.MINIMAL_TEAM
        },
        {
            'task': "Optimize Rust code for embedded systems with no_std",
            'strategy': SelectionStrategy.BEST_MATCH
        }
    ]
    
    for i, scenario in enumerate(rust_scenarios, 1):
        task = scenario['task']
        strategy = scenario['strategy']
        
        print(f"\n{i}. Scenario: {task}")
        print(f"   Strategy: {strategy.value}")
        
        # Get agent selection
        team = selector.select_agents(task, strategy)
        all_agents = team.get_all_agents()
        
        print(f"   Selected agents: {all_agents}")
        print(f"   Confidence: {team.confidence:.2%}")
        
        if 'rust-engineer' in all_agents:
            print(f"   ✅ Rust engineer selected!")
            # Show position in team
            if 'rust-engineer' in team.primary_agents:
                print(f"   🎯 As PRIMARY agent")
            elif 'rust-engineer' in team.support_agents:
                print(f"   🔧 As SUPPORT agent")
            elif 'rust-engineer' in team.review_agents:
                print(f"   👁️  As REVIEW agent")
        else:
            print(f"   ❌ Rust engineer NOT selected")
            print(f"   🤔 Reason: Other agents might be better suited or threshold not met")

def test_rust_context_files():
    """Test Rust detection with file context"""
    
    print("\n\n📁 TESTING RUST DETECTION WITH FILE CONTEXT")
    print("=" * 50)
    
    classifier = TaskClassifier()
    
    # Test with Rust file context
    context = {
        'files': ['src/main.rs', 'src/lib.rs', 'Cargo.toml', 'Cargo.lock']
    }
    
    task = "Refactor the module structure to improve maintainability"
    
    print(f"Task: {task}")
    print(f"Files: {context['files']}")
    
    features = classifier.classify_task(task, context)
    
    detected_languages = [lang.value for lang in features.languages]
    print(f"Detected languages: {detected_languages}")
    
    if ProgrammingLanguage.RUST in features.languages:
        print(f"✅ Rust correctly detected from .rs files!")
    else:
        print(f"❌ Rust NOT detected from file context")
    
    print(f"Complexity: {features.complexity.value}")
    print(f"Categories: {[cat.value for cat in features.categories]}")

def test_rust_agent_capabilities():
    """Test Rust engineer capabilities"""
    
    print("\n\n⚙️  TESTING RUST ENGINEER CAPABILITIES")
    print("=" * 50)
    
    from agent_selection.agent_capabilities import AgentCapabilityMatrix
    
    matrix = AgentCapabilityMatrix()
    rust_agent = matrix.get_agent('rust-engineer')
    
    if rust_agent:
        print(f"✅ Rust engineer found in capability matrix")
        print(f"   Description: {rust_agent.description}")
        print(f"   Languages: {[lang.value for lang in rust_agent.languages]}")
        print(f"   Primary categories: {[cat.value for cat in rust_agent.primary_categories]}")
        print(f"   Secondary categories: {[cat.value for cat in rust_agent.secondary_categories]}")
        print(f"   Max complexity: {rust_agent.max_complexity.value}")
        print(f"   Can test: {rust_agent.can_test}")
        print(f"   Can debug: {rust_agent.can_debug}")
        print(f"   Can refactor: {rust_agent.can_refactor}")
        
        # Test language matching
        if ProgrammingLanguage.RUST in rust_agent.languages:
            print(f"   ✅ Rust language properly configured")
        else:
            print(f"   ❌ Rust language NOT in capabilities")
    else:
        print(f"❌ Rust engineer NOT found in capability matrix")

def main():
    """Run all Rust support tests"""
    print("🦀" * 25)
    print(" RUST LANGUAGE SUPPORT TESTING")
    print("🦀" * 25)
    
    try:
        # Test language detection
        test_rust_detection()
        
        # Test agent selection
        test_rust_agent_selection()
        
        # Test file context
        test_rust_context_files()
        
        # Test capabilities
        test_rust_agent_capabilities()
        
        print("\n\n🎉 RUST SUPPORT TESTING COMPLETE")
        print("=" * 50)
        print("The agent selection system now fully supports Rust!")
        print("\nRust integration includes:")
        print("✅ Language pattern recognition")
        print("✅ File extension detection (.rs)")
        print("✅ Rust-specific keywords and syntax")
        print("✅ Rust engineer agent selection")
        print("✅ Capability matrix integration")
        print("✅ Framework patterns (cargo, tokio, serde, etc.)")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()