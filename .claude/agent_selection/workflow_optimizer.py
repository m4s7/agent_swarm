"""
Workflow optimization for selected agent teams
"""

import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from pathlib import Path

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent_selection.agent_selector import TeamComposition
from agent_selection.task_classifier import TaskFeatures, TaskComplexity


@dataclass
class WorkflowStage:
    """Represents a stage in the workflow"""
    stage_id: str
    name: str
    agents: List[str]
    parallel: bool = False
    timeout: Optional[int] = None
    dependencies: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.stage_id,
            'name': self.name,
            'agents': self.agents,
            'parallel': self.parallel,
            'timeout': self.timeout,
            'dependencies': self.dependencies,
            'outputs': self.outputs
        }


@dataclass
class OptimizedWorkflow:
    """Optimized workflow for task execution"""
    workflow_id: str
    workflow_type: str
    stages: List[WorkflowStage]
    total_agents: int
    estimated_time: float
    parallelization_factor: float  # 0.0 to 1.0
    description: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.workflow_id,
            'type': self.workflow_type,
            'stages': [stage.to_dict() for stage in self.stages],
            'metadata': {
                'total_agents': self.total_agents,
                'estimated_time': self.estimated_time,
                'parallelization_factor': self.parallelization_factor,
                'description': self.description
            }
        }
    
    def to_json(self) -> str:
        """Convert workflow to JSON"""
        return json.dumps(self.to_dict(), indent=2)


