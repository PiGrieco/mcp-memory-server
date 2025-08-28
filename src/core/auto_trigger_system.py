#!/usr/bin/env python3
"""
Auto-Trigger System for MCP Memory Server
Intelligent automatic triggering of memory tools based on conversation analysis
"""

import re
import time
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from enum import Enum

from ..utils.logging import get_logger, log_performance
from ..config.settings import get_config
from ..services.embedding_service import EmbeddingService
from ..services.memory_service import MemoryService


logger = get_logger(__name__)


class TriggerType(Enum):
    """Types of automatic triggers"""
    KEYWORD_BASED = "keyword"
    SEMANTIC_SIMILARITY = "semantic" 
    IMPORTANCE_THRESHOLD = "importance"
    CONVERSATION_LENGTH = "length"
    TIME_BASED = "time"
    PATTERN_RECOGNITION = "pattern"
    CONTEXT_CHANGE = "context"


@dataclass
class TriggerRule:
    """Definition of a trigger rule"""
    trigger_type: TriggerType
    condition: Dict[str, Any]
    action: str  # save_memory, search_memories, get_memory_context
    priority: int = 1
    cooldown_seconds: int = 30
    enabled: bool = True


@dataclass
class ConversationAnalysis:
    """Analysis result of a conversation"""
    importance_score: float
    keywords: List[str]
    entities: List[str]
    intent: str
    emotional_context: str
    code_content: bool
    question_asked: bool
    solution_provided: bool
    error_mentioned: bool
    decision_made: bool


