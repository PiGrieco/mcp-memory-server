#!/usr/bin/env python3
"""
Build Realistic Dataset with Actually Available Sources
Focus on proven working datasets + heavy synthetic generation
"""

import os
import sys
import asyncio
import argparse
from pathlib import Path
import pandas as pd
import random
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from datasets import Dataset, DatasetDict, load_dataset, concatenate_datasets
    from sklearn.model_selection import train_test_split
    from huggingface_hub import upload_file, create_repo, login
    HAS_DATASETS = True
except ImportError:
    HAS_DATASETS = False

from src.utils.logging import get_logger

logger = get_logger(__name__)


class RealisticDatasetBuilder:
    """Build dataset with actually working sources"""
    
    def __init__(self, hf_token: str = None):
        self.hf_token = hf_token
        self.label_mapping = {
            'SAVE_MEMORY': 0,
            'SEARCH_MEMORY': 1,
            'NO_ACTION': 2
        }
    
    def build_comprehensive_dataset(self, target_size: int = 100000) -> DatasetDict:
        """Build dataset from working sources + synthetic"""
        
        logger.info(f"Building realistic dataset with target size: {target_size:,}")
        
        all_examples = []
        
        # 1. Load confirmed working datasets
        logger.info("Loading confirmed working datasets...")
        
        # BANKING77 (13K examples)
        banking_examples = self.load_banking77(4000)
        all_examples.extend(banking_examples)
        logger.info(f"✅ BANKING77: {len(banking_examples)} examples")
        
        # CLINC150 (19K examples) 
        clinc_examples = self.load_clinc150(15000)
        all_examples.extend(clinc_examples)
        logger.info(f"✅ CLINC150: {len(clinc_examples)} examples")
        
        # SNIPS (328 examples - small but useful)
        snips_examples = self.load_snips(328)
        all_examples.extend(snips_examples)
        logger.info(f"✅ SNIPS: {len(snips_examples)} examples")
        
        # Try MASSIVE (if it works with different approach)
        massive_examples = self.try_load_massive(10000)
        if massive_examples:
            all_examples.extend(massive_examples)
            logger.info(f"✅ MASSIVE: {len(massive_examples)} examples")
        else:
            logger.warning("❌ MASSIVE: Not accessible, skipping")
        
        # 2. Generate synthetic data to reach target
        current_size = len(all_examples)
        synthetic_needed = max(0, target_size - current_size)
        
        if synthetic_needed > 0:
            logger.info(f"Generating {synthetic_needed} synthetic examples...")
            synthetic_examples = self.generate_synthetic_data(synthetic_needed)
            all_examples.extend(synthetic_examples)
            logger.info(f"✅ Synthetic: {len(synthetic_examples)} examples")
        
        logger.info(f"Total examples collected: {len(all_examples):,}")
        
        # 3. Process and create dataset
        dataset_dict = self.create_dataset_splits(all_examples)
        
        return dataset_dict
    
    def load_banking77(self, target_samples: int) -> list:
        """Load BANKING77 dataset"""
        examples = []
        
        try:
            dataset = load_dataset("banking77", use_auth_token=self.hf_token)
            
            for split in ['train', 'test']:
                if split in dataset:
                    for item in dataset[split]:
                        text = item.get('text', '')
                        
                        if text:
                            # Banking queries are mostly searches
                            if '?' in text or any(word in text.lower() for word in ['how', 'what', 'where', 'when']):
                                action = 'SEARCH_MEMORY'
                            elif any(word in text.lower() for word in ['activate', 'create', 'setup', 'enable']):
                                action = 'SAVE_MEMORY'
                            else:
                                action = 'SEARCH_MEMORY'  # Default for banking
                            
                            examples.append({
                                'text': text,
                                'label': self.label_mapping[action],
                                'label_name': action,
                                'language': 'en',
                                'source': 'banking77'
                            })
                            
                            if len(examples) >= target_samples:
                                break
                
                if len(examples) >= target_samples:
                    break
                    
        except Exception as e:
            logger.error(f"Failed to load BANKING77: {e}")
        
        return examples[:target_samples]
    
    def load_clinc150(self, target_samples: int) -> list:
        """Load CLINC150 dataset"""
        examples = []
        
        try:
            dataset = load_dataset("clinc_oos", "imbalanced", use_auth_token=self.hf_token)
            
            # Intent mapping for CLINC150
            save_intents = [
                'create_list', 'reminder', 'calendar_set', 'todo_list',
                'contact_manager', 'schedule', 'appointment_set',
                'alarm_set', 'timer_set', 'order_checks'
            ]
            
            search_intents = [
                'weather', 'translate', 'find_phone', 'restaurant_reviews',
                'flight_status', 'gas_type', 'insurance_change',
                'account_blocked', 'balance', 'bill_balance'
            ]
            
            for split in ['train', 'validation', 'test']:
                if split in dataset:
                    for item in dataset[split]:
                        text = item.get('text', '')
                        intent = item.get('intent', '')
                        
                        if text and intent != 'oos':  # Skip out-of-scope
                            # Map intent to action
                            if isinstance(intent, str):
                                if intent in save_intents:
                                    action = 'SAVE_MEMORY'
                                elif intent in search_intents:
                                    action = 'SEARCH_MEMORY'
                                elif any(word in intent for word in ['create', 'add', 'set', 'make']):
                                    action = 'SAVE_MEMORY'
                                elif any(word in intent for word in ['find', 'search', 'get', 'query', 'check']):
                                    action = 'SEARCH_MEMORY'
                                else:
                                    action = 'NO_ACTION'
                            else:
                                action = 'NO_ACTION'
                            
                            examples.append({
                                'text': text,
                                'label': self.label_mapping[action],
                                'label_name': action,
                                'language': 'en',
                                'source': 'clinc150',
                                'original_intent': intent
                            })
                            
                            if len(examples) >= target_samples:
                                break
                
                if len(examples) >= target_samples:
                    break
                    
        except Exception as e:
            logger.error(f"Failed to load CLINC150: {e}")
        
        return examples[:target_samples]
    
    def load_snips(self, target_samples: int) -> list:
        """Load SNIPS dataset"""
        examples = []
        
        try:
            dataset = load_dataset("snips_built_in_intents", use_auth_token=self.hf_token)
            
            intent_mapping = {
                'AddToPlaylist': 'SAVE_MEMORY',
                'BookRestaurant': 'SAVE_MEMORY',
                'GetWeather': 'SEARCH_MEMORY',
                'PlayMusic': 'SEARCH_MEMORY',
                'RateBook': 'SAVE_MEMORY',
                'SearchCreativeWork': 'SEARCH_MEMORY',
                'SearchScreeningEvent': 'SEARCH_MEMORY'
            }
            
            for split in ['train']:  # Only train split available
                if split in dataset:
                    for item in dataset[split]:
                        text = item.get('text', '')
                        intent = item.get('intent', '')
                        
                        if text and intent:
                            action = intent_mapping.get(intent, 'NO_ACTION')
                            
                            examples.append({
                                'text': text,
                                'label': self.label_mapping[action],
                                'label_name': action,
                                'language': 'en',
                                'source': 'snips',
                                'original_intent': intent
                            })
                            
                            if len(examples) >= target_samples:
                                break
                    
        except Exception as e:
            logger.error(f"Failed to load SNIPS: {e}")
        
        return examples[:target_samples]
    
    def try_load_massive(self, target_samples: int) -> list:
        """Try to load MASSIVE dataset with different approaches"""
        examples = []
        
        # Try different approaches for MASSIVE
        approaches = [
            lambda: load_dataset("AmazonScience/massive", use_auth_token=self.hf_token),
            lambda: load_dataset("AmazonScience/massive", "en", use_auth_token=self.hf_token),
            lambda: load_dataset("AmazonScience/massive", streaming=True, use_auth_token=self.hf_token)
        ]
        
        for i, approach in enumerate(approaches):
            try:
                logger.info(f"Trying MASSIVE approach {i+1}...")
                dataset = approach()
                
                # Focus on English and Italian
                target_languages = ['en-US', 'it-IT']
                collected = 0
                
                for split in ['train', 'dev', 'test']:
                    if split in dataset:
                        for item in dataset[split]:
                            locale = item.get('locale', '')
                            text = item.get('utt', '')
                            intent = item.get('intent', '')
                            
                            if any(locale.startswith(lang[:2]) for lang in target_languages) and text:
                                # Map MASSIVE intents to our actions
                                if any(word in intent for word in ['create', 'add', 'set', 'reminder']):
                                    action = 'SAVE_MEMORY'
                                elif any(word in intent for word in ['query', 'search', 'find', 'get']):
                                    action = 'SEARCH_MEMORY'
                                else:
                                    action = 'NO_ACTION'
                                
                                language = 'it' if locale.startswith('it') else 'en'
                                
                                examples.append({
                                    'text': text,
                                    'label': self.label_mapping[action],
                                    'label_name': action,
                                    'language': language,
                                    'source': 'massive',
                                    'original_intent': intent
                                })
                                
                                collected += 1
                                if collected >= target_samples:
                                    break
                        
                        if collected >= target_samples:
                            break
                
                logger.info(f"✅ MASSIVE loaded successfully with approach {i+1}")
                break
                
            except Exception as e:
                logger.warning(f"MASSIVE approach {i+1} failed: {e}")
                continue
        
        return examples[:target_samples]
    
    def generate_synthetic_data(self, target_samples: int) -> list:
        """Generate high-quality synthetic data"""
        
        # Enhanced synthetic templates
        templates = {
            'SAVE_MEMORY': [
                # English templates
                "Remember that {technical_info}",
                "Important: {solution_info}", 
                "Save this configuration: {config_info}",
                "Note for later: {important_note}",
                "I solved {problem} with {solution}",
                "Fixed {issue} by {fix_method}",
                "Configuration: {system_config}",
                "Documentation: {doc_info}",
                "Backup this setting: {setting_info}",
                "Store credentials for {service_name}",
                "Archive this solution: {solution_detail}",
                
                # Italian templates
                "Ricorda che {technical_info}",
                "Importante: {solution_info}",
                "Salva questa configurazione: {config_info}",
                "Nota per dopo: {important_note}",
                "Ho risolto {problem} con {solution}",
                "Risolto {issue} usando {fix_method}",
                "Configurazione: {system_config}",
                "Documentazione: {doc_info}",
                "Backup di questa impostazione: {setting_info}",
                "Salva credenziali per {service_name}",
                "Archivia questa soluzione: {solution_detail}"
            ],
            
            'SEARCH_MEMORY': [
                # English templates
                "How can I {technical_question}?",
                "What's the best way to {task_description}?",
                "Where did I save {information_type}?",
                "Help with {technical_issue}",
                "Looking for {search_target}",
                "I need to find {information_need}",
                "Show me how to {action_description}",
                "What was the fix for {past_issue}?",
                "How do I handle {situation_type}?",
                "Find documentation for {feature_name}",
                "Search for {code_pattern}",
                
                # Italian templates  
                "Come posso {technical_question}?",
                "Qual è il modo migliore per {task_description}?",
                "Dove ho salvato {information_type}?",
                "Aiuto con {technical_issue}",
                "Cerco {search_target}",
                "Devo trovare {information_need}",
                "Mostrami come {action_description}",
                "Qual era il fix per {past_issue}?",
                "Come gestisco {situation_type}?",
                "Trova documentazione per {feature_name}",
                "Cerca {code_pattern}"
            ],
            
            'NO_ACTION': [
                # English templates
                "Hello, how are you?", "Thanks for the help", "OK, perfect",
                "I understand", "Good morning", "Have a nice day",
                "Yes, exactly", "No, that's fine", "Maybe later",
                "Sounds good", "Great job!", "Alright", "Sure thing",
                "Got it", "Makes sense", "No problem",
                
                # Italian templates
                "Ciao, come stai?", "Grazie per l'aiuto", "OK, perfetto",
                "Ho capito", "Buongiorno", "Buona giornata",
                "Sì, esatto", "No, va bene", "Magari dopo",
                "Suona bene", "Ottimo lavoro!", "D'accordo", "Certo",
                "Capito", "Ha senso", "Nessun problema"
            ]
        }
        
        # Enhanced vocabularies
        vocabularies = {
            'technical_info': [
                'CORS requires Access-Control-Allow-Origin header',
                'JWT tokens should expire in 24 hours',
                'use environment variables for sensitive data',
                'always validate input before database queries',
                'implement rate limiting to prevent abuse',
                'use HTTPS in production environments',
                'cache frequently accessed data in Redis',
                'implement proper error handling in async functions',
                'use connection pooling for database efficiency',
                'implement circuit breaker pattern for resilience'
            ],
            'solution_info': [
                'increase timeout to 30 seconds for slow connections',
                'use connection pooling for database efficiency',
                'implement circuit breaker pattern for resilience',
                'add retry logic with exponential backoff',
                'use CDN for static asset delivery',
                'implement database indexing for query optimization',
                'use message queues for async processing',
                'implement health checks for monitoring'
            ],
            'problem': [
                'memory leak in the application',
                'slow database queries',
                'CORS errors in browser',
                'authentication token expiration',
                'file upload timeout issues',
                'cache invalidation problems',
                'API rate limiting errors',
                'container deployment failures'
            ],
            'solution': [
                'implementing proper cleanup in useEffect',
                'adding database indexes on frequently queried columns',
                'configuring proper CORS headers on server',
                'implementing refresh token mechanism',
                'increasing file upload timeout limits',
                'using cache-aside pattern with TTL',
                'implementing exponential backoff retry',
                'fixing container health check configuration'
            ],
            'technical_question': [
                'optimize React performance',
                'handle database transactions',
                'implement user authentication',
                'deploy to production',
                'debug memory issues',
                'configure load balancing',
                'implement caching strategy',
                'handle API errors'
            ]
        }
        
        examples = []
        
        # Distribution: 40% SAVE, 35% SEARCH, 25% NO_ACTION
        save_count = int(target_samples * 0.4)
        search_count = int(target_samples * 0.35)
        no_action_count = target_samples - save_count - search_count
        
        counts = {
            'SAVE_MEMORY': save_count,
            'SEARCH_MEMORY': search_count,
            'NO_ACTION': no_action_count
        }
        
        for action, count in counts.items():
            for _ in range(count):
                template = random.choice(templates[action])
                
                # Fill template with vocabularies
                text = template
                for placeholder, options in vocabularies.items():
                    if f'{{{placeholder}}}' in text:
                        text = text.replace(f'{{{placeholder}}}', random.choice(options))
                
                # Determine language
                language = 'it' if any(italian_word in text for italian_word in ['Ricorda', 'Importante', 'Salva', 'Ciao', 'Come']) else 'en'
                
                examples.append({
                    'text': text,
                    'label': self.label_mapping[action],
                    'label_name': action,
                    'language': language,
                    'source': 'synthetic'
                })
        
        return examples
    
    def create_dataset_splits(self, all_examples: list) -> DatasetDict:
        """Create train/validation/test splits"""
        
        # Convert to DataFrame
        df = pd.DataFrame(all_examples)
        
        # Remove duplicates
        initial_size = len(df)
        df = df.drop_duplicates(subset=['text'])
        logger.info(f"Removed {initial_size - len(df)} duplicate examples")
        
        # Balance classes
        df = self.balance_classes(df)
        
        # Create splits
        train_df, temp_df = train_test_split(df, test_size=0.2, stratify=df['label'], random_state=42)
        val_df, test_df = train_test_split(temp_df, test_size=0.5, stratify=temp_df['label'], random_state=42)
        
        # Convert to HuggingFace format
        dataset_dict = DatasetDict({
            'train': Dataset.from_pandas(train_df),
            'validation': Dataset.from_pandas(val_df),
            'test': Dataset.from_pandas(test_df)
        })
        
        logger.info(f"Final dataset created:")
        logger.info(f"  Train: {len(train_df):,} examples")
        logger.info(f"  Validation: {len(val_df):,} examples")
        logger.info(f"  Test: {len(test_df):,} examples")
        logger.info(f"  Total: {len(df):,} examples")
        
        # Show class distribution
        class_dist = df['label_name'].value_counts()
        logger.info(f"  Class distribution: {class_dist.to_dict()}")
        
        return dataset_dict
    
    def balance_classes(self, df: pd.DataFrame) -> pd.DataFrame:
        """Balance classes to desired distribution"""
        
        target_distribution = {
            'SAVE_MEMORY': 0.4,
            'SEARCH_MEMORY': 0.35,
            'NO_ACTION': 0.25
        }
        
        total_size = len(df)
        balanced_dfs = []
        
        for class_name, ratio in target_distribution.items():
            target_count = int(total_size * ratio)
            class_df = df[df['label_name'] == class_name]
            
            if len(class_df) > target_count:
                # Downsample
                class_df = class_df.sample(n=target_count, random_state=42)
            elif len(class_df) < target_count:
                # Upsample with repetition
                factor = target_count // len(class_df) if len(class_df) > 0 else 1
                remainder = target_count % len(class_df) if len(class_df) > 0 else 0
                
                if len(class_df) > 0:
                    upsampled = pd.concat([class_df] * factor)
                    if remainder > 0:
                        upsampled = pd.concat([upsampled, class_df.sample(n=remainder, random_state=42)])
                    class_df = upsampled
            
            balanced_dfs.append(class_df)
        
        balanced_df = pd.concat(balanced_dfs).sample(frac=1, random_state=42).reset_index(drop=True)
        
        logger.info("Classes balanced to target distribution")
        return balanced_df
    
    async def upload_to_huggingface(self, dataset: DatasetDict, repo_name: str) -> str:
        """Upload dataset to Hugging Face Hub"""
        
        if not self.hf_token:
            raise ValueError("HF token required for upload")
        
        try:
            # Login to HuggingFace
            login(token=self.hf_token)
            
            # Create repository
            repo_id = f"pigrieco/{repo_name}"
            
            try:
                create_repo(repo_id, repo_type="dataset", private=False)
                logger.info(f"Created new repository: {repo_id}")
            except Exception as e:
                logger.info(f"Repository {repo_id} might already exist: {e}")
            
            # Push dataset to hub
            dataset.push_to_hub(repo_id)
            
            logger.info(f"✅ Dataset uploaded to: https://huggingface.co/datasets/{repo_id}")
            return repo_id
            
        except Exception as e:
            logger.error(f"Failed to upload dataset: {e}")
            raise


