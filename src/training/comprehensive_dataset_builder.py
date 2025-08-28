#!/usr/bin/env python3
"""
Comprehensive Dataset Builder
Builds 100K+ training examples from multiple sources
"""

import asyncio
import pandas as pd
from typing import Dict, List, Any
from dataclasses import dataclass

# ML imports
try:
    from datasets import Dataset, DatasetDict, load_dataset, concatenate_datasets
    from sklearn.model_selection import train_test_split
    from huggingface_hub import upload_file, create_repo, login
    HAS_DATASETS = True
except ImportError:
    HAS_DATASETS = False

from .dataset_builder import SyntheticDataGenerator, DatasetConfig
from ..utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class DatasetSource:
    """Configuration for a dataset source"""
    name: str
    hf_dataset_id: str
    target_samples: int
    mapping_function: str
    priority: int
    languages: List[str] = None
    requires_approval: bool = False
    status: str = "pending"  # pending, loaded, mapped, error


class IntentMapper:
    """Advanced intent mapping for multiple datasets"""
    
    def __init__(self):
        self.label_mapping = {
            'SAVE_MEMORY': 0,
            'SEARCH_MEMORY': 1,
            'NO_ACTION': 2
        }
        
        # Comprehensive intent mappings
        self.mapping_rules = {
            'save_triggers': [
                # Core saving actions
                'add_to_playlist', 'create_reminder', 'book_restaurant',
                'transfer_money', 'make_payment', 'set_alarm',
                'create_account', 'update_profile', 'save_contact',
                'schedule_meeting', 'create_note', 'bookmark',
                
                # CLINC150 save intents
                'create_list', 'reminder', 'calendar_set', 'todo_list',
                'contact_manager', 'schedule', 'appointment_set',
                
                # MASSIVE save intents
                'takeaway_order', 'recommendation_events', 'calendar_set',
                'alarm_set', 'reminder_update', 'list_create',
                
                # Banking save actions
                'activate_my_card', 'age_limit', 'apple_pay_or_google_pay',
                'automatic_top_up', 'beneficiary_not_allowed',
                
                # Technical/Programming saves
                'commit_code', 'save_configuration', 'store_credentials',
                'backup_data', 'export_settings', 'documentation'
            ],
            
            'search_triggers': [
                # Core search actions
                'search_music', 'find_restaurant', 'get_weather',
                'balance_inquiry', 'transaction_history', 'find_flight',
                'play_music', 'search_creative_work', 'query_contact',
                
                # CLINC150 search intents
                'restaurant_reviews', 'flight_status', 'find_phone',
                'weather', 'music_query', 'news_query', 'translate',
                
                # MASSIVE search intents
                'weather_query', 'music_query', 'general_quirky',
                'qa_factoid', 'qa_stock', 'recommendation_locations',
                
                # Banking search actions
                'balance_not_updated_after_cheque_or_cash_deposit',
                'card_acceptance', 'card_arrival', 'card_linking',
                
                # Technical/Programming searches
                'search_documentation', 'find_function', 'lookup_api',
                'debug_error', 'find_tutorial', 'query_stackoverflow'
            ],
            
            'no_action_triggers': [
                # Greetings and social
                'greetings', 'goodbye', 'thank_you', 'affirmation',
                'negation', 'maybe', 'unknown', 'out_of_scope',
                'small_talk', 'personal_chat', 'casual_conversation',
                
                # Acknowledgments
                'yes', 'no', 'ok', 'alright', 'sure', 'perhaps',
                'understood', 'got_it', 'makes_sense',
                
                # Emotional/Social
                'compliment', 'joke', 'encouragement', 'sympathy',
                'excitement', 'concern', 'curiosity'
            ]
        }
        
        # Keyword-based fallback mapping
        self.keyword_mappings = {
            'save_keywords': [
                'save', 'store', 'remember', 'note', 'keep', 'record',
                'bookmark', 'archive', 'backup', 'commit', 'create',
                'ricorda', 'salva', 'memorizza', 'conserva'
            ],
            'search_keywords': [
                'find', 'search', 'look', 'get', 'show', 'display',
                'query', 'retrieve', 'fetch', 'lookup', 'check',
                'cerca', 'trova', 'mostra', 'controlla'
            ],
            'casual_keywords': [
                'hi', 'hello', 'thanks', 'bye', 'ok', 'yes', 'no',
                'ciao', 'grazie', 'ok', 'sì', 'no'
            ]
        }
    
    def map_intent_to_memory_action(self, intent: str, text: str = "") -> str:
        """Map intent to memory action with fallback"""
        
        intent_lower = intent.lower()
        text_lower = text.lower()
        
        # Direct intent mapping
        if intent_lower in self.mapping_rules['save_triggers']:
            return 'SAVE_MEMORY'
        elif intent_lower in self.mapping_rules['search_triggers']:
            return 'SEARCH_MEMORY'
        elif intent_lower in self.mapping_rules['no_action_triggers']:
            return 'NO_ACTION'
        
        # Keyword-based fallback
        if any(kw in text_lower for kw in self.keyword_mappings['save_keywords']):
            return 'SAVE_MEMORY'
        elif any(kw in text_lower for kw in self.keyword_mappings['search_keywords']):
            return 'SEARCH_MEMORY'
        elif any(kw in text_lower for kw in self.keyword_mappings['casual_keywords']):
            return 'NO_ACTION'
        
        # Default mapping based on intent patterns
        if any(word in intent_lower for word in ['find', 'search', 'get', 'query', 'check']):
            return 'SEARCH_MEMORY'
        elif any(word in intent_lower for word in ['create', 'add', 'set', 'make', 'book']):
            return 'SAVE_MEMORY'
        else:
            return 'NO_ACTION'


