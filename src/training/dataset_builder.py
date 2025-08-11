#!/usr/bin/env python3
"""
Dataset Builder for Auto-Trigger ML Training
Generates comprehensive training data from multiple sources
"""

import random
import json
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import asyncio
from datetime import datetime

# ML imports
try:
    from datasets import Dataset, DatasetDict, load_dataset
    from transformers import AutoTokenizer
    from sklearn.model_selection import train_test_split
    HAS_DATASETS = True
except ImportError:
    HAS_DATASETS = False

from ..utils.logging import get_logger


logger = get_logger(__name__)


@dataclass
class DatasetConfig:
    """Configuration for dataset generation"""
    total_samples: int = 10000
    train_split: float = 0.8
    val_split: float = 0.1
    test_split: float = 0.1
    
    # Sources distribution
    synthetic_ratio: float = 0.6
    adapted_existing_ratio: float = 0.3
    real_user_ratio: float = 0.1
    
    # Language distribution
    english_ratio: float = 0.6
    italian_ratio: float = 0.4
    
    # Class balance
    save_memory_ratio: float = 0.4
    search_memory_ratio: float = 0.35
    no_action_ratio: float = 0.25


class SyntheticDataGenerator:
    """Generate synthetic training examples for auto-trigger"""
    
    def __init__(self, config: DatasetConfig):
        self.config = config
        self.label_mapping = {
            'SAVE_MEMORY': 0,
            'SEARCH_MEMORY': 1,
            'NO_ACTION': 2
        }
        
        # Initialize templates and vocabularies
        self._load_templates()
        self._load_vocabularies()
    
    def _load_templates(self):
        """Load text generation templates"""
        
        self.templates = {
            'SAVE_MEMORY': {
                'en': [
                    "Remember that {technical_info}",
                    "Important: {solution_info}",
                    "Save this configuration: {config_info}",
                    "Note for later: {important_info}",
                    "I solved {problem} with {solution}",
                    "Bug fix: {error_description} → {fix_description}",
                    "Tutorial: how to {action_description}",
                    "Documentation: {technical_explanation}",
                    "Fixed {issue_type} by {solution_method}",
                    "Configuration for {technology}: {config_details}",
                    "Solution found: {problem_context} solved with {solution_approach}",
                    "Critical: {urgent_info}",
                    "Store this pattern: {code_pattern}",
                    "Deployment notes: {deployment_info}",
                    "API key setup: {api_configuration}"
                ],
                'it': [
                    "Ricorda che {technical_info}",
                    "Importante: {solution_info}",
                    "Salva questa configurazione: {config_info}",
                    "Nota per dopo: {important_info}",
                    "Ho risolto {problem} con {solution}",
                    "Bug fix: {error_description} → {fix_description}",
                    "Tutorial: come {action_description}",
                    "Documentazione: {technical_explanation}",
                    "Risolto {issue_type} usando {solution_method}",
                    "Configurazione per {technology}: {config_details}",
                    "Soluzione trovata: {problem_context} risolto con {solution_approach}",
                    "Critico: {urgent_info}",
                    "Salva questo pattern: {code_pattern}",
                    "Note deployment: {deployment_info}",
                    "Setup API key: {api_configuration}"
                ]
            },
            
            'SEARCH_MEMORY': {
                'en': [
                    "How can I {question_about_topic}?",
                    "Did we already solve {problem_type}?",
                    "What's the best way to {technical_question}?",
                    "How do I configure {technology}?",
                    "Where did I save {information_type}?",
                    "Help with {technical_issue}",
                    "How to debug {error_type}?",
                    "Previous solution for {problem_pattern}?",
                    "I need to find {information_need}",
                    "Looking for {search_target}",
                    "Can you show me how to {task_description}?",
                    "What was the fix for {past_issue}?",
                    "How do I handle {situation_type}?",
                    "Where is the documentation for {feature}?",
                    "I'm getting {error_message}, how to fix?"
                ],
                'it': [
                    "Come posso {question_about_topic}?",
                    "Avevamo già risolto {problem_type}?",
                    "Qual è il modo migliore per {technical_question}?",
                    "Come si configura {technology}?",
                    "Dove avevo salvato {information_type}?",
                    "Aiuto con {technical_issue}",
                    "Come si debugga {error_type}?",
                    "Soluzione precedente per {problem_pattern}?",
                    "Devo trovare {information_need}",
                    "Cerco {search_target}",
                    "Puoi mostrarmi come {task_description}?",
                    "Qual era il fix per {past_issue}?",
                    "Come gestisco {situation_type}?",
                    "Dov'è la documentazione per {feature}?",
                    "Sto ricevendo {error_message}, come risolvere?"
                ]
            },
            
            'NO_ACTION': {
                'en': [
                    "Hello, how are you?",
                    "Thanks for the help",
                    "Alright, got it",
                    "Sure, no problem",
                    "OK, perfect",
                    "I understand",
                    "That makes sense",
                    "Good morning!",
                    "Have a nice day",
                    "See you later",
                    "Yes, exactly",
                    "No, that's fine",
                    "Maybe later",
                    "Sounds good",
                    "Great job!"
                ],
                'it': [
                    "Ciao, come stai?",
                    "Grazie per l'aiuto",
                    "Ok, capito",
                    "Certo, nessun problema",
                    "OK, perfetto",
                    "Ho capito",
                    "Ha senso",
                    "Buongiorno!",
                    "Buona giornata",
                    "Ci vediamo dopo",
                    "Sì, esatto",
                    "No, va bene",
                    "Magari dopo",
                    "Suona bene",
                    "Ottimo lavoro!"
                ]
            }
        }
    
    def _load_vocabularies(self):
        """Load domain-specific vocabularies for template filling"""
        
        self.vocabularies = {
            'technical_info': [
                "CORS requires Access-Control-Allow-Origin header",
                "JWT tokens should expire in 24 hours",
                "use environment variables for sensitive data",
                "always validate input before database queries",
                "implement rate limiting to prevent abuse",
                "use HTTPS in production environments",
                "cache frequently accessed data in Redis",
                "implement proper error handling in async functions"
            ],
            
            'solution_info': [
                "increase timeout to 30 seconds for slow connections",
                "use connection pooling for database efficiency",
                "implement circuit breaker pattern for resilience",
                "add retry logic with exponential backoff",
                "use CDN for static asset delivery",
                "implement database indexing for query optimization",
                "use message queues for async processing",
                "implement health checks for monitoring"
            ],
            
            'config_info': [
                "server { listen 80; location / { proxy_pass http://backend; }}",
                "DATABASE_URL=postgresql://user:pass@localhost:5432/db",
                "redis: { host: localhost, port: 6379, password: secret }",
                "cors: { origin: true, credentials: true }",
                "jwt: { secret: env.JWT_SECRET, expiresIn: '24h' }",
                "logging: { level: 'info', format: 'json' }",
                "docker: { image: node:18, ports: ['3000:3000'] }",
                "kubernetes: { replicas: 3, resources: { memory: '512Mi' }}"
            ],
            
            'problem': [
                "memory leak in the application",
                "slow database queries",
                "CORS errors in browser",
                "authentication token expiration",
                "file upload timeout issues",
                "cache invalidation problems",
                "API rate limiting errors",
                "container deployment failures"
            ],
            
            'solution': [
                "implementing proper cleanup in useEffect",
                "adding database indexes on frequently queried columns",
                "configuring proper CORS headers on server",
                "implementing refresh token mechanism",
                "increasing file upload timeout limits",
                "using cache-aside pattern with TTL",
                "implementing exponential backoff retry",
                "fixing container health check configuration"
            ],
            
            'technology': [
                "Docker", "Kubernetes", "React", "Node.js", "PostgreSQL",
                "Redis", "MongoDB", "nginx", "Apache", "AWS",
                "TypeScript", "Python", "Java", "Go", "Rust"
            ],
            
            'error_type': [
                "connection timeout", "memory leak", "null pointer exception",
                "CORS error", "authentication failure", "database deadlock",
                "file not found", "permission denied", "rate limit exceeded"
            ],
            
            'question_about_topic': [
                "optimize React performance",
                "handle database transactions",
                "implement user authentication",
                "deploy to production",
                "debug memory issues",
                "configure load balancing",
                "implement caching strategy",
                "handle API errors"
            ]
        }
    
    def generate_examples(self, num_samples: int, language: str = 'en') -> List[Dict[str, Any]]:
        """Generate synthetic training examples"""
        
        examples = []
        
        # Calculate samples per class
        save_samples = int(num_samples * self.config.save_memory_ratio)
        search_samples = int(num_samples * self.config.search_memory_ratio)
        no_action_samples = num_samples - save_samples - search_samples
        
        class_samples = {
            'SAVE_MEMORY': save_samples,
            'SEARCH_MEMORY': search_samples,
            'NO_ACTION': no_action_samples
        }
        
        for class_name, sample_count in class_samples.items():
            for _ in range(sample_count):
                example = self._generate_single_example(class_name, language)
                examples.append(example)
        
        # Shuffle examples
        random.shuffle(examples)
        
        logger.info(f"Generated {len(examples)} synthetic examples in {language}")
        return examples
    
    def _generate_single_example(self, class_name: str, language: str) -> Dict[str, Any]:
        """Generate a single training example"""
        
        template = random.choice(self.templates[class_name][language])
        
        # Fill template with vocabulary
        filled_text = self._fill_template(template)
        
        # Add variations
        varied_text = self._add_variations(filled_text, class_name)
        
        return {
            'text': varied_text,
            'label': self.label_mapping[class_name],
            'label_name': class_name,
            'language': language,
            'source': 'synthetic',
            'template': template
        }
    
    def _fill_template(self, template: str) -> str:
        """Fill template with random vocabulary"""
        
        # Find all placeholders in template
        import re
        placeholders = re.findall(r'\{(\w+)\}', template)
        
        filled_template = template
        for placeholder in placeholders:
            if placeholder in self.vocabularies:
                replacement = random.choice(self.vocabularies[placeholder])
                filled_template = filled_template.replace(f'{{{placeholder}}}', replacement)
        
        return filled_template
    
    def _add_variations(self, text: str, class_name: str) -> str:
        """Add variations to make text more natural"""
        
        variations = []
        
        # Add emphasis for important content
        if class_name == 'SAVE_MEMORY' and random.random() < 0.3:
            variations.extend([
                lambda t: t.upper() if len(t) < 50 else t,
                lambda t: f"⚠️ {t}",
                lambda t: f"IMPORTANT: {t}",
                lambda t: f"{t}!"
            ])
        
        # Add uncertainty for questions
        elif class_name == 'SEARCH_MEMORY' and random.random() < 0.2:
            variations.extend([
                lambda t: f"I think {t.lower()}",
                lambda t: f"Maybe {t.lower()}",
                lambda t: f"Probably {t.lower()}"
            ])
        
        # Add context for casual conversation
        elif class_name == 'NO_ACTION' and random.random() < 0.2:
            variations.extend([
                lambda t: f"Btw, {t.lower()}",
                lambda t: f"Just saying, {t.lower()}",
                lambda t: f"By the way, {t.lower()}"
            ])
        
        # Apply random variation
        if variations and random.random() < 0.4:
            variation = random.choice(variations)
            text = variation(text)
        
        return text


