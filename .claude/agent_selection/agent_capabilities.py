"""
Agent capability matrix for automated agent selection
"""

from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent_selection.task_classifier import (
    TaskCategory, TaskComplexity, ProgrammingLanguage, 
    Framework, TaskFeatures
)


@dataclass
class AgentCapability:
    """Defines capabilities of a single agent"""
    agent_id: str
    agent_type: str
    description: str
    
    # Core competencies
    primary_categories: List[TaskCategory]
    secondary_categories: List[TaskCategory] = field(default_factory=list)
    
    # Technical skills
    languages: List[ProgrammingLanguage] = field(default_factory=list)
    frameworks: List[Framework] = field(default_factory=list)
    
    # Complexity handling
    max_complexity: TaskComplexity = TaskComplexity.COMPLEX
    preferred_complexity: TaskComplexity = TaskComplexity.MODERATE
    
    # Special capabilities
    can_test: bool = False
    can_review: bool = False
    can_deploy: bool = False
    can_document: bool = False
    can_refactor: bool = False
    can_debug: bool = False
    can_research: bool = False
    can_architect: bool = False
    
    # MCP servers (if applicable)
    mcp_servers: List[str] = field(default_factory=list)
    
    # Performance metrics
    success_rate: float = 0.95  # Historical success rate
    avg_completion_time: float = 1.0  # Relative time (1.0 = average)
    
    # Collaboration preferences
    works_well_with: List[str] = field(default_factory=list)
    conflicts_with: List[str] = field(default_factory=list)
    
    def matches_task(self, features: TaskFeatures) -> float:
        """Calculate how well this agent matches a task (0.0 to 1.0)"""
        score = 0.0
        
        # Category matching (40% weight)
        category_score = 0.0
        for category in features.categories:
            if category in self.primary_categories:
                category_score += 1.0
            elif category in self.secondary_categories:
                category_score += 0.5
        
        if features.categories:
            category_score /= len(features.categories)
        score += category_score * 0.4
        
        # Language matching (25% weight)
        language_score = 0.0
        if features.languages:
            matching_languages = set(features.languages) & set(self.languages)
            language_score = len(matching_languages) / len(features.languages)
        elif not self.languages:  # No specific language requirement
            language_score = 1.0
        score += language_score * 0.25
        
        # Framework matching (15% weight)
        framework_score = 0.0
        if features.frameworks:
            matching_frameworks = set(features.frameworks) & set(self.frameworks)
            framework_score = len(matching_frameworks) / len(features.frameworks)
        elif not self.frameworks:  # No specific framework requirement
            framework_score = 1.0
        score += framework_score * 0.15
        
        # Complexity matching (10% weight)
        complexity_score = 0.0
        if features.complexity.value <= self.max_complexity.value:
            complexity_score = 1.0
            if features.complexity == self.preferred_complexity:
                complexity_score = 1.0
            else:
                # Penalize for complexity mismatch
                diff = abs(features.complexity.value.count('_') - 
                          self.preferred_complexity.value.count('_'))
                complexity_score = max(0.5, 1.0 - (diff * 0.2))
        score += complexity_score * 0.1
        
        # Special requirements matching (10% weight)
        special_score = 1.0
        requirement_count = 0
        
        if features.requires_testing:
            requirement_count += 1
            if not self.can_test:
                special_score -= 0.2
        
        if features.requires_review:
            requirement_count += 1
            if not self.can_review:
                special_score -= 0.2
        
        if features.requires_deployment:
            requirement_count += 1
            if not self.can_deploy:
                special_score -= 0.2
        
        if features.is_bug_fix:
            requirement_count += 1
            if not self.can_debug:
                special_score -= 0.2
        
        if features.is_refactoring:
            requirement_count += 1
            if not self.can_refactor:
                special_score -= 0.2
        
        score += max(0, special_score) * 0.1
        
        return min(1.0, score)