class ComprehensiveDatasetBuilder:
    """Builds comprehensive 100K+ dataset from multiple sources"""
    
    def __init__(self, hf_token: str = None):
        if not HAS_DATASETS:
            raise ImportError("datasets library required")
        
        self.hf_token = hf_token
        self.intent_mapper = IntentMapper()
        self.synthetic_generator = SyntheticDataGenerator(DatasetConfig())
        
        # Configure dataset sources
        self.dataset_sources = self._configure_dataset_sources()
        
        logger.info(f"Comprehensive dataset builder initialized with {len(self.dataset_sources)} sources")
    
    def _configure_dataset_sources(self) -> List[DatasetSource]:
        """Configure all dataset sources"""
        
        return [
            # Large-scale intent datasets
            DatasetSource(
                name="CLINC150",
                hf_dataset_id="clinc_oos",
                target_samples=15000,
                mapping_function="map_clinc150",
                priority=1
            ),
            DatasetSource(
                name="MASSIVE",
                hf_dataset_id="AmazonScience/massive",
                target_samples=10000,
                mapping_function="map_massive",
                priority=1,
                languages=["en", "it"],
                requires_approval=True
            ),
            DatasetSource(
                name="BANKING77",
                hf_dataset_id="banking77",
                target_samples=4000,
                mapping_function="map_banking77",
                priority=2
            ),
            DatasetSource(
                name="SNIPS",
                hf_dataset_id="snips_built_in_intents",
                target_samples=3000,
                mapping_function="map_snips",
                priority=2
            ),
            DatasetSource(
                name="TOP",
                hf_dataset_id="facebook/top_v2",
                target_samples=2000,
                mapping_function="map_top",
                priority=3
            ),
            DatasetSource(
                name="HWU64",
                hf_dataset_id="hwu_64",
                target_samples=2000,
                mapping_function="map_hwu64",
                priority=3
            ),
            DatasetSource(
                name="MultiWOZ",
                hf_dataset_id="multi_woz_v22",
                target_samples=5000,
                mapping_function="map_multiwoz",
                priority=2
            ),
            DatasetSource(
                name="PersonaChat",
                hf_dataset_id="persona_chat",
                target_samples=1000,
                mapping_function="map_persona_chat",
                priority=4
            ),
            DatasetSource(
                name="DailyDialog",
                hf_dataset_id="daily_dialog",
                target_samples=1000,
                mapping_function="map_daily_dialog",
                priority=4
            ),
            DatasetSource(
                name="Synthetic",
                hf_dataset_id="synthetic",
                target_samples=60000,
                mapping_function="generate_synthetic",
                priority=1
            )
        ]
    
    async def build_massive_dataset(self, target_size: int = 100000) -> DatasetDict:
        """Build comprehensive dataset with 100K+ examples"""
        
        logger.info(f"Building massive dataset with target size: {target_size:,}")
        
        all_examples = []
        successful_sources = []
        failed_sources = []
        
        # Process each dataset source
        for source in self.dataset_sources:
            try:
                logger.info(f"Processing {source.name}...")
                
                # Load and map dataset
                examples = await self._process_dataset_source(source)
                
                if examples:
                    all_examples.extend(examples)
                    successful_sources.append(source.name)
                    source.status = "completed"
                    logger.info(f"✅ {source.name}: {len(examples)} examples")
                else:
                    failed_sources.append(source.name)
                    source.status = "failed"
                    logger.warning(f"❌ {source.name}: No examples extracted")
                    
            except Exception as e:
                logger.error(f"❌ {source.name} failed: {e}")
                failed_sources.append(source.name)
                source.status = "error"
        
        # Summary
        logger.info("\n📊 Dataset Processing Summary:")
        logger.info(f"   Successful sources: {len(successful_sources)}")
        logger.info(f"   Failed sources: {len(failed_sources)}")
        logger.info(f"   Total examples collected: {len(all_examples):,}")
        
        if failed_sources:
            logger.warning(f"   Failed sources: {', '.join(failed_sources)}")
        
        if len(all_examples) < target_size * 0.8:
            logger.warning(f"⚠️ Only collected {len(all_examples):,} examples (target: {target_size:,})")
            logger.info("Consider increasing synthetic generation to reach target")
        
        # Process and split dataset
        dataset_dict = self._process_final_dataset(all_examples, target_size)
        
        return dataset_dict
    
    async def _process_dataset_source(self, source: DatasetSource) -> List[Dict[str, Any]]:
        """Process a single dataset source"""
        
        if source.name == "Synthetic":
            return self._generate_synthetic_examples(source.target_samples)
        
        try:
            # Load dataset from Hugging Face
            if source.requires_approval and not self.hf_token:
                logger.warning(f"Skipping {source.name} - requires HF token for approval")
                return []
            
            dataset = load_dataset(source.hf_dataset_id, use_auth_token=self.hf_token)
            
            # Get mapping function
            mapping_func = getattr(self, source.mapping_function)
            
            # Apply mapping
            examples = mapping_func(dataset, source.target_samples)
            
            return examples
            
        except Exception as e:
            logger.error(f"Failed to process {source.name}: {e}")
            return []
    
    def map_clinc150(self, dataset, target_samples: int) -> List[Dict[str, Any]]:
        """Map CLINC150 dataset"""
        
        examples = []
        
        # CLINC150 has train/validation/test splits
        for split in ['train', 'validation', 'test']:
            if split in dataset:
                for item in dataset[split]:
                    text = item.get('text', '')
                    intent = item.get('intent', '')
                    
                    if text and intent != 'oos':  # Skip out-of-scope
                        action = self.intent_mapper.map_intent_to_memory_action(intent, text)
                        
                        examples.append({
                            'text': text,
                            'label': self.intent_mapper.label_mapping[action],
                            'label_name': action,
                            'language': 'en',
                            'source': 'clinc150',
                            'original_intent': intent
                        })
                        
                        if len(examples) >= target_samples:
                            break
                
                if len(examples) >= target_samples:
                    break
        
        return examples[:target_samples]
    
    def map_massive(self, dataset, target_samples: int) -> List[Dict[str, Any]]:
        """Map MASSIVE dataset (multilingual)"""
        
        examples = []
        
        # MASSIVE has train/dev/test splits
        for split in ['train', 'dev', 'test']:
            if split in dataset:
                for item in dataset[split]:
                    text = item.get('utt', '')
                    intent = item.get('intent', '')
                    language = item.get('locale', 'en')[:2]  # Get language code
                    
                    # Focus on English and Italian
                    if language in ['en', 'it'] and text and intent:
                        action = self.intent_mapper.map_intent_to_memory_action(intent, text)
                        
                        examples.append({
                            'text': text,
                            'label': self.intent_mapper.label_mapping[action],
                            'label_name': action,
                            'language': language,
                            'source': 'massive',
                            'original_intent': intent
                        })
                        
                        if len(examples) >= target_samples:
                            break
                
                if len(examples) >= target_samples:
                    break
        
        return examples[:target_samples]
    
    def map_banking77(self, dataset, target_samples: int) -> List[Dict[str, Any]]:
        """Map BANKING77 dataset"""
        
        examples = []
        
        for split in ['train', 'test']:
            if split in dataset:
                for item in dataset[split]:
                    text = item.get('text', '')
                    label_idx = item.get('label', -1)
                    
                    if text and label_idx != -1:
                        # Map based on text patterns (banking queries)
                        action = self._map_banking_query(text)
                        
                        examples.append({
                            'text': text,
                            'label': self.intent_mapper.label_mapping[action],
                            'label_name': action,
                            'language': 'en',
                            'source': 'banking77',
                            'original_label': label_idx
                        })
                        
                        if len(examples) >= target_samples:
                            break
                
                if len(examples) >= target_samples:
                    break
        
        return examples[:target_samples]
    
    def map_snips(self, dataset, target_samples: int) -> List[Dict[str, Any]]:
        """Map SNIPS dataset"""
        
        examples = []
        
        for split in ['train', 'validation']:
            if split in dataset:
                for item in dataset[split]:
                    text = item.get('text', '')
                    intent = item.get('intent', '')
                    
                    if text and intent:
                        action = self.intent_mapper.map_intent_to_memory_action(intent, text)
                        
                        examples.append({
                            'text': text,
                            'label': self.intent_mapper.label_mapping[action],
                            'label_name': action,
                            'language': 'en',
                            'source': 'snips',
                            'original_intent': intent
                        })
                        
                        if len(examples) >= target_samples:
                            break
                
                if len(examples) >= target_samples:
                    break
        
        return examples[:target_samples]
    
    def map_top(self, dataset, target_samples: int) -> List[Dict[str, Any]]:
        """Map TOP dataset"""
        
        examples = []
        
        try:
            for split in ['train', 'eval', 'test']:
                if split in dataset:
                    for item in dataset[split]:
                        text = item.get('utterance', '')
                        intent = item.get('intent', '')
                        
                        if text and intent:
                            action = self.intent_mapper.map_intent_to_memory_action(intent, text)
                            
                            examples.append({
                                'text': text,
                                'label': self.intent_mapper.label_mapping[action],
                                'label_name': action,
                                'language': 'en',
                                'source': 'top',
                                'original_intent': intent
                            })
                            
                            if len(examples) >= target_samples:
                                break
                    
                    if len(examples) >= target_samples:
                        break
        except Exception as e:
            logger.warning(f"TOP dataset mapping partial failure: {e}")
        
        return examples[:target_samples]
    
    def map_hwu64(self, dataset, target_samples: int) -> List[Dict[str, Any]]:
        """Map HWU64 dataset"""
        
        examples = []
        
        try:
            for split in ['train', 'dev', 'test']:
                if split in dataset:
                    for item in dataset[split]:
                        text = item.get('text', '')
                        intent = item.get('intent', '')
                        
                        if text and intent:
                            action = self.intent_mapper.map_intent_to_memory_action(intent, text)
                            
                            examples.append({
                                'text': text,
                                'label': self.intent_mapper.label_mapping[action],
                                'label_name': action,
                                'language': 'en',
                                'source': 'hwu64',
                                'original_intent': intent
                            })
                            
                            if len(examples) >= target_samples:
                                break
                    
                    if len(examples) >= target_samples:
                        break
        except Exception as e:
            logger.warning(f"HWU64 dataset mapping partial failure: {e}")
        
        return examples[:target_samples]
    
    def map_multiwoz(self, dataset, target_samples: int) -> List[Dict[str, Any]]:
        """Map MultiWOZ dataset (conversational)"""
        
        examples = []
        
        try:
            for split in ['train', 'validation', 'test']:
                if split in dataset:
                    for dialog in dataset[split]:
                        turns = dialog.get('turns', [])
                        
                        for turn in turns:
                            text = turn.get('utterance', '')
                            speaker = turn.get('speaker', '')
                            
                            # Focus on user utterances
                            if speaker == 'USER' and text:
                                # Conversational context - mostly searches or casual
                                if any(word in text.lower() for word in ['find', 'search', 'what', 'where', 'how']):
                                    action = 'SEARCH_MEMORY'
                                elif any(word in text.lower() for word in ['book', 'reserve', 'create', 'make']):
                                    action = 'SAVE_MEMORY'
                                else:
                                    action = 'NO_ACTION'
                                
                                examples.append({
                                    'text': text,
                                    'label': self.intent_mapper.label_mapping[action],
                                    'label_name': action,
                                    'language': 'en',
                                    'source': 'multiwoz',
                                    'context': 'dialog'
                                })
                                
                                if len(examples) >= target_samples:
                                    break
                        
                        if len(examples) >= target_samples:
                            break
                    
                    if len(examples) >= target_samples:
                        break
        except Exception as e:
            logger.warning(f"MultiWOZ dataset mapping partial failure: {e}")
        
        return examples[:target_samples]
    
    def map_persona_chat(self, dataset, target_samples: int) -> List[Dict[str, Any]]:
        """Map PersonaChat dataset (casual conversation)"""
        
        examples = []
        
        try:
            for split in ['train', 'validation']:
                if split in dataset:
                    for item in dataset[split]:
                        history = item.get('history', [])
                        
                        for utterance in history:
                            if utterance and len(utterance.split()) > 2:  # Skip very short
                                # PersonaChat is mostly casual conversation
                                action = 'NO_ACTION'
                                
                                examples.append({
                                    'text': utterance,
                                    'label': self.intent_mapper.label_mapping[action],
                                    'label_name': action,
                                    'language': 'en',
                                    'source': 'persona_chat',
                                    'context': 'casual'
                                })
                                
                                if len(examples) >= target_samples:
                                    break
                        
                        if len(examples) >= target_samples:
                            break
                    
                    if len(examples) >= target_samples:
                        break
        except Exception as e:
            logger.warning(f"PersonaChat dataset mapping partial failure: {e}")
        
        return examples[:target_samples]
    
    def map_daily_dialog(self, dataset, target_samples: int) -> List[Dict[str, Any]]:
        """Map DailyDialog dataset"""
        
        examples = []
        
        try:
            for split in ['train', 'validation', 'test']:
                if split in dataset:
                    for item in dataset[split]:
                        dialog = item.get('dialog', [])
                        
                        for utterance in dialog:
                            if utterance and len(utterance.split()) > 2:
                                # Daily dialog - mostly casual with some questions
                                if '?' in utterance:
                                    action = 'SEARCH_MEMORY'
                                else:
                                    action = 'NO_ACTION'
                                
                                examples.append({
                                    'text': utterance,
                                    'label': self.intent_mapper.label_mapping[action],
                                    'label_name': action,
                                    'language': 'en',
                                    'source': 'daily_dialog',
                                    'context': 'daily'
                                })
                                
                                if len(examples) >= target_samples:
                                    break
                        
                        if len(examples) >= target_samples:
                            break
                    
                    if len(examples) >= target_samples:
                        break
        except Exception as e:
            logger.warning(f"DailyDialog dataset mapping partial failure: {e}")
        
        return examples[:target_samples]
    
    def _generate_synthetic_examples(self, target_samples: int) -> List[Dict[str, Any]]:
        """Generate synthetic examples"""
        
        # Split between English and Italian
        en_samples = int(target_samples * 0.6)
        it_samples = target_samples - en_samples
        
        examples = []
        
        # Generate English examples
        en_examples = self.synthetic_generator.generate_examples(en_samples, 'en')
        examples.extend(en_examples)
        
        # Generate Italian examples
        it_examples = self.synthetic_generator.generate_examples(it_samples, 'it')
        examples.extend(it_examples)
        
        logger.info(f"Generated {len(examples)} synthetic examples")
        return examples
    
    def _map_banking_query(self, text: str) -> str:
        """Map banking query to memory action"""
        
        text_lower = text.lower()
        
        # Questions are typically searches
        if '?' in text or any(word in text_lower for word in ['how', 'what', 'where', 'when', 'why']):
            return 'SEARCH_MEMORY'
        
        # Account actions are saves
        elif any(word in text_lower for word in ['activate', 'create', 'setup', 'enable', 'add']):
            return 'SAVE_MEMORY'
        
        # Inquiries are searches
        else:
            return 'SEARCH_MEMORY'
    
    def _process_final_dataset(self, all_examples: List[Dict], target_size: int) -> DatasetDict:
        """Process final dataset and create splits"""
        
        # Convert to DataFrame for processing
        df = pd.DataFrame(all_examples)
        
        # Remove duplicates
        initial_size = len(df)
        df = df.drop_duplicates(subset=['text'])
        logger.info(f"Removed {initial_size - len(df)} duplicate examples")
        
        # Balance classes
        df = self._balance_classes(df, target_size)
        
        # Create train/val/test splits
        train_df, temp_df = train_test_split(df, test_size=0.2, stratify=df['label'], random_state=42)
        val_df, test_df = train_test_split(temp_df, test_size=0.5, stratify=temp_df['label'], random_state=42)
        
        # Convert to HuggingFace format
        dataset_dict = DatasetDict({
            'train': Dataset.from_pandas(train_df),
            'validation': Dataset.from_pandas(val_df),
            'test': Dataset.from_pandas(test_df)
        })
        
        logger.info("Final dataset created:")
        logger.info(f"  Train: {len(train_df):,} examples")
        logger.info(f"  Validation: {len(val_df):,} examples")
        logger.info(f"  Test: {len(test_df):,} examples")
        logger.info(f"  Total: {len(df):,} examples")
        
        # Show class distribution
        class_dist = df['label_name'].value_counts()
        logger.info(f"  Class distribution: {class_dist.to_dict()}")
        
        return dataset_dict
    
    def _balance_classes(self, df: pd.DataFrame, target_size: int) -> pd.DataFrame:
        """Balance classes to desired distribution"""
        
        # Target distribution
        target_distribution = {
            'SAVE_MEMORY': 0.4,
            'SEARCH_MEMORY': 0.35,
            'NO_ACTION': 0.25
        }
        
        balanced_dfs = []
        
        for class_name, ratio in target_distribution.items():
            target_count = int(target_size * ratio)
            class_df = df[df['label_name'] == class_name]
            
            if len(class_df) > target_count:
                # Downsample
                class_df = class_df.sample(n=target_count, random_state=42)
            elif len(class_df) < target_count:
                # Upsample with repetition
                factor = target_count // len(class_df)
                remainder = target_count % len(class_df)
                
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


async def build_and_upload_massive_dataset(
    hf_token: str,
    target_size: int = 100000,
    repo_name: str = "mcp-memory-auto-trigger-dataset"
) -> str:
    """Convenience function to build and upload massive dataset"""
    
    builder = ComprehensiveDatasetBuilder(hf_token=hf_token)
    
    # Build dataset
    dataset = await builder.build_massive_dataset(target_size)
    
    # Upload to HuggingFace
    repo_id = await builder.upload_to_huggingface(dataset, repo_name)
    
    return repo_id


if __name__ == "__main__":
    import os
    
    # Get HF token from environment
    hf_token = os.getenv("HF_TOKEN")
    if not hf_token:
        print("Please set HF_TOKEN environment variable")
        exit(1)
    
    # Build and upload dataset
    async def main():
        repo_id = await build_and_upload_massive_dataset(
            hf_token=hf_token,
            target_size=100000,
            repo_name="mcp-memory-auto-trigger-dataset"
        )
        print(f"Dataset uploaded to: {repo_id}")
    
    asyncio.run(main())
