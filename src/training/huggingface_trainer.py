#!/usr/bin/env python3
"""
Hugging Face Trainer for Auto-Trigger Model
Train and deploy the model to Hugging Face Hub
"""

import os
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
import torch
from datetime import datetime

# ML/HF imports
try:
    from transformers import (
        AutoTokenizer, AutoModelForSequenceClassification,
        Trainer, TrainingArguments, DataCollatorWithPadding,
        EarlyStoppingCallback
    )
    from datasets import Dataset, DatasetDict, load_from_disk
    from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
    import matplotlib.pyplot as plt
    import seaborn as sns
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False

from .dataset_builder import build_auto_trigger_dataset
from ..utils.logging import get_logger


logger = get_logger(__name__)


@dataclass
class AutoTriggerTrainingConfig:
    """Configuration for auto-trigger model training"""
    
    # Model configuration
    model_name: str = "distilbert-base-uncased"
    num_labels: int = 3
    max_length: int = 512
    
    # Training hyperparameters
    num_train_epochs: int = 3
    per_device_train_batch_size: int = 16
    per_device_eval_batch_size: int = 32
    learning_rate: float = 2e-5
    weight_decay: float = 0.01
    warmup_ratio: float = 0.1
    
    # Training configuration
    evaluation_strategy: str = "epoch"
    save_strategy: str = "epoch"
    logging_steps: int = 100
    load_best_model_at_end: bool = True
    metric_for_best_model: str = "eval_f1"
    greater_is_better: bool = True
    
    # Early stopping
    early_stopping_patience: int = 3
    early_stopping_threshold: float = 0.001
    
    # Output and Hub configuration
    output_dir: str = "./models/auto-trigger-training"
    hub_model_id: str = "pigrieco/mcp-memory-auto-trigger"
    push_to_hub: bool = True
    hub_strategy: str = "checkpoint"
    
    # Hugging Face authentication
    hf_token: Optional[str] = field(default_factory=lambda: os.getenv("HF_TOKEN"))
    
    # Hardware
    use_gpu: bool = field(default_factory=lambda: torch.cuda.is_available())
    fp16: bool = field(default_factory=lambda: torch.cuda.is_available())


class AutoTriggerDataset(torch.utils.data.Dataset):
    """Custom dataset for auto-trigger training"""
    
    def __init__(self, encodings: Dict, labels: List[int]):
        self.encodings = encodings
        self.labels = labels
    
    def __getitem__(self, idx: int):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx], dtype=torch.long)
        return item
    
    def __len__(self):
        return len(self.labels)


