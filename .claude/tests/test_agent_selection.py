#!/usr/bin/env python3
"""
Test suite for automated agent selection system
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import unittest
from agent_selection import (
    TaskClassifier, TaskCategory, TaskComplexity,
    ProgrammingLanguage, Framework, TaskFeatures,
    AgentCapabilityMatrix, AgentCapability,
    AgentSelector, SelectionStrategy, TeamComposition
)
from agent_selection.workflow_optimizer import WorkflowOptimizer


class TestTaskClassifier(unittest.TestCase):
    """Test task classification functionality"""
    
    def setUp(self):
        self.classifier = TaskClassifier()
    
    def test_simple_development_task(self):
        """Test classification of simple development task"""
        task = "Create a simple Python function to calculate fibonacci numbers"
        features = self.classifier.classify_task(task)
        
        self.assertIn(TaskCategory.DEVELOPMENT, features.categories)
        self.assertIn(ProgrammingLanguage.PYTHON, features.languages)
        self.assertEqual(features.complexity, TaskComplexity.SIMPLE)
        self.assertTrue(features.is_new_feature)
    
    def test_complex_debugging_task(self):
        """Test classification of complex debugging task"""
        task = "Debug the memory leak in our production React application that causes the browser to crash after extended use"
        features = self.classifier.classify_task(task)
        
        self.assertIn(TaskCategory.DEBUGGING, features.categories)
        self.assertIn(TaskCategory.PERFORMANCE, features.categories)
        self.assertIn(ProgrammingLanguage.JAVASCRIPT, features.languages)
        self.assertIn(Framework.REACT, features.frameworks)
        self.assertTrue(features.is_bug_fix)
        self.assertIn(features.complexity, [TaskComplexity.COMPLEX, TaskComplexity.VERY_COMPLEX])
    
    def test_testing_task(self):
        """Test classification of testing task"""
        task = "Write unit tests for the user authentication module using pytest"
        features = self.classifier.classify_task(task)
        
        self.assertIn(TaskCategory.TESTING, features.categories)
        self.assertIn(ProgrammingLanguage.PYTHON, features.languages)
        self.assertTrue(features.requires_testing)
        self.assertIn('pytest', features.keywords)
    
    def test_database_task(self):
        """Test classification of database task"""
        task = "Optimize the PostgreSQL query that joins user and order tables"
        features = self.classifier.classify_task(task)
        
        self.assertIn(TaskCategory.DATABASE, features.categories)
        self.assertIn(TaskCategory.PERFORMANCE, features.categories)
        self.assertIn(ProgrammingLanguage.SQL, features.languages)
        self.assertIn(Framework.POSTGRES, features.frameworks)
        self.assertTrue(features.has_database)
    
    def test_deployment_task(self):
        """Test classification of deployment task"""
        task = "Deploy the application to AWS using Docker containers and Kubernetes"
        features = self.classifier.classify_task(task)
        
        self.assertIn(TaskCategory.DEPLOYMENT, features.categories)
        self.assertIn(Framework.DOCKER, features.frameworks)
        self.assertIn(Framework.KUBERNETES, features.frameworks)
        self.assertIn(Framework.AWS, features.frameworks)
        self.assertTrue(features.requires_deployment)
    
    def test_context_aware_classification(self):
        """Test classification with context"""
        task = "Fix the bug in the component"
        context = {
            'files': ['src/components/UserProfile.tsx', 'src/components/UserProfile.test.tsx']
        }
        features = self.classifier.classify_task(task, context)
        
        self.assertIn(TaskCategory.DEBUGGING, features.categories)
        self.assertIn(ProgrammingLanguage.TYPESCRIPT, features.languages)
        self.assertTrue(features.is_bug_fix)


class TestAgentCapabilityMatrix(unittest.TestCase):
    """Test agent capability matrix"""
    
    def setUp(self):
        self.matrix = AgentCapabilityMatrix()
    
    def test_agent_registration(self):
        """Test that all agents are registered"""
        # Check some key agents
        self.assertIn('python-pro', self.matrix.agents)
        self.assertIn('frontend-developer', self.matrix.agents)
        self.assertIn('debugger', self.matrix.agents)
        self.assertIn('code-reviewer', self.matrix.agents)
        
        # Check total count (should be 31 agents)
        self.assertEqual(len(self.matrix.agents), 31)
    
    def test_agent_capabilities(self):
        """Test agent capability properties"""
        python_agent = self.matrix.get_agent('python-pro')
        self.assertIsNotNone(python_agent)
        self.assertIn(TaskCategory.DEVELOPMENT, python_agent.primary_categories)
        self.assertIn(ProgrammingLanguage.PYTHON, python_agent.languages)
        self.assertTrue(python_agent.can_debug)
        self.assertTrue(python_agent.can_test)
    
    def test_category_filtering(self):
        """Test filtering agents by category"""
        testing_agents = self.matrix.get_agents_for_category(TaskCategory.TESTING)
        self.assertGreater(len(testing_agents), 0)
        
        # Check that test-automator is included
        agent_ids = [a.agent_id for a in testing_agents]
        self.assertIn('test-automator', agent_ids)
        self.assertIn('qa-expert', agent_ids)
    
    def test_language_filtering(self):
        """Test filtering agents by language"""
        python_agents = self.matrix.get_agents_for_language(ProgrammingLanguage.PYTHON)
        self.assertGreater(len(python_agents), 0)
        
        agent_ids = [a.agent_id for a in python_agents]
        self.assertIn('python-pro', agent_ids)
        self.assertIn('data-scientist', agent_ids)
    
    def test_task_matching(self):
        """Test agent-task matching score"""
        # Create a Python development task
        features = TaskFeatures(
            categories=[TaskCategory.DEVELOPMENT],
            complexity=TaskComplexity.MODERATE,
            languages=[ProgrammingLanguage.PYTHON],
            frameworks=[Framework.DJANGO],
            keywords=['api', 'endpoint'],
            file_patterns=['*.py'],
            requires_testing=True,
            requires_review=False,
            requires_deployment=False,
            requires_documentation=False,
            is_bug_fix=False,
            is_new_feature=True,
            is_refactoring=False,
            is_research=False,
            estimated_files=5,
            has_database=False,
            has_api=True,
            has_ui=False,
            has_security_implications=False,
            confidence=0.8
        )
        
        python_agent = self.matrix.get_agent('python-pro')
        score = python_agent.matches_task(features)
        
        # Python-pro should have high score for Python development
        self.assertGreater(score, 0.7)


class TestAgentSelector(unittest.TestCase):
    """Test agent selection functionality"""
    
    def setUp(self):
        self.selector = AgentSelector()
    
    def test_best_match_selection(self):
        """Test best match selection strategy"""
        task = "Create a Python script to process CSV files using pandas"
        team = self.selector.select_agents(task, SelectionStrategy.BEST_MATCH)
        
        self.assertIsNotNone(team)
        self.assertGreater(len(team.primary_agents), 0)
        # Should select Python specialist
        self.assertIn(team.primary_agents[0], ['python-pro', 'data-analyst', 'data-scientist'])
    
    def test_specialized_team_selection(self):
        """Test specialized team selection"""
        task = "Build a React frontend with TypeScript that connects to a REST API and includes comprehensive tests"
        team = self.selector.select_agents(task, SelectionStrategy.SPECIALIZED_TEAM)
        
        self.assertIsNotNone(team)
        self.assertGreater(len(team.primary_agents), 0)
        self.assertGreater(team.total_agents, 1)  # Should have multiple specialists
        
        # Check for frontend and testing agents
        all_agents = team.get_all_agents()
        has_frontend = any('frontend' in agent or 'typescript' in agent for agent in all_agents)
        has_testing = any('test' in agent or 'qa' in agent for agent in all_agents)
        
        self.assertTrue(has_frontend)
        self.assertTrue(has_testing or team.total_agents == 1)  # May optimize to single capable agent
    
    def test_minimal_team_selection(self):
        """Test minimal team selection"""
        task = "Fix a typo in the README file"
        team = self.selector.select_agents(task, SelectionStrategy.MINIMAL_TEAM)
        
        self.assertIsNotNone(team)
        self.assertEqual(team.total_agents, 1)  # Should use minimum agents
    
    def test_complex_task_selection(self):
        """Test selection for complex task"""
        task = """
        Redesign the entire authentication system to support OAuth2, 
        implement multi-factor authentication, update the database schema,
        create comprehensive tests, and deploy to production
        """
        team = self.selector.select_agents(task, SelectionStrategy.SPECIALIZED_TEAM)
        
        self.assertIsNotNone(team)
        self.assertGreater(team.total_agents, 2)  # Complex task needs multiple agents
        self.assertIn(team.workflow_suggestion, 
                     ['parallel-collaboration', 'team-orchestration'])
    
    def test_performance_update(self):
        """Test agent performance tracking"""
        # Update performance
        self.selector.update_agent_performance('python-pro', success=True, time_taken=0.8)
        self.selector.update_agent_performance('python-pro', success=True, time_taken=0.9)
        self.selector.update_agent_performance('python-pro', success=False, time_taken=1.5)
        
        # Check performance metrics
        perf = self.selector.agent_performance.get('python-pro')
        self.assertIsNotNone(perf)
        self.assertEqual(perf['total_tasks'], 3)
        self.assertEqual(perf['successful_tasks'], 2)
        self.assertAlmostEqual(perf['success_rate'], 0.667, places=2)


class TestWorkflowOptimizer(unittest.TestCase):
    """Test workflow optimization"""
    
    def setUp(self):
        self.optimizer = WorkflowOptimizer()
        self.selector = AgentSelector()
    
    def test_single_agent_workflow(self):
        """Test single agent workflow generation"""
        task = "Write a simple Python function"
        team = self.selector.select_agents(task, SelectionStrategy.BEST_MATCH)
        
        # Create task features
        features = self.selector.task_classifier.classify_task(task)
        
        # Optimize workflow
        workflow = self.optimizer.optimize_workflow(team, features)
        
        self.assertEqual(workflow.workflow_type, 'single-agent')
        self.assertGreater(len(workflow.stages), 0)
        self.assertEqual(workflow.parallelization_factor, 0.0)
    
    def test_parallel_workflow(self):
        """Test parallel workflow generation"""
        task = "Implement multiple independent features in different modules"
        
        # Create team with multiple agents
        team = TeamComposition(
            primary_agents=['python-pro', 'frontend-developer'],
            support_agents=['test-automator'],
            review_agents=['code-reviewer'],
            total_agents=4,
            estimated_time=2.0,
            confidence=0.8,
            reasoning="Multiple specialists",
            workflow_suggestion='parallel-collaboration'
        )
        
        features = self.selector.task_classifier.classify_task(task)
        workflow = self.optimizer.optimize_workflow(team, features)
        
        self.assertEqual(workflow.workflow_type, 'parallel-collaboration')
        self.assertGreater(workflow.parallelization_factor, 0.0)
        
        # Check for parallel stage
        has_parallel = any(stage.parallel for stage in workflow.stages)
        self.assertTrue(has_parallel)
    
    def test_enhanced_workflow(self):
        """Test enhanced team orchestration workflow"""
        task = """
        Build a complete e-commerce platform with user authentication,
        product catalog, shopping cart, payment integration, and admin dashboard
        """
        
        team = self.selector.select_agents(task, SelectionStrategy.FULL_TEAM)
        features = self.selector.task_classifier.classify_task(task)
        workflow = self.optimizer.optimize_workflow(team, features)
        
        self.assertEqual(workflow.workflow_type, 'team-orchestration')
        self.assertGreater(len(workflow.stages), 3)  # Should have multiple stages
        
        # Check stage names
        stage_names = [stage.name for stage in workflow.stages]
        
        # Should have some of these stages
        expected_stages = ['Research & Analysis', 'Design & Architecture', 
                          'Implementation', 'Testing & QA', 'Review']
        has_expected = any(name in " ".join(stage_names) for name in expected_stages)
        self.assertTrue(has_expected)
    
    def test_workflow_visualization(self):
        """Test workflow visualization"""
        task = "Create a REST API with testing"
        team = self.selector.select_agents(task, SelectionStrategy.SPECIALIZED_TEAM)
        features = self.selector.task_classifier.classify_task(task)
        workflow = self.optimizer.optimize_workflow(team, features)
        
        # Generate visualization
        viz = self.optimizer.visualize_workflow(workflow)
        
        self.assertIsInstance(viz, str)
        self.assertIn('Workflow:', viz)
        self.assertIn('Stages:', viz)
        self.assertIn('Agents:', viz)


class TestIntegration(unittest.TestCase):
    """Integration tests for complete agent selection flow"""
    
    def test_end_to_end_selection(self):
        """Test complete selection and optimization flow"""
        
        # Initialize components
        selector = AgentSelector()
        optimizer = WorkflowOptimizer()
        
        # Test task
        task = """
        Refactor the user service to improve performance,
        add comprehensive unit tests, and update the API documentation
        """
        
        # Select agents
        team = selector.select_agents(task, SelectionStrategy.SPECIALIZED_TEAM)
        
        self.assertIsNotNone(team)
        self.assertGreater(team.total_agents, 0)
        
        # Classify task
        features = selector.task_classifier.classify_task(task)
        
        self.assertIn(TaskCategory.REFACTORING, features.categories)
        self.assertIn(TaskCategory.PERFORMANCE, features.categories)
        self.assertTrue(features.requires_testing)
        self.assertTrue(features.requires_documentation)
        
        # Optimize workflow
        workflow = optimizer.optimize_workflow(team, features)
        
        self.assertIsNotNone(workflow)
        self.assertGreater(len(workflow.stages), 0)
        
        # Verify workflow structure
        for stage in workflow.stages:
            self.assertIsNotNone(stage.stage_id)
            self.assertIsNotNone(stage.name)
            self.assertGreater(len(stage.agents), 0)
        
        # Get statistics
        stats = selector.get_selection_statistics()
        self.assertIn('total_selections', stats)
        self.assertEqual(stats['total_selections'], 1)
    
    def test_various_task_types(self):
        """Test selection for various task types"""
        
        selector = AgentSelector()
        
        test_cases = [
            ("Fix the bug in the login function", TaskCategory.DEBUGGING),
            ("Write tests for the payment module", TaskCategory.TESTING),
            ("Deploy the application to production", TaskCategory.DEPLOYMENT),
            ("Analyze user behavior data", TaskCategory.DATA_ANALYSIS),
            ("Research best practices for microservices", TaskCategory.RESEARCH),
            ("Review the pull request", TaskCategory.REVIEW),
            ("Optimize database queries", TaskCategory.DATABASE),
            ("Design the API for the new feature", TaskCategory.API_DESIGN)
        ]
        
        for task_desc, expected_category in test_cases:
            with self.subTest(task=task_desc):
                team = selector.select_agents(task_desc)
                features = selector.task_classifier.classify_task(task_desc)
                
                self.assertIn(expected_category, features.categories)
                self.assertGreater(team.total_agents, 0)
                self.assertGreater(team.confidence, 0.0)


if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.WARNING)
    
    unittest.main(verbosity=2)