class WorkflowOptimizer:
    """Optimizes workflow for selected agent teams"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Load workflow templates
        self._load_workflow_templates()
    
    def _load_workflow_templates(self):
        """Load predefined workflow templates"""
        
        self.templates = {
            'single-agent': {
                'stages': ['execute'],
                'parallel': False,
                'description': 'Single agent execution'
            },
            'sequential-collaboration': {
                'stages': ['analyze', 'implement', 'review'],
                'parallel': False,
                'description': 'Sequential collaboration between agents'
            },
            'parallel-collaboration': {
                'stages': ['parallel-execute', 'merge', 'review'],
                'parallel': True,
                'description': 'Parallel execution with merge'
            },
            'parallel-redundant': {
                'stages': ['parallel-execute', 'validate', 'select-best'],
                'parallel': True,
                'description': 'Redundant parallel execution'
            },
            'team-orchestration': {
                'stages': ['research', 'design', 'parallel-implement', 
                          'integrate', 'test', 'review', 'deploy'],
                'parallel': 'mixed',
                'description': 'Full team orchestration with mixed parallel/sequential'
            }
        }
    
    def optimize_workflow(self,
                         team: TeamComposition,
                         features: TaskFeatures) -> OptimizedWorkflow:
        """
        Optimize workflow for team and task
        
        Args:
            team: Selected team composition
            features: Task features
        
        Returns:
            Optimized workflow
        """
        
        workflow_type = team.workflow_suggestion
        
        # Generate workflow based on type
        if workflow_type == 'single-agent':
            workflow = self._create_single_agent_workflow(team, features)
        elif workflow_type == 'sequential-collaboration':
            workflow = self._create_sequential_workflow(team, features)
        elif workflow_type == 'parallel-collaboration':
            workflow = self._create_parallel_workflow(team, features)
        elif workflow_type == 'parallel-redundant':
            workflow = self._create_redundant_workflow(team, features)
        elif workflow_type == 'team-orchestration':
            workflow = self._create_enhanced_workflow(team, features)
        else:
            # Default to sequential
            workflow = self._create_sequential_workflow(team, features)
        
        self.logger.info(f"Optimized workflow: {workflow.workflow_type} "
                        f"with {len(workflow.stages)} stages")
        
        return workflow
    
    def _create_single_agent_workflow(self,
                                     team: TeamComposition,
                                     features: TaskFeatures) -> OptimizedWorkflow:
        """Create workflow for single agent"""
        
        stages = []
        
        # Single execution stage
        if team.primary_agents:
            stages.append(WorkflowStage(
                stage_id='execute',
                name='Execute Task',
                agents=team.primary_agents,
                parallel=False,
                timeout=self._calculate_timeout(features.complexity)
            ))
        
        # Optional review stage
        if team.review_agents:
            stages.append(WorkflowStage(
                stage_id='review',
                name='Review',
                agents=team.review_agents,
                parallel=False,
                dependencies=['execute']
            ))
        
        return OptimizedWorkflow(
            workflow_id=f"workflow_{hash(str(team))}"[:10],
            workflow_type='single-agent',
            stages=stages,
            total_agents=team.total_agents,
            estimated_time=team.estimated_time,
            parallelization_factor=0.0,
            description='Single agent sequential execution'
        )
    
    def _create_sequential_workflow(self,
                                  team: TeamComposition,
                                  features: TaskFeatures) -> OptimizedWorkflow:
        """Create sequential collaboration workflow"""
        
        stages = []
        stage_count = 0
        
        # Analysis stage if research needed
        if features.is_research or features.complexity == TaskComplexity.VERY_COMPLEX:
            stages.append(WorkflowStage(
                stage_id=f'stage_{stage_count}',
                name='Analysis',
                agents=team.support_agents[:1] if team.support_agents else team.primary_agents[:1],
                parallel=False
            ))
            stage_count += 1
        
        # Implementation stages (one per primary agent)
        for i, agent in enumerate(team.primary_agents):
            dependencies = [f'stage_{stage_count-1}'] if stage_count > 0 else []
            
            stages.append(WorkflowStage(
                stage_id=f'stage_{stage_count}',
                name=f'Implementation {i+1}',
                agents=[agent],
                parallel=False,
                dependencies=dependencies,
                timeout=self._calculate_timeout(features.complexity)
            ))
            stage_count += 1
        
        # Testing stage if needed
        if features.requires_testing and team.support_agents:
            stages.append(WorkflowStage(
                stage_id=f'stage_{stage_count}',
                name='Testing',
                agents=team.support_agents[:1],
                parallel=False,
                dependencies=[f'stage_{stage_count-1}']
            ))
            stage_count += 1
        
        # Review stage
        if team.review_agents:
            stages.append(WorkflowStage(
                stage_id=f'stage_{stage_count}',
                name='Review',
                agents=team.review_agents,
                parallel=False,
                dependencies=[f'stage_{stage_count-1}']
            ))
        
        return OptimizedWorkflow(
            workflow_id=f"workflow_{hash(str(team))}"[:10],
            workflow_type='sequential-collaboration',
            stages=stages,
            total_agents=team.total_agents,
            estimated_time=team.estimated_time,
            parallelization_factor=0.0,
            description='Sequential agent collaboration'
        )
    
    def _create_parallel_workflow(self,
                                team: TeamComposition,
                                features: TaskFeatures) -> OptimizedWorkflow:
        """Create parallel collaboration workflow"""
        
        stages = []
        
        # Parallel execution stage
        if len(team.primary_agents) > 1:
            stages.append(WorkflowStage(
                stage_id='parallel_execute',
                name='Parallel Execution',
                agents=team.primary_agents,
                parallel=True,
                timeout=self._calculate_timeout(features.complexity)
            ))
            
            # Merge/integration stage
            stages.append(WorkflowStage(
                stage_id='integrate',
                name='Integration',
                agents=[team.primary_agents[0]],  # First agent coordinates
                parallel=False,
                dependencies=['parallel_execute']
            ))
        else:
            # Fall back to sequential if only one agent
            stages.append(WorkflowStage(
                stage_id='execute',
                name='Execute',
                agents=team.primary_agents,
                parallel=False
            ))
        
        # Testing in parallel if multiple testers
        if features.requires_testing and team.support_agents:
            if len(team.support_agents) > 1:
                stages.append(WorkflowStage(
                    stage_id='parallel_test',
                    name='Parallel Testing',
                    agents=team.support_agents,
                    parallel=True,
                    dependencies=['integrate' if len(stages) > 1 else 'execute']
                ))
            else:
                stages.append(WorkflowStage(
                    stage_id='test',
                    name='Testing',
                    agents=team.support_agents,
                    parallel=False,
                    dependencies=['integrate' if len(stages) > 1 else 'execute']
                ))
        
        # Review stage
        if team.review_agents:
            stages.append(WorkflowStage(
                stage_id='review',
                name='Review',
                agents=team.review_agents,
                parallel=len(team.review_agents) > 1,
                dependencies=[stages[-1].stage_id]
            ))
        
        # Calculate parallelization factor
        parallel_stages = sum(1 for s in stages if s.parallel)
        parallelization_factor = parallel_stages / len(stages) if stages else 0.0
        
        return OptimizedWorkflow(
            workflow_id=f"workflow_{hash(str(team))}"[:10],
            workflow_type='parallel-collaboration',
            stages=stages,
            total_agents=team.total_agents,
            estimated_time=team.estimated_time * (1 - parallelization_factor * 0.3),
            parallelization_factor=parallelization_factor,
            description='Parallel agent collaboration with integration'
        )
    
    def _create_redundant_workflow(self,
                                 team: TeamComposition,
                                 features: TaskFeatures) -> OptimizedWorkflow:
        """Create redundant parallel workflow"""
        
        stages = []
        
        # Parallel redundant execution
        stages.append(WorkflowStage(
            stage_id='redundant_execute',
            name='Redundant Parallel Execution',
            agents=team.primary_agents,
            parallel=True,
            timeout=self._calculate_timeout(features.complexity)
        ))
        
        # Validation stage - compare results
        stages.append(WorkflowStage(
            stage_id='validate',
            name='Validate Results',
            agents=[team.primary_agents[0]],  # First agent validates
            parallel=False,
            dependencies=['redundant_execute'],
            outputs=['validation_report']
        ))
        
        # Selection stage - choose best result
        stages.append(WorkflowStage(
            stage_id='select',
            name='Select Best Result',
            agents=team.review_agents if team.review_agents else [team.primary_agents[0]],
            parallel=False,
            dependencies=['validate'],
            outputs=['final_result']
        ))
        
        return OptimizedWorkflow(
            workflow_id=f"workflow_{hash(str(team))}"[:10],
            workflow_type='parallel-redundant',
            stages=stages,
            total_agents=team.total_agents,
            estimated_time=team.estimated_time * 0.8,  # Faster due to parallel
            parallelization_factor=0.33,  # First stage is parallel
            description='Redundant parallel execution with validation'
        )
    
    def _create_enhanced_workflow(self,
                                team: TeamComposition,
                                features: TaskFeatures) -> OptimizedWorkflow:
        """Create enhanced team orchestration workflow"""
        
        stages = []
        stage_id = 0
        
        # Research phase
        if features.is_research or features.categories:
            research_agents = team.support_agents[:2] if team.support_agents else team.primary_agents[:1]
            stages.append(WorkflowStage(
                stage_id=f'stage_{stage_id}',
                name='Research & Analysis',
                agents=research_agents,
                parallel=len(research_agents) > 1,
                outputs=['research_findings']
            ))
            stage_id += 1
        
        # Design/Architecture phase
        if features.complexity in [TaskComplexity.COMPLEX, TaskComplexity.VERY_COMPLEX]:
            design_agents = [a for a in team.primary_agents if 'architect' in a or 'design' in a]
            if not design_agents:
                design_agents = team.primary_agents[:1]
            
            stages.append(WorkflowStage(
                stage_id=f'stage_{stage_id}',
                name='Design & Architecture',
                agents=design_agents,
                parallel=False,
                dependencies=[f'stage_{stage_id-1}'] if stage_id > 0 else [],
                outputs=['design_spec']
            ))
            stage_id += 1
        
        # Parallel implementation
        if len(team.primary_agents) > 1:
            stages.append(WorkflowStage(
                stage_id=f'stage_{stage_id}',
                name='Parallel Implementation',
                agents=team.primary_agents,
                parallel=True,
                dependencies=[f'stage_{stage_id-1}'] if stage_id > 0 else [],
                timeout=self._calculate_timeout(features.complexity),
                outputs=['implementation_modules']
            ))
            stage_id += 1
            
            # Integration stage
            stages.append(WorkflowStage(
                stage_id=f'stage_{stage_id}',
                name='Integration',
                agents=[team.primary_agents[0]],
                parallel=False,
                dependencies=[f'stage_{stage_id-1}'],
                outputs=['integrated_solution']
            ))
            stage_id += 1
        else:
            # Sequential implementation if single agent
            stages.append(WorkflowStage(
                stage_id=f'stage_{stage_id}',
                name='Implementation',
                agents=team.primary_agents,
                parallel=False,
                dependencies=[f'stage_{stage_id-1}'] if stage_id > 0 else [],
                outputs=['implementation']
            ))
            stage_id += 1
        
        # Testing phase
        if features.requires_testing:
            test_agents = [a for a in team.support_agents if 'test' in a or 'qa' in a]
            if not test_agents and team.support_agents:
                test_agents = team.support_agents[:2]
            
            if test_agents:
                stages.append(WorkflowStage(
                    stage_id=f'stage_{stage_id}',
                    name='Testing & QA',
                    agents=test_agents,
                    parallel=len(test_agents) > 1,
                    dependencies=[f'stage_{stage_id-1}'],
                    outputs=['test_results']
                ))
                stage_id += 1
        
        # Documentation phase
        if features.requires_documentation:
            doc_agents = [a for a in team.support_agents if 'doc' in a or 'product' in a]
            if not doc_agents:
                doc_agents = team.primary_agents[:1]
            
            stages.append(WorkflowStage(
                stage_id=f'stage_{stage_id}',
                name='Documentation',
                agents=doc_agents,
                parallel=False,
                dependencies=[f'stage_{stage_id-1}'],
                outputs=['documentation']
            ))
            stage_id += 1
        
        # Review phase
        if team.review_agents:
            stages.append(WorkflowStage(
                stage_id=f'stage_{stage_id}',
                name='Final Review',
                agents=team.review_agents,
                parallel=len(team.review_agents) > 1,
                dependencies=[f'stage_{stage_id-1}'],
                outputs=['review_report']
            ))
            stage_id += 1
        
        # Deployment phase
        if features.requires_deployment:
            deploy_agents = [a for a in team.support_agents if 'deploy' in a]
            if not deploy_agents:
                deploy_agents = team.primary_agents[:1]
            
            stages.append(WorkflowStage(
                stage_id=f'stage_{stage_id}',
                name='Deployment',
                agents=deploy_agents,
                parallel=False,
                dependencies=[f'stage_{stage_id-1}'],
                outputs=['deployment_status']
            ))
        
        # Calculate parallelization factor
        parallel_stages = sum(1 for s in stages if s.parallel)
        parallelization_factor = parallel_stages / len(stages) if stages else 0.0
        
        return OptimizedWorkflow(
            workflow_id=f"workflow_{hash(str(team))}"[:10],
            workflow_type='team-orchestration',
            stages=stages,
            total_agents=team.total_agents,
            estimated_time=team.estimated_time * (1 - parallelization_factor * 0.25),
            parallelization_factor=parallelization_factor,
            description='Enhanced team orchestration with mixed parallel/sequential execution'
        )
    
    def _calculate_timeout(self, complexity: TaskComplexity) -> int:
        """Calculate timeout based on complexity"""
        
        timeouts = {
            TaskComplexity.TRIVIAL: 60,      # 1 minute
            TaskComplexity.SIMPLE: 300,      # 5 minutes
            TaskComplexity.MODERATE: 600,    # 10 minutes
            TaskComplexity.COMPLEX: 1800,    # 30 minutes
            TaskComplexity.VERY_COMPLEX: 3600  # 1 hour
        }
        
        return timeouts.get(complexity, 600)
    
    def export_workflow(self, workflow: OptimizedWorkflow, output_path: str):
        """Export workflow to file"""
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            f.write(workflow.to_json())
        
        self.logger.info(f"Workflow exported to {output_path}")
    
    def visualize_workflow(self, workflow: OptimizedWorkflow) -> str:
        """Generate text visualization of workflow"""
        
        lines = []
        lines.append(f"Workflow: {workflow.workflow_type}")
        lines.append(f"Agents: {workflow.total_agents}")
        lines.append(f"Estimated Time: {workflow.estimated_time:.1f}x")
        lines.append(f"Parallelization: {workflow.parallelization_factor:.0%}")
        lines.append("")
        lines.append("Stages:")
        
        for i, stage in enumerate(workflow.stages):
            prefix = "  ├─" if i < len(workflow.stages) - 1 else "  └─"
            
            parallel_marker = " [P]" if stage.parallel else ""
            agents_str = ", ".join(stage.agents)
            
            lines.append(f"{prefix} {stage.name}{parallel_marker}")
            lines.append(f"     Agents: {agents_str}")
            
            if stage.dependencies:
                deps_str = ", ".join(stage.dependencies)
                lines.append(f"     Dependencies: {deps_str}")
            
            if stage.outputs:
                outputs_str = ", ".join(stage.outputs)
                lines.append(f"     Outputs: {outputs_str}")
        
        return "\n".join(lines)