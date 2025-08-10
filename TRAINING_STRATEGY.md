# 🎓 ML Training Strategy & Dataset Selection

## 📊 **Dataset Options per Auto-Trigger Training**

Ho identificato diverse strategie per ottenere dati di training di alta qualità per il nostro sistema ML auto-trigger.

### **🎯 Option 1: Intent Classification Datasets (RECOMMENDED)**

#### **Dataset Pronti da Adattare:**

1. **ATIS (Airline Travel Information System)**
   - **Size:** ~5,000 esempi
   - **Classes:** 21 intent categories
   - **Format:** Text → Intent classification
   - **Adaptation:** Map intents to SAVE/SEARCH/NO_ACTION
   - **Pros:** Conversational, well-structured
   - **Cons:** Domain-specific (travel)

2. **BANKING77**
   - **Size:** 13,083 esempi
   - **Classes:** 77 banking intents  
   - **Format:** Customer queries → Banking intent
   - **Adaptation:** Map to memory actions
   - **Pros:** Real user queries, diverse
   - **Cons:** Banking domain

3. **SNIPS NLU Dataset**
   - **Size:** ~16,000 esempi
   - **Classes:** 7 intents (AddToPlaylist, BookRestaurant, etc.)
   - **Format:** Natural language → Structured intent
   - **Adaptation:** Perfect for our use case
   - **Pros:** Conversational AI focused
   - **Cons:** Limited size

4. **Facebook Multilingual Task-Oriented Dialog (MTOD)**
   - **Size:** 37,800+ esempi
   - **Classes:** Multiple domains & intents
   - **Format:** Dialog turns → Intent + slots
   - **Adaptation:** Extract relevant intents
   - **Pros:** Large, multilingual, conversational
   - **Cons:** Complex structure

#### **Mapping Strategy:**
```python
INTENT_MAPPING = {
    # SAVE_MEMORY intents
    'add_to_playlist': 'SAVE_MEMORY',
    'create_reminder': 'SAVE_MEMORY', 
    'save_contact': 'SAVE_MEMORY',
    'store_information': 'SAVE_MEMORY',
    
    # SEARCH_MEMORY intents  
    'search_music': 'SEARCH_MEMORY',
    'find_restaurant': 'SEARCH_MEMORY',
    'get_weather': 'SEARCH_MEMORY',
    'query_information': 'SEARCH_MEMORY',
    
    # NO_ACTION intents
    'greetings': 'NO_ACTION',
    'goodbye': 'NO_ACTION',
    'small_talk': 'NO_ACTION'
}
```

### **🔧 Option 2: Synthetic Data Generation (PREFERRED)**

#### **Vantaggi:**
- ✅ **Controllo completo** sui dati
- ✅ **Domain-specific** per memory triggers
- ✅ **Bilanciamento perfetto** delle classi
- ✅ **Multilingual** (italiano + inglese)
- ✅ **Scalabile** a qualsiasi dimensione

#### **Strategia di Generazione:**

```python
SYNTHETIC_TEMPLATES = {
    'SAVE_MEMORY': [
        "Ricorda che {technical_info}",
        "Importante: {solution_info}",
        "Salva questa configurazione: {config_info}",
        "Note per dopo: {important_info}",
        "Ho risolto {problem} con {solution}",
        "Bug fix: {error_description} → {fix_description}",
        "Tutorial: come {action_description}",
        "Documentation: {technical_explanation}"
    ],
    
    'SEARCH_MEMORY': [
        "Come posso {question_about_topic}?",
        "Avevamo già risolto {problem_type}?",
        "What's the best way to {technical_question}?",
        "Come si configura {technology}?",
        "Dove avevo salvato {information_type}?",
        "Help with {technical_issue}",
        "How to debug {error_type}?",
        "Previous solution for {problem_pattern}?"
    ],
    
    'NO_ACTION': [
        "Ciao, come stai?",
        "Grazie per l'aiuto",
        "Ok, perfetto",
        "Capito, grazie",
        "Hello! How are you?",
        "Thanks, that's helpful",
        "Alright, got it",
        "Sure, no problem"
    ]
}
```

### **🤖 Option 3: Hybrid Dataset Creation**

#### **Strategia Combinata:**
1. **Base:** Dataset intent classification esistenti (30%)
2. **Synthetic:** Dati generati per memory actions (50%)  
3. **Real User Data:** Dati raccolti da utenti beta (20%)

#### **Pipeline di Creazione:**

```python
def create_hybrid_dataset():
    # 1. Load existing intent datasets
    atis_data = load_atis_adapted()
    snips_data = load_snips_adapted()
    
    # 2. Generate synthetic data
    synthetic_data = generate_synthetic_examples(
        num_samples=5000,
        languages=['it', 'en'],
        domains=['programming', 'devops', 'general']
    )
    
    # 3. Collect real user data (if available)
    real_data = collect_user_interactions()
    
    # 4. Combine and balance
    dataset = combine_and_balance([
        atis_data, snips_data, synthetic_data, real_data
    ])
    
    return dataset
```

