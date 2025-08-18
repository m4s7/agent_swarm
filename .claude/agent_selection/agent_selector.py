"""
Automated agent selection system based on task requirements
"""

import logging
from typing import Dict, List, Set, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent_selection.task_classifier import (
    TaskClassifier, TaskFeatures, TaskCategory, 
    TaskComplexity, ProgrammingLanguage
)
from agent_selection.agent_capabilities import (
    AgentCapabilityMatrix, AgentCapability
)


class SelectionStrategy(Enum):
    """Agent selection strategies"""
    BEST_MATCH = "best_match"           # Single best agent
    SPECIALIZED_TEAM = "specialized_team"  # Multiple specialists
    REDUNDANT_TEAM = "redundant_team"    # Multiple agents for reliability
    MINIMAL_TEAM = "minimal_team"        # Minimum agents needed
    FULL_TEAM = "full_team"              # All relevant agents


@dataclass
class AgentScore:
    """Score for an agent-task match"""
    agent_id: str
    match_score: float  # 0.0 to 1.0
    confidence: float   # 0.0 to 1.0
    reasons: List[str] = field(default_factory=list)
    penalties: List[str] = field(default_factory=list)
    
    @property
    def final_score(self) -> float:
        """Calculate final score with confidence"""
        return self.match_score * self.confidence


@dataclass
class TeamComposition:
    """Recommended team of agents for a task"""
    primary_agents: List[str]      # Main agents for the task
    support_agents: List[str]       # Supporting agents
    review_agents: List[str]        # Review and QA agents
    total_agents: int
    estimated_time: float           # Relative time estimate
    confidence: float               # Team confidence score
    reasoning: str                  # Explanation of selection
    workflow_suggestion: str        # Suggested workflow type
    
    def get_all_agents(self) -> List[str]:
        """Get all agents in the team"""
        all_agents = []
        all_agents.extend(self.primary_agents)
        all_agents.extend(self.support_agents)
        all_agents.extend(self.review_agents)
        # Remove duplicates while preserving order
        seen = set()
        return [x for x in all_agents if not (x in seen or seen.add(x))]


