"""
Automated agent selection system
"""

from .task_classifier import (
    TaskClassifier,
    TaskCategory,
    TaskComplexity,
    ProgrammingLanguage,
    Framework,
    TaskFeatures
)

from .agent_capabilities import (
    AgentCapability,
    AgentCapabilityMatrix
)

from .agent_selector import (
    AgentSelector,
    SelectionStrategy,
    AgentScore,
    TeamComposition
)

__all__ = [
    # Task classification
    'TaskClassifier',
    'TaskCategory',
    'TaskComplexity',
    'ProgrammingLanguage',
    'Framework',
    'TaskFeatures',
    
    # Agent capabilities
    'AgentCapability',
    'AgentCapabilityMatrix',
    
    # Agent selection
    'AgentSelector',
    'SelectionStrategy',
    'AgentScore',
    'TeamComposition'
]