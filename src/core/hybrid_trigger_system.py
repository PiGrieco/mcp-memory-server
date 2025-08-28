#!/usr/bin/env python3
"""
Hybrid Auto-Trigger System
Combines deterministic rules with ML predictions for optimal performance
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

from .auto_trigger_system import AutoTriggerSystem
from .ml_trigger_system import ActionType, MLPrediction, create_ml_auto_trigger_system
from ..utils.logging import get_logger
from ..config.settings import get_config
from ..services.embedding_service import EmbeddingService
from ..services.memory_service import MemoryService


logger = get_logger(__name__)


class TriggerMode(Enum):
    """Operating modes for trigger system"""
    DETERMINISTIC = "deterministic"  # Only rule-based triggers
    ML_ONLY = "ml_only"             # Only ML-based triggers
    HYBRID = "hybrid"               # Combine both systems
    LEARNING = "learning"           # ML learns from deterministic system


@dataclass
class HybridPrediction:
    """Combined prediction from both systems"""
    final_action: ActionType
    confidence: float
    deterministic_result: Optional[Dict[str, Any]]
    ml_result: Optional[MLPrediction]
    reasoning: List[str]
    method_used: str  # "deterministic", "ml", "hybrid"


class HybridAutoTriggerSystem:
    """
    Hybrid system that combines deterministic rules with ML predictions
    """
    
    def __init__(self, memory_service: MemoryService, embedding_service: EmbeddingService):
        self.config = get_config()
        self.memory_service = memory_service
        self.embedding_service = embedding_service
        
        # Initialize both systems
        self.deterministic_system = AutoTriggerSystem(memory_service, embedding_service)
        self.ml_system = create_ml_auto_trigger_system(memory_service, embedding_service)
        
        # Configuration
        self.mode = TriggerMode(self.config.ml_trigger.mode)
        self.ml_confidence_threshold = self.config.ml_trigger.ml_confidence_threshold
        self.learning_phase = self.config.ml_trigger.training_enabled
        
        # Performance tracking
        self.performance_metrics = {
            'deterministic_correct': 0,
            'ml_correct': 0,
            'hybrid_decisions': 0,
            'learning_samples': 0,
            'mode_switches': 0
        }
        
        # Learning and adaptation
        self.adaptation_history = []
        self.confidence_calibration = {}
        
        logger.info(f"Hybrid auto-trigger system initialized in {self.mode.value} mode")
    
    async def initialize(self):
        """Initialize both systems"""
        await self.ml_system.initialize()
        logger.info("Hybrid trigger system fully initialized")
    
    async def analyze_and_decide(
        self,
        messages: List[Dict[str, str]],
        platform: str = "unknown",
        user_id: str = "default",
        context: Dict[str, Any] = None
    ) -> HybridPrediction:
        """
        Analyze messages and decide on action using hybrid approach
        """
        
        context = context or {}
        current_message = messages[-1]['content'] if messages else ""
        
        deterministic_result = None
        ml_result = None
        
        try:
            # Get predictions from both systems based on mode
            if self.mode in [TriggerMode.DETERMINISTIC, TriggerMode.HYBRID, TriggerMode.LEARNING]:
                deterministic_result = await self._get_deterministic_prediction(messages, platform, context)
            
            if self.mode in [TriggerMode.ML_ONLY, TriggerMode.HYBRID, TriggerMode.LEARNING]:
                ml_result = await self._get_ml_prediction(current_message, messages, platform, user_id)
            
            # Decide final action based on mode
            final_prediction = await self._combine_predictions(
                deterministic_result, ml_result, messages, context
            )
            
            # Learning: if in learning mode, use deterministic as ground truth
            if self.mode == TriggerMode.LEARNING and deterministic_result and ml_result:
                await self._learn_from_deterministic(deterministic_result, ml_result, user_id)
            
            return final_prediction
            
        except Exception as e:
            logger.error(f"Hybrid analysis failed: {e}")
            return HybridPrediction(
                final_action=ActionType.NO_ACTION,
                confidence=0.0,
                deterministic_result=deterministic_result,
                ml_result=ml_result,
                reasoning=[f"Analysis failed: {str(e)}"],
                method_used="error"
            )
    
    async def _get_deterministic_prediction(
        self, 
        messages: List[Dict[str, str]], 
        platform: str, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get prediction from deterministic system"""
        try:
            # Use the original auto-trigger system
            results = await self.deterministic_system.check_triggers(
                messages=messages,
                platform=platform,
                context=context
            )
            
            # Convert to standardized format
            if results['triggers_activated']:
                trigger = results['triggers_activated'][0]  # Take highest priority
                action_map = {
                    'save_memory': ActionType.SAVE_MEMORY,
                    'search_memories': ActionType.SEARCH_MEMORY,
                    'get_memory_context': ActionType.SEARCH_MEMORY
                }
                action = action_map.get(trigger['action'], ActionType.NO_ACTION)
            else:
                action = ActionType.NO_ACTION
            
            return {
                'action': action,
                'confidence': results.get('confidence', 0.8),  # Deterministic has high confidence
                'reasoning': results.get('reasoning', []),
                'raw_results': results
            }
            
        except Exception as e:
            logger.error(f"Deterministic prediction failed: {e}")
            return {
                'action': ActionType.NO_ACTION,
                'confidence': 0.0,
                'reasoning': [f"Deterministic system failed: {str(e)}"],
                'raw_results': None
            }
    
    async def _get_ml_prediction(
        self,
        message: str,
        conversation_history: List[Dict[str, str]],
        platform: str,
        user_id: str
    ) -> MLPrediction:
        """Get prediction from ML system"""
        try:
            return await self.ml_system.analyze_and_predict(
                message=message,
                conversation_history=conversation_history,
                platform=platform,
                user_id=user_id
            )
        except Exception as e:
            logger.error(f"ML prediction failed: {e}")
            return MLPrediction(
                action=ActionType.NO_ACTION,
                confidence=0.0,
                reasoning=[f"ML system failed: {str(e)}"],
                features_used=[],
                should_learn=False
            )
    
    async def _combine_predictions(
        self,
        deterministic_result: Optional[Dict[str, Any]],
        ml_result: Optional[MLPrediction],
        messages: List[Dict[str, str]],
        context: Dict[str, Any]
    ) -> HybridPrediction:
        """Combine predictions from both systems"""
        
        
        # Mode-specific logic
        if self.mode == TriggerMode.DETERMINISTIC:
            if deterministic_result:
                return HybridPrediction(
                    final_action=deterministic_result['action'],
                    confidence=deterministic_result['confidence'],
                    deterministic_result=deterministic_result,
                    ml_result=None,
                    reasoning=deterministic_result['reasoning'],
                    method_used="deterministic"
                )
        
        elif self.mode == TriggerMode.ML_ONLY:
            if ml_result:
                return HybridPrediction(
                    final_action=ml_result.action,
                    confidence=ml_result.confidence,
                    deterministic_result=None,
                    ml_result=ml_result,
                    reasoning=ml_result.reasoning,
                    method_used="ml"
                )
        
        elif self.mode == TriggerMode.LEARNING:
            # In learning mode, use deterministic but train ML
            if deterministic_result:
                return HybridPrediction(
                    final_action=deterministic_result['action'],
                    confidence=deterministic_result['confidence'],
                    deterministic_result=deterministic_result,
                    ml_result=ml_result,
                    reasoning=deterministic_result['reasoning'] + ["(Learning mode: using deterministic)"],
                    method_used="deterministic_learning"
                )
        
        elif self.mode == TriggerMode.HYBRID:
            # Hybrid logic: combine both predictions intelligently
            return await self._hybrid_combination(deterministic_result, ml_result, context)
        
        # Fallback
        return HybridPrediction(
            final_action=ActionType.NO_ACTION,
            confidence=0.0,
            deterministic_result=deterministic_result,
            ml_result=ml_result,
            reasoning=["No valid prediction available"],
            method_used="fallback"
        )
    
    async def _hybrid_combination(
        self,
        deterministic_result: Optional[Dict[str, Any]],
        ml_result: Optional[MLPrediction],
        context: Dict[str, Any]
    ) -> HybridPrediction:
        """Intelligent combination of deterministic and ML predictions"""
        
        reasoning = []
        
        # Both systems available
        if deterministic_result and ml_result:
            det_action = deterministic_result['action']
            det_confidence = deterministic_result['confidence']
            ml_action = ml_result.action
            ml_confidence = ml_result.confidence
            
            # Case 1: Both agree
            if det_action == ml_action:
                combined_confidence = (det_confidence + ml_confidence) / 2
                reasoning.append(f"Both systems agree on {det_action.value}")
                reasoning.extend(deterministic_result['reasoning'])
                reasoning.extend(ml_result.reasoning)
                
                return HybridPrediction(
                    final_action=det_action,
                    confidence=combined_confidence,
                    deterministic_result=deterministic_result,
                    ml_result=ml_result,
                    reasoning=reasoning,
                    method_used="hybrid_agreement"
                )
            
            # Case 2: Disagreement - use confidence and context to decide
            else:
                # High ML confidence overrides deterministic
                if ml_confidence > self.ml_confidence_threshold and ml_confidence > det_confidence:
                    reasoning.append(f"ML high confidence ({ml_confidence:.2f}) overrides deterministic")
                    reasoning.extend(ml_result.reasoning)
                    
                    return HybridPrediction(
                        final_action=ml_action,
                        confidence=ml_confidence,
                        deterministic_result=deterministic_result,
                        ml_result=ml_result,
                        reasoning=reasoning,
                        method_used="hybrid_ml_override"
                    )
                
                # Otherwise, prefer deterministic (more reliable)
                else:
                    reasoning.append(f"Deterministic system preferred (ML confidence: {ml_confidence:.2f})")
                    reasoning.extend(deterministic_result['reasoning'])
                    
                    return HybridPrediction(
                        final_action=det_action,
                        confidence=det_confidence,
                        deterministic_result=deterministic_result,
                        ml_result=ml_result,
                        reasoning=reasoning,
                        method_used="hybrid_deterministic_preferred"
                    )
        
        # Only deterministic available
        elif deterministic_result:
            reasoning.append("Only deterministic system available")
            reasoning.extend(deterministic_result['reasoning'])
            
            return HybridPrediction(
                final_action=deterministic_result['action'],
                confidence=deterministic_result['confidence'],
                deterministic_result=deterministic_result,
                ml_result=ml_result,
                reasoning=reasoning,
                method_used="hybrid_deterministic_only"
            )
        
        # Only ML available
        elif ml_result:
            reasoning.append("Only ML system available")
            reasoning.extend(ml_result.reasoning)
            
            return HybridPrediction(
                final_action=ml_result.action,
                confidence=ml_result.confidence,
                deterministic_result=deterministic_result,
                ml_result=ml_result,
                reasoning=reasoning,
                method_used="hybrid_ml_only"
            )
        
        # Neither available
        else:
            return HybridPrediction(
                final_action=ActionType.NO_ACTION,
                confidence=0.0,
                deterministic_result=None,
                ml_result=None,
                reasoning=["No predictions available from either system"],
                method_used="hybrid_none"
            )
    
    async def _learn_from_deterministic(
        self,
        deterministic_result: Dict[str, Any],
        ml_result: MLPrediction,
        user_id: str
    ):
        """Use deterministic system results to train ML system"""
        
        if not ml_result.should_learn:
            return
        
        try:
            # Use deterministic action as ground truth
            ground_truth = deterministic_result['action']
            
            # Extract features that were used for ML prediction
            if hasattr(ml_result, 'features_used') and ml_result.features_used:
                # Learn from this example
                await self.ml_system.learn_from_action(
                    features=None,  # Would need to reconstruct features
                    action_taken=ground_truth,
                    user_id=user_id,
                    user_feedback={
                        'source': 'deterministic_system',
                        'deterministic_confidence': deterministic_result['confidence'],
                        'ml_prediction': ml_result.action.value,
                        'ml_confidence': ml_result.confidence
                    }
                )
                
                self.performance_metrics['learning_samples'] += 1
                
                logger.debug(f"ML system learned from deterministic: {ground_truth.value}")
        
        except Exception as e:
            logger.error(f"Learning from deterministic failed: {e}")
    
    async def record_user_feedback(
        self,
        prediction: HybridPrediction,
        actual_action: ActionType,
        user_id: str = "default",
        feedback: Optional[Dict[str, Any]] = None
    ):
        """Record user feedback for system improvement"""
        
        try:
            # Record for ML system
            if prediction.ml_result and prediction.ml_result.should_learn:
                await self.ml_system.learn_from_action(
                    features=None,  # Would need original features
                    action_taken=actual_action,
                    user_id=user_id,
                    user_feedback=feedback
                )
            
            # Update performance metrics
            if prediction.method_used.startswith('deterministic'):
                if (prediction.deterministic_result and 
                    prediction.deterministic_result['action'] == actual_action):
                    self.performance_metrics['deterministic_correct'] += 1
            
            elif prediction.method_used.startswith('ml') or prediction.method_used.startswith('hybrid_ml'):
                if prediction.ml_result and prediction.ml_result.action == actual_action:
                    self.performance_metrics['ml_correct'] += 1
            
            # Store feedback for analysis
            self.adaptation_history.append({
                'timestamp': datetime.now().isoformat(),
                'user_id': user_id,
                'predicted_action': prediction.final_action.value,
                'actual_action': actual_action.value,
                'method_used': prediction.method_used,
                'confidence': prediction.confidence,
                'feedback': feedback
            })
            
            logger.info(f"User feedback recorded: predicted {prediction.final_action.value}, actual {actual_action.value}")
            
        except Exception as e:
            logger.error(f"Recording user feedback failed: {e}")
    
    def switch_mode(self, new_mode: TriggerMode):
        """Switch operating mode"""
        old_mode = self.mode
        self.mode = new_mode
        self.performance_metrics['mode_switches'] += 1
        
        logger.info(f"Switched trigger mode from {old_mode.value} to {new_mode.value}")
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics"""
        ml_metrics = self.ml_system.get_metrics()
        
        return {
            'hybrid_metrics': self.performance_metrics,
            'ml_metrics': ml_metrics,
            'current_mode': self.mode.value,
            'total_adaptations': len(self.adaptation_history),
            'ml_confidence_threshold': self.ml_confidence_threshold
        }
    
    async def optimize_thresholds(self):
        """Automatically optimize confidence thresholds based on performance"""
        
        if len(self.adaptation_history) < 50:  # Need sufficient data
            return
        
        try:
            # Analyze recent performance
            recent_feedback = self.adaptation_history[-100:]  # Last 100 examples
            
            # Calculate accuracy for different confidence levels
            confidence_levels = [0.5, 0.6, 0.7, 0.8, 0.9]
            best_threshold = self.ml_confidence_threshold
            best_accuracy = 0.0
            
            for threshold in confidence_levels:
                correct = 0
                total = 0
                
                for feedback in recent_feedback:
                    if (feedback['method_used'].startswith('hybrid_ml') and 
                        feedback['confidence'] >= threshold):
                        total += 1
                        if feedback['predicted_action'] == feedback['actual_action']:
                            correct += 1
                
                if total > 10:  # Minimum samples
                    accuracy = correct / total
                    if accuracy > best_accuracy:
                        best_accuracy = accuracy
                        best_threshold = threshold
            
            # Update threshold if improvement is significant
            if best_threshold != self.ml_confidence_threshold and best_accuracy > 0.1:
                old_threshold = self.ml_confidence_threshold
                self.ml_confidence_threshold = best_threshold
                
                logger.info(f"Optimized ML confidence threshold: {old_threshold:.2f} → {best_threshold:.2f} (accuracy: {best_accuracy:.2f})")
        
        except Exception as e:
            logger.error(f"Threshold optimization failed: {e}")
    
    async def export_analysis_data(self, file_path: str):
        """Export data for analysis and debugging"""
        
        analysis_data = {
            'performance_metrics': self.get_performance_metrics(),
            'adaptation_history': self.adaptation_history,
            'current_mode': self.mode.value,
            'ml_confidence_threshold': self.ml_confidence_threshold,
            'export_timestamp': datetime.now().isoformat()
        }
        
        with open(file_path, 'w') as f:
            json.dump(analysis_data, f, indent=2)
        
        logger.info(f"Analysis data exported to {file_path}")


def create_hybrid_auto_trigger_system(
    memory_service: MemoryService, 
    embedding_service: EmbeddingService
) -> HybridAutoTriggerSystem:
    """Create and initialize hybrid auto-trigger system"""
    return HybridAutoTriggerSystem(memory_service, embedding_service)