class AgentCapabilityMatrix:
    """Matrix of all agent capabilities"""
    
    def __init__(self):
        self.agents: Dict[str, AgentCapability] = {}
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize all agent capabilities"""
        
        # Python specialist
        self.agents['python-pro'] = AgentCapability(
            agent_id='python-pro',
            agent_type='python-pro',
            description='Expert Python developer with deep expertise',
            primary_categories=[TaskCategory.DEVELOPMENT, TaskCategory.DEBUGGING],
            secondary_categories=[TaskCategory.TESTING, TaskCategory.REFACTORING],
            languages=[ProgrammingLanguage.PYTHON],
            frameworks=[Framework.DJANGO, Framework.FLASK, Framework.FASTAPI, 
                       Framework.PANDAS, Framework.NUMPY],
            max_complexity=TaskComplexity.VERY_COMPLEX,
            can_test=True,
            can_debug=True,
            can_refactor=True,
            can_document=True,
            mcp_servers=['memory', 'ref', 'sequential_thinking']
        )
        
        # Frontend developer
        self.agents['frontend-developer'] = AgentCapability(
            agent_id='frontend-developer',
            agent_type='frontend-developer',
            description='Expert UI engineer for frontend solutions',
            primary_categories=[TaskCategory.UI_UX, TaskCategory.DEVELOPMENT],
            secondary_categories=[TaskCategory.TESTING, TaskCategory.PERFORMANCE],
            languages=[ProgrammingLanguage.JAVASCRIPT, ProgrammingLanguage.TYPESCRIPT,
                      ProgrammingLanguage.HTML_CSS],
            frameworks=[Framework.REACT, Framework.VUE, Framework.ANGULAR],
            max_complexity=TaskComplexity.COMPLEX,
            can_test=True,
            can_document=True,
            mcp_servers=['memory', 'ref', 'shadcn_ui', 'playwright', 'puppeteer']
        )
        
        # TypeScript specialist
        self.agents['typescript-pro'] = AgentCapability(
            agent_id='typescript-pro',
            agent_type='typescript-pro',
            description='Expert TypeScript developer',
            primary_categories=[TaskCategory.DEVELOPMENT],
            secondary_categories=[TaskCategory.API_DESIGN, TaskCategory.TESTING],
            languages=[ProgrammingLanguage.TYPESCRIPT, ProgrammingLanguage.JAVASCRIPT],
            frameworks=[Framework.NEXTJS, Framework.EXPRESS],
            max_complexity=TaskComplexity.VERY_COMPLEX,
            can_test=True,
            can_refactor=True,
            mcp_servers=['memory', 'ref', 'sequential_thinking', 'exa']
        )
        
        # Next.js developer
        self.agents['nextjs-developer'] = AgentCapability(
            agent_id='nextjs-developer',
            agent_type='nextjs-developer',
            description='Expert Next.js developer',
            primary_categories=[TaskCategory.DEVELOPMENT, TaskCategory.UI_UX],
            secondary_categories=[TaskCategory.PERFORMANCE, TaskCategory.DEPLOYMENT],
            languages=[ProgrammingLanguage.TYPESCRIPT, ProgrammingLanguage.JAVASCRIPT],
            frameworks=[Framework.NEXTJS, Framework.REACT],
            max_complexity=TaskComplexity.COMPLEX,
            can_test=True,
            can_deploy=True
        )
        
        # Data analyst
        self.agents['data-analyst'] = AgentCapability(
            agent_id='data-analyst',
            agent_type='data-analyst',
            description='Expert data analyst',
            primary_categories=[TaskCategory.DATA_ANALYSIS],
            secondary_categories=[TaskCategory.RESEARCH, TaskCategory.DOCUMENTATION],
            languages=[ProgrammingLanguage.PYTHON, ProgrammingLanguage.SQL],
            frameworks=[Framework.PANDAS, Framework.NUMPY],
            max_complexity=TaskComplexity.COMPLEX,
            can_document=True,
            can_research=True,
            mcp_servers=['memory', 'exa', 'sequential_thinking', 'ref']
        )
        
        # Data scientist
        self.agents['data-scientist'] = AgentCapability(
            agent_id='data-scientist',
            agent_type='data-scientist',
            description='Expert data scientist',
            primary_categories=[TaskCategory.DATA_ANALYSIS],
            secondary_categories=[TaskCategory.RESEARCH, TaskCategory.PERFORMANCE],
            languages=[ProgrammingLanguage.PYTHON],
            frameworks=[Framework.TENSORFLOW, Framework.PYTORCH, Framework.PANDAS],
            max_complexity=TaskComplexity.VERY_COMPLEX,
            can_research=True,
            mcp_servers=['memory', 'exa', 'sequential_thinking', 'ref']
        )
        
        # Debugger
        self.agents['debugger'] = AgentCapability(
            agent_id='debugger',
            agent_type='debugger',
            description='Expert debugger for complex issues',
            primary_categories=[TaskCategory.DEBUGGING],
            secondary_categories=[TaskCategory.TESTING, TaskCategory.PERFORMANCE],
            languages=[],  # Language agnostic
            max_complexity=TaskComplexity.VERY_COMPLEX,
            can_debug=True,
            can_test=True,
            mcp_servers=['memory', 'sequential_thinking', 'ref']
        )
        
        # Code reviewer
        self.agents['code-reviewer'] = AgentCapability(
            agent_id='code-reviewer',
            agent_type='code-reviewer',
            description='Expert code reviewer',
            primary_categories=[TaskCategory.REVIEW],
            secondary_categories=[TaskCategory.SECURITY, TaskCategory.REFACTORING],
            languages=[],  # Language agnostic
            max_complexity=TaskComplexity.VERY_COMPLEX,
            can_review=True,
            can_refactor=True,
            mcp_servers=['memory', 'ref', 'sequential_thinking']
        )
        
        # Architect reviewer
        self.agents['architect-reviewer'] = AgentCapability(
            agent_id='architect-reviewer',
            agent_type='architect-reviewer',
            description='Expert architecture reviewer',
            primary_categories=[TaskCategory.ARCHITECTURE, TaskCategory.REVIEW],
            secondary_categories=[TaskCategory.PERFORMANCE, TaskCategory.SECURITY],
            languages=[],
            max_complexity=TaskComplexity.VERY_COMPLEX,
            can_review=True,
            can_architect=True,
            mcp_servers=['memory', 'sequential_thinking', 'ref', 'exa']
        )
        
        # Test automator
        self.agents['test-automator'] = AgentCapability(
            agent_id='test-automator',
            agent_type='test-automator',
            description='Expert test automation engineer',
            primary_categories=[TaskCategory.TESTING],
            secondary_categories=[TaskCategory.AUTOMATION, TaskCategory.INTEGRATION],
            languages=[],
            max_complexity=TaskComplexity.COMPLEX,
            can_test=True,
            mcp_servers=['memory', 'ref', 'sequential_thinking', 'exa']
        )
        
        # QA expert
        self.agents['qa-expert'] = AgentCapability(
            agent_id='qa-expert',
            agent_type='qa-expert',
            description='Expert QA engineer',
            primary_categories=[TaskCategory.TESTING, TaskCategory.REVIEW],
            secondary_categories=[TaskCategory.DOCUMENTATION],
            languages=[],
            max_complexity=TaskComplexity.COMPLEX,
            can_test=True,
            can_review=True,
            can_document=True
        )
        
        # Deployment engineer
        self.agents['deployment-engineer'] = AgentCapability(
            agent_id='deployment-engineer',
            agent_type='deployment-engineer',
            description='Expert deployment engineer',
            primary_categories=[TaskCategory.DEPLOYMENT, TaskCategory.INFRASTRUCTURE],
            secondary_categories=[TaskCategory.MONITORING, TaskCategory.AUTOMATION],
            languages=[ProgrammingLanguage.SHELL, ProgrammingLanguage.YAML],
            frameworks=[Framework.DOCKER, Framework.KUBERNETES, Framework.AWS],
            max_complexity=TaskComplexity.VERY_COMPLEX,
            can_deploy=True,
            mcp_servers=['memory', 'ref', 'sequential_thinking', 'exa']
        )
        
        # API designer
        self.agents['api-designer'] = AgentCapability(
            agent_id='api-designer',
            agent_type='api-designer',
            description='API architecture expert',
            primary_categories=[TaskCategory.API_DESIGN],
            secondary_categories=[TaskCategory.DOCUMENTATION, TaskCategory.ARCHITECTURE],
            languages=[],
            frameworks=[Framework.REST, Framework.GRAPHQL],
            max_complexity=TaskComplexity.COMPLEX,
            can_document=True,
            can_architect=True,
            mcp_servers=['memory', 'ref', 'sequential_thinking', 'exa']
        )
        
        # WebSocket engineer
        self.agents['websocket-engineer'] = AgentCapability(
            agent_id='websocket-engineer',
            agent_type='websocket-engineer',
            description='Real-time communication specialist',
            primary_categories=[TaskCategory.DEVELOPMENT],
            secondary_categories=[TaskCategory.PERFORMANCE, TaskCategory.INTEGRATION],
            languages=[ProgrammingLanguage.JAVASCRIPT, ProgrammingLanguage.TYPESCRIPT],
            frameworks=[Framework.WEBSOCKET],
            max_complexity=TaskComplexity.COMPLEX,
            mcp_servers=['memory', 'ref', 'sequential_thinking']
        )
        
        # PostgreSQL specialist
        self.agents['postgres-pro'] = AgentCapability(
            agent_id='postgres-pro',
            agent_type='postgres-pro',
            description='Expert PostgreSQL specialist',
            primary_categories=[TaskCategory.DATABASE],
            secondary_categories=[TaskCategory.PERFORMANCE, TaskCategory.MAINTENANCE],
            languages=[ProgrammingLanguage.SQL],
            frameworks=[Framework.POSTGRES],
            max_complexity=TaskComplexity.VERY_COMPLEX,
            can_debug=True,
            mcp_servers=['memory', 'ref', 'sequential_thinking']
        )
        
        # Data engineer
        self.agents['data-engineer'] = AgentCapability(
            agent_id='data-engineer',
            agent_type='data-engineer',
            description='Expert data engineer',
            primary_categories=[TaskCategory.DATA_ANALYSIS, TaskCategory.INFRASTRUCTURE],
            secondary_categories=[TaskCategory.PERFORMANCE, TaskCategory.AUTOMATION],
            languages=[ProgrammingLanguage.PYTHON, ProgrammingLanguage.SQL],
            frameworks=[Framework.PANDAS, Framework.DOCKER],
            max_complexity=TaskComplexity.VERY_COMPLEX,
            mcp_servers=['memory', 'ref', 'sequential_thinking', 'exa']
        )
        
        # Research analyst
        self.agents['research-analyst'] = AgentCapability(
            agent_id='research-analyst',
            agent_type='research-analyst',
            description='Expert research analyst',
            primary_categories=[TaskCategory.RESEARCH],
            secondary_categories=[TaskCategory.DOCUMENTATION, TaskCategory.DATA_ANALYSIS],
            languages=[],
            max_complexity=TaskComplexity.VERY_COMPLEX,
            can_research=True,
            can_document=True,
            mcp_servers=['memory', 'exa', 'sequential_thinking', 'ref']
        )
        
        # Data researcher
        self.agents['data-researcher'] = AgentCapability(
            agent_id='data-researcher',
            agent_type='data-researcher',
            description='Expert data researcher',
            primary_categories=[TaskCategory.RESEARCH, TaskCategory.DATA_ANALYSIS],
            secondary_categories=[TaskCategory.DOCUMENTATION],
            languages=[ProgrammingLanguage.PYTHON],
            frameworks=[Framework.PANDAS],
            max_complexity=TaskComplexity.COMPLEX,
            can_research=True,
            mcp_servers=['memory', 'exa', 'sequential_thinking', 'ref']
        )
        
        # Search specialist
        self.agents['search-specialist'] = AgentCapability(
            agent_id='search-specialist',
            agent_type='search-specialist',
            description='Expert search specialist',
            primary_categories=[TaskCategory.RESEARCH],
            secondary_categories=[],
            languages=[],
            max_complexity=TaskComplexity.COMPLEX,
            can_research=True,
            mcp_servers=['memory', 'exa', 'ref', 'sequential_thinking']
        )
        
        # Refactoring specialist
        self.agents['refactoring-specialist'] = AgentCapability(
            agent_id='refactoring-specialist',
            agent_type='refactoring-specialist',
            description='Expert refactoring specialist',
            primary_categories=[TaskCategory.REFACTORING],
            secondary_categories=[TaskCategory.PERFORMANCE, TaskCategory.REVIEW],
            languages=[],
            max_complexity=TaskComplexity.VERY_COMPLEX,
            can_refactor=True,
            can_review=True,
            mcp_servers=['memory', 'ref', 'sequential_thinking']
        )
        
        # Tooling engineer
        self.agents['tooling-engineer'] = AgentCapability(
            agent_id='tooling-engineer',
            agent_type='tooling-engineer',
            description='Expert tooling engineer',
            primary_categories=[TaskCategory.AUTOMATION, TaskCategory.DEVELOPMENT],
            secondary_categories=[TaskCategory.INTEGRATION],
            languages=[ProgrammingLanguage.PYTHON, ProgrammingLanguage.JAVASCRIPT],
            max_complexity=TaskComplexity.COMPLEX,
            mcp_servers=['memory', 'ref', 'sequential_thinking', 'exa']
        )
        
        # FinTech engineer
        self.agents['fintech-engineer'] = AgentCapability(
            agent_id='fintech-engineer',
            agent_type='fintech-engineer',
            description='Expert fintech engineer',
            primary_categories=[TaskCategory.DEVELOPMENT, TaskCategory.SECURITY],
            secondary_categories=[TaskCategory.INTEGRATION, TaskCategory.PERFORMANCE],
            languages=[ProgrammingLanguage.PYTHON, ProgrammingLanguage.JAVA],
            max_complexity=TaskComplexity.VERY_COMPLEX,
            mcp_servers=['memory', 'ref', 'sequential_thinking']
        )
        
        # Quantitative analyst
        self.agents['quant-analyst'] = AgentCapability(
            agent_id='quant-analyst',
            agent_type='quant-analyst',
            description='Expert quantitative analyst',
            primary_categories=[TaskCategory.DATA_ANALYSIS],
            secondary_categories=[TaskCategory.RESEARCH, TaskCategory.PERFORMANCE],
            languages=[ProgrammingLanguage.PYTHON],
            frameworks=[Framework.PANDAS, Framework.NUMPY],
            max_complexity=TaskComplexity.VERY_COMPLEX,
            can_research=True
        )
        
        # Product manager
        self.agents['product-manager'] = AgentCapability(
            agent_id='product-manager',
            agent_type='product-manager',
            description='Expert product manager',
            primary_categories=[TaskCategory.DOCUMENTATION],
            secondary_categories=[TaskCategory.RESEARCH],
            languages=[],
            max_complexity=TaskComplexity.COMPLEX,
            can_document=True,
            can_research=True
        )
        
        # UX researcher
        self.agents['ux-researcher'] = AgentCapability(
            agent_id='ux-researcher',
            agent_type='ux-researcher',
            description='Expert UX researcher',
            primary_categories=[TaskCategory.UI_UX, TaskCategory.RESEARCH],
            secondary_categories=[TaskCategory.DOCUMENTATION],
            languages=[],
            max_complexity=TaskComplexity.COMPLEX,
            can_research=True,
            can_document=True,
            mcp_servers=['memory', 'exa', 'sequential_thinking', 'shadcn_ui']
        )
        
        # AI engineer
        self.agents['ai-engineer'] = AgentCapability(
            agent_id='ai-engineer',
            agent_type='ai-engineer',
            description='Expert AI engineer',
            primary_categories=[TaskCategory.DEVELOPMENT, TaskCategory.DATA_ANALYSIS],
            secondary_categories=[TaskCategory.RESEARCH, TaskCategory.PERFORMANCE],
            languages=[ProgrammingLanguage.PYTHON],
            frameworks=[Framework.TENSORFLOW, Framework.PYTORCH],
            max_complexity=TaskComplexity.VERY_COMPLEX,
            can_research=True,
            mcp_servers=['memory', 'exa', 'sequential_thinking', 'ref']
        )
        
        # Futures tick data specialist
        self.agents['futures-tick-data-specialist'] = AgentCapability(
            agent_id='futures-tick-data-specialist',
            agent_type='futures-tick-data-specialist',
            description='Expert in Level 1 & Level 2 futures tick data',
            primary_categories=[TaskCategory.DATA_ANALYSIS],
            secondary_categories=[TaskCategory.PERFORMANCE, TaskCategory.RESEARCH],
            languages=[ProgrammingLanguage.PYTHON],
            frameworks=[Framework.PANDAS, Framework.NUMPY],
            max_complexity=TaskComplexity.VERY_COMPLEX,
            can_research=True
        )
        
        # Rust engineer
        self.agents['rust-engineer'] = AgentCapability(
            agent_id='rust-engineer',
            agent_type='rust-engineer',
            description='Expert Rust developer specializing in systems programming',
            primary_categories=[TaskCategory.DEVELOPMENT],
            secondary_categories=[TaskCategory.PERFORMANCE, TaskCategory.SECURITY, TaskCategory.DEBUGGING, TaskCategory.REFACTORING],
            languages=[ProgrammingLanguage.RUST],
            frameworks=[],
            max_complexity=TaskComplexity.VERY_COMPLEX,
            preferred_complexity=TaskComplexity.COMPLEX,
            can_test=True,
            can_debug=True,
            can_refactor=True,
            can_document=True,
            can_architect=True,
            mcp_servers=['memory', 'ref', 'sequential_thinking'],
            success_rate=0.98,  # Rust's compile-time guarantees lead to high success
            works_well_with=['python-pro', 'debugger', 'frontend-developer', 'typescript-pro']
        )
        
        # Set up collaboration preferences
        self._setup_collaborations()
    
    def _setup_collaborations(self):
        """Set up agent collaboration preferences"""
        
        # Python agents work well together
        python_agents = ['python-pro', 'data-analyst', 'data-scientist', 
                        'data-engineer', 'ai-engineer']
        for agent_id in python_agents:
            if agent_id in self.agents:
                self.agents[agent_id].works_well_with.extend(
                    [a for a in python_agents if a != agent_id]
                )
        
        # Frontend agents work well together
        frontend_agents = ['frontend-developer', 'typescript-pro', 
                          'nextjs-developer', 'ux-researcher']
        for agent_id in frontend_agents:
            if agent_id in self.agents:
                self.agents[agent_id].works_well_with.extend(
                    [a for a in frontend_agents if a != agent_id]
                )
        
        # Testing agents complement developers
        for test_agent in ['test-automator', 'qa-expert']:
            if test_agent in self.agents:
                self.agents[test_agent].works_well_with.extend(
                    ['python-pro', 'frontend-developer', 'typescript-pro']
                )
        
        # Reviewers work with everyone
        for reviewer in ['code-reviewer', 'architect-reviewer']:
            if reviewer in self.agents:
                self.agents[reviewer].works_well_with = list(self.agents.keys())
    
    def get_agent(self, agent_id: str) -> Optional[AgentCapability]:
        """Get agent capability by ID"""
        return self.agents.get(agent_id)
    
    def get_agents_for_category(self, category: TaskCategory) -> List[AgentCapability]:
        """Get all agents that can handle a category"""
        agents = []
        for agent in self.agents.values():
            if category in agent.primary_categories or category in agent.secondary_categories:
                agents.append(agent)
        return agents
    
    def get_agents_for_language(self, language: ProgrammingLanguage) -> List[AgentCapability]:
        """Get all agents that can handle a language"""
        agents = []
        for agent in self.agents.values():
            if not agent.languages or language in agent.languages:
                agents.append(agent)
        return agents
    
    def get_agents_for_framework(self, framework: Framework) -> List[AgentCapability]:
        """Get all agents that can handle a framework"""
        agents = []
        for agent in self.agents.values():
            if not agent.frameworks or framework in agent.frameworks:
                agents.append(agent)
        return agents