class AgentSelector:
    """Intelligent agent selection based on task requirements"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.task_classifier = TaskClassifier()
        self.capability_matrix = AgentCapabilityMatrix()
        
        # Selection history for learning
        self.selection_history: List[Tuple[TaskFeatures, TeamComposition]] = []
        
        # Performance tracking
        self.agent_performance: Dict[str, Dict[str, float]] = {}
    
    def select_agents(self, 
                      task_description: str,
                      strategy: SelectionStrategy = SelectionStrategy.SPECIALIZED_TEAM,
                      context: Optional[Dict[str, Any]] = None) -> TeamComposition:
        """
        Select agents for a task
        
        Args:
            task_description: Natural language task description
            strategy: Selection strategy to use
            context: Additional context
        
        Returns:
            TeamComposition with recommended agents
        """
        
        # Classify the task
        features = self.task_classifier.classify_task(task_description, context)
        
        self.logger.info(f"Task classified: {features.categories}, "
                        f"complexity: {features.complexity.value}")
        
        # Score all agents
        agent_scores = self._score_agents(features)
        
        # Select team based on strategy
        if strategy == SelectionStrategy.BEST_MATCH:
            team = self._select_best_match(agent_scores, features)
        elif strategy == SelectionStrategy.SPECIALIZED_TEAM:
            team = self._select_specialized_team(agent_scores, features)
        elif strategy == SelectionStrategy.REDUNDANT_TEAM:
            team = self._select_redundant_team(agent_scores, features)
        elif strategy == SelectionStrategy.MINIMAL_TEAM:
            team = self._select_minimal_team(agent_scores, features)
        else:  # FULL_TEAM
            team = self._select_full_team(agent_scores, features)
        
        # Add to history
        self.selection_history.append((features, team))
        
        self.logger.info(f"Selected {team.total_agents} agents: "
                        f"Primary: {team.primary_agents}")
        
        return team
    
    def _score_agents(self, features: TaskFeatures) -> List[AgentScore]:
        """Score all agents for task features"""
        scores = []
        
        for agent_id, agent in self.capability_matrix.agents.items():
            # Calculate base match score
            match_score = agent.matches_task(features)
            
            # Initialize score
            score = AgentScore(
                agent_id=agent_id,
                match_score=match_score,
                confidence=features.confidence
            )
            
            # Add reasoning
            if match_score > 0.8:
                score.reasons.append("Excellent match for task requirements")
            elif match_score > 0.6:
                score.reasons.append("Good match for task requirements")
            elif match_score > 0.4:
                score.reasons.append("Moderate match for task requirements")
            
            # Check specific matches
            for category in features.categories:
                if category in agent.primary_categories:
                    score.reasons.append(f"Primary expertise in {category.value}")
                elif category in agent.secondary_categories:
                    score.reasons.append(f"Secondary expertise in {category.value}")
            
            # Language matches
            if features.languages:
                matching_langs = set(features.languages) & set(agent.languages)
                if matching_langs:
                    lang_names = [l.value for l in matching_langs]
                    score.reasons.append(f"Proficient in {', '.join(lang_names)}")
            
            # Apply performance-based adjustments
            if agent_id in self.agent_performance:
                perf = self.agent_performance[agent_id]
                if 'success_rate' in perf:
                    # Boost score for high performers
                    if perf['success_rate'] > 0.95:
                        score.match_score *= 1.1
                        score.reasons.append("High historical success rate")
                    elif perf['success_rate'] < 0.8:
                        score.match_score *= 0.9
                        score.penalties.append("Lower historical success rate")
            
            # Complexity penalties
            if features.complexity.value > agent.max_complexity.value:
                score.match_score *= 0.5
                score.penalties.append("Task complexity exceeds agent capability")
            
            # Cap score at 1.0
            score.match_score = min(1.0, score.match_score)
            
            scores.append(score)
        
        # Sort by final score
        scores.sort(key=lambda x: x.final_score, reverse=True)
        
        return scores
    
    def _select_best_match(self, 
                          scores: List[AgentScore],
                          features: TaskFeatures) -> TeamComposition:
        """Select single best matching agent"""
        
        if not scores:
            return self._create_empty_team("No agents available")
        
        best_agent = scores[0]
        
        team = TeamComposition(
            primary_agents=[best_agent.agent_id],
            support_agents=[],
            review_agents=[],
            total_agents=1,
            estimated_time=1.0,
            confidence=best_agent.final_score,
            reasoning=f"Best match: {best_agent.agent_id} "
                     f"(score: {best_agent.final_score:.2f})",
            workflow_suggestion="single-agent"
        )
        
        # Add reviewer if needed and different agent available
        if features.requires_review and len(scores) > 1:
            for score in scores[1:]:
                agent = self.capability_matrix.get_agent(score.agent_id)
                if agent and agent.can_review:
                    team.review_agents.append(score.agent_id)
                    team.total_agents += 1
                    break
        
        return team
    
    def _select_specialized_team(self,
                                scores: List[AgentScore],
                                features: TaskFeatures) -> TeamComposition:
        """Select team of specialists for different aspects"""
        
        primary_agents = []
        support_agents = []
        review_agents = []
        used_agents = set()
        
        # Select primary agents for each category
        for category in features.categories[:3]:  # Limit to top 3 categories
            # Find best agent for this category
            for score in scores:
                if score.agent_id in used_agents:
                    continue
                
                agent = self.capability_matrix.get_agent(score.agent_id)
                if agent and category in agent.primary_categories:
                    primary_agents.append(score.agent_id)
                    used_agents.add(score.agent_id)
                    break
        
        # If no specialists found, use best overall
        if not primary_agents and scores:
            primary_agents.append(scores[0].agent_id)
            used_agents.add(scores[0].agent_id)
        
        # Add support agents for specific needs
        if features.requires_testing:
            self._add_specialist(scores, used_agents, support_agents, 'can_test')
        
        if features.requires_documentation:
            self._add_specialist(scores, used_agents, support_agents, 'can_document')
        
        if features.requires_deployment:
            self._add_specialist(scores, used_agents, support_agents, 'can_deploy')
        
        # Add reviewer if needed
        if features.requires_review:
            self._add_specialist(scores, used_agents, review_agents, 'can_review')
        
        # Calculate team metrics
        total_agents = len(primary_agents) + len(support_agents) + len(review_agents)
        avg_score = sum(s.final_score for s in scores[:total_agents]) / max(total_agents, 1)
        
        # Suggest workflow based on team size
        if total_agents == 1:
            workflow = "single-agent"
        elif total_agents <= 3:
            workflow = "sequential-collaboration"
        else:
            workflow = "parallel-collaboration"
        
        return TeamComposition(
            primary_agents=primary_agents,
            support_agents=support_agents,
            review_agents=review_agents,
            total_agents=total_agents,
            estimated_time=self._estimate_time(features, total_agents),
            confidence=avg_score,
            reasoning=self._generate_team_reasoning(primary_agents, support_agents, review_agents),
            workflow_suggestion=workflow
        )
    
    def _select_redundant_team(self,
                              scores: List[AgentScore],
                              features: TaskFeatures) -> TeamComposition:
        """Select redundant agents for reliability"""
        
        primary_agents = []
        used_categories = set()
        
        # Select top 2-3 agents per category for redundancy
        for category in features.categories[:2]:  # Focus on top 2 categories
            agents_for_category = []
            
            for score in scores:
                if score.final_score < 0.5:  # Minimum threshold
                    break
                
                agent = self.capability_matrix.get_agent(score.agent_id)
                if agent and category in agent.primary_categories:
                    agents_for_category.append(score.agent_id)
                    
                    if len(agents_for_category) >= 2:  # 2 agents per category
                        break
            
            primary_agents.extend(agents_for_category)
            if agents_for_category:
                used_categories.add(category)
        
        # Remove duplicates
        primary_agents = list(dict.fromkeys(primary_agents))
        
        # Add reviewer
        review_agents = []
        if features.requires_review:
            for score in scores:
                if score.agent_id not in primary_agents:
                    agent = self.capability_matrix.get_agent(score.agent_id)
                    if agent and agent.can_review:
                        review_agents.append(score.agent_id)
                        break
        
        total_agents = len(primary_agents) + len(review_agents)
        
        return TeamComposition(
            primary_agents=primary_agents,
            support_agents=[],
            review_agents=review_agents,
            total_agents=total_agents,
            estimated_time=self._estimate_time(features, total_agents) * 0.8,  # Faster with redundancy
            confidence=min(0.95, scores[0].final_score * 1.2),  # Higher confidence
            reasoning=f"Redundant team for reliability with {len(primary_agents)} primary agents",
            workflow_suggestion="parallel-redundant"
        )
    
    def _select_minimal_team(self,
                           scores: List[AgentScore],
                           features: TaskFeatures) -> TeamComposition:
        """Select minimum agents needed"""
        
        # Find one agent that covers most requirements
        best_agent = None
        best_coverage = 0
        
        for score in scores:
            if score.final_score < 0.4:  # Minimum threshold
                continue
            
            agent = self.capability_matrix.get_agent(score.agent_id)
            if not agent:
                continue
            
            # Calculate requirement coverage
            coverage = 0
            for category in features.categories:
                if category in agent.primary_categories:
                    coverage += 1
                elif category in agent.secondary_categories:
                    coverage += 0.5
            
            # Check special requirements
            if features.requires_testing and agent.can_test:
                coverage += 1
            if features.requires_review and agent.can_review:
                coverage += 1
            if features.requires_deployment and agent.can_deploy:
                coverage += 1
            
            if coverage > best_coverage:
                best_coverage = coverage
                best_agent = score.agent_id
        
        if not best_agent and scores:
            best_agent = scores[0].agent_id
        
        primary_agents = [best_agent] if best_agent else []
        
        return TeamComposition(
            primary_agents=primary_agents,
            support_agents=[],
            review_agents=[],
            total_agents=len(primary_agents),
            estimated_time=self._estimate_time(features, 1),
            confidence=scores[0].final_score if scores else 0.0,
            reasoning=f"Minimal team with {best_agent or 'no agent'}",
            workflow_suggestion="single-agent"
        )
    
    def _select_full_team(self,
                         scores: List[AgentScore],
                         features: TaskFeatures) -> TeamComposition:
        """Select all relevant agents"""
        
        primary_agents = []
        support_agents = []
        review_agents = []
        
        # Add all agents with reasonable scores
        for score in scores:
            if score.final_score < 0.3:  # Minimum relevance threshold
                break
            
            agent = self.capability_matrix.get_agent(score.agent_id)
            if not agent:
                continue
            
            # Categorize by role
            if any(cat in agent.primary_categories for cat in features.categories):
                if len(primary_agents) < 5:  # Limit primary agents
                    primary_agents.append(score.agent_id)
                else:
                    support_agents.append(score.agent_id)
            elif agent.can_review and features.requires_review:
                review_agents.append(score.agent_id)
            elif len(support_agents) < 5:  # Limit support agents
                support_agents.append(score.agent_id)
        
        total_agents = len(primary_agents) + len(support_agents) + len(review_agents)
        
        return TeamComposition(
            primary_agents=primary_agents,
            support_agents=support_agents,
            review_agents=review_agents,
            total_agents=total_agents,
            estimated_time=self._estimate_time(features, total_agents) * 1.5,  # Slower with many agents
            confidence=min(0.9, scores[0].final_score) if scores else 0.0,
            reasoning=f"Full team with {total_agents} agents for comprehensive coverage",
            workflow_suggestion="team-orchestration"
        )
    
    def _add_specialist(self,
                       scores: List[AgentScore],
                       used_agents: Set[str],
                       target_list: List[str],
                       capability: str):
        """Add a specialist agent with specific capability"""
        
        for score in scores:
            if score.agent_id in used_agents:
                continue
            
            agent = self.capability_matrix.get_agent(score.agent_id)
            if agent and getattr(agent, capability, False):
                target_list.append(score.agent_id)
                used_agents.add(score.agent_id)
                break
    
    def _estimate_time(self, features: TaskFeatures, agent_count: int) -> float:
        """Estimate relative completion time"""
        
        # Base time from complexity
        if features.complexity == TaskComplexity.TRIVIAL:
            base_time = 0.2
        elif features.complexity == TaskComplexity.SIMPLE:
            base_time = 0.5
        elif features.complexity == TaskComplexity.MODERATE:
            base_time = 1.0
        elif features.complexity == TaskComplexity.COMPLEX:
            base_time = 2.0
        else:  # VERY_COMPLEX
            base_time = 3.0
        
        # Adjust for agent count (diminishing returns)
        if agent_count == 1:
            time_multiplier = 1.0
        elif agent_count == 2:
            time_multiplier = 0.7
        elif agent_count == 3:
            time_multiplier = 0.6
        elif agent_count <= 5:
            time_multiplier = 0.5
        else:
            time_multiplier = 0.6  # Too many agents cause overhead
        
        return base_time * time_multiplier
    
    def _generate_team_reasoning(self,
                                primary: List[str],
                                support: List[str],
                                review: List[str]) -> str:
        """Generate reasoning for team selection"""
        
        parts = []
        
        if primary:
            parts.append(f"Primary: {', '.join(primary)}")
        
        if support:
            parts.append(f"Support: {', '.join(support)}")
        
        if review:
            parts.append(f"Review: {', '.join(review)}")
        
        return "Specialized team - " + "; ".join(parts)
    
    def _create_empty_team(self, reason: str) -> TeamComposition:
        """Create empty team composition"""
        return TeamComposition(
            primary_agents=[],
            support_agents=[],
            review_agents=[],
            total_agents=0,
            estimated_time=0.0,
            confidence=0.0,
            reasoning=reason,
            workflow_suggestion="none"
        )
    
    def update_agent_performance(self, 
                                agent_id: str,
                                success: bool,
                                time_taken: Optional[float] = None):
        """Update agent performance metrics"""
        
        if agent_id not in self.agent_performance:
            self.agent_performance[agent_id] = {
                'total_tasks': 0,
                'successful_tasks': 0,
                'success_rate': 1.0,
                'avg_time': 1.0
            }
        
        perf = self.agent_performance[agent_id]
        perf['total_tasks'] += 1
        
        if success:
            perf['successful_tasks'] += 1
        
        perf['success_rate'] = perf['successful_tasks'] / perf['total_tasks']
        
        if time_taken is not None:
            # Update average time (exponential moving average)
            alpha = 0.3  # Weight for new observation
            perf['avg_time'] = alpha * time_taken + (1 - alpha) * perf['avg_time']
        
        self.logger.info(f"Updated performance for {agent_id}: "
                        f"success_rate={perf['success_rate']:.2f}")
    
    def get_selection_statistics(self) -> Dict[str, Any]:
        """Get statistics about agent selection"""
        
        if not self.selection_history:
            return {}
        
        stats = {
            'total_selections': len(self.selection_history),
            'avg_team_size': 0,
            'category_frequency': {},
            'agent_frequency': {},
            'workflow_distribution': {}
        }
        
        total_agents = 0
        all_agents = []
        
        for features, team in self.selection_history:
            # Team size
            total_agents += team.total_agents
            
            # Categories
            for category in features.categories:
                cat_name = category.value
                stats['category_frequency'][cat_name] = \
                    stats['category_frequency'].get(cat_name, 0) + 1
            
            # Agents
            for agent in team.get_all_agents():
                all_agents.append(agent)
                stats['agent_frequency'][agent] = \
                    stats['agent_frequency'].get(agent, 0) + 1
            
            # Workflows
            workflow = team.workflow_suggestion
            stats['workflow_distribution'][workflow] = \
                stats['workflow_distribution'].get(workflow, 0) + 1
        
        stats['avg_team_size'] = total_agents / len(self.selection_history)
        
        # Most used agents
        if all_agents:
            from collections import Counter
            agent_counts = Counter(all_agents)
            stats['top_agents'] = agent_counts.most_common(5)
        
        return stats