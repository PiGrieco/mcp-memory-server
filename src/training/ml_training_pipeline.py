#!/usr/bin/env python3
"""
ML Training Pipeline for Auto-Trigger System
Generates training data and trains initial models
"""

import json
import random
import numpy as np
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Any, Tuple

# ML imports
try:
    from sklearn.model_selection import train_test_split, cross_val_score
    from sklearn.metrics import classification_report, confusion_matrix
    from sklearn.ensemble import RandomForestClassifier

    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

from ..core.ml_trigger_system import (
    MLFeatures, ActionType, FeatureExtractor
)
from ..services.embedding_service import EmbeddingService
from ..services.memory_service import MemoryService
from ..utils.logging import get_logger


logger = get_logger(__name__)


class TrainingDataGenerator:
    """Generate synthetic training data for initial model training"""
    
    def __init__(self, embedding_service: EmbeddingService, memory_service: MemoryService):
        self.embedding_service = embedding_service
        self.memory_service = memory_service
        self.feature_extractor = FeatureExtractor(embedding_service)
        
        # Training scenarios
        self.save_scenarios = [
            # High importance content
            {
                'messages': [
                    "Ricorda che per fixare il CORS devi aggiungere Access-Control-Allow-Origin nell'header",
                    "Importante: il bug di memory leak era causato dalla mancata chiusura delle connessioni database",
                    "Soluzione trovata: aumentare il timeout di connessione a 30 secondi per risolvere il problema",
                    "Note: utilizzare useCallback per ottimizzare le performance di React",
                    "CRITICAL: il deployment deve includere le variabili d'ambiente per la produzione"
                ],
                'action': ActionType.SAVE_MEMORY,
                'importance': 0.9
            },
            
            # Technical solutions
            {
                'messages': [
                    "Ho risolto il problema di autenticazione implementando JWT con refresh tokens",
                    "Fixed: il bug dei character encoding era dovuto al charset UTF-8 non impostato",
                    "Tutorial: ecco come configurare Docker per il deployment automatico",
                    "Soluzione: usare Redis per il caching delle query frequenti",
                    "How to: implementare pagination efficiente con cursors invece di offset"
                ],
                'action': ActionType.SAVE_MEMORY,
                'importance': 0.8
            },
            
            # Code examples and configurations
            {
                'messages': [
                    "Questo pattern funziona bene per la gestione degli errori async:\n\ntry {\n  await apiCall();\n} catch (error) {\n  handleError(error);\n}",
                    "Configurazione nginx per reverse proxy:\nserver {\n  listen 80;\n  location / {\n    proxy_pass http://backend;\n  }\n}",
                    "Query SQL ottimizzata per large datasets:\nSELECT * FROM users WHERE created_at > '2024-01-01' LIMIT 1000;",
                    "Docker compose per sviluppo:\nversion: '3.8'\nservices:\n  app:\n    build: .\n    ports:\n      - '3000:3000'"
                ],
                'action': ActionType.SAVE_MEMORY,
                'importance': 0.7
            }
        ]
        
        self.search_scenarios = [
            # Questions about existing topics
            {
                'messages': [
                    "Come posso gestire i timeout nel database?",
                    "What's the best way to handle CORS errors?",
                    "How do I optimize React performance?",
                    "Come configurare Docker per production?",
                    "What are the best practices for JWT authentication?"
                ],
                'action': ActionType.SEARCH_MEMORY,
                'importance': 0.6
            },
            
            # Troubleshooting queries
            {
                'messages': [
                    "Sto avendo problemi con memory leaks nell'applicazione",
                    "L'API sta ritornando errori 500, come posso debuggare?",
                    "Il deployment failed, dove posso controllare i log?",
                    "La performance è degradata, come posso identificare il bottleneck?",
                    "Character encoding issues con UTF-8, avevamo già risolto?"
                ],
                'action': ActionType.SEARCH_MEMORY,
                'importance': 0.7
            }
        ]
        
        self.no_action_scenarios = [
            # General conversation
            {
                'messages': [
                    "Ciao, come stai?",
                    "Che tempo fa oggi?",
                    "Ho mangiato bene a pranzo",
                    "Il weekend è stato rilassante",
                    "Grazie per l'aiuto di ieri"
                ],
                'action': ActionType.NO_ACTION,
                'importance': 0.1
            },
            
            # Low-value content
            {
                'messages': [
                    "Ok",
                    "Perfetto",
                    "Capito",
                    "Va bene così",
                    "Sì, esatto"
                ],
                'action': ActionType.NO_ACTION,
                'importance': 0.0
            },
            
            # Incomplete or unclear content
            {
                'messages': [
                    "Non sono sicuro di...",
                    "Forse potrebbe essere...",
                    "Uhm, non so se...",
                    "Dipende da...",
                    "Potrebbe funzionare ma..."
                ],
                'action': ActionType.NO_ACTION,
                'importance': 0.2
            }
        ]
    
    async def generate_training_samples(self, num_samples: int = 1000) -> List[Tuple[MLFeatures, ActionType]]:
        """Generate synthetic training samples"""
        
        samples = []
        scenarios = [
            (self.save_scenarios, ActionType.SAVE_MEMORY),
            (self.search_scenarios, ActionType.SEARCH_MEMORY),
            (self.no_action_scenarios, ActionType.NO_ACTION)
        ]
        
        # Distribute samples across scenarios
        samples_per_action = num_samples // 3
        
        for scenario_list, action_type in scenarios:
            for _ in range(samples_per_action):
                # Pick random scenario
                scenario = random.choice(scenario_list)
                message = random.choice(scenario['messages'])
                
                # Generate conversation history
                history = await self._generate_conversation_history()
                
                # Add some variation to the message
                varied_message = self._add_message_variation(message)
                
                # Extract features
                features = await self.feature_extractor.extract_features(
                    message=varied_message,
                    conversation_history=history,
                    platform=random.choice(['cursor', 'claude', 'browser', 'api']),
                    user_context={
                        'save_frequency': random.uniform(0.0, 1.0),
                        'search_frequency': random.uniform(0.0, 1.0)
                    }
                )
                
                samples.append((features, action_type))
        
        logger.info(f"Generated {len(samples)} training samples")
        return samples
    
    async def _generate_conversation_history(self) -> List[Dict[str, Any]]:
        """Generate realistic conversation history"""
        
        history_templates = [
            # Technical discussion
            [
                {"role": "user", "content": "Sto lavorando su un progetto React"},
                {"role": "assistant", "content": "Ottimo! Su cosa ti serve aiuto?"},
                {"role": "user", "content": "Ho problemi con le performance"}
            ],
            
            # Debugging session
            [
                {"role": "user", "content": "L'applicazione sta crashando"},
                {"role": "assistant", "content": "Puoi condividere il messaggio di errore?"},
                {"role": "user", "content": "Error: Cannot read property of undefined"}
            ],
            
            # Learning session
            [
                {"role": "user", "content": "Come funziona Docker?"},
                {"role": "assistant", "content": "Docker è una piattaforma di containerizzazione..."},
                {"role": "user", "content": "Interessante, potresti fare un esempio?"}
            ]
        ]
        
        template = random.choice(history_templates)
        
        # Add timestamps
        history = []
        base_time = datetime.now(timezone.utc) - timedelta(minutes=30)
        
        for i, msg in enumerate(template):
            history.append({
                **msg,
                'timestamp': (base_time + timedelta(minutes=i*2)).isoformat()
            })
        
        return history
    
    def _add_message_variation(self, message: str) -> str:
        """Add variation to messages to increase diversity"""
        
        variations = [
            # Add emphasis
            lambda m: m.upper() if len(m) < 50 else m,
            
            # Add punctuation
            lambda m: m + "!" if not m.endswith(('!', '?', '.')) else m,
            
            # Add context
            lambda m: f"Btw, {m.lower()}" if random.random() < 0.3 else m,
            
            # Add uncertainty
            lambda m: f"Penso che {m.lower()}" if random.random() < 0.2 else m,
            
            # Keep original
            lambda m: m
        ]
        
        variation = random.choice(variations)
        return variation(message)
    
    async def generate_user_behavior_data(self, num_users: int = 50) -> Dict[str, Any]:
        """Generate realistic user behavior patterns"""
        
        user_patterns = []
        
        for user_id in range(num_users):
            # Define user archetypes
            if user_id < 15:  # Power users
                pattern = {
                    'user_id': f'power_user_{user_id}',
                    'save_frequency': random.uniform(0.7, 1.0),
                    'search_frequency': random.uniform(0.6, 0.9),
                    'technical_preference': random.uniform(0.8, 1.0),
                    'platforms': ['cursor', 'claude', 'api'],
                    'session_length_avg': random.randint(20, 50)
                }
            elif user_id < 35:  # Regular users
                pattern = {
                    'user_id': f'regular_user_{user_id}',
                    'save_frequency': random.uniform(0.3, 0.7),
                    'search_frequency': random.uniform(0.4, 0.8),
                    'technical_preference': random.uniform(0.4, 0.8),
                    'platforms': ['cursor', 'claude'],
                    'session_length_avg': random.randint(10, 30)
                }
            else:  # Casual users
                pattern = {
                    'user_id': f'casual_user_{user_id}',
                    'save_frequency': random.uniform(0.1, 0.4),
                    'search_frequency': random.uniform(0.2, 0.5),
                    'technical_preference': random.uniform(0.1, 0.5),
                    'platforms': ['browser', 'claude'],
                    'session_length_avg': random.randint(5, 15)
                }
            
            user_patterns.append(pattern)
        
        return {'user_patterns': user_patterns}


