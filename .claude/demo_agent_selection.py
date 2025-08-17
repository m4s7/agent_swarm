#!/usr/bin/env python3
"""
Demo script for automated agent selection system
"""

import sys
import os
sys.path.append('.claude')

from agent_selection import (
    AgentSelector, SelectionStrategy,
    TaskClassifier, AgentCapabilityMatrix
)
from agent_selection.workflow_optimizer import WorkflowOptimizer


def print_section(title):
    """Print a section header"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)


def demo_task_classification():
    """Demo task classification"""
    print_section("TASK CLASSIFICATION DEMO")
    
    classifier = TaskClassifier()
    
    tasks = [
        "Build a React dashboard with real-time data visualization",
        "Fix the memory leak in the Python data processing pipeline",
        "Write comprehensive unit tests for the authentication module",
        "Deploy the application to AWS using Docker and Kubernetes",
        "Refactor the database queries to improve performance"
    ]
    
    for task in tasks:
        print(f"\nTask: {task[:60]}...")
        features = classifier.classify_task(task)
        
        print(f"Categories: {[c.value for c in features.categories[:3]]}")
        print(f"Complexity: {features.complexity.value}")
        print(f"Languages: {[l.value for l in features.languages]}")
        print(f"Frameworks: {[f.value for f in features.frameworks]}")
        print(f"Confidence: {features.confidence:.2f}")


def demo_agent_selection():
    """Demo agent selection with different strategies"""
    print_section("AGENT SELECTION DEMO")
    
    selector = AgentSelector()
    
    task = """
    Create a comprehensive e-commerce backend with Python/FastAPI including:
    - User authentication and authorization
    - Product catalog with search
    - Shopping cart and checkout
    - Payment integration
    - Admin dashboard
    - Unit and integration tests
    - API documentation
    """
    
    print(f"\nTask: Building e-commerce backend...")
    
    strategies = [
        SelectionStrategy.BEST_MATCH,
        SelectionStrategy.MINIMAL_TEAM,
        SelectionStrategy.SPECIALIZED_TEAM,
        SelectionStrategy.FULL_TEAM
    ]
    
    for strategy in strategies:
        print(f"\n--- Strategy: {strategy.value} ---")
        team = selector.select_agents(task, strategy)
        
        print(f"Primary agents: {team.primary_agents}")
        print(f"Support agents: {team.support_agents}")
        print(f"Review agents: {team.review_agents}")
        print(f"Total agents: {team.total_agents}")
        print(f"Estimated time: {team.estimated_time:.1f}x")
        print(f"Confidence: {team.confidence:.2f}")
        print(f"Workflow: {team.workflow_suggestion}")


def demo_workflow_optimization():
    """Demo workflow optimization"""
    print_section("WORKFLOW OPTIMIZATION DEMO")
    
    selector = AgentSelector()
    optimizer = WorkflowOptimizer()
    
    tasks = [
        ("Fix a typo in the README", SelectionStrategy.MINIMAL_TEAM),
        ("Add a new API endpoint with tests", SelectionStrategy.SPECIALIZED_TEAM),
        ("Redesign the entire authentication system", SelectionStrategy.FULL_TEAM)
    ]
    
    for task_desc, strategy in tasks:
        print(f"\nTask: {task_desc}")
        print(f"Strategy: {strategy.value}")
        
        # Select team
        team = selector.select_agents(task_desc, strategy)
        
        # Get task features
        features = selector.task_classifier.classify_task(task_desc)
        
        # Optimize workflow
        workflow = optimizer.optimize_workflow(team, features)
        
        # Visualize workflow
        print("\n" + optimizer.visualize_workflow(workflow))


def demo_agent_capabilities():
    """Demo agent capability matrix"""
    print_section("AGENT CAPABILITIES DEMO")
    
    matrix = AgentCapabilityMatrix()
    
    print(f"\nTotal agents available: {len(matrix.agents)}")
    
    # Show agents by category
    from agent_selection.task_classifier import TaskCategory
    
    categories_to_show = [
        TaskCategory.DEVELOPMENT,
        TaskCategory.TESTING,
        TaskCategory.DEBUGGING,
        TaskCategory.DATA_ANALYSIS,
        TaskCategory.DEPLOYMENT
    ]
    
    for category in categories_to_show:
        agents = matrix.get_agents_for_category(category)
        agent_names = [a.agent_id for a in agents[:5]]  # Show top 5
        print(f"\n{category.value.capitalize()} agents: {agent_names}")


def demo_intelligent_selection():
    """Demo intelligent agent selection for various scenarios"""
    print_section("INTELLIGENT SELECTION SCENARIOS")
    
    selector = AgentSelector()
    
    scenarios = [
        {
            'name': "Startup MVP",
            'task': "Build a minimal viable product for a social media app",
            'strategy': SelectionStrategy.MINIMAL_TEAM
        },
        {
            'name': "Enterprise Migration",
            'task': "Migrate legacy Java monolith to microservices architecture with comprehensive testing and zero downtime deployment",
            'strategy': SelectionStrategy.FULL_TEAM
        },
        {
            'name': "Bug Fix",
            'task': "Fix the critical bug causing data loss in production",
            'strategy': SelectionStrategy.SPECIALIZED_TEAM
        },
        {
            'name': "Data Science Project",
            'task': "Analyze customer behavior data, build predictive models, and create interactive dashboards",
            'strategy': SelectionStrategy.SPECIALIZED_TEAM
        }
    ]
    
    for scenario in scenarios:
        print(f"\n### Scenario: {scenario['name']} ###")
        print(f"Task: {scenario['task'][:80]}...")
        
        team = selector.select_agents(scenario['task'], scenario['strategy'])
        
        print(f"\nRecommended Team ({team.total_agents} agents):")
        if team.primary_agents:
            print(f"  Lead: {team.primary_agents}")
        if team.support_agents:
            print(f"  Support: {team.support_agents}")
        if team.review_agents:
            print(f"  Review: {team.review_agents}")
        
        print(f"\nWorkflow: {team.workflow_suggestion}")
        print(f"Time estimate: {team.estimated_time:.1f}x baseline")
        print(f"Confidence: {team.confidence:.0%}")


def main():
    """Run all demos"""
    print("\n" + "🤖"*30)
    print(" AUTOMATED AGENT SELECTION SYSTEM DEMO")
    print("🤖"*30)
    
    # Run demos
    demo_task_classification()
    demo_agent_capabilities()
    demo_agent_selection()
    demo_workflow_optimization()
    demo_intelligent_selection()
    
    print_section("DEMO COMPLETE")
    print("""
The automated agent selection system provides:

✅ Intelligent task classification
✅ Capability-based agent matching  
✅ Multiple selection strategies
✅ Workflow optimization
✅ Performance tracking
✅ Team composition recommendations

The system can automatically select the best agent(s) for any task!
    """)


if __name__ == '__main__':
    main()