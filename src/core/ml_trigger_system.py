#!/usr/bin/env python3
"""
ML-Based Auto-Trigger System for MCP Memory Server
Intelligent triggering using machine learning instead of deterministic rules
"""

import json
import numpy as np
import pickle
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

# ML imports
try:
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.preprocessing import StandardScaler
    from sklearn.neural_network import MLPClassifier
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from transformers import AutoTokenizer, AutoModel, AutoModelForSequenceClassification, pipeline
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False

from ..utils.logging import get_logger
from ..config.settings import get_settings
from ..services.embedding_service import EmbeddingService
from ..services.memory_service import MemoryService


logger = get_logger(__name__)


class ActionType(Enum):
    """Types of memory actions"""
    SAVE_MEMORY = "save"
    SEARCH_MEMORY = "search"
    NO_ACTION = "none"


@dataclass
class MLFeatures:
    """Rich feature set for ML model"""
    # Text features
    text_length: int
    word_count: int
    sentence_count: int
    avg_word_length: float
    
    # Semantic features
    semantic_density: float  # How information-dense the content is
    technical_content_score: float
    question_score: float
    solution_score: float
    
    # Context features
    conversation_position: int  # Position in conversation
    time_since_last_message: float
    user_engagement_score: float
    
    # Memory-related features
    similarity_to_existing: float  # Max similarity to existing memories
    novelty_score: float  # How novel the information is
    importance_indicators: int  # Count of importance indicators
    
    # Platform features
    platform_type: str
    session_length: int
    
    # Behavioral features (learned over time)
    user_save_frequency: float
    user_search_frequency: float
    topic_coherence: float


@dataclass
class MLPrediction:
    """ML model prediction result"""
    action: ActionType
    confidence: float
    reasoning: List[str]
    features_used: List[str]
    should_learn: bool = True