async def main():
    """Main execution function"""
    
    parser = argparse.ArgumentParser(description="Build realistic dataset with working sources")
    parser.add_argument("--hf-token", type=str, help="Hugging Face token")
    parser.add_argument("--target-size", type=int, default=100000, help="Target dataset size")
    parser.add_argument("--repo-name", type=str, default="mcp-memory-auto-trigger-100k", help="HF repo name")
    parser.add_argument("--upload", action="store_true", help="Upload to Hugging Face")
    
    args = parser.parse_args()
    
    print("🚀 **REALISTIC DATASET BUILDER**")
    print("=" * 50)
    print(f"Target size: {args.target_size:,}")
    print(f"Upload to HF: {args.upload}")
    
    try:
        # Build dataset
        builder = RealisticDatasetBuilder(args.hf_token)
        dataset = builder.build_comprehensive_dataset(args.target_size)
        
        # Upload if requested
        if args.upload and args.hf_token:
            repo_id = await builder.upload_to_huggingface(dataset, args.repo_name)
            print(f"\n🎉 Dataset ready: https://huggingface.co/datasets/{repo_id}")
        else:
            print(f"\n✅ Dataset built successfully!")
            print(f"Use --upload --hf-token to upload to Hugging Face")
        
        return dataset
        
    except Exception as e:
        logger.error(f"Dataset building failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