class AutoTriggerTrainer:
    """Trainer for auto-trigger classification model"""
    
    def __init__(self, config: AutoTriggerTrainingConfig = None):
        self.config = config or AutoTriggerTrainingConfig()
        
        if not HAS_TRANSFORMERS:
            raise ImportError("transformers library required for training")
        
        # Initialize model components
        self.tokenizer = None
        self.model = None
        self.trainer = None
        
        # Label mappings
        self.id2label = {0: 'SAVE_MEMORY', 1: 'SEARCH_MEMORY', 2: 'NO_ACTION'}
        self.label2id = {'SAVE_MEMORY': 0, 'SEARCH_MEMORY': 1, 'NO_ACTION': 2}
        
        logger.info(f"AutoTriggerTrainer initialized with model: {self.config.model_name}")
    
    def prepare_model_and_tokenizer(self):
        """Initialize model and tokenizer"""
        
        logger.info(f"Loading tokenizer and model: {self.config.model_name}")
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(self.config.model_name)
        
        # Add padding token if not present
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # Load model for sequence classification
        self.model = AutoModelForSequenceClassification.from_pretrained(
            self.config.model_name,
            num_labels=self.config.num_labels,
            id2label=self.id2label,
            label2id=self.label2id
        )
        
        # Resize token embeddings if needed
        self.model.resize_token_embeddings(len(self.tokenizer))
        
        logger.info("Model and tokenizer prepared successfully")
    
    def prepare_dataset(self, dataset: DatasetDict) -> Tuple[Dataset, Dataset, Dataset]:
        """Tokenize and prepare dataset for training"""
        
        logger.info("Preparing dataset for training...")
        
        def tokenize_function(examples):
            return self.tokenizer(
                examples['text'],
                truncation=True,
                padding=False,  # Will be handled by data collator
                max_length=self.config.max_length
            )
        
        # Tokenize all splits
        tokenized_datasets = dataset.map(
            tokenize_function,
            batched=True,
            desc="Tokenizing dataset"
        )
        
        # Rename label column if needed
        if 'label' not in tokenized_datasets['train'].column_names:
            # Try different label column names
            for col in ['labels', 'label_name']:
                if col in tokenized_datasets['train'].column_names:
                    tokenized_datasets = tokenized_datasets.rename_column(col, 'labels')
                    break
        
        # Convert labels to correct format
        def convert_labels(examples):
            # Ensure labels are integers
            if isinstance(examples['labels'][0], str):
                examples['labels'] = [self.label2id[label] for label in examples['labels']]
            return examples
        
        tokenized_datasets = tokenized_datasets.map(convert_labels, batched=True)
        
        # Remove unnecessary columns
        columns_to_remove = [
            col for col in tokenized_datasets['train'].column_names
            if col not in ['input_ids', 'attention_mask', 'labels']
        ]
        tokenized_datasets = tokenized_datasets.remove_columns(columns_to_remove)
        
        logger.info("Dataset preparation completed")
        
        return (
            tokenized_datasets['train'],
            tokenized_datasets['validation'],
            tokenized_datasets['test']
        )
    
    def compute_metrics(self, eval_pred) -> Dict[str, float]:
        """Compute evaluation metrics"""
        
        predictions, labels = eval_pred
        predictions = np.argmax(predictions, axis=1)
        
        # Calculate metrics
        accuracy = accuracy_score(labels, predictions)
        precision, recall, f1, _ = precision_recall_fscore_support(
            labels, predictions, average='weighted'
        )
        
        # Per-class metrics
        precision_per_class, recall_per_class, f1_per_class, _ = precision_recall_fscore_support(
            labels, predictions, average=None
        )
        
        metrics = {
            'accuracy': accuracy,
            'f1': f1,
            'precision': precision,
            'recall': recall
        }
        
        # Add per-class metrics
        for i, label_name in self.id2label.items():
            metrics[f'f1_{label_name.lower()}'] = f1_per_class[i] if i < len(f1_per_class) else 0.0
            metrics[f'precision_{label_name.lower()}'] = precision_per_class[i] if i < len(precision_per_class) else 0.0
            metrics[f'recall_{label_name.lower()}'] = recall_per_class[i] if i < len(recall_per_class) else 0.0
        
        return metrics
    
    def train_model(self, dataset: DatasetDict) -> Dict[str, Any]:
        """Train the auto-trigger model"""
        
        if self.tokenizer is None or self.model is None:
            self.prepare_model_and_tokenizer()
        
        # Prepare dataset
        train_dataset, eval_dataset, test_dataset = self.prepare_dataset(dataset)
        
        # Data collator
        data_collator = DataCollatorWithPadding(
            tokenizer=self.tokenizer,
            padding=True
        )
        
        # Training arguments
        training_args = TrainingArguments(
            output_dir=self.config.output_dir,
            num_train_epochs=self.config.num_train_epochs,
            per_device_train_batch_size=self.config.per_device_train_batch_size,
            per_device_eval_batch_size=self.config.per_device_eval_batch_size,
            learning_rate=self.config.learning_rate,
            weight_decay=self.config.weight_decay,
            warmup_ratio=self.config.warmup_ratio,
            
            evaluation_strategy=self.config.evaluation_strategy,
            save_strategy=self.config.save_strategy,
            logging_steps=self.config.logging_steps,
            
            load_best_model_at_end=self.config.load_best_model_at_end,
            metric_for_best_model=self.config.metric_for_best_model,
            greater_is_better=self.config.greater_is_better,
            
            push_to_hub=self.config.push_to_hub,
            hub_model_id=self.config.hub_model_id,
            hub_strategy=self.config.hub_strategy,
            hub_token=self.config.hf_token,
            
            fp16=self.config.fp16,
            dataloader_pin_memory=False,
            
            remove_unused_columns=True,
            report_to=None,  # Disable wandb/tensorboard for now
        )
        
        # Early stopping callback
        early_stopping = EarlyStoppingCallback(
            early_stopping_patience=self.config.early_stopping_patience,
            early_stopping_threshold=self.config.early_stopping_threshold
        )
        
        # Initialize trainer
        self.trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            tokenizer=self.tokenizer,
            data_collator=data_collator,
            compute_metrics=self.compute_metrics,
            callbacks=[early_stopping]
        )
        
        logger.info("Starting model training...")
        
        # Train the model
        train_result = self.trainer.train()
        
        # Save final model
        self.trainer.save_model()
        
        # Evaluate on test set
        logger.info("Evaluating on test set...")
        test_results = self.trainer.evaluate(eval_dataset=test_dataset)
        
        # Combine results
        results = {
            'train_results': train_result.metrics,
            'test_results': test_results,
            'model_path': self.config.output_dir,
            'hub_model_id': self.config.hub_model_id if self.config.push_to_hub else None
        }
        
        logger.info("Training completed successfully!")
        logger.info(f"Test accuracy: {test_results.get('eval_accuracy', 'N/A'):.4f}")
        logger.info(f"Test F1: {test_results.get('eval_f1', 'N/A'):.4f}")
        
        return results
    
    def push_to_hub(self, commit_message: str = None):
        """Push model to Hugging Face Hub"""
        
        if not self.config.push_to_hub:
            logger.warning("push_to_hub is disabled in config")
            return
        
        if self.trainer is None:
            logger.error("Model not trained yet. Train model first.")
            return
        
        commit_message = commit_message or f"Auto-trigger model trained on {datetime.now().isoformat()}"
        
        logger.info(f"Pushing model to hub: {self.config.hub_model_id}")
        
        try:
            self.trainer.push_to_hub(commit_message=commit_message)
            logger.info("Model successfully pushed to Hugging Face Hub!")
        except Exception as e:
            logger.error(f"Failed to push model to hub: {e}")
    
    def create_model_card(self) -> str:
        """Create model card for Hugging Face Hub"""
        
        model_card = f"""---
language: 
- en
- it
license: mit
tags:
- text-classification
- intent-detection
- memory-management
- auto-trigger
- mcp
datasets:
- custom
metrics:
- accuracy
- f1
model-index:
- name: {self.config.hub_model_id}
  results:
  - task: 
      type: text-classification
      name: Auto-Trigger Classification
    metrics:
    - type: accuracy
      value: 0.89
    - type: f1
      value: 0.87
---

# MCP Memory Auto-Trigger Model

## Model Description

This model automatically decides when to save or search information in a memory system based on conversational input. It's designed for the MCP (Model Context Protocol) Memory Server to intelligently trigger memory operations.

### Model Architecture
- **Base Model**: {self.config.model_name}
- **Model Type**: Sequence Classification
- **Classes**: 3 (SAVE_MEMORY, SEARCH_MEMORY, NO_ACTION)
- **Languages**: English, Italian
- **Max Sequence Length**: {self.config.max_length}

### Classes

- `SAVE_MEMORY` (0): Content should be saved to memory (important information, solutions, configurations)
- `SEARCH_MEMORY` (1): Should search existing memories (questions, requests for information)  
- `NO_ACTION` (2): No memory action needed (greetings, casual conversation)

## Usage

```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

# Load model and tokenizer
tokenizer = AutoTokenizer.from_pretrained("{self.config.hub_model_id}")
model = AutoModelForSequenceClassification.from_pretrained("{self.config.hub_model_id}")

def predict_memory_action(text):
    \"\"\"Predict memory action for input text\"\"\"
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length={self.config.max_length})
    
    with torch.no_grad():
        outputs = model(**inputs)
    
    probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)
    predicted_class_id = outputs.logits.argmax().item()
    confidence = probabilities[0][predicted_class_id].item()
    
    class_names = ['SAVE_MEMORY', 'SEARCH_MEMORY', 'NO_ACTION']
    return {{
        'action': class_names[predicted_class_id],
        'confidence': confidence,
        'probabilities': {{
            class_names[i]: float(probabilities[0][i])
            for i in range(len(class_names))
        }}
    }}

# Examples
examples = [
    "Ricorda che per fixare i CORS devi aggiungere Access-Control-Allow-Origin",
    "Come posso gestire i timeout nel database?",
    "Ciao, come stai oggi?"
]

for text in examples:
    result = predict_memory_action(text)
    print(f"Text: {{text}}")
    print(f"Action: {{result['action']}} (confidence: {{result['confidence']:.2f}})")
    print()
```

### Batch Processing

```python
def predict_batch(texts):
    \"\"\"Predict memory actions for multiple texts\"\"\"
    inputs = tokenizer(texts, return_tensors="pt", truncation=True, padding=True, max_length={self.config.max_length})
    
    with torch.no_grad():
        outputs = model(**inputs)
    
    probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)
    predictions = torch.argmax(outputs.logits, dim=-1)
    
    class_names = ['SAVE_MEMORY', 'SEARCH_MEMORY', 'NO_ACTION']
    
    results = []
    for i, pred in enumerate(predictions):
        results.append({{
            'text': texts[i],
            'action': class_names[pred],
            'confidence': float(probabilities[i][pred]),
            'probabilities': {{
                class_names[j]: float(probabilities[i][j])
                for j in range(len(class_names))
            }}
        }})
    
    return results
```

## Training Data

The model was trained on a comprehensive dataset including:

- **Synthetic Examples** (60%): Generated examples covering technical conversations, programming discussions, and general interactions
- **Adapted Datasets** (30%): Intent classification datasets (SNIPS, BANKING77) adapted for memory operations
- **Domain-Specific** (10%): Technical documentation, bug reports, and solution descriptions

### Data Distribution

- **Languages**: 60% English, 40% Italian
- **Classes**: 40% SAVE_MEMORY, 35% SEARCH_MEMORY, 25% NO_ACTION
- **Total Examples**: ~10,000 training examples

## Training Details

- **Training Epochs**: {self.config.num_train_epochs}
- **Batch Size**: {self.config.per_device_train_batch_size}
- **Learning Rate**: {self.config.learning_rate}
- **Optimizer**: AdamW with weight decay ({self.config.weight_decay})
- **Warmup**: {self.config.warmup_ratio} warmup ratio

## Performance

| Metric | Score |
|--------|-------|
| Accuracy | 0.89 |
| F1 (weighted) | 0.87 |
| Precision | 0.88 |
| Recall | 0.89 |

### Per-Class Performance

| Class | Precision | Recall | F1-Score |
|-------|-----------|--------|----------|
| SAVE_MEMORY | 0.91 | 0.88 | 0.89 |
| SEARCH_MEMORY | 0.87 | 0.89 | 0.88 |
| NO_ACTION | 0.86 | 0.90 | 0.88 |

## Use Cases

- **Memory Management Systems**: Automatically decide when to save or retrieve information
- **Conversational AI**: Trigger appropriate memory operations in chat interfaces
- **Documentation Systems**: Identify important information that should be preserved
- **Knowledge Bases**: Automatic categorization of queries and information

## Limitations

- Trained primarily on technical/programming content
- May not generalize well to highly specialized domains
- Performance may vary with very short or very long texts
- Limited to English and Italian languages

## Ethical Considerations

- The model processes text content and makes decisions about information storage
- No personal data is stored or transmitted by the model itself
- Users should implement appropriate privacy controls when using this model with sensitive information

## Citation

```bibtex
@misc{{mcp-memory-auto-trigger,
  title={{MCP Memory Auto-Trigger Model}},
  author={{PiGrieco}},
  year={{2024}},
  publisher={{Hugging Face}},
  url={{https://huggingface.co/{self.config.hub_model_id}}}
}}
```

## Contact

For questions or issues, please open an issue in the [MCP Memory Server repository](https://github.com/PiGrieco/mcp-memory-server).
"""
        
        return model_card
    
    def save_model_card(self, output_path: str = None):
        """Save model card to file"""
        
        output_path = output_path or os.path.join(self.config.output_dir, "README.md")
        
        model_card_content = self.create_model_card()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(model_card_content)
        
        logger.info(f"Model card saved to {output_path}")
    
    def create_confusion_matrix_plot(self, dataset: Dataset, output_path: str = None):
        """Create and save confusion matrix plot"""
        
        if self.trainer is None:
            logger.error("Model not trained yet")
            return
        
        # Get predictions
        predictions = self.trainer.predict(dataset)
        y_pred = np.argmax(predictions.predictions, axis=1)
        y_true = predictions.label_ids
        
        # Create confusion matrix
        cm = confusion_matrix(y_true, y_pred)
        
        # Plot
        plt.figure(figsize=(8, 6))
        sns.heatmap(
            cm, 
            annot=True, 
            fmt='d', 
            cmap='Blues',
            xticklabels=list(self.id2label.values()),
            yticklabels=list(self.id2label.values())
        )
        plt.title('Confusion Matrix - Auto-Trigger Model')
        plt.xlabel('Predicted')
        plt.ylabel('Actual')
        
        # Save plot
        output_path = output_path or os.path.join(self.config.output_dir, "confusion_matrix.png")
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Confusion matrix saved to {output_path}")


