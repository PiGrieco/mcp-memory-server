#!/usr/bin/env python3
"""
Complete Training and Deployment Script
Train the auto-trigger model and deploy to Hugging Face Hub
"""

import os
import sys
import argparse
import json
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.training.dataset_builder import build_auto_trigger_dataset, DatasetConfig
from src.training.huggingface_trainer import train_auto_trigger_model, AutoTriggerTrainingConfig
from src.utils.logging import get_logger

logger = get_logger(__name__)


def parse_arguments():
    """Parse command line arguments"""
    
    parser = argparse.ArgumentParser(description="Train and deploy auto-trigger model")
    
    # Dataset arguments
    parser.add_argument(
        "--dataset-size",
        type=int,
        default=10000,
        help="Total number of training examples to generate"
    )
    
    parser.add_argument(
        "--dataset-path",
        type=str,
        default=None,
        help="Path to existing dataset (if not provided, will generate new one)"
    )
    
    # Training arguments
    parser.add_argument(
        "--model-name",
        type=str,
        default="distilbert-base-uncased",
        help="Base model name from Hugging Face"
    )
    
    parser.add_argument(
        "--epochs",
        type=int,
        default=3,
        help="Number of training epochs"
    )
    
    parser.add_argument(
        "--batch-size",
        type=int,
        default=16,
        help="Training batch size"
    )
    
    parser.add_argument(
        "--learning-rate",
        type=float,
        default=2e-5,
        help="Learning rate"
    )
    
    # Deployment arguments
    parser.add_argument(
        "--hub-model-id",
        type=str,
        default="pigrieco/mcp-memory-auto-trigger",
        help="Hugging Face Hub model ID"
    )
    
    parser.add_argument(
        "--push-to-hub",
        action="store_true",
        help="Push trained model to Hugging Face Hub"
    )
    
    parser.add_argument(
        "--hf-token",
        type=str,
        default=None,
        help="Hugging Face token (or set HF_TOKEN environment variable)"
    )
    
    # Output arguments
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./models/auto-trigger-training",
        help="Output directory for training artifacts"
    )
    
    parser.add_argument(
        "--data-dir",
        type=str,
        default="./data/auto_trigger_dataset",
        help="Directory for dataset storage"
    )
    
    # Options
    parser.add_argument(
        "--skip-dataset-generation",
        action="store_true",
        help="Skip dataset generation and use existing dataset"
    )
    
    parser.add_argument(
        "--skip-training",
        action="store_true",
        help="Skip training (only generate dataset)"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Dry run - show configuration but don't execute"
    )
    
    return parser.parse_args()


def setup_environment(args):
    """Setup environment and validate configuration"""
    
    logger.info("Setting up environment...")
    
    # Create output directories
    Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    Path(args.data_dir).mkdir(parents=True, exist_ok=True)
    
    # Setup Hugging Face token
    if args.push_to_hub:
        hf_token = args.hf_token or os.getenv("HF_TOKEN")
        if not hf_token:
            logger.warning("No Hugging Face token provided. Set HF_TOKEN environment variable or use --hf-token")
            logger.warning("Model will be trained but not pushed to Hub")
            args.push_to_hub = False
        else:
            os.environ["HF_TOKEN"] = hf_token
            logger.info("Hugging Face token configured")
    
    # Validate model name
    try:
        from transformers import AutoTokenizer
        tokenizer = AutoTokenizer.from_pretrained(args.model_name)
        logger.info(f"Base model validated: {args.model_name}")
    except Exception as e:
        logger.error(f"Failed to load base model {args.model_name}: {e}")
        sys.exit(1)
    
    return True