## 🚀 **Training Pipeline Implementation**

### **Phase 1: Dataset Preparation**

```python
class AutoTriggerDatasetBuilder:
    def __init__(self):
        self.label_mapping = {
            'SAVE_MEMORY': 0,
            'SEARCH_MEMORY': 1, 
            'NO_ACTION': 2
        }
    
    def build_comprehensive_dataset(self, size=10000):
        """Build comprehensive training dataset"""
        
        # 1. Existing datasets (adapted)
        existing_data = self.load_and_adapt_existing_datasets()
        
        # 2. Synthetic generation
        synthetic_data = self.generate_synthetic_examples(size // 2)
        
        # 3. Technical content simulation
        technical_data = self.generate_technical_scenarios(size // 4)
        
        # 4. Conversational data
        conversation_data = self.generate_conversation_patterns(size // 4)
        
        # Combine all sources
        full_dataset = pd.concat([
            existing_data, synthetic_data, 
            technical_data, conversation_data
        ]).reset_index(drop=True)
        
        # Balance classes
        balanced_dataset = self.balance_classes(full_dataset)
        
        return balanced_dataset
    
    def generate_technical_scenarios(self, num_samples):
        """Generate technical programming/devops scenarios"""
        scenarios = []
        
        for _ in range(num_samples):
            scenario_type = random.choice(['bug_fix', 'configuration', 'tutorial', 'question'])
            
            if scenario_type == 'bug_fix':
                text = f"Fixed {random.choice(BUG_TYPES)} by {random.choice(SOLUTIONS)}"
                label = 'SAVE_MEMORY'
            elif scenario_type == 'configuration':
                text = f"Configuration for {random.choice(TECHNOLOGIES)}: {random.choice(CONFIG_EXAMPLES)}"
                label = 'SAVE_MEMORY'
            elif scenario_type == 'tutorial':
                text = f"How to {random.choice(ACTIONS)} in {random.choice(TECHNOLOGIES)}"
                label = 'SAVE_MEMORY'
            else:  # question
                text = f"How can I {random.choice(QUESTIONS)} with {random.choice(TECHNOLOGIES)}?"
                label = 'SEARCH_MEMORY'
                
            scenarios.append({'text': text, 'label': label})
        
        return pd.DataFrame(scenarios)
```

### **Phase 2: Model Training**

```python
class AutoTriggerTrainer:
    def __init__(self):
        self.model_name = "distilbert-base-uncased"
        self.num_labels = 3
        
    def prepare_model_and_tokenizer(self):
        """Prepare model and tokenizer for training"""
        
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            self.model_name,
            num_labels=self.num_labels,
            id2label={0: 'SAVE_MEMORY', 1: 'SEARCH_MEMORY', 2: 'NO_ACTION'},
            label2id={'SAVE_MEMORY': 0, 'SEARCH_MEMORY': 1, 'NO_ACTION': 2}
        )
    
    def train_model(self, dataset, output_dir="./auto-trigger-model"):
        """Train the auto-trigger model"""
        
        # Split dataset
        train_dataset, val_dataset = train_test_split(dataset, test_size=0.2)
        
        # Tokenize
        train_encodings = self.tokenizer(
            train_dataset['text'].tolist(),
            truncation=True, padding=True, max_length=512
        )
        val_encodings = self.tokenizer(
            val_dataset['text'].tolist(),
            truncation=True, padding=True, max_length=512
        )
        
        # Training arguments
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=3,
            per_device_train_batch_size=16,
            per_device_eval_batch_size=64,
            warmup_steps=500,
            weight_decay=0.01,
            logging_dir='./logs',
            evaluation_strategy="epoch",
            save_strategy="epoch",
            load_best_model_at_end=True,
            metric_for_best_model="eval_accuracy",
            push_to_hub=True,
            hub_model_id="pigrieco/mcp-memory-auto-trigger"
        )
        
        # Trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=AutoTriggerDataset(train_encodings, train_dataset['label']),
            eval_dataset=AutoTriggerDataset(val_encodings, val_dataset['label']),
            compute_metrics=self.compute_metrics
        )
        
        # Train
        trainer.train()
        
        # Push to hub
        trainer.push_to_hub("Auto-trigger model for MCP Memory Server")
        
        return trainer
```

## 🤗 **Hugging Face Deployment Strategy**

### **1. Model Repository Setup**

```bash
# Create Hugging Face repository
huggingface-cli repo create mcp-memory-auto-trigger --type model

# Clone repository  
git clone https://huggingface.co/pigrieco/mcp-memory-auto-trigger
cd mcp-memory-auto-trigger
```

### **2. Model Card (README.md)**