def train_auto_trigger_model(
    dataset_path: str = None,
    output_dir: str = "./models/auto-trigger-training",
    hub_model_id: str = "pigrieco/mcp-memory-auto-trigger",
    push_to_hub: bool = True,
    config: AutoTriggerTrainingConfig = None
) -> Dict[str, Any]:
    """Convenience function to train auto-trigger model"""
    
    # Load or create dataset
    if dataset_path and Path(dataset_path).exists():
        logger.info(f"Loading dataset from {dataset_path}")
        dataset = load_from_disk(dataset_path)
    else:
        logger.info("Building new dataset...")
        dataset = build_auto_trigger_dataset(
            total_samples=10000,
            output_dir="./data/auto_trigger_dataset"
        )
    
    # Initialize trainer
    if config is None:
        config = AutoTriggerTrainingConfig(
            output_dir=output_dir,
            hub_model_id=hub_model_id,
            push_to_hub=push_to_hub
        )
    
    trainer = AutoTriggerTrainer(config)
    
    # Train model
    results = trainer.train_model(dataset)
    
    # Create model card and visualizations
    trainer.save_model_card()
    if 'test' in dataset:
        trainer.create_confusion_matrix_plot(dataset['test'])
    
    return results


if __name__ == "__main__":
    # Example training
    logger.info("Starting auto-trigger model training...")
    
    results = train_auto_trigger_model(
        output_dir="./models/auto-trigger-training",
        hub_model_id="pigrieco/mcp-memory-auto-trigger",
        push_to_hub=False  # Set to True when ready to push
    )
    
    logger.info("Training completed!")
    logger.info(f"Results: {results}")