class MLTrainingPipeline:
    """Complete training pipeline for ML trigger system"""
    
    def __init__(self, embedding_service: EmbeddingService, memory_service: MemoryService):
        self.embedding_service = embedding_service
        self.memory_service = memory_service
        self.data_generator = TrainingDataGenerator(embedding_service, memory_service)
        
        # Training configuration
        self.config = {
            'train_test_split': 0.8,
            'validation_split': 0.1,
            'cross_validation_folds': 5,
            'random_state': 42
        }
    
    async def run_full_pipeline(self, output_dir: Path, num_samples: int = 1000):
        """Run complete training pipeline"""
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("Starting ML training pipeline")
        
        # Step 1: Generate training data
        logger.info("Generating training data...")
        training_samples = await self.data_generator.generate_training_samples(num_samples)
        
        # Step 2: Prepare data for training
        logger.info("Preparing data for training...")
        X, y_save, y_search = await self._prepare_training_data(training_samples)
        
        # Step 3: Train models
        logger.info("Training models...")
        models = await self._train_models(X, y_save, y_search)
        
        # Step 4: Evaluate models
        logger.info("Evaluating models...")
        evaluation_results = await self._evaluate_models(models, X, y_save, y_search)
        
        # Step 5: Save models and results
        logger.info("Saving models and results...")
        await self._save_training_results(
            output_dir, models, evaluation_results, training_samples
        )
        
        logger.info(f"Training pipeline completed. Results saved to {output_dir}")
        
        return {
            'models': models,
            'evaluation': evaluation_results,
            'data_samples': len(training_samples)
        }
    
    async def _prepare_training_data(
        self, 
        training_samples: List[Tuple[MLFeatures, ActionType]]
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Prepare training data for sklearn models"""
        
        # Convert features to vectors
        feature_vectors = []
        save_labels = []
        search_labels = []
        
        for features, action in training_samples:
            # Convert MLFeatures to numpy array
            vector = self._features_to_vector(features)
            feature_vectors.append(vector)
            
            # Create binary labels
            save_labels.append(1 if action == ActionType.SAVE_MEMORY else 0)
            search_labels.append(1 if action == ActionType.SEARCH_MEMORY else 0)
        
        X = np.array(feature_vectors)
        y_save = np.array(save_labels)
        y_search = np.array(search_labels)
        
        return X, y_save, y_search
    
    def _features_to_vector(self, features: MLFeatures) -> np.ndarray:
        """Convert MLFeatures to numpy vector"""
        
        # Platform encoding
        platform_encoding = {
            'cursor': 0, 'claude': 1, 'browser': 2, 'api': 3, 'unknown': 4
        }
        platform_encoded = platform_encoding.get(features.platform_type, 4)
        
        return np.array([
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
    
    async def _train_models(
        self, 
        X: np.ndarray, 
        y_save: np.ndarray, 
        y_search: np.ndarray
    ) -> Dict[str, Any]:
        """Train ML models"""
        
        if not HAS_SKLEARN:
            logger.error("scikit-learn not available for training")
            return {}
        
        # Split data
        X_train, X_test, y_save_train, y_save_test = train_test_split(
            X, y_save, test_size=1-self.config['train_test_split'], 
            random_state=self.config['random_state']
        )
        
        _, _, y_search_train, y_search_test = train_test_split(
            X, y_search, test_size=1-self.config['train_test_split'], 
            random_state=self.config['random_state']
        )
        
        # Train save model
        save_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=self.config['random_state']
        )
        save_model.fit(X_train, y_save_train)
        
        # Train search model
        search_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=self.config['random_state']
        )
        search_model.fit(X_train, y_search_train)
        
        return {
            'save_model': save_model,
            'search_model': search_model,
            'X_train': X_train,
            'X_test': X_test,
            'y_save_train': y_save_train,
            'y_save_test': y_save_test,
            'y_search_train': y_search_train,
            'y_search_test': y_search_test
        }
    
    async def _evaluate_models(
        self, 
        models: Dict[str, Any], 
        X: np.ndarray, 
        y_save: np.ndarray, 
        y_search: np.ndarray
    ) -> Dict[str, Any]:
        """Evaluate trained models"""
        
        if not HAS_SKLEARN or not models:
            return {}
        
        evaluation = {}
        
        # Evaluate save model
        save_model = models['save_model']
        X_test = models['X_test']
        y_save_test = models['y_save_test']
        
        y_save_pred = save_model.predict(X_test)
        save_scores = cross_val_score(
            save_model, X, y_save, 
            cv=self.config['cross_validation_folds']
        )
        
        evaluation['save_model'] = {
            'accuracy': save_model.score(X_test, y_save_test),
            'cross_val_scores': save_scores.tolist(),
            'cross_val_mean': save_scores.mean(),
            'cross_val_std': save_scores.std(),
            'classification_report': classification_report(
                y_save_test, y_save_pred, output_dict=True
            ),
            'confusion_matrix': confusion_matrix(y_save_test, y_save_pred).tolist()
        }
        
        # Evaluate search model
        search_model = models['search_model']
        y_search_test = models['y_search_test']
        
        y_search_pred = search_model.predict(X_test)
        search_scores = cross_val_score(
            search_model, X, y_search, 
            cv=self.config['cross_validation_folds']
        )
        
        evaluation['search_model'] = {
            'accuracy': search_model.score(X_test, y_search_test),
            'cross_val_scores': search_scores.tolist(),
            'cross_val_mean': search_scores.mean(),
            'cross_val_std': search_scores.std(),
            'classification_report': classification_report(
                y_search_test, y_search_pred, output_dict=True
            ),
            'confusion_matrix': confusion_matrix(y_search_test, y_search_pred).tolist()
        }
        
        # Feature importance
        if hasattr(save_model, 'feature_importances_'):
            feature_names = [
                'text_length', 'word_count', 'sentence_count', 'avg_word_length',
                'semantic_density', 'technical_content_score', 'question_score',
                'solution_score', 'conversation_position', 'time_since_last_message',
                'user_engagement_score', 'similarity_to_existing', 'novelty_score',
                'importance_indicators', 'platform_type', 'session_length',
                'user_save_frequency', 'user_search_frequency', 'topic_coherence'
            ]
            
            evaluation['feature_importance'] = {
                'save_model': dict(zip(feature_names, save_model.feature_importances_)),
                'search_model': dict(zip(feature_names, search_model.feature_importances_))
            }
        
        return evaluation
    
    async def _save_training_results(
        self,
        output_dir: Path,
        models: Dict[str, Any],
        evaluation: Dict[str, Any],
        training_samples: List[Tuple[MLFeatures, ActionType]]
    ):
        """Save training results and models"""
        
        # Save evaluation results
        evaluation_file = output_dir / 'evaluation_results.json'
        with open(evaluation_file, 'w') as f:
            json.dump(evaluation, f, indent=2)
        
        # Save training data summary
        data_summary = {
            'total_samples': len(training_samples),
            'save_samples': sum(1 for _, action in training_samples if action == ActionType.SAVE_MEMORY),
            'search_samples': sum(1 for _, action in training_samples if action == ActionType.SEARCH_MEMORY),
            'no_action_samples': sum(1 for _, action in training_samples if action == ActionType.NO_ACTION),
            'generation_timestamp': datetime.now().isoformat()
        }
        
        summary_file = output_dir / 'training_summary.json'
        with open(summary_file, 'w') as f:
            json.dump(data_summary, f, indent=2)
        
        # Save models if sklearn is available
        if HAS_SKLEARN and models:
            import pickle
            
            models_file = output_dir / 'trained_models.pkl'
            with open(models_file, 'wb') as f:
                pickle.dump({
                    'save_model': models['save_model'],
                    'search_model': models['search_model']
                }, f)
        
        # Generate and save feature importance plot
        if HAS_SKLEARN and 'feature_importance' in evaluation:
            await self._plot_feature_importance(evaluation['feature_importance'], output_dir)
        
        logger.info(f"Training results saved to {output_dir}")
    
    async def _plot_feature_importance(self, feature_importance: Dict[str, Dict], output_dir: Path):
        """Plot and save feature importance charts"""
        
        try:
            import matplotlib.pyplot as plt
            
            # Create subplots
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
            
            # Save model feature importance
            save_features = feature_importance['save_model']
            features = list(save_features.keys())
            importances = list(save_features.values())
            
            ax1.barh(features, importances)
            ax1.set_title('Save Model - Feature Importance')
            ax1.set_xlabel('Importance')
            
            # Search model feature importance
            search_features = feature_importance['search_model']
            features = list(search_features.keys())
            importances = list(search_features.values())
            
            ax2.barh(features, importances)
            ax2.set_title('Search Model - Feature Importance')
            ax2.set_xlabel('Importance')
            
            plt.tight_layout()
            plt.savefig(output_dir / 'feature_importance.png', dpi=300, bbox_inches='tight')
            plt.close()
            
        except Exception as e:
            logger.warning(f"Could not generate feature importance plot: {e}")


async def run_training_pipeline(
    embedding_service: EmbeddingService,
    memory_service: MemoryService,
    output_dir: str = "models/ml_training",
    num_samples: int = 1000
):
    """Convenience function to run the training pipeline"""
    
    pipeline = MLTrainingPipeline(embedding_service, memory_service)
    output_path = Path(output_dir)
    
    results = await pipeline.run_full_pipeline(output_path, num_samples)
    
    return results
