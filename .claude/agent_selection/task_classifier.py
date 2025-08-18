"""
Task classification system for automated agent selection
"""

import re
import json
import logging
from typing import Dict, List, Set, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TaskCategory(Enum):
    """High-level task categories"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    DEBUGGING = "debugging"
    REFACTORING = "refactoring"
    ARCHITECTURE = "architecture"
    DATA_ANALYSIS = "data_analysis"
    RESEARCH = "research"
    DEPLOYMENT = "deployment"
    DOCUMENTATION = "documentation"
    SECURITY = "security"
    PERFORMANCE = "performance"
    UI_UX = "ui_ux"
    API_DESIGN = "api_design"
    DATABASE = "database"
    INFRASTRUCTURE = "infrastructure"
    REVIEW = "review"
    AUTOMATION = "automation"
    INTEGRATION = "integration"
    MONITORING = "monitoring"
    MAINTENANCE = "maintenance"


class TaskComplexity(Enum):
    """Task complexity levels"""
    TRIVIAL = "trivial"      # Single file, simple change
    SIMPLE = "simple"        # Few files, straightforward logic
    MODERATE = "moderate"    # Multiple files, some complexity
    COMPLEX = "complex"      # Many files, complex logic
    VERY_COMPLEX = "very_complex"  # System-wide, architectural changes


class ProgrammingLanguage(Enum):
    """Programming languages"""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    GO = "go"
    RUST = "rust"
    CPP = "cpp"
    CSHARP = "csharp"
    RUBY = "ruby"
    PHP = "php"
    SWIFT = "swift"
    KOTLIN = "kotlin"
    SQL = "sql"
    SHELL = "shell"
    HTML_CSS = "html_css"
    YAML = "yaml"
    JSON = "json"
    MARKDOWN = "markdown"
    UNKNOWN = "unknown"


class Framework(Enum):
    """Common frameworks and libraries"""
    REACT = "react"
    NEXTJS = "nextjs"
    VUE = "vue"
    ANGULAR = "angular"
    DJANGO = "django"
    FLASK = "flask"
    FASTAPI = "fastapi"
    EXPRESS = "express"
    SPRING = "spring"
    RAILS = "rails"
    LARAVEL = "laravel"
    TENSORFLOW = "tensorflow"
    PYTORCH = "pytorch"
    PANDAS = "pandas"
    NUMPY = "numpy"
    DOCKER = "docker"
    KUBERNETES = "kubernetes"
    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"
    POSTGRES = "postgres"
    MONGODB = "mongodb"
    REDIS = "redis"
    GRAPHQL = "graphql"
    REST = "rest"
    WEBSOCKET = "websocket"


@dataclass
class TaskFeatures:
    """Features extracted from a task description"""
    categories: List[TaskCategory]
    complexity: TaskComplexity
    languages: List[ProgrammingLanguage]
    frameworks: List[Framework]
    keywords: List[str]
    file_patterns: List[str]
    requires_testing: bool
    requires_review: bool
    requires_deployment: bool
    requires_documentation: bool
    is_bug_fix: bool
    is_new_feature: bool
    is_refactoring: bool
    is_research: bool
    estimated_files: int
    has_database: bool
    has_api: bool
    has_ui: bool
    has_security_implications: bool
    confidence: float  # 0.0 to 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result['categories'] = [c.value for c in self.categories]
        result['complexity'] = self.complexity.value
        result['languages'] = [l.value for l in self.languages]
        result['frameworks'] = [f.value for f in self.frameworks]
        return result


class TaskClassifier:
    """Classifies tasks to determine required agents and workflow"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Load classification patterns
        self._load_patterns()
        
        # Task history for learning
        self.task_history: List[Tuple[str, TaskFeatures]] = []
    
    def _load_patterns(self):
        """Load classification patterns"""
        
        # Category keywords
        self.category_patterns = {
            TaskCategory.DEVELOPMENT: [
                'implement', 'create', 'build', 'develop', 'add', 'feature',
                'functionality', 'component', 'module', 'service', 'endpoint'
            ],
            TaskCategory.TESTING: [
                'test', 'testing', 'unit test', 'integration test', 'coverage',
                'spec', 'pytest', 'jest', 'mocha', 'assert', 'verify'
            ],
            TaskCategory.DEBUGGING: [
                'debug', 'fix', 'bug', 'error', 'issue', 'problem', 'crash',
                'exception', 'failing', 'broken', 'not working', 'investigate'
            ],
            TaskCategory.REFACTORING: [
                'refactor', 'optimize', 'improve', 'clean up', 'reorganize',
                'restructure', 'simplify', 'extract', 'rename', 'move'
            ],
            TaskCategory.ARCHITECTURE: [
                'architecture', 'design', 'structure', 'pattern', 'system',
                'scalability', 'microservice', 'monolith', 'distributed'
            ],
            TaskCategory.DATA_ANALYSIS: [
                'analyze', 'data', 'statistics', 'metrics', 'report', 'visualization',
                'pandas', 'numpy', 'matplotlib', 'dashboard', 'insights'
            ],
            TaskCategory.RESEARCH: [
                'research', 'investigate', 'explore', 'find', 'search', 'understand',
                'learn', 'study', 'compare', 'evaluate', 'assess'
            ],
            TaskCategory.DEPLOYMENT: [
                'deploy', 'deployment', 'release', 'production', 'staging',
                'ci/cd', 'pipeline', 'docker', 'kubernetes', 'aws', 'azure'
            ],
            TaskCategory.DOCUMENTATION: [
                'document', 'documentation', 'readme', 'docs', 'comment',
                'explain', 'describe', 'guide', 'tutorial', 'api docs'
            ],
            TaskCategory.SECURITY: [
                'security', 'vulnerability', 'authentication', 'authorization',
                'encryption', 'csrf', 'xss', 'sql injection', 'owasp', 'audit'
            ],
            TaskCategory.PERFORMANCE: [
                'performance', 'optimization', 'speed', 'faster', 'slow',
                'latency', 'throughput', 'memory', 'cpu', 'profiling'
            ],
            TaskCategory.UI_UX: [
                'ui', 'ux', 'interface', 'design', 'layout', 'style', 'css',
                'responsive', 'accessibility', 'user experience', 'frontend'
            ],
            TaskCategory.API_DESIGN: [
                'api', 'endpoint', 'rest', 'graphql', 'grpc', 'swagger',
                'openapi', 'schema', 'route', 'controller', 'webhook'
            ],
            TaskCategory.DATABASE: [
                'database', 'sql', 'query', 'migration', 'schema', 'table',
                'index', 'postgres', 'mysql', 'mongodb', 'redis', 'orm'
            ],
            TaskCategory.REVIEW: [
                'review', 'code review', 'pr review', 'check', 'validate',
                'approve', 'feedback', 'suggestion', 'quality', 'standards'
            ]
        }
        
        # Language patterns
        self.language_patterns = {
            ProgrammingLanguage.PYTHON: [
                '.py', 'python', 'django', 'flask', 'fastapi', 'pandas', 'numpy',
                'pip', 'pytest', 'pyenv', 'poetry', '__init__', 'def ', 'import '
            ],
            ProgrammingLanguage.JAVASCRIPT: [
                '.js', 'javascript', 'node', 'npm', 'express', 'react', 'vue',
                'angular', 'webpack', 'babel', 'eslint', 'const ', 'let ', 'var '
            ],
            ProgrammingLanguage.TYPESCRIPT: [
                '.ts', '.tsx', 'typescript', 'interface', 'type', 'enum',
                'tsc', 'tsconfig', 'nextjs', ': string', ': number', ': boolean'
            ],
            ProgrammingLanguage.JAVA: [
                '.java', 'java', 'spring', 'maven', 'gradle', 'junit',
                'public class', 'private', 'protected', 'extends', 'implements'
            ],
            ProgrammingLanguage.GO: [
                '.go', 'golang', 'go mod', 'package main', 'func', 'goroutine',
                'channel', 'defer', 'fmt.', 'gin', 'echo'
            ],
            ProgrammingLanguage.RUST: [
                '.rs', 'rust', 'cargo', 'rustc', 'fn ', 'let ', 'mut ', 'struct ',
                'impl ', 'trait ', 'enum ', 'match ', 'Result<', 'Option<', 
                'Vec<', 'String', 'Box<', 'Arc<', 'Mutex<', 'async fn', 'await',
                'tokio', 'serde', 'clap', '&str', 'unsafe ', 'lifetime', 'borrow'
            ],
            ProgrammingLanguage.SQL: [
                '.sql', 'select', 'insert', 'update', 'delete', 'join',
                'where', 'group by', 'order by', 'create table', 'alter'
            ]
        }
        
        # Framework patterns
        self.framework_patterns = {
            Framework.REACT: ['react', 'jsx', 'usestate', 'useeffect', 'component'],
            Framework.NEXTJS: ['next.js', 'nextjs', 'getserversideprops', 'app router'],
            Framework.DJANGO: ['django', 'models.py', 'views.py', 'urls.py', 'manage.py'],
            Framework.FASTAPI: ['fastapi', 'pydantic', 'uvicorn', '@app.'],
            Framework.DOCKER: ['docker', 'dockerfile', 'docker-compose', 'container'],
            Framework.KUBERNETES: ['kubernetes', 'k8s', 'kubectl', 'pod', 'deployment'],
            Framework.POSTGRES: ['postgres', 'postgresql', 'psql', 'pg_'],
            Framework.MONGODB: ['mongodb', 'mongoose', 'collection', 'document']
        }
        
        # Rust-specific patterns (can be expanded to full Framework enum later)
        self.rust_frameworks = [
            'tokio', 'async-std', 'serde', 'clap', 'rocket', 'axum', 'warp',
            'diesel', 'sqlx', 'reqwest', 'hyper', 'tonic', 'wasm-bindgen',
            'yew', 'bevy', 'actix-web', 'tauri', 'crossbeam', 'rayon'
        ]
        
        # Complexity indicators
        self.complexity_indicators = {
            'trivial': ['simple', 'basic', 'quick', 'minor', 'small', 'typo'],
            'simple': ['straightforward', 'easy', 'single', 'one'],
            'moderate': ['several', 'multiple', 'some', 'few'],
            'complex': ['complex', 'complicated', 'many', 'large', 'significant'],
            'very_complex': ['entire', 'system', 'architecture', 'redesign', 'major']
        }
    
    def classify_task(self, task_description: str, context: Optional[Dict[str, Any]] = None) -> TaskFeatures:
        """
        Classify a task based on its description and context
        
        Args:
            task_description: Natural language description of the task
            context: Additional context (files, current state, etc.)
        
        Returns:
            TaskFeatures object with classification results
        """
        
        # Normalize text for analysis
        text_lower = task_description.lower()
        
        # Extract categories
        categories = self._extract_categories(text_lower)
        
        # Determine complexity
        complexity = self._determine_complexity(text_lower, context)
        
        # Extract languages
        languages = self._extract_languages(text_lower, context)
        
        # Extract frameworks
        frameworks = self._extract_frameworks(text_lower, context)
        
        # Extract keywords
        keywords = self._extract_keywords(task_description)
        
        # Extract file patterns
        file_patterns = self._extract_file_patterns(task_description, context)
        
        # Determine task characteristics
        requires_testing = self._requires_testing(text_lower, categories)
        requires_review = self._requires_review(text_lower, complexity)
        requires_deployment = TaskCategory.DEPLOYMENT in categories
        requires_documentation = self._requires_documentation(text_lower, categories)
        
        # Determine task type
        is_bug_fix = TaskCategory.DEBUGGING in categories or 'fix' in text_lower
        is_new_feature = TaskCategory.DEVELOPMENT in categories and 'new' in text_lower
        is_refactoring = TaskCategory.REFACTORING in categories
        is_research = TaskCategory.RESEARCH in categories
        
        # Estimate scope
        estimated_files = self._estimate_file_count(text_lower, complexity)
        
        # Check for specific components
        has_database = TaskCategory.DATABASE in categories or any(
            keyword in text_lower for keyword in ['database', 'sql', 'query', 'table']
        )
        has_api = TaskCategory.API_DESIGN in categories or 'api' in text_lower
        has_ui = TaskCategory.UI_UX in categories or any(
            keyword in text_lower for keyword in ['ui', 'frontend', 'interface', 'component']
        )
        has_security_implications = TaskCategory.SECURITY in categories or any(
            keyword in text_lower for keyword in ['security', 'auth', 'permission', 'sensitive']
        )
        
        # Calculate confidence
        confidence = self._calculate_confidence(categories, languages, frameworks)
        
        # Create features object
        features = TaskFeatures(
            categories=categories,
            complexity=complexity,
            languages=languages,
            frameworks=frameworks,
            keywords=keywords,
            file_patterns=file_patterns,
            requires_testing=requires_testing,
            requires_review=requires_review,
            requires_deployment=requires_deployment,
            requires_documentation=requires_documentation,
            is_bug_fix=is_bug_fix,
            is_new_feature=is_new_feature,
            is_refactoring=is_refactoring,
            is_research=is_research,
            estimated_files=estimated_files,
            has_database=has_database,
            has_api=has_api,
            has_ui=has_ui,
            has_security_implications=has_security_implications,
            confidence=confidence
        )
        
        # Add to history for learning
        self.task_history.append((task_description, features))
        
        self.logger.info(f"Task classified: {categories}, complexity: {complexity.value}")
        
        return features
    
    def _extract_categories(self, text: str) -> List[TaskCategory]:
        """Extract task categories from text"""
        categories = []
        
        for category, keywords in self.category_patterns.items():
            if any(keyword in text for keyword in keywords):
                categories.append(category)
        
        # Default to development if no category found
        if not categories:
            categories.append(TaskCategory.DEVELOPMENT)
        
        return categories
    
    def _determine_complexity(self, text: str, context: Optional[Dict[str, Any]]) -> TaskComplexity:
        """Determine task complexity"""
        
        # Check for explicit complexity indicators
        for level, indicators in self.complexity_indicators.items():
            if any(indicator in text for indicator in indicators):
                if level == 'trivial':
                    return TaskComplexity.TRIVIAL
                elif level == 'simple':
                    return TaskComplexity.SIMPLE
                elif level == 'moderate':
                    return TaskComplexity.MODERATE
                elif level == 'complex':
                    return TaskComplexity.COMPLEX
                elif level == 'very_complex':
                    return TaskComplexity.VERY_COMPLEX
        
        # Check context for file count
        if context and 'files' in context:
            file_count = len(context['files'])
            if file_count == 1:
                return TaskComplexity.SIMPLE
            elif file_count <= 3:
                return TaskComplexity.MODERATE
            elif file_count <= 10:
                return TaskComplexity.COMPLEX
            else:
                return TaskComplexity.VERY_COMPLEX
        
        # Default based on word count and structure
        word_count = len(text.split())
        if word_count < 20:
            return TaskComplexity.SIMPLE
        elif word_count < 50:
            return TaskComplexity.MODERATE
        else:
            return TaskComplexity.COMPLEX
    
    def _extract_languages(self, text: str, context: Optional[Dict[str, Any]]) -> List[ProgrammingLanguage]:
        """Extract programming languages"""
        languages = []
        
        # Check text for language patterns
        for language, patterns in self.language_patterns.items():
            if any(pattern in text for pattern in patterns):
                languages.append(language)
        
        # Check context for file extensions
        if context and 'files' in context:
            for file in context['files']:
                ext = Path(file).suffix.lower()
                if ext == '.py':
                    if ProgrammingLanguage.PYTHON not in languages:
                        languages.append(ProgrammingLanguage.PYTHON)
                elif ext in ['.js', '.jsx']:
                    if ProgrammingLanguage.JAVASCRIPT not in languages:
                        languages.append(ProgrammingLanguage.JAVASCRIPT)
                elif ext in ['.ts', '.tsx']:
                    if ProgrammingLanguage.TYPESCRIPT not in languages:
                        languages.append(ProgrammingLanguage.TYPESCRIPT)
                elif ext == '.rs':
                    if ProgrammingLanguage.RUST not in languages:
                        languages.append(ProgrammingLanguage.RUST)
        
        return languages
    
    def _extract_frameworks(self, text: str, context: Optional[Dict[str, Any]]) -> List[Framework]:
        """Extract frameworks and libraries"""
        frameworks = []
        
        for framework, patterns in self.framework_patterns.items():
            if any(pattern in text for pattern in patterns):
                frameworks.append(framework)
        
        return frameworks
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords"""
        # Simple keyword extraction - can be enhanced with NLP
        import re
        
        # Remove common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                     'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be'}
        
        # Extract words
        words = re.findall(r'\b[a-z]+\b', text.lower())
        
        # Filter and count
        word_freq = {}
        for word in words:
            if word not in stop_words and len(word) > 2:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Return top keywords
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, _ in sorted_words[:10]]
    
    def _extract_file_patterns(self, text: str, context: Optional[Dict[str, Any]]) -> List[str]:
        """Extract file patterns mentioned in task"""
        patterns = []
        
        # Look for file extensions
        import re
        ext_pattern = r'\.\w{2,4}\b'
        extensions = re.findall(ext_pattern, text)
        patterns.extend(extensions)
        
        # Look for directory patterns
        dir_patterns = ['src/', 'test/', 'tests/', 'lib/', 'components/', 'utils/']
        for pattern in dir_patterns:
            if pattern in text:
                patterns.append(pattern + '*')
        
        return patterns
    
    def _requires_testing(self, text: str, categories: List[TaskCategory]) -> bool:
        """Determine if task requires testing"""
        if TaskCategory.TESTING in categories:
            return True
        
        if any(keyword in text for keyword in ['test', 'testing', 'coverage', 'spec']):
            return True
        
        # New features and bug fixes should have tests
        if TaskCategory.DEVELOPMENT in categories or TaskCategory.DEBUGGING in categories:
            return True
        
        return False
    
    def _requires_review(self, text: str, complexity: TaskComplexity) -> bool:
        """Determine if task requires review"""
        if 'review' in text:
            return True
        
        # Complex tasks should be reviewed
        if complexity in [TaskComplexity.COMPLEX, TaskComplexity.VERY_COMPLEX]:
            return True
        
        return False
    
    def _requires_documentation(self, text: str, categories: List[TaskCategory]) -> bool:
        """Determine if task requires documentation"""
        if TaskCategory.DOCUMENTATION in categories:
            return True
        
        if any(keyword in text for keyword in ['document', 'docs', 'readme', 'comment']):
            return True
        
        # New features and APIs need documentation
        if TaskCategory.DEVELOPMENT in categories or TaskCategory.API_DESIGN in categories:
            return True
        
        return False
    
    def _estimate_file_count(self, text: str, complexity: TaskComplexity) -> int:
        """Estimate number of files affected"""
        if complexity == TaskComplexity.TRIVIAL:
            return 1
        elif complexity == TaskComplexity.SIMPLE:
            return 2
        elif complexity == TaskComplexity.MODERATE:
            return 5
        elif complexity == TaskComplexity.COMPLEX:
            return 10
        else:  # VERY_COMPLEX
            return 20
    
    def _calculate_confidence(self, 
                            categories: List[TaskCategory],
                            languages: List[ProgrammingLanguage],
                            frameworks: List[Framework]) -> float:
        """Calculate classification confidence"""
        confidence = 0.5  # Base confidence
        
        # More categories increase confidence
        confidence += len(categories) * 0.1
        
        # Identified languages increase confidence
        confidence += len(languages) * 0.1
        
        # Identified frameworks increase confidence
        confidence += len(frameworks) * 0.05
        
        # Cap at 1.0
        return min(confidence, 1.0)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get classification statistics"""
        if not self.task_history:
            return {}
        
        stats = {
            'total_tasks': len(self.task_history),
            'category_distribution': {},
            'complexity_distribution': {},
            'language_distribution': {},
            'average_confidence': 0
        }
        
        for _, features in self.task_history:
            # Categories
            for category in features.categories:
                cat_name = category.value
                stats['category_distribution'][cat_name] = \
                    stats['category_distribution'].get(cat_name, 0) + 1
            
            # Complexity
            comp_name = features.complexity.value
            stats['complexity_distribution'][comp_name] = \
                stats['complexity_distribution'].get(comp_name, 0) + 1
            
            # Languages
            for language in features.languages:
                lang_name = language.value
                stats['language_distribution'][lang_name] = \
                    stats['language_distribution'].get(lang_name, 0) + 1
            
            # Confidence
            stats['average_confidence'] += features.confidence
        
        stats['average_confidence'] /= len(self.task_history)
        
        return stats