class ExistingDatasetAdapter:
    """Adapter for existing intent classification datasets"""
    
    def __init__(self):
        self.intent_mappings = {
            # Map existing intents to our classes
            'save_intents': [
                'add_to_playlist', 'create_reminder', 'save_contact',
                'store_information', 'bookmark', 'create_note',
                'schedule_meeting', 'set_alarm', 'create_todo'
            ],
            'search_intents': [
                'search_music', 'find_restaurant', 'get_weather',
                'query_information', 'find_contact', 'search_email',
                'lookup_definition', 'find_movie', 'search_news'
            ],
            'no_action_intents': [
                'greetings', 'goodbye', 'small_talk', 'thank_you',
                'affirmation', 'negation', 'unknown', 'out_of_scope'
            ]
        }
    
    def adapt_snips_dataset(self) -> List[Dict[str, Any]]:
        """Adapt SNIPS dataset for our use case"""
        
        if not HAS_DATASETS:
            logger.warning("datasets library not available, skipping SNIPS adaptation")
            return []
        
        try:
            # Load SNIPS dataset
            dataset = load_dataset("snips_built_in_intents")
            
            adapted_examples = []
            
            for split in ['train', 'validation']:
                if split in dataset:
                    for example in dataset[split]:
                        adapted_example = self._adapt_snips_example(example)
                        if adapted_example:
                            adapted_examples.append(adapted_example)
            
            logger.info(f"Adapted {len(adapted_examples)} examples from SNIPS dataset")
            return adapted_examples
            
        except Exception as e:
            logger.error(f"Failed to load SNIPS dataset: {e}")
            return []
    
    def _adapt_snips_example(self, example: Dict) -> Optional[Dict[str, Any]]:
        """Adapt single SNIPS example"""
        
        intent = example.get('intent', '').lower()
        text = example.get('text', '')
        
        if not text:
            return None
        
        # Map intent to our classes
        if any(save_intent in intent for save_intent in self.intent_mappings['save_intents']):
            label_name = 'SAVE_MEMORY'
        elif any(search_intent in intent for search_intent in self.intent_mappings['search_intents']):
            label_name = 'SEARCH_MEMORY'
        else:
            label_name = 'NO_ACTION'
        
        return {
            'text': text,
            'label': {'SAVE_MEMORY': 0, 'SEARCH_MEMORY': 1, 'NO_ACTION': 2}[label_name],
            'label_name': label_name,
            'language': 'en',
            'source': 'snips',
            'original_intent': intent
        }
    
    def adapt_banking77_dataset(self) -> List[Dict[str, Any]]:
        """Adapt BANKING77 dataset for our use case"""
        
        if not HAS_DATASETS:
            logger.warning("datasets library not available, skipping BANKING77 adaptation")
            return []
        
        try:
            # Load BANKING77 dataset
            dataset = load_dataset("banking77")
            
            adapted_examples = []
            
            # Banking intent to our class mapping
            banking_mappings = {
                'SAVE_MEMORY': [
                    'activate_my_card', 'age_limit', 'apple_pay_or_google_pay',
                    'atm_support', 'automatic_top_up', 'balance_not_updated_after_bank_transfer'
                ],
                'SEARCH_MEMORY': [
                    'balance_not_updated_after_cheque_or_cash_deposit', 'beneficiary_not_allowed',
                    'cancel_transfer', 'card_about_to_expire', 'card_acceptance'
                ],
                'NO_ACTION': [
                    'thank_you', 'goodbye', 'hello'  # These are rare in banking77
                ]
            }
            
            for split in ['train', 'test']:
                if split in dataset:
                    for example in dataset[split]:
                        adapted_example = self._adapt_banking_example(example, banking_mappings)
                        if adapted_example:
                            adapted_examples.append(adapted_example)
            
            logger.info(f"Adapted {len(adapted_examples)} examples from BANKING77 dataset")
            return adapted_examples[:1000]  # Limit to 1000 examples
            
        except Exception as e:
            logger.error(f"Failed to load BANKING77 dataset: {e}")
            return []
    
    def _adapt_banking_example(self, example: Dict, mappings: Dict) -> Optional[Dict[str, Any]]:
        """Adapt single BANKING77 example"""
        
        text = example.get('text', '')
        label_idx = example.get('label', -1)
        
        if not text or label_idx == -1:
            return None
        
        # For simplicity, map based on text patterns
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['how', 'what', 'where', 'when', 'why']):
            label_name = 'SEARCH_MEMORY'
        elif any(word in text_lower for word in ['setup', 'activate', 'enable', 'configure']):
            label_name = 'SAVE_MEMORY'
        else:
            # Most banking queries are searches
            label_name = 'SEARCH_MEMORY'
        
        return {
            'text': text,
            'label': {'SAVE_MEMORY': 0, 'SEARCH_MEMORY': 1, 'NO_ACTION': 2}[label_name],
            'label_name': label_name,
            'language': 'en',
            'source': 'banking77',
            'original_label': label_idx
        }