def generate_dataset(args):
    """Generate or load training dataset"""
    
    if args.skip_dataset_generation and args.dataset_path:
        logger.info(f"Loading existing dataset from {args.dataset_path}")
        try:
            from datasets import load_from_disk
            dataset = load_from_disk(args.dataset_path)
            logger.info("Dataset loaded successfully")
            return dataset
        except Exception as e:
            logger.error(f"Failed to load dataset: {e}")
            logger.info("Falling back to dataset generation...")
    
    logger.info("Generating new training dataset...")
    
    # Configure dataset generation
    config = DatasetConfig(
        total_samples=args.dataset_size,
        synthetic_ratio=0.7,
        adapted_existing_ratio=0.3,
        real_user_ratio=0.0,
        english_ratio=0.6,
        italian_ratio=0.4
    )
    
    # Generate dataset
    dataset = build_auto_trigger_dataset(
        total_samples=args.dataset_size,
        output_dir=args.data_dir,
        config=config
    )
    
    logger.info(f"Dataset generated with {args.dataset_size} total examples")
    
    # Log dataset statistics
    if hasattr(dataset, 'keys'):
        for split_name in dataset.keys():
            split_data = dataset[split_name]
            if hasattr(split_data, '__len__'):
                logger.info(f"  {split_name}: {len(split_data)} examples")
    
    return dataset


def train_model(dataset, args):
    """Train the auto-trigger model"""
    
    if args.skip_training:
        logger.info("Skipping training as requested")
        return None
    
    logger.info("Starting model training...")
    
    # Configure training
    training_config = AutoTriggerTrainingConfig(
        model_name=args.model_name,
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        output_dir=args.output_dir,
        hub_model_id=args.hub_model_id,
        push_to_hub=args.push_to_hub,
        hf_token=os.getenv("HF_TOKEN")
    )
    
    # Train model
    results = train_auto_trigger_model(
        dataset_path=None,  # Use provided dataset
        output_dir=args.output_dir,
        hub_model_id=args.hub_model_id,
        push_to_hub=args.push_to_hub,
        config=training_config
    )
    
    logger.info("Training completed successfully!")
    
    # Log results
    if 'test_results' in results:
        test_results = results['test_results']
        logger.info(f"Test Results:")
        logger.info(f"  Accuracy: {test_results.get('eval_accuracy', 'N/A'):.4f}")
        logger.info(f"  F1 Score: {test_results.get('eval_f1', 'N/A'):.4f}")
        logger.info(f"  Precision: {test_results.get('eval_precision', 'N/A'):.4f}")
        logger.info(f"  Recall: {test_results.get('eval_recall', 'N/A'):.4f}")
    
    return results


def create_deployment_summary(results, args):
    """Create deployment summary"""
    
    summary = {
        "deployment_info": {
            "timestamp": datetime.now().isoformat(),
            "model_id": args.hub_model_id,
            "base_model": args.model_name,
            "dataset_size": args.dataset_size,
            "training_epochs": args.epochs,
            "batch_size": args.batch_size,
            "learning_rate": args.learning_rate,
            "pushed_to_hub": args.push_to_hub
        }
    }
    
    if results:
        summary["training_results"] = results
    
    # Save summary
    summary_file = Path(args.output_dir) / "deployment_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2, default=str)
    
    logger.info(f"Deployment summary saved to {summary_file}")
    
    return summary