class FeatureExtractor:
    """Extract rich features from conversation context"""
    
    def __init__(self, embedding_service: EmbeddingService, memory_service: MemoryService = None):
        self.embedding_service = embedding_service
        self.memory_service = memory_service
        self.config = get_settings()
        
        # Initialize text analysis components
        if HAS_SKLEARN:
            self.tfidf = TfidfVectorizer(max_features=1000, stop_words='english')
            self.scaler = StandardScaler()
        
        # Keywords for different types of content
        self.technical_keywords = [
            'code', 'function', 'class', 'method', 'variable', 'error', 'bug',
            'implementation', 'algorithm', 'database', 'api', 'framework',
            'library', 'configuration', 'deployment', 'architecture'
        ]
        
        self.question_patterns = [
            'how', 'what', 'when', 'where', 'why', 'which', 'who',
            'come', 'cosa', 'quando', 'dove', 'perché', 'quale', 'chi'
        ]
        
        self.solution_patterns = [
            'solved', 'fixed', 'solution', 'answer', 'resolved', 'working',
            'risolto', 'soluzione', 'risposta', 'funziona'
        ]
        
        self.importance_indicators = [
            'important', 'critical', 'urgent', 'key', 'essential', 'vital',
            'remember', 'note', 'save', 'store', 'keep',
            'importante', 'critico', 'urgente', 'chiave', 'essenziale',
            'ricorda', 'nota', 'salva', 'memorizza'
        ]
    
    async def extract_features(
        self,
        message: str,
        conversation_history: List[Dict[str, Any]],
        platform: str = "unknown",
        user_context: Dict[str, Any] = None
    ) -> MLFeatures:
        """Extract comprehensive features from message and context"""
        
        user_context = user_context or {}
        
        # Basic text features
        words = message.split()
        sentences = message.split('.')
        
        text_length = len(message)
        word_count = len(words)
        sentence_count = len([s for s in sentences if s.strip()])
        avg_word_length = sum(len(w) for w in words) / max(word_count, 1)
        
        # Semantic features
        semantic_density = await self._calculate_semantic_density(message)
        technical_content_score = self._calculate_technical_score(message)
        question_score = self._calculate_question_score(message)
        solution_score = self._calculate_solution_score(message)
        
        # Context features
        conversation_position = len(conversation_history)
        time_since_last_message = self._calculate_time_since_last_message(conversation_history)
        user_engagement_score = self._calculate_engagement_score(conversation_history)
        
        # Memory-related features
        similarity_to_existing = await self._calculate_similarity_to_existing(message)
        novelty_score = 1.0 - similarity_to_existing  # Inverse of similarity
        importance_indicators = self._count_importance_indicators(message)
        
        # Platform features
        session_length = len(conversation_history)
        
        # Behavioral features
        user_save_frequency = user_context.get('save_frequency', 0.0)
        user_search_frequency = user_context.get('search_frequency', 0.0)
        topic_coherence = await self._calculate_topic_coherence(message, conversation_history)
        
        return MLFeatures(
            text_length=text_length,
            word_count=word_count,
            sentence_count=sentence_count,
            avg_word_length=avg_word_length,
            semantic_density=semantic_density,
            technical_content_score=technical_content_score,
            question_score=question_score,
            solution_score=solution_score,
            conversation_position=conversation_position,
            time_since_last_message=time_since_last_message,
            user_engagement_score=user_engagement_score,
            similarity_to_existing=similarity_to_existing,
            novelty_score=novelty_score,
            importance_indicators=importance_indicators,
            platform_type=platform,
            session_length=session_length,
            user_save_frequency=user_save_frequency,
            user_search_frequency=user_search_frequency,
            topic_coherence=topic_coherence
        )
    
    async def _calculate_semantic_density(self, text: str) -> float:
        """Calculate how information-dense the text is"""
        try:
            # Use embedding to measure information density
            embedding = await self.embedding_service.generate_embedding(text)
            
            # Calculate variance of embedding dimensions as density proxy
            embedding_array = np.array(embedding)
            density = float(np.var(embedding_array))
            
            # Normalize to 0-1 range
            return min(max(density, 0.0), 1.0)
        except Exception:
            # Fallback: use word diversity
            words = set(text.lower().split())
            total_words = len(text.split())
            return len(words) / max(total_words, 1)
    
    def _calculate_technical_score(self, text: str) -> float:
        """Calculate how technical the content is"""
        text_lower = text.lower()
        technical_count = sum(1 for keyword in self.technical_keywords 
                            if keyword in text_lower)
        return min(technical_count / 5.0, 1.0)  # Normalize to 0-1
    
    def _calculate_question_score(self, text: str) -> float:
        """Calculate how much the text is asking questions"""
        text_lower = text.lower()
        question_count = text.count('?')
        pattern_count = sum(1 for pattern in self.question_patterns 
                          if pattern in text_lower)
        return min((question_count + pattern_count) / 3.0, 1.0)
    
    def _calculate_solution_score(self, text: str) -> float:
        """Calculate how much the text provides solutions"""
        text_lower = text.lower()
        solution_count = sum(1 for pattern in self.solution_patterns 
                           if pattern in text_lower)
        return min(solution_count / 3.0, 1.0)
    
    def _calculate_time_since_last_message(self, history: List[Dict]) -> float:
        """Calculate time since last message in minutes"""
        if not history:
            return 0.0
        
        try:
            last_timestamp = history[-1].get('timestamp')
            if last_timestamp:
                last_time = datetime.fromisoformat(last_timestamp.replace('Z', '+00:00'))
                now = datetime.now(timezone.utc)
                delta = (now - last_time).total_seconds() / 60.0  # Convert to minutes
                return min(delta, 1440.0)  # Cap at 24 hours
        except Exception:
            pass
        
        return 0.0
    
    def _calculate_engagement_score(self, history: List[Dict]) -> float:
        """Calculate user engagement based on conversation pattern"""
        if len(history) < 2:
            return 0.5
        
        # Look at message frequency and length trends
        recent_messages = history[-5:]  # Last 5 messages
        avg_length = sum(len(msg.get('content', '')) for msg in recent_messages) / len(recent_messages)
        
        # Normalize based on typical message length (100 chars)
        engagement = min(avg_length / 100.0, 1.0)
        return engagement
    
    async def _calculate_similarity_to_existing(self, text: str) -> float:
        """Calculate similarity to existing memories"""
        try:
            if not self.memory_service:
                return 0.0
                
            # Search for similar content in existing memories
            memories = await self.memory_service.search_memories(
                query=text,
                max_results=1,
                similarity_threshold=0.0
            )
            
            if memories:
                # Check if it's a Memory object or dict
                if hasattr(memories[0], 'similarity_score'):
                    return memories[0].similarity_score
                elif isinstance(memories[0], dict):
                    return memories[0].get('similarity', 0.0)
                else:
                    return 0.0
            return 0.0
        except Exception as e:
            logger.debug(f"Error calculating similarity to existing: {e}")
            return 0.0
    
    def _count_importance_indicators(self, text: str) -> int:
        """Count indicators of important content"""
        text_lower = text.lower()
        return sum(1 for indicator in self.importance_indicators 
                  if indicator in text_lower)
    
    async def _calculate_topic_coherence(self, text: str, history: List[Dict]) -> float:
        """Calculate how coherent the current message is with conversation topic"""
        if not history:
            return 1.0
        
        try:
            # Get recent conversation context
            recent_context = " ".join([
                msg.get('content', '') for msg in history[-3:]
            ])
            
            if not recent_context.strip():
                return 1.0
            
            # Calculate semantic similarity between current message and recent context
            current_embedding = await self.embedding_service.generate_embedding(text)
            context_embedding = await self.embedding_service.generate_embedding(recent_context)
            
            # Calculate cosine similarity
            similarity = cosine_similarity(
                [current_embedding], [context_embedding]
            )[0][0]
            
            return float(similarity)
        except Exception:
            return 0.5