class AutoTriggerDatasetBuilder:
    """Main dataset builder that combines all sources"""
    
    def __init__(self, config: DatasetConfig = None):
        self.config = config or DatasetConfig()
        self.synthetic_generator = SyntheticDataGenerator(self.config)
        self.existing_adapter = ExistingDatasetAdapter()
    
    def build_comprehensive_dataset(self):
        """Build comprehensive training dataset from all sources"""
        
        logger.info("Building comprehensive auto-trigger dataset...")
        
        all_examples = []
        
        # 1. Generate synthetic data (60%)
        synthetic_samples = int(self.config.total_samples * self.config.synthetic_ratio)
        
        # Split by language
        en_samples = int(synthetic_samples * self.config.english_ratio)
        it_samples = synthetic_samples - en_samples
        
        logger.info(f"Generating {en_samples} English synthetic examples...")
        all_examples.extend(self.synthetic_generator.generate_examples(en_samples, 'en'))
        
        logger.info(f"Generating {it_samples} Italian synthetic examples...")
        all_examples.extend(self.synthetic_generator.generate_examples(it_samples, 'it'))
        
        # 2. Adapt existing datasets (30%)
        logger.info("Adapting existing datasets...")
        
        snips_examples = self.existing_adapter.adapt_snips_dataset()
        banking_examples = self.existing_adapter.adapt_banking77_dataset()
        
        existing_examples = snips_examples + banking_examples
        
        # Limit to desired ratio
        max_existing = int(self.config.total_samples * self.config.adapted_existing_ratio)
        if len(existing_examples) > max_existing:
            existing_examples = random.sample(existing_examples, max_existing)
        
        all_examples.extend(existing_examples)
        
        # 3. Placeholder for real user data (10%)
        # In production, this would load real user interaction data
        logger.info("Placeholder for real user data (not implemented)")
        
        # Create DataFrame
        df = pd.DataFrame(all_examples)
        
        # Balance classes if needed
        df = self._balance_classes(df)
        
        # Split into train/val/test
        dataset_dict = self._create_dataset_splits(df)
        
        logger.info(f"Dataset built successfully:")
        logger.info(f"  Total examples: {len(df)}")
        logger.info(f"  Train: {len(dataset_dict['train'])}")
        logger.info(f"  Validation: {len(dataset_dict['validation'])}")
        logger.info(f"  Test: {len(dataset_dict['test'])}")
        
        # Class distribution
        class_dist = df['label_name'].value_counts()
        logger.info(f"  Class distribution: {class_dist.to_dict()}")
        
        return dataset_dict
    
    def _balance_classes(self, df: pd.DataFrame) -> pd.DataFrame:
        """Balance classes to desired ratios"""
        
        target_counts = {
            'SAVE_MEMORY': int(len(df) * self.config.save_memory_ratio),
            'SEARCH_MEMORY': int(len(df) * self.config.search_memory_ratio),
            'NO_ACTION': int(len(df) * self.config.no_action_ratio)
        }
        
        balanced_dfs = []
        
        for class_name, target_count in target_counts.items():
            class_df = df[df['label_name'] == class_name]
            
            if len(class_df) > target_count:
                # Downsample
                class_df = class_df.sample(n=target_count, random_state=42)
            elif len(class_df) < target_count:
                # Upsample by repeating examples
                factor = target_count // len(class_df)
                remainder = target_count % len(class_df)
                
                upsampled = pd.concat([class_df] * factor)
                if remainder > 0:
                    upsampled = pd.concat([upsampled, class_df.sample(n=remainder, random_state=42)])
                
                class_df = upsampled
            
            balanced_dfs.append(class_df)
        
        balanced_df = pd.concat(balanced_dfs).sample(frac=1, random_state=42).reset_index(drop=True)
        
        logger.info("Classes balanced to target ratios")
        return balanced_df
    
    def _create_dataset_splits(self, df: pd.DataFrame):
        """Create train/validation/test splits"""
        
        # First split: train vs (val + test)
        train_df, temp_df = train_test_split(
            df, 
            test_size=(self.config.val_split + self.config.test_split),
            stratify=df['label'],
            random_state=42
        )
        
        # Second split: val vs test
        val_size = self.config.val_split / (self.config.val_split + self.config.test_split)
        val_df, test_df = train_test_split(
            temp_df,
            test_size=(1 - val_size),
            stratify=temp_df['label'],
            random_state=42
        )
        
        # Convert to HuggingFace datasets if available
        if HAS_DATASETS:
            dataset_dict = DatasetDict({
                'train': Dataset.from_pandas(train_df),
                'validation': Dataset.from_pandas(val_df),
                'test': Dataset.from_pandas(test_df)
            })
        else:
            # Fallback to dict format
            dataset_dict = {
                'train': train_df.to_dict('records'),
                'validation': val_df.to_dict('records'),
                'test': test_df.to_dict('records')
            }
        
        return dataset_dict
    
    def save_dataset(self, dataset, output_dir: Path):
        """Save dataset to disk"""
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if HAS_DATASETS and isinstance(dataset, DatasetDict):
            # Save as HuggingFace dataset
            dataset.save_to_disk(str(output_dir))
            logger.info(f"Dataset saved to {output_dir}")
        else:
            # Save as JSON files
            for split_name, split_data in dataset.items():
                split_file = output_dir / f"{split_name}.json"
                with open(split_file, 'w', encoding='utf-8') as f:
                    json.dump(split_data, f, indent=2, ensure_ascii=False)
                logger.info(f"Split '{split_name}' saved to {split_file}")
        
        # Save dataset statistics
        stats_file = output_dir / "dataset_stats.json"
        stats = self._calculate_dataset_stats(dataset)
        with open(stats_file, 'w') as f:
            json.dump(stats, f, indent=2)
        
        logger.info(f"Dataset statistics saved to {stats_file}")
    
    def _calculate_dataset_stats(self, dataset) -> Dict[str, Any]:
        """Calculate and return dataset statistics"""
        
        stats = {
            'creation_time': datetime.now().isoformat(),
            'config': {
                'total_samples': self.config.total_samples,
                'train_split': self.config.train_split,
                'val_split': self.config.val_split,
                'test_split': self.config.test_split
            },
            'splits': {}
        }
        
        for split_name, split_data in dataset.items():
            if HAS_DATASETS and hasattr(split_data, '__len__'):
                split_size = len(split_data)
                if hasattr(split_data, 'to_pandas'):
                    split_df = split_data.to_pandas()
                    class_dist = split_df['label_name'].value_counts().to_dict()
                    lang_dist = split_df['language'].value_counts().to_dict()
                    source_dist = split_df['source'].value_counts().to_dict()
                else:
                    class_dist = {}
                    lang_dist = {}
                    source_dist = {}
            else:
                split_size = len(split_data)
                class_dist = {}
                lang_dist = {}
                source_dist = {}
            
            stats['splits'][split_name] = {
                'size': split_size,
                'class_distribution': class_dist,
                'language_distribution': lang_dist,
                'source_distribution': source_dist
            }
        
        return stats


def build_auto_trigger_dataset(
    total_samples: int = 10000,
    output_dir: str = "./data/auto_trigger_dataset",
    config: DatasetConfig = None
):
    """Convenience function to build auto-trigger dataset"""
    
    if config is None:
        config = DatasetConfig(total_samples=total_samples)
    
    builder = AutoTriggerDatasetBuilder(config)
    dataset = builder.build_comprehensive_dataset()
    
    output_path = Path(output_dir)
    builder.save_dataset(dataset, output_path)
    
    return dataset


if __name__ == "__main__":
    # Example usage
    logger.info("Building auto-trigger dataset...")
    
    dataset = build_auto_trigger_dataset(
        total_samples=5000,  # Smaller for testing
        output_dir="./data/test_dataset"
    )
    
    logger.info("Dataset building completed!")
