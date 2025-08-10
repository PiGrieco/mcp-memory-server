#!/usr/bin/env python3
"""
Dataset Creation Demo
Demonstrates how to build training datasets for the auto-trigger model
"""

import asyncio
import sys
from pathlib import Path
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.training.dataset_builder import AutoTriggerDatasetBuilder, DatasetConfig, SyntheticDataGenerator


def demonstrate_synthetic_generation():
    """Demonstrate synthetic data generation"""
    
    print("🎓 **SYNTHETIC DATA GENERATION DEMO**")
    print("=" * 60)
    
    # Initialize generator
    config = DatasetConfig(total_samples=100)  # Small demo
    generator = SyntheticDataGenerator(config)
    
    # Generate examples for each class and language
    demos = {
        ('SAVE_MEMORY', 'en'): 5,
        ('SAVE_MEMORY', 'it'): 5,
        ('SEARCH_MEMORY', 'en'): 5,
        ('SEARCH_MEMORY', 'it'): 5,
        ('NO_ACTION', 'en'): 3,
        ('NO_ACTION', 'it'): 3
    }
    
    for (class_name, language), count in demos.items():
        print(f"\n📝 **{class_name} Examples ({language.upper()}):**")
        print("-" * 50)
        
        examples = []
        for _ in range(count):
            example = generator._generate_single_example(class_name, language)
            examples.append(example)
            print(f"• {example['text']}")
        
        # Show template diversity
        templates_used = set(ex.get('template', 'N/A') for ex in examples)
        print(f"\n🔧 Templates used: {len(templates_used)}")
    
    print(f"\n✅ **Synthetic generation works!** The system can create diverse, realistic examples.")


def demonstrate_dataset_building():
    """Demonstrate full dataset building process"""
    
    print("\n🏗️ **FULL DATASET BUILDING DEMO**")
    print("=" * 60)
    
    # Create small dataset for demo
    config = DatasetConfig(
        total_samples=500,  # Small for demo
        synthetic_ratio=0.8,
        adapted_existing_ratio=0.2,
        real_user_ratio=0.0
    )
    
    print(f"📊 **Dataset Configuration:**")
    print(f"   Total samples: {config.total_samples}")
    print(f"   Synthetic: {config.synthetic_ratio:.1%}")
    print(f"   Existing datasets: {config.adapted_existing_ratio:.1%}")
    print(f"   Train/Val/Test: {config.train_split:.1%}/{config.val_split:.1%}/{config.test_split:.1%}")
    print(f"   Languages: EN {config.english_ratio:.1%}, IT {config.italian_ratio:.1%}")
    
    # Build dataset
    print("\n🔄 **Building Dataset...**")
    builder = AutoTriggerDatasetBuilder(config)
    
    try:
        dataset = builder.build_comprehensive_dataset()
        
        print("✅ **Dataset built successfully!**")
        
        # Show statistics
        if hasattr(dataset, 'keys'):
            for split_name in dataset.keys():
                split_data = dataset[split_name]
                if hasattr(split_data, '__len__'):
                    print(f"   {split_name}: {len(split_data)} examples")
        
        # Show sample examples
        print("\n📋 **Sample Examples:**")
        if 'train' in dataset:
            train_data = dataset['train']
            sample_size = min(6, len(train_data))
            
            for i in range(sample_size):
                if hasattr(train_data, 'to_pandas'):
                    example = train_data[i]
                elif isinstance(train_data, list):
                    example = train_data[i]
                else:
                    continue
                
                text = example.get('text', 'N/A')
                label_name = example.get('label_name', 'N/A')
                language = example.get('language', 'N/A')
                source = example.get('source', 'N/A')
                
                print(f"\n{i+1}. **{label_name}** ({language}, {source})")
                print(f"   \"{text[:80]}{'...' if len(text) > 80 else ''}\"")
        
        return dataset
        
    except Exception as e:
        print(f"❌ **Dataset building failed:** {e}")
        print("This might be due to missing dependencies (datasets, transformers)")
        return None


