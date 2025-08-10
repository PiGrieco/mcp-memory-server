#!/usr/bin/env python3
"""
Example: ML-Based Auto-Trigger System
Demonstrates how to use the machine learning trigger system
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.ml_trigger_system import create_ml_auto_trigger_system, ActionType
from src.core.hybrid_trigger_system import create_hybrid_auto_trigger_system, TriggerMode
from src.services.embedding_service import EmbeddingService
from src.services.memory_service import MemoryService
from src.services.database_service import DatabaseService
from src.training.ml_training_pipeline import run_training_pipeline


class MockMemoryService:
    """Mock memory service for demonstration"""
    
    def __init__(self):
        self.memories = [
            {
                'id': 'mem_001',
                'content': 'To fix CORS errors, add Access-Control-Allow-Origin header',
                'similarity': 0.9
            },
            {
                'id': 'mem_002', 
                'content': 'Use useCallback to optimize React performance',
                'similarity': 0.8
            },
            {
                'id': 'mem_003',
                'content': 'Increase timeout to 30 seconds for slow connections',
                'similarity': 0.7
            }
        ]
    
    async def search_memories(self, query: str, **kwargs):
        """Mock search that returns relevant memories"""
        if 'timeout' in query.lower():
            return [self.memories[2]]
        elif 'cors' in query.lower():
            return [self.memories[0]]
        elif 'react' in query.lower():
            return [self.memories[1]]
        return []


class MockEmbeddingService:
    """Mock embedding service for demonstration"""
    
    async def generate_embedding(self, text: str):
        """Generate mock embedding"""
        # Simple hash-based mock embedding
        import hashlib
        hash_obj = hashlib.md5(text.encode())
        hash_hex = hash_obj.hexdigest()
        
        # Convert to float array
        embedding = []
        for i in range(0, len(hash_hex), 2):
            byte_val = int(hash_hex[i:i+2], 16)
            embedding.append(float(byte_val) / 255.0)
        
        # Pad to 384 dimensions (typical for sentence transformers)
        while len(embedding) < 384:
            embedding.extend(embedding[:min(10, 384 - len(embedding))])
        
        return embedding[:384]


async def demonstrate_ml_triggers():
    """Demonstrate ML trigger system"""
    
    print("🧠 ML Auto-Trigger System Demonstration")
    print("=" * 50)
    
    # Initialize services
    embedding_service = MockEmbeddingService()
    memory_service = MockMemoryService()
    
    # Create ML trigger system
    ml_system = create_ml_auto_trigger_system(memory_service, embedding_service)
    await ml_system.initialize()
    
    # Test scenarios
    test_scenarios = [
        {
            'name': 'Important Information',
            'message': 'Ricorda che per fixare i CORS devi aggiungere Access-Control-Allow-Origin',
            'expected': ActionType.SAVE_MEMORY
        },
        {
            'name': 'Technical Solution',
            'message': 'Ho risolto il bug di timeout aumentando connection_timeout a 30 secondi',
            'expected': ActionType.SAVE_MEMORY
        },
        {
            'name': 'Question about Known Topic',
            'message': 'Come posso gestire i timeout nel database?',
            'expected': ActionType.SEARCH_MEMORY
        },
        {
            'name': 'General Conversation',
            'message': 'Ciao, come stai oggi?',
            'expected': ActionType.NO_ACTION
        },
        {
            'name': 'Code Example',
            'message': 'Questo pattern funziona bene: useCallback(() => {...}, [deps])',
            'expected': ActionType.SAVE_MEMORY
        }
    ]
    
    # Test each scenario
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n📋 Test {i}: {scenario['name']}")
        print(f"Message: \"{scenario['message']}\"")
        
        # Create conversation context
        conversation_history = [
            {
                'role': 'user',
                'content': 'Sto lavorando su un progetto',
                'timestamp': '2024-01-01T10:00:00Z'
            },
            {
                'role': 'assistant', 
                'content': 'Ottimo! Come posso aiutarti?',
                'timestamp': '2024-01-01T10:01:00Z'
            }
        ]
        
        # Get ML prediction
        prediction = await ml_system.analyze_and_predict(
            message=scenario['message'],
            conversation_history=conversation_history,
            platform='cursor',
            user_id='demo_user'
        )
        
        # Display results
        print(f"🔮 Prediction: {prediction.action.value}")
        print(f"🎯 Confidence: {prediction.confidence:.2f}")
        print(f"💭 Reasoning: {', '.join(prediction.reasoning)}")
        print(f"🔧 Features: {', '.join(prediction.features_used)}")
        
        # Check if prediction matches expectation
        if prediction.action == scenario['expected']:
            print("✅ Prediction matches expectation")
        else:
            print(f"❌ Expected {scenario['expected'].value}, got {prediction.action.value}")
        
        # Simulate learning from user feedback (skip for demo to avoid errors)
        # In real implementation, this would extract features again and learn
        # await ml_system.learn_from_action(
        #     features=features_from_prediction,  # Would use actual features
        #     action_taken=scenario['expected'],
        #     user_id='demo_user'
        # )
    
    # Display system metrics
    print("\n📊 System Metrics:")
    metrics = ml_system.get_metrics()
    for key, value in metrics.items():
        print(f"   {key}: {value}")


async def demonstrate_hybrid_system():
    """Demonstrate hybrid trigger system"""
    
    print("\n🔀 Hybrid Auto-Trigger System Demonstration")
    print("=" * 50)
    
    # Initialize services
    embedding_service = MockEmbeddingService()
    memory_service = MockMemoryService()
    
    # Create hybrid system
    hybrid_system = create_hybrid_auto_trigger_system(memory_service, embedding_service)
    await hybrid_system.initialize()
    
    # Test different modes
    modes = [
        TriggerMode.DETERMINISTIC,
        TriggerMode.ML_ONLY,
        TriggerMode.HYBRID,
        TriggerMode.LEARNING
    ]
    
    test_message = "Ricorda questa importante configurazione: timeout=30s"
    conversation = [
        {'role': 'user', 'content': test_message}
    ]
    
    for mode in modes:
        print(f"\n🔧 Testing {mode.value.upper()} mode:")
        
        # Switch mode
        hybrid_system.switch_mode(mode)
        
        # Get prediction
        prediction = await hybrid_system.analyze_and_decide(
            messages=conversation,
            platform='cursor',
            user_id='demo_user'
        )
        
        print(f"   Action: {prediction.final_action.value}")
        print(f"   Confidence: {prediction.confidence:.2f}")
        print(f"   Method: {prediction.method_used}")
        print(f"   Reasoning: {', '.join(prediction.reasoning[:2])}")  # First 2 reasons
    
    # Performance metrics
    print("\n📈 Hybrid System Metrics:")
    metrics = hybrid_system.get_performance_metrics()
    print(f"   Current mode: {metrics['current_mode']}")
    print(f"   Mode switches: {metrics['hybrid_metrics']['mode_switches']}")


async def demonstrate_training_pipeline():
    """Demonstrate ML training pipeline"""
    
    print("\n🎓 ML Training Pipeline Demonstration")
    print("=" * 50)
    
    # Initialize services
    embedding_service = MockEmbeddingService()
    memory_service = MockMemoryService()
    
    try:
        # Run training pipeline with small dataset for demo
        results = await run_training_pipeline(
            embedding_service=embedding_service,
            memory_service=memory_service,
            output_dir="models/demo_training",
            num_samples=100  # Small dataset for demo
        )
        
        print(f"✅ Training completed!")
        print(f"   Data samples: {results['data_samples']}")
        
        if 'evaluation' in results:
            eval_results = results['evaluation']
            
            if 'save_model' in eval_results:
                save_acc = eval_results['save_model']['accuracy']
                print(f"   Save model accuracy: {save_acc:.2f}")
            
            if 'search_model' in eval_results:
                search_acc = eval_results['search_model']['accuracy']
                print(f"   Search model accuracy: {search_acc:.2f}")
    
    except Exception as e:
        print(f"❌ Training failed: {e}")
        print("Note: This is expected in demo mode without full ML dependencies")


async def main():
    """Run all demonstrations"""
    
    print("🚀 MCP Memory Server - ML Auto-Trigger Demonstration")
    print("=" * 60)
    print("This demo shows how the ML-based trigger system works")
    print("compared to traditional deterministic rules.\n")
    
    try:
        # Test ML triggers
        await demonstrate_ml_triggers()
        
        # Test hybrid system
        await demonstrate_hybrid_system()
        
        # Test training pipeline
        await demonstrate_training_pipeline()
        
        print("\n🎉 Demonstration completed!")
        print("\nKey Benefits of ML Triggers:")
        print("✅ Learns from user behavior patterns")
        print("✅ Adapts to different contexts and users")
        print("✅ Reduces false positives over time")
        print("✅ Can combine with deterministic rules")
        print("✅ Provides confidence scores and reasoning")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        print("This might be due to missing ML dependencies.")
        print("Install with: pip install scikit-learn pandas matplotlib")


if __name__ == "__main__":
    asyncio.run(main())