class HuggingFaceMLTriggerModel:
    """Production-ready ML model using trained Hugging Face model"""
    
    def __init__(self, model_name: str = "PiGrieco/mcp-memory-auto-trigger-model"):
        """Initialize with the trained HF model"""
        self.model_name = model_name
        self.classifier = None
        self.class_mapping = {
            "SAVE_MEMORY": ActionType.SAVE_MEMORY,
            "SEARCH_MEMORY": ActionType.SEARCH_MEMORY, 
            "NO_ACTION": ActionType.NO_ACTION
        }
        self.label_mapping = {0: "SAVE_MEMORY", 1: "SEARCH_MEMORY", 2: "NO_ACTION"}
        self.confidence_threshold = 0.7  # Minimum confidence for prediction
        
        logger.info(f"Initializing HuggingFace ML model: {model_name}")
        
    def load_model(self) -> bool:
        """Load the trained model from Hugging Face Hub"""
        try:
            if not HAS_TORCH:
                logger.error("PyTorch not available for HuggingFace model")
                return False
                
            logger.info(f"Loading model from HuggingFace Hub: {self.model_name}")
            
            # Load using pipeline for easy inference
            device = -1  # Default to CPU
            if HAS_TORCH:
                try:
                    import torch
                    if torch.cuda.is_available():
                        device = 0  # Use GPU if available
                except Exception:
                    pass  # Keep CPU device
                
            self.classifier = pipeline(
                "text-classification",
                model=self.model_name,
                tokenizer=self.model_name,
                return_all_scores=True,
                device=device
            )
            
            logger.info("✅ HuggingFace model loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load HuggingFace model: {e}")
            return False
    
    def predict(self, text: str, features: MLFeatures = None) -> Tuple[ActionType, float]:
        """Make prediction using the HuggingFace model"""
        if not self.classifier:
            if not self.load_model():
                return ActionType.NO_ACTION, 0.0
        
        try:
            # Use the provided text for prediction
            if not text or not text.strip():
                return ActionType.NO_ACTION, 0.5
            
            # Get predictions with confidence scores
            predictions = self.classifier(text)
            
            # Handle both single prediction and list of predictions
            if isinstance(predictions, list) and len(predictions) > 0:
                if isinstance(predictions[0], list):
                    # Multiple predictions per input - take first input's predictions
                    pred_list = predictions[0]
                else:
                    # Single input predictions
                    pred_list = predictions
            else:
                # Single prediction
                pred_list = [predictions] if not isinstance(predictions, list) else predictions
            
            # Find the prediction with highest score
            best_prediction = max(pred_list, key=lambda x: x['score'])
            predicted_label = best_prediction['label']
            confidence = best_prediction['score']
            
            # Map to ActionType
            action = self.class_mapping.get(predicted_label, ActionType.NO_ACTION)
            
            logger.debug(f"HF Prediction: {predicted_label} (confidence: {confidence:.3f})")
            
            return action, confidence
            
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return ActionType.NO_ACTION, 0.0
    
    def update_model(self, features: MLFeatures, action: ActionType, user_feedback: Optional[Dict[str, Any]] = None) -> bool:
        """
        Note: The HuggingFace model is pre-trained and frozen.
        For online learning, we'd need to implement fine-tuning, which is complex.
        For now, we log the feedback for future retraining.
        """
        try:
            feedback_data = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'predicted_action': action.value,
                'user_feedback': user_feedback,
                'features': asdict(features) if features else None
            }
            
            # Log for future retraining
            logger.info(f"Feedback logged for model improvement: {feedback_data}")
            
            # TODO: Implement periodic retraining pipeline
            return True
            
        except Exception as e:
            logger.error(f"Error logging feedback: {e}")
            return False
    
    def get_feature_importance(self) -> Dict[str, float]:
        """
        Feature importance for transformer models is complex.
        Return placeholder values.
        """
        return {
            "message_text": 0.8,
            "conversation_context": 0.15,
            "user_patterns": 0.05
        }