```markdown
---
language: 
- en
- it
license: mit
tags:
- text-classification
- intent-detection
- memory-management
- auto-trigger
datasets:
- custom
metrics:
- accuracy
- f1
model-index:
- name: mcp-memory-auto-trigger
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

This model automatically decides when to save or search information in a memory system based on conversational input.

### Classes:
- `SAVE_MEMORY`: Content should be saved to memory
- `SEARCH_MEMORY`: Should search existing memories  
- `NO_ACTION`: No memory action needed

## Usage

```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

tokenizer = AutoTokenizer.from_pretrained("pigrieco/mcp-memory-auto-trigger")
model = AutoModelForSequenceClassification.from_pretrained("pigrieco/mcp-memory-auto-trigger")

def predict_action(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
    
    probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)
    predicted_class_id = outputs.logits.argmax().item()
    confidence = probabilities[0][predicted_class_id].item()
    
    class_names = ['SAVE_MEMORY', 'SEARCH_MEMORY', 'NO_ACTION']
    return {
        'action': class_names[predicted_class_id],
        'confidence': confidence
    }

# Example
result = predict_action("Ricorda che per fixare i CORS devi aggiungere Access-Control-Allow-Origin")
print(result)  # {'action': 'SAVE_MEMORY', 'confidence': 0.95}
```
```

### **3. Hugging Face Spaces Demo**

```python
# spaces/app.py
import gradio as gr
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

# Load model
tokenizer = AutoTokenizer.from_pretrained("pigrieco/mcp-memory-auto-trigger")
model = AutoModelForSequenceClassification.from_pretrained("pigrieco/mcp-memory-auto-trigger")

def predict_memory_action(text):
    """Predict memory action for input text"""
    
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    
    with torch.no_grad():
        outputs = model(**inputs)
    
    probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)
    
    class_names = ['SAVE_MEMORY', 'SEARCH_MEMORY', 'NO_ACTION']
    confidences = {
        class_names[i]: float(probabilities[0][i])
        for i in range(len(class_names))
    }
    
    predicted_class_id = outputs.logits.argmax().item()
    predicted_action = class_names[predicted_class_id]
    confidence = confidences[predicted_action]
    
    # Create result text
    result_text = f"🎯 **Predicted Action:** {predicted_action}\n"
    result_text += f"🔮 **Confidence:** {confidence:.2%}\n\n"
    result_text += "📊 **All Probabilities:**\n"
    for action, prob in confidences.items():
        emoji = "💾" if action == "SAVE_MEMORY" else "🔍" if action == "SEARCH_MEMORY" else "⏸️"
        result_text += f"{emoji} {action}: {prob:.2%}\n"
    
    return result_text, confidences

# Gradio interface
with gr.Blocks(title="MCP Memory Auto-Trigger Demo") as demo:
    gr.Markdown("# 🧠 MCP Memory Auto-Trigger Demo")
    gr.Markdown("Enter text to see if it should trigger a memory save, search, or no action.")
    
    with gr.Row():
        with gr.Column():
            input_text = gr.Textbox(
                label="Input Text",
                placeholder="Enter your message here...",
                lines=3
            )
            submit_btn = gr.Button("🔍 Analyze", variant="primary")
            
        with gr.Column():
            result_text = gr.Textbox(label="Prediction Result", lines=8)
            confidence_plot = gr.BarPlot(
                x="action",
                y="confidence", 
                title="Confidence Scores",
                x_title="Memory Action",
                y_title="Confidence"
            )
    
    # Examples
    gr.Examples(
        examples=[
            ["Ricorda che per fixare i CORS devi aggiungere Access-Control-Allow-Origin"],
            ["Come posso gestire i timeout nel database?"],
            ["Ciao, come stai oggi?"],
            ["Ho risolto il bug aumentando il timeout a 30 secondi"],
            ["What's the best way to handle API errors?"]
        ],
        inputs=input_text
    )
    
    submit_btn.click(
        fn=predict_memory_action,
        inputs=input_text,
        outputs=[result_text, confidence_plot]
    )

demo.launch()
```

## 📈 **Implementation Roadmap**

### **Week 1: Dataset Creation**
- [ ] Implement synthetic data generation
- [ ] Adapt existing intent datasets
- [ ] Create technical scenarios
- [ ] Generate 10K+ training examples

### **Week 2: Model Training**  
- [ ] Fine-tune DistilBERT model
- [ ] Implement cross-validation
- [ ] Optimize hyperparameters
- [ ] Achieve >85% accuracy

### **Week 3: Deployment**
- [ ] Create Hugging Face model repository
- [ ] Deploy model to HF Hub
- [ ] Create interactive demo with Spaces
- [ ] Write comprehensive documentation

### **Week 4: Integration**
- [ ] Update MCP server to use HF model
- [ ] Implement model caching and optimization
- [ ] Add fallback mechanisms
- [ ] Deploy to production

## 🎯 **Next Steps**

1. **Immediate:** Implement dataset generation pipeline
2. **Short-term:** Train and deploy first model version
3. **Medium-term:** Collect real user data for improvement
4. **Long-term:** Implement advanced features (multi-user learning, adaptive thresholds)

**Ready to start implementation?** 🚀