def create_usage_example():
    """Create usage example script"""
    
    usage_example = '''#!/usr/bin/env python3
"""
Usage Example for MCP Memory Auto-Trigger Model
"""

from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

def load_model(model_id="pigrieco/mcp-memory-auto-trigger"):
    """Load the trained auto-trigger model"""
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForSequenceClassification.from_pretrained(model_id)
    return tokenizer, model

def predict_memory_action(text, tokenizer, model):
    """Predict memory action for input text"""
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
    
    with torch.no_grad():
        outputs = model(**inputs)
    
    probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)
    predicted_class_id = outputs.logits.argmax().item()
    confidence = probabilities[0][predicted_class_id].item()
    
    class_names = ['SAVE_MEMORY', 'SEARCH_MEMORY', 'NO_ACTION']
    return {
        'action': class_names[predicted_class_id],
        'confidence': confidence,
        'probabilities': {
            class_names[i]: float(probabilities[0][i])
            for i in range(len(class_names))
        }
    }

def main():
    """Example usage"""
    
    # Load model
    tokenizer, model = load_model()
    
    # Test examples
    examples = [
        "Ricorda che per fixare i CORS devi aggiungere Access-Control-Allow-Origin",
        "Come posso gestire i timeout nel database?",
        "Ciao, come stai oggi?",
        "Ho risolto il bug aumentando il timeout a 30 secondi",
        "What's the best way to handle API errors?"
    ]
    
    print("🧠 MCP Memory Auto-Trigger Model - Usage Example")
    print("=" * 60)
    
    for i, text in enumerate(examples, 1):
        result = predict_memory_action(text, tokenizer, model)
        
        print(f"\\n{i}. Text: \\"{text}\\"")
        print(f"   Action: {result['action']}")
        print(f"   Confidence: {result['confidence']:.2%}")
        
        # Show top 2 probabilities
        sorted_probs = sorted(result['probabilities'].items(), key=lambda x: x[1], reverse=True)
        print(f"   Top predictions:")
        for action, prob in sorted_probs[:2]:
            print(f"     {action}: {prob:.2%}")

if __name__ == "__main__":
    main()
'''
    
    return usage_example


def main():
    """Main execution function"""
    
    args = parse_arguments()
    
    print("🚀 **MCP MEMORY AUTO-TRIGGER TRAINING & DEPLOYMENT**")
    print("=" * 70)
    
    # Show configuration
    print(f"📊 **Configuration:**")
    print(f"   Dataset size: {args.dataset_size:,}")
    print(f"   Base model: {args.model_name}")
    print(f"   Training epochs: {args.epochs}")
    print(f"   Batch size: {args.batch_size}")
    print(f"   Learning rate: {args.learning_rate}")
    print(f"   Hub model ID: {args.hub_model_id}")
    print(f"   Push to Hub: {args.push_to_hub}")
    print(f"   Output directory: {args.output_dir}")
    
    if args.dry_run:
        print("\\n🔍 **DRY RUN - Configuration shown, exiting**")
        return
    
    try:
        # Setup environment
        setup_environment(args)
        
        # Generate/load dataset
        print("\\n📊 **DATASET PREPARATION**")
        print("-" * 40)
        dataset = generate_dataset(args)
        
        # Train model
        print("\\n🎓 **MODEL TRAINING**")
        print("-" * 40)
        results = train_model(dataset, args)
        
        # Create deployment artifacts
        print("\\n📦 **DEPLOYMENT ARTIFACTS**")
        print("-" * 40)
        
        summary = create_deployment_summary(results, args)
        
        # Create usage example
        usage_example = create_usage_example()
        usage_file = Path(args.output_dir) / "usage_example.py"
        with open(usage_file, 'w') as f:
            f.write(usage_example)
        logger.info(f"Usage example saved to {usage_file}")
        
        # Final status
        print("\\n🎉 **DEPLOYMENT COMPLETED SUCCESSFULLY!**")
        print("=" * 70)
        
        if args.push_to_hub:
            print(f"✅ Model deployed to Hugging Face Hub: {args.hub_model_id}")
            print(f"🔗 Access at: https://huggingface.co/{args.hub_model_id}")
        else:
            print(f"📁 Model saved locally: {args.output_dir}")
            print("   Use --push-to-hub to deploy to Hugging Face Hub")
        
        print(f"\\n📋 **Next Steps:**")
        print(f"   1. Test the model using: python {usage_file}")
        print(f"   2. Integrate into MCP Memory Server")
        print(f"   3. Monitor performance and collect user feedback")
        print(f"   4. Retrain with real usage data")
        
        return summary
        
    except KeyboardInterrupt:
        logger.info("Training interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Training failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