class MLTriggerModel:
    """Machine Learning model for trigger decisions"""
    
    def __init__(self, model_dir: Path):
        self.model_dir = model_dir
        self.model_dir.mkdir(parents=True, exist_ok=True)
        
        # Model components
        self.save_model = None
        self.search_model = None
        self.feature_scaler = None
        
        # Training data
        self.training_data = []
        self.model_version = "1.0.0"
        
        # Initialize models
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize ML models"""
        if not HAS_SKLEARN:
            logger.warning("scikit-learn not available, using fallback model")
            return
        
        # Binary classifiers for save/search decisions
        self.save_model = GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=6,
            random_state=42
        )
        
        self.search_model = GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=6,
            random_state=42
        )
        
        self.feature_scaler = StandardScaler()
    
    def features_to_vector(self, features: MLFeatures) -> np.ndarray:
        """Convert MLFeatures to numpy vector"""
        # Convert categorical platform to numeric
        platform_encoding = {
            'cursor': 0, 'claude': 1, 'browser': 2, 'api': 3, 'unknown': 4
        }
        platform_encoded = platform_encoding.get(features.platform_type, 4)
        
        vector = np.array([
            features.text_length,
            features.word_count, 
            features.sentence_count,
            features.avg_word_length,
            features.semantic_density,
            features.technical_content_score,
            features.question_score,
            features.solution_score,
            features.conversation_position,
            features.time_since_last_message,
            features.user_engagement_score,
            features.similarity_to_existing,
            features.novelty_score,
            features.importance_indicators,
            platform_encoded,
            features.session_length,
            features.user_save_frequency,
            features.user_search_frequency,
            features.topic_coherence
        ])
        
        return vector.reshape(1, -1)
    
    async def predict(self, features: MLFeatures) -> MLPrediction:
        """Predict action based on features"""
        if not HAS_SKLEARN or self.save_model is None:
            return self._fallback_prediction(features)
        
        try:
            # Convert features to vector
            feature_vector = self.features_to_vector(features)
            
            # Scale features if trained
            if hasattr(self.feature_scaler, 'mean_'):
                feature_vector = self.feature_scaler.transform(feature_vector)
            
            # Get predictions and confidence scores
            save_proba = self.save_model.predict_proba(feature_vector)[0]
            search_proba = self.search_model.predict_proba(feature_vector)[0]
            
            save_confidence = save_proba[1] if len(save_proba) > 1 else 0.0
            search_confidence = search_proba[1] if len(search_proba) > 1 else 0.0
            
            # Determine action based on confidence scores
            if save_confidence > 0.7:  # High confidence for save
                action = ActionType.SAVE_MEMORY
                confidence = save_confidence
                reasoning = self._generate_reasoning(features, "save", confidence)
            elif search_confidence > 0.6:  # Medium confidence for search
                action = ActionType.SEARCH_MEMORY
                confidence = search_confidence
                reasoning = self._generate_reasoning(features, "search", confidence)
            else:
                action = ActionType.NO_ACTION
                confidence = max(1.0 - save_confidence, 1.0 - search_confidence)
                reasoning = ["Confidence too low for any action"]
            
            return MLPrediction(
                action=action,
                confidence=confidence,
                reasoning=reasoning,
                features_used=self._get_important_features(features),
                should_learn=True
            )
            
        except Exception as e:
            logger.error(f"ML prediction failed: {e}")
            return self._fallback_prediction(features)
    
    def _fallback_prediction(self, features: MLFeatures) -> MLPrediction:
        """Fallback prediction when ML is not available"""
        # Simple heuristic-based prediction
        score = 0.0
        reasoning = []
        
        # High importance indicators suggest save
        if features.importance_indicators > 2:
            score += 0.3
            reasoning.append("High importance indicators")
        
        # Technical content with solutions suggests save
        if features.technical_content_score > 0.6 and features.solution_score > 0.5:
            score += 0.4
            reasoning.append("Technical solution content")
        
        # High novelty suggests save
        if features.novelty_score > 0.8:
            score += 0.2
            reasoning.append("Novel information")
        
        # Questions with low similarity suggest search
        if features.question_score > 0.5 and features.similarity_to_existing > 0.3:
            action = ActionType.SEARCH_MEMORY
            confidence = 0.6
            reasoning.append("Question with potential existing answers")
        elif score > 0.7:
            action = ActionType.SAVE_MEMORY
            confidence = score
        else:
            action = ActionType.NO_ACTION
            confidence = 1.0 - score
            reasoning.append("No strong indicators for action")
        
        return MLPrediction(
            action=action,
            confidence=confidence,
            reasoning=reasoning,
            features_used=["heuristic_fallback"],
            should_learn=False
        )
    
    def _generate_reasoning(self, features: MLFeatures, action: str, confidence: float) -> List[str]:
        """Generate human-readable reasoning for the prediction"""
        reasoning = []
        
        if action == "save":
            if features.importance_indicators > 1:
                reasoning.append(f"High importance signals ({features.importance_indicators} indicators)")
            if features.technical_content_score > 0.5:
                reasoning.append(f"Technical content (score: {features.technical_content_score:.2f})")
            if features.solution_score > 0.5:
                reasoning.append(f"Solution provided (score: {features.solution_score:.2f})")
            if features.novelty_score > 0.7:
                reasoning.append(f"Novel information (novelty: {features.novelty_score:.2f})")
        
        elif action == "search":
            if features.question_score > 0.5:
                reasoning.append(f"Question asked (score: {features.question_score:.2f})")
            if features.similarity_to_existing > 0.3:
                reasoning.append(f"Similar content exists (similarity: {features.similarity_to_existing:.2f})")
        
        reasoning.append(f"Model confidence: {confidence:.2f}")
        return reasoning
    
    def _get_important_features(self, features: MLFeatures) -> List[str]:
        """Get list of most important features for this prediction"""
        important = []
        
        if features.importance_indicators > 0:
            important.append("importance_indicators")
        if features.technical_content_score > 0.5:
            important.append("technical_content")
        if features.question_score > 0.5:
            important.append("question_content")
        if features.solution_score > 0.5:
            important.append("solution_content")
        if features.novelty_score > 0.7:
            important.append("novelty")
        if features.similarity_to_existing > 0.3:
            important.append("similarity")
        
        return important
    
    async def learn_from_feedback(
        self, 
        features: MLFeatures, 
        actual_action: ActionType,
        user_feedback: Optional[Dict[str, Any]] = None
    ):
        """Learn from user actions and feedback"""
        if not HAS_SKLEARN:
            return
        
        # Add to training data
        feature_vector = self.features_to_vector(features)[0]
        
        # Create labels (1 if action was taken, 0 if not)
        save_label = 1 if actual_action == ActionType.SAVE_MEMORY else 0
        search_label = 1 if actual_action == ActionType.SEARCH_MEMORY else 0
        
        self.training_data.append({
            'features': feature_vector,
            'save_label': save_label,
            'search_label': search_label,
            'timestamp': datetime.now().isoformat(),
            'user_feedback': user_feedback
        })
        
        # Retrain models periodically
        if len(self.training_data) % 50 == 0:  # Retrain every 50 examples
            await self._retrain_models()
    
    async def _retrain_models(self):
        """Retrain models with accumulated data"""
        if len(self.training_data) < 10:  # Need minimum data
            return
        
        try:
            # Prepare training data
            X = np.array([item['features'] for item in self.training_data])
            y_save = np.array([item['save_label'] for item in self.training_data])
            y_search = np.array([item['search_label'] for item in self.training_data])
            
            # Scale features
            X_scaled = self.feature_scaler.fit_transform(X)
            
            # Train models
            self.save_model.fit(X_scaled, y_save)
            self.search_model.fit(X_scaled, y_search)
            
            # Save models
            await self._save_models()
            
            logger.info(f"Models retrained with {len(self.training_data)} examples")
            
        except Exception as e:
            logger.error(f"Model retraining failed: {e}")
    
    async def _save_models(self):
        """Save trained models to disk"""
        try:
            model_data = {
                'save_model': self.save_model,
                'search_model': self.search_model,
                'feature_scaler': self.feature_scaler,
                'training_data': self.training_data[-1000:],  # Keep last 1000 examples
                'model_version': self.model_version,
                'timestamp': datetime.now().isoformat()
            }
            
            model_file = self.model_dir / 'ml_trigger_models.pkl'
            with open(model_file, 'wb') as f:
                pickle.dump(model_data, f)
            
            logger.info(f"Models saved to {model_file}")
            
        except Exception as e:
            logger.error(f"Model saving failed: {e}")
    
    async def load_models(self):
        """Load trained models from disk"""
        try:
            model_file = self.model_dir / 'ml_trigger_models.pkl'
            if model_file.exists():
                with open(model_file, 'rb') as f:
                    model_data = pickle.load(f)
                
                self.save_model = model_data.get('save_model')
                self.search_model = model_data.get('search_model')
                self.feature_scaler = model_data.get('feature_scaler')
                self.training_data = model_data.get('training_data', [])
                self.model_version = model_data.get('model_version', '1.0.0')
                
                logger.info(f"Models loaded from {model_file}")
                return True
            
        except Exception as e:
            logger.error(f"Model loading failed: {e}")
        
        return False


class MLAutoTriggerSystem:
    """
    ML-based auto-trigger system that learns when to save/retrieve memories
    """
    
    def __init__(self, memory_service: MemoryService, embedding_service: EmbeddingService):
        self.config = get_settings()
        self.memory_service = memory_service
        self.embedding_service = embedding_service
        
        # Initialize components
        self.feature_extractor = FeatureExtractor(embedding_service, memory_service)
        
        # Initialize ML model based on configuration
        if self.config.ml_triggers.model_type == "huggingface":
            self.ml_model = HuggingFaceMLTriggerModel(
                model_name=self.config.ml_triggers.huggingface_model_name
            )
            logger.info(f"Using HuggingFace model: {self.config.ml_triggers.huggingface_model_name}")
        else:
            # Fallback to sklearn model
            model_dir = Path(self.config.embedding.model_cache_dir)
            self.ml_model = MLTriggerModel(model_dir)
            logger.info(f"Using sklearn model: {self.config.ml_triggers.model_type}")
        
        # User behavior tracking
        self.user_contexts = {}
        self.action_history = []
        
        # Performance metrics
        self.metrics = {
            'predictions_made': 0,
            'actions_taken': 0,
            'save_actions': 0,
            'search_actions': 0,
            'correct_predictions': 0,
            'user_corrections': 0
        }
        
        logger.info("ML Auto-trigger system initialized")
    
    async def initialize(self):
        """Initialize the ML system"""
        # Load pre-trained models if available
        if hasattr(self.ml_model, 'load_models'):
            # For sklearn-based models
            await self.ml_model.load_models()
        elif hasattr(self.ml_model, 'load_model'):
            # For HuggingFace models
            self.ml_model.load_model()
        
        # Initialize user contexts from history
        await self._initialize_user_contexts()
    
    async def analyze_and_predict(
        self,
        message: str,
        conversation_history: List[Dict[str, Any]],
        platform: str = "unknown",
        user_id: str = "default"
    ) -> MLPrediction:
        """Analyze message and predict required action"""
        
        try:
            # Get or create user context
            user_context = self.user_contexts.get(user_id, {
                'save_frequency': 0.0,
                'search_frequency': 0.0,
                'total_interactions': 0,
                'preferences': {}
            })
            
            # Extract features
            features = await self.feature_extractor.extract_features(
                message=message,
                conversation_history=conversation_history,
                platform=platform,
                user_context=user_context
            )
            
            # Get ML prediction
            if hasattr(self.ml_model, 'predict'):
                # For HuggingFace models, pass the text directly
                if isinstance(self.ml_model, HuggingFaceMLTriggerModel):
                    action, confidence = self.ml_model.predict(message)
                    prediction = MLPrediction(
                        action=action,
                        confidence=confidence,
                        reasoning=[f"HuggingFace prediction: {action.value}"],
                        features_used=["message_text"],
                        should_learn=True
                    )
                else:
                    # For sklearn models, use features
                    prediction = await self.ml_model.predict(features)
            else:
                # Fallback prediction
                prediction = MLPrediction(
                    action=ActionType.NO_ACTION,
                    confidence=0.0,
                    reasoning=["ML model not available"],
                    features_used=[],
                    should_learn=False
                )
            
            # Update metrics
            self.metrics['predictions_made'] += 1
            
            # Update user context
            self._update_user_context(user_id, features, prediction)
            
            logger.info(f"ML prediction: {prediction.action.value} (confidence: {prediction.confidence:.2f})")
            return prediction
            
        except Exception as e:
            logger.error(f"ML analysis failed: {e}")
            # Fallback to simple heuristics
            return MLPrediction(
                action=ActionType.NO_ACTION,
                confidence=0.0,
                reasoning=[f"Analysis failed: {str(e)}"],
                features_used=[],
                should_learn=False
            )
    
    async def learn_from_action(
        self,
        features: MLFeatures,
        action_taken: ActionType,
        user_id: str = "default",
        user_feedback: Optional[Dict[str, Any]] = None
    ):
        """Learn from actual actions taken"""
        
        # Record action in history
        self.action_history.append({
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'action': action_taken.value,
            'features': asdict(features) if features else None,
            'feedback': user_feedback
        })
        
        # Update user context
        if user_id in self.user_contexts:
            context = self.user_contexts[user_id]
            context['total_interactions'] += 1
            
            if action_taken == ActionType.SAVE_MEMORY:
                context['save_frequency'] = (
                    context['save_frequency'] * 0.9 + 0.1
                )  # Moving average
                self.metrics['save_actions'] += 1
                
            elif action_taken == ActionType.SEARCH_MEMORY:
                context['search_frequency'] = (
                    context['search_frequency'] * 0.9 + 0.1
                )
                self.metrics['search_actions'] += 1
        
        # Learn from the action
        await self.ml_model.learn_from_feedback(features, action_taken, user_feedback)
        
        self.metrics['actions_taken'] += 1
        
        logger.info(f"Learned from action: {action_taken.value} for user {user_id}")
    
    def _update_user_context(self, user_id: str, features: MLFeatures, prediction: MLPrediction):
        """Update user context based on interaction"""
        if user_id not in self.user_contexts:
            self.user_contexts[user_id] = {
                'save_frequency': 0.0,
                'search_frequency': 0.0,
                'total_interactions': 0,
                'preferences': {}
            }
        
        context = self.user_contexts[user_id]
        context['total_interactions'] += 1
        
        # Update preferences based on features
        prefs = context['preferences']
        if features.technical_content_score > 0.5:
            prefs['prefers_technical'] = prefs.get('prefers_technical', 0) + 1
        
        if features.question_score > 0.5:
            prefs['asks_questions'] = prefs.get('asks_questions', 0) + 1
    
    async def _initialize_user_contexts(self):
        """Initialize user contexts from historical data"""
        # This could load from database or previous sessions
        pass
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get system performance metrics"""
        return {
            **self.metrics,
            'accuracy': (
                self.metrics['correct_predictions'] / 
                max(self.metrics['predictions_made'], 1)
            ),
            'users_tracked': len(self.user_contexts),
            'model_version': self.ml_model.model_version
        }
    
    async def export_training_data(self, file_path: Path):
        """Export training data for analysis"""
        data = {
            'action_history': self.action_history,
            'user_contexts': self.user_contexts,
            'metrics': self.metrics,
            'export_timestamp': datetime.now().isoformat()
        }
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Training data exported to {file_path}")


def create_ml_auto_trigger_system(
    memory_service: MemoryService, 
    embedding_service: EmbeddingService
) -> MLAutoTriggerSystem:
    """Create and initialize ML auto-trigger system"""
    system = MLAutoTriggerSystem(memory_service, embedding_service)
    return system