class AutoTriggerSystem:
    """
    Intelligent automatic triggering system for MCP tools
    """
    
    def __init__(self, memory_service: MemoryService, embedding_service: EmbeddingService):
        self.config = get_config()
        self.memory_service = memory_service
        self.embedding_service = embedding_service
        
        # Trigger rules configuration
        self.trigger_rules = self._load_trigger_rules()
        
        # State tracking
        self.conversation_buffer = []
        self.last_trigger_times = {}
        self.session_context = {}
        
        # Pattern compilation for performance
        self.compiled_patterns = self._compile_patterns()
        
        logger.info("Auto-trigger system initialized")
    
    def _load_trigger_rules(self) -> List[TriggerRule]:
        """Load trigger rules from configuration"""
        return [
            # 1. KEYWORD-BASED TRIGGERS
            TriggerRule(
                trigger_type=TriggerType.KEYWORD_BASED,
                condition={
                    "keywords": [
                        "ricorda", "remember", "nota", "note", "importante", "important",
                        "salva", "save", "memorizza", "store", "non dimenticare", "don't forget",
                        "per dopo", "for later", "riferimento", "reference"
                    ],
                    "threshold": 1  # At least 1 keyword
                },
                action="save_memory",
                priority=10,
                cooldown_seconds=10
            ),
            
            # 2. SOLUTION/ERROR PATTERNS
            TriggerRule(
                trigger_type=TriggerType.PATTERN_RECOGNITION,
                condition={
                    "patterns": [
                        r"(?:risolto|solved|fixed|bug fix|solution)",
                        r"(?:errore|error|bug|issue).*(?:risolto|fixed|solved)",
                        r"(?:come fare|how to|tutorial|step by step)",
                        r"(?:funziona così|works like this|here's how)"
                    ],
                    "context_required": ["error", "solution", "code"]
                },
                action="save_memory",
                priority=9,
                cooldown_seconds=30
            ),
            
            # 3. SEMANTIC SIMILARITY TRIGGER
            TriggerRule(
                trigger_type=TriggerType.SEMANTIC_SIMILARITY,
                condition={
                    "similarity_threshold": 0.8,
                    "min_content_length": 100,
                    "search_recent_memories": True
                },
                action="search_memories",
                priority=8,
                cooldown_seconds=60
            ),
            
            # 4. IMPORTANCE THRESHOLD
            TriggerRule(
                trigger_type=TriggerType.IMPORTANCE_THRESHOLD,
                condition={
                    "importance_threshold": 0.7,
                    "content_indicators": ["code", "configuration", "architecture", "decision"]
                },
                action="save_memory", 
                priority=7,
                cooldown_seconds=45
            ),
            
            # 5. CONVERSATION LENGTH TRIGGER
            TriggerRule(
                trigger_type=TriggerType.CONVERSATION_LENGTH,
                condition={
                    "message_count": 5,
                    "min_avg_length": 50,
                    "substantive_content": True
                },
                action="save_memory",
                priority=6,
                cooldown_seconds=120
            ),
            
            # 6. CONTEXT CHANGE DETECTION
            TriggerRule(
                trigger_type=TriggerType.CONTEXT_CHANGE,
                condition={
                    "topic_shift_threshold": 0.6,
                    "new_project_keywords": ["nuovo progetto", "new project", "different", "altro"]
                },
                action="get_memory_context",
                priority=5,
                cooldown_seconds=30
            ),
            
            # 7. TIME-BASED PERIODIC SEARCH
            TriggerRule(
                trigger_type=TriggerType.TIME_BASED,
                condition={
                    "interval_minutes": 10,
                    "active_conversation": True,
                    "min_messages": 3
                },
                action="search_memories",
                priority=3,
                cooldown_seconds=600
            )
        ]
    
    def _compile_patterns(self) -> Dict[str, re.Pattern]:
        """Compile regex patterns for performance"""
        patterns = {}
        for rule in self.trigger_rules:
            if rule.trigger_type == TriggerType.PATTERN_RECOGNITION:
                for i, pattern in enumerate(rule.condition.get("patterns", [])):
                    patterns[f"{rule.trigger_type.value}_{i}"] = re.compile(pattern, re.IGNORECASE)
        return patterns
    
    @log_performance("conversation_analysis")
    async def analyze_conversation(self, messages: List[Dict[str, str]]) -> ConversationAnalysis:
        """Analyze conversation for trigger conditions"""
        if not messages:
            return ConversationAnalysis(0.0, [], [], "unknown", "neutral", False, False, False, False, False)
        
        # Combine all message content
        all_content = " ".join([msg.get("content", "") for msg in messages]).lower()
        
        # Extract keywords
        keywords = self._extract_keywords(all_content)
        
        # Detect entities (simplified)
        entities = self._extract_entities(all_content)
        
        # Calculate importance score
        importance = await self._calculate_importance_score(messages, keywords)
        
        # Detect conversation characteristics
        code_content = any(marker in all_content for marker in ["```", "def ", "function", "class ", "import", "const"])
        question_asked = any(marker in all_content for marker in ["?", "come", "how", "what", "why", "when", "where"])
        solution_provided = any(marker in all_content for marker in ["risolto", "solved", "ecco", "here's", "solution", "fix"])
        error_mentioned = any(marker in all_content for marker in ["errore", "error", "bug", "issue", "problema", "problem"])
        decision_made = any(marker in all_content for marker in ["decido", "decide", "sceglio", "choose", "useremo", "we'll use"])
        
        # Determine intent
        intent = self._determine_intent(all_content, question_asked, solution_provided, error_mentioned)
        
        # Emotional context (simplified)
        emotional_context = self._determine_emotional_context(all_content)
        
        return ConversationAnalysis(
            importance_score=importance,
            keywords=keywords,
            entities=entities,
            intent=intent,
            emotional_context=emotional_context,
            code_content=code_content,
            question_asked=question_asked,
            solution_provided=solution_provided,
            error_mentioned=error_mentioned,
            decision_made=decision_made
        )
    
    async def check_triggers(
        self, 
        messages: List[Dict[str, str]], 
        platform: str = "unknown"
    ) -> List[Tuple[str, Dict[str, Any]]]:
        """
        Check all trigger rules and return triggered actions
        Returns list of (action, parameters) tuples
        """
        triggered_actions = []
        
        # Analyze conversation
        analysis = await self.analyze_conversation(messages)
        
        # Check each trigger rule
        for rule in sorted(self.trigger_rules, key=lambda x: x.priority, reverse=True):
            if not rule.enabled:
                continue
            
            # Check cooldown
            rule_key = f"{rule.trigger_type.value}_{rule.action}"
            if self._is_in_cooldown(rule_key, rule.cooldown_seconds):
                continue
            
            # Check trigger condition
            triggered, params = await self._check_trigger_condition(rule, analysis, messages, platform)
            
            if triggered:
                triggered_actions.append((rule.action, params))
                self.last_trigger_times[rule_key] = time.time()
                
                logger.info(f"Trigger activated: {rule.trigger_type.value} -> {rule.action}")
        
        return triggered_actions
    
    async def _check_trigger_condition(
        self, 
        rule: TriggerRule, 
        analysis: ConversationAnalysis, 
        messages: List[Dict], 
        platform: str
    ) -> Tuple[bool, Dict[str, Any]]:
        """Check if a specific trigger rule condition is met"""
        
        if rule.trigger_type == TriggerType.KEYWORD_BASED:
            return self._check_keyword_trigger(rule, analysis, messages)
        
        elif rule.trigger_type == TriggerType.PATTERN_RECOGNITION:
            return self._check_pattern_trigger(rule, analysis, messages)
        
        elif rule.trigger_type == TriggerType.SEMANTIC_SIMILARITY:
            return await self._check_semantic_trigger(rule, analysis, messages)
        
        elif rule.trigger_type == TriggerType.IMPORTANCE_THRESHOLD:
            return self._check_importance_trigger(rule, analysis, messages)
        
        elif rule.trigger_type == TriggerType.CONVERSATION_LENGTH:
            return self._check_length_trigger(rule, analysis, messages)
        
        elif rule.trigger_type == TriggerType.CONTEXT_CHANGE:
            return self._check_context_trigger(rule, analysis, messages, platform)
        
        elif rule.trigger_type == TriggerType.TIME_BASED:
            return self._check_time_trigger(rule, analysis, messages)
        
        return False, {}
    
    def _check_keyword_trigger(self, rule: TriggerRule, analysis: ConversationAnalysis, messages: List[Dict]) -> Tuple[bool, Dict]:
        """Check keyword-based trigger"""
        keywords = rule.condition.get("keywords", [])
        threshold = rule.condition.get("threshold", 1)
        
        # Check content for keywords
        all_content = " ".join([msg.get("content", "") for msg in messages]).lower()
        found_keywords = [kw for kw in keywords if kw.lower() in all_content]
        
        if len(found_keywords) >= threshold:
            # Extract the relevant content around keywords
            content = self._extract_relevant_content_around_keywords(messages, found_keywords)
            
            return True, {
                "content": content,
                "importance": min(0.9, analysis.importance_score + 0.2),  # Boost importance for explicit requests
                "memory_type": "explicit_request",
                "metadata": {
                    "trigger_keywords": found_keywords,
                    "trigger_type": "keyword_based",
                    "auto_triggered": True
                }
            }
        
        return False, {}
    
    def _check_pattern_trigger(self, rule: TriggerRule, analysis: ConversationAnalysis, messages: List[Dict]) -> Tuple[bool, Dict]:
        """Check pattern recognition trigger"""
        patterns = rule.condition.get("patterns", [])
        context_required = rule.condition.get("context_required", [])
        
        all_content = " ".join([msg.get("content", "") for msg in messages])
        
        # Check if any pattern matches
        matched_patterns = []
        for i, pattern in enumerate(patterns):
            pattern_key = f"pattern_recognition_{i}"
            if pattern_key in self.compiled_patterns:
                if self.compiled_patterns[pattern_key].search(all_content):
                    matched_patterns.append(pattern)
        
        if matched_patterns:
            # Check context requirements
            context_met = True
            if context_required:
                context_indicators = {
                    "error": analysis.error_mentioned,
                    "solution": analysis.solution_provided,
                    "code": analysis.code_content,
                    "decision": analysis.decision_made
                }
                context_met = any(context_indicators.get(req, False) for req in context_required)
            
            if context_met:
                return True, {
                    "content": all_content,
                    "importance": analysis.importance_score,
                    "memory_type": self._determine_memory_type_from_pattern(matched_patterns[0]),
                    "metadata": {
                        "matched_patterns": matched_patterns,
                        "trigger_type": "pattern_recognition",
                        "auto_triggered": True
                    }
                }
        
        return False, {}
    
    async def _check_semantic_trigger(self, rule: TriggerRule, analysis: ConversationAnalysis, messages: List[Dict]) -> Tuple[bool, Dict]:
        """Check semantic similarity trigger"""
        threshold = rule.condition.get("similarity_threshold", 0.8)
        min_length = rule.condition.get("min_content_length", 100)
        
        current_content = " ".join([msg.get("content", "") for msg in messages])
        
        if len(current_content) < min_length:
            return False, {}
        
        # Search for similar memories
        try:
            similar_memories = await self.memory_service.search_memories(
                query=current_content[:500],  # Limit query length
                limit=3,
                similarity_threshold=threshold
            )
            
            if similar_memories:
                return True, {
                    "query": current_content[:200],
                    "limit": 5,
                    "metadata": {
                        "trigger_type": "semantic_similarity",
                        "found_similar": len(similar_memories),
                        "auto_triggered": True
                    }
                }
        except Exception as e:
            logger.warning(f"Semantic trigger search failed: {e}")
        
        return False, {}
    
    def _check_importance_trigger(self, rule: TriggerRule, analysis: ConversationAnalysis, messages: List[Dict]) -> Tuple[bool, Dict]:
        """Check importance threshold trigger"""
        threshold = rule.condition.get("importance_threshold", 0.7)
        indicators = rule.condition.get("content_indicators", [])
        
        if analysis.importance_score >= threshold:
            # Check for content indicators
            all_content = " ".join([msg.get("content", "") for msg in messages]).lower()
            found_indicators = [ind for ind in indicators if ind in all_content]
            
            if found_indicators or not indicators:  # Trigger if no specific indicators required
                return True, {
                    "content": all_content,
                    "importance": analysis.importance_score,
                    "memory_type": "high_importance",
                    "metadata": {
                        "importance_score": analysis.importance_score,
                        "content_indicators": found_indicators,
                        "trigger_type": "importance_threshold",
                        "auto_triggered": True
                    }
                }
        
        return False, {}
    
    def _check_length_trigger(self, rule: TriggerRule, analysis: ConversationAnalysis, messages: List[Dict]) -> Tuple[bool, Dict]:
        """Check conversation length trigger"""
        min_messages = rule.condition.get("message_count", 5)
        min_avg_length = rule.condition.get("min_avg_length", 50)
        
        if len(messages) >= min_messages:
            total_length = sum(len(msg.get("content", "")) for msg in messages)
            avg_length = total_length / len(messages)
            
            if avg_length >= min_avg_length:
                # Summarize the conversation
                conversation_summary = self._create_conversation_summary(messages)
                
                return True, {
                    "content": conversation_summary,
                    "importance": analysis.importance_score,
                    "memory_type": "conversation_summary",
                    "metadata": {
                        "message_count": len(messages),
                        "avg_message_length": avg_length,
                        "trigger_type": "conversation_length",
                        "auto_triggered": True
                    }
                }
        
        return False, {}
    
    def _check_context_trigger(self, rule: TriggerRule, analysis: ConversationAnalysis, messages: List[Dict], platform: str) -> Tuple[bool, Dict]:
        """Check context change trigger"""
        new_project_keywords = rule.condition.get("new_project_keywords", [])
        
        all_content = " ".join([msg.get("content", "") for msg in messages]).lower()
        
        # Check for project/context change keywords
        context_change_detected = any(keyword in all_content for keyword in new_project_keywords)
        
        if context_change_detected:
            return True, {
                "context": all_content[:200],
                "limit": 5,
                "metadata": {
                    "trigger_type": "context_change",
                    "platform": platform,
                    "auto_triggered": True
                }
            }
        
        return False, {}
    
    def _check_time_trigger(self, rule: TriggerRule, analysis: ConversationAnalysis, messages: List[Dict]) -> Tuple[bool, Dict]:
        """Check time-based trigger"""
        interval_minutes = rule.condition.get("interval_minutes", 10)
        min_messages = rule.condition.get("min_messages", 3)
        
        # Check if enough time has passed and conversation is active
        last_time_trigger = self.last_trigger_times.get("time_based_search_memories", 0)
        time_since_last = time.time() - last_time_trigger
        
        if time_since_last >= (interval_minutes * 60) and len(messages) >= min_messages:
            # Get recent conversation context
            recent_content = " ".join([msg.get("content", "") for msg in messages[-3:]])
            
            return True, {
                "query": recent_content[:200],
                "limit": 3,
                "metadata": {
                    "trigger_type": "time_based",
                    "interval_minutes": interval_minutes,
                    "auto_triggered": True
                }
            }
        
        return False, {}
    
    # Helper methods
    def _extract_keywords(self, content: str) -> List[str]:
        """Extract relevant keywords from content"""
        # Simplified keyword extraction
        important_words = []
        for word in content.split():
            if len(word) > 3 and word.isalpha():
                important_words.append(word.lower())
        return list(set(important_words))[:20]  # Limit to 20 keywords
    
    def _extract_entities(self, content: str) -> List[str]:
        """Extract entities from content (simplified)"""
        # Basic entity patterns
        entities = []
        
        # File paths
        import re
        file_patterns = re.findall(r'[\w/]+\.\w+', content)
        entities.extend(file_patterns)
        
        # URLs
        url_patterns = re.findall(r'https?://[\w\.-]+', content)
        entities.extend(url_patterns)
        
        return entities[:10]  # Limit to 10 entities
    
    async def _calculate_importance_score(self, messages: List[Dict], keywords: List[str]) -> float:
        """Calculate importance score for conversation"""
        base_score = 0.5
        
        # Factor in message length
        total_length = sum(len(msg.get("content", "")) for msg in messages)
        if total_length > 500:
            base_score += 0.1
        if total_length > 1000:
            base_score += 0.1
        
        # Factor in keyword importance
        important_keywords = ["importante", "ricorda", "bug", "errore", "soluzione", "decisione"]
        keyword_boost = sum(0.05 for kw in keywords if kw in important_keywords)
        base_score += min(0.3, keyword_boost)
        
        return min(1.0, base_score)
    
    def _determine_intent(self, content: str, question: bool, solution: bool, error: bool) -> str:
        """Determine conversation intent"""
        if error and solution:
            return "problem_solving"
        elif question:
            return "information_seeking"
        elif solution:
            return "solution_sharing"
        elif error:
            return "error_reporting"
        else:
            return "general_conversation"
    
    def _determine_emotional_context(self, content: str) -> str:
        """Determine emotional context (simplified)"""
        if any(word in content for word in ["frustrato", "arrabbiato", "confused", "stuck"]):
            return "frustrated"
        elif any(word in content for word in ["grazie", "perfetto", "excellent", "great"]):
            return "positive"
        else:
            return "neutral"
    
    def _is_in_cooldown(self, rule_key: str, cooldown_seconds: int) -> bool:
        """Check if trigger is in cooldown period"""
        last_time = self.last_trigger_times.get(rule_key, 0)
        return (time.time() - last_time) < cooldown_seconds
    
    def _extract_relevant_content_around_keywords(self, messages: List[Dict], keywords: List[str]) -> str:
        """Extract content around found keywords"""
        relevant_parts = []
        for msg in messages:
            content = msg.get("content", "")
            for keyword in keywords:
                if keyword.lower() in content.lower():
                    # Find sentence containing the keyword
                    sentences = content.split('.')
                    for sentence in sentences:
                        if keyword.lower() in sentence.lower():
                            relevant_parts.append(sentence.strip())
                            break
        
        return ". ".join(relevant_parts) if relevant_parts else " ".join([msg.get("content", "") for msg in messages])
    
    def _determine_memory_type_from_pattern(self, pattern: str) -> str:
        """Determine memory type based on matched pattern"""
        if "error" in pattern or "bug" in pattern:
            return "error_solution"
        elif "how to" in pattern or "tutorial" in pattern:
            return "knowledge"
        elif "risolto" in pattern or "solved" in pattern:
            return "solution"
        else:
            return "conversation"
    
    def _create_conversation_summary(self, messages: List[Dict]) -> str:
        """Create a summary of the conversation"""
        # Simple summarization - take key sentences
        all_content = " ".join([msg.get("content", "") for msg in messages])
        
        # Split into sentences and take the longer, more meaningful ones
        sentences = [s.strip() for s in all_content.split('.') if len(s.strip()) > 20]
        
        # Take up to 3 most meaningful sentences
        summary_sentences = sentences[:3] if len(sentences) >= 3 else sentences
        
        return ". ".join(summary_sentences) + "."


# Factory function for easy integration
def create_auto_trigger_system(memory_service: MemoryService, embedding_service: EmbeddingService) -> AutoTriggerSystem:
    """Create and configure auto-trigger system"""
    return AutoTriggerSystem(memory_service, embedding_service)