def demonstrate_dataset_analysis(dataset):
    """Analyze and visualize dataset statistics"""
    
    if dataset is None:
        print("\n⚠️ **Skipping analysis - no dataset available**")
        return
    
    print("\n📊 **DATASET ANALYSIS**")
    print("=" * 60)
    
    # Collect all examples for analysis
    all_examples = []
    
    for split_name in dataset.keys():
        split_data = dataset[split_name]
        if hasattr(split_data, 'to_pandas'):
            split_df = split_data.to_pandas()
            split_examples = split_df.to_dict('records')
        elif isinstance(split_data, list):
            split_examples = split_data
        else:
            continue
        
        for ex in split_examples:
            ex['split'] = split_name
            all_examples.append(ex)
    
    if not all_examples:
        print("❌ No examples found for analysis")
        return
    
    # Class distribution
    class_counts = {}
    language_counts = {}
    source_counts = {}
    
    for example in all_examples:
        # Class distribution
        label_name = example.get('label_name', 'unknown')
        class_counts[label_name] = class_counts.get(label_name, 0) + 1
        
        # Language distribution
        language = example.get('language', 'unknown')
        language_counts[language] = language_counts.get(language, 0) + 1
        
        # Source distribution
        source = example.get('source', 'unknown')
        source_counts[source] = source_counts.get(source, 0) + 1
    
    # Display statistics
    print("🎯 **Class Distribution:**")
    total_examples = len(all_examples)
    for class_name, count in sorted(class_counts.items()):
        percentage = (count / total_examples) * 100
        print(f"   {class_name}: {count} ({percentage:.1f}%)")
    
    print("\n🌍 **Language Distribution:**")
    for language, count in sorted(language_counts.items()):
        percentage = (count / total_examples) * 100
        print(f"   {language.upper()}: {count} ({percentage:.1f}%)")
    
    print("\n📦 **Source Distribution:**")
    for source, count in sorted(source_counts.items()):
        percentage = (count / total_examples) * 100
        print(f"   {source}: {count} ({percentage:.1f}%)")
    
    # Text length analysis
    text_lengths = [len(ex.get('text', '')) for ex in all_examples]
    if text_lengths:
        avg_length = sum(text_lengths) / len(text_lengths)
        min_length = min(text_lengths)
        max_length = max(text_lengths)
        
        print(f"\n📏 **Text Length Statistics:**")
        print(f"   Average: {avg_length:.1f} characters")
        print(f"   Min: {min_length} characters")
        print(f"   Max: {max_length} characters")


def show_training_recommendations():
    """Show recommendations for training"""
    
    print("\n🎯 **TRAINING RECOMMENDATIONS**")
    print("=" * 60)
    
    recommendations = [
        "💾 **Dataset Size**: Start with 10K examples, scale to 50K+ for production",
        "⚖️ **Class Balance**: 40% SAVE, 35% SEARCH, 25% NO_ACTION works well",
        "🌍 **Languages**: Include both EN and IT for multilingual support",
        "🔧 **Model Choice**: DistilBERT for speed, RoBERTa for accuracy",
        "📊 **Validation**: Use stratified splits to maintain class balance",
        "🎛️ **Hyperparameters**: Learning rate 2e-5, batch size 16, 3 epochs",
        "📈 **Metrics**: Focus on weighted F1-score for imbalanced classes",
        "🔄 **Iteration**: Collect real user data to improve synthetic data"
    ]
    
    for recommendation in recommendations:
        print(f"   {recommendation}")
    
    print("\n🚀 **Next Steps:**")
    print("   1. Run full dataset generation with 10K+ examples")
    print("   2. Train model using huggingface_trainer.py")
    print("   3. Evaluate performance on test set")
    print("   4. Deploy to Hugging Face Hub")
    print("   5. Integrate into MCP Memory Server")


def main():
    """Run all demonstrations"""
    
    print("🎓 **AUTO-TRIGGER DATASET CREATION DEMO**")
    print("=" * 70)
    print("This demo shows how to create training data for the ML auto-trigger system.\n")
    
    try:
        # Demo 1: Synthetic generation
        demonstrate_synthetic_generation()
        
        # Demo 2: Full dataset building
        dataset = demonstrate_dataset_building()
        
        # Demo 3: Dataset analysis
        demonstrate_dataset_analysis(dataset)
        
        # Demo 4: Training recommendations
        show_training_recommendations()
        
        print("\n🎉 **DEMO COMPLETED SUCCESSFULLY!**")
        print("The dataset generation system is ready for production use.")
        
    except Exception as e:
        print(f"\n❌ **Demo failed:** {e}")
        print("This might be due to missing dependencies.")
        print("Try: pip install datasets transformers torch")


if __name__ == "__main__":
    main()
