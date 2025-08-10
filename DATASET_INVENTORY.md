# 📊 Complete Dataset Inventory for Auto-Trigger Training

## 🎯 **Target: 100K+ Training Examples**

Distribution plan:
- **Synthetic Data**: 60K examples (60%)
- **Existing Datasets**: 35K examples (35%) 
- **Real User Data**: 5K examples (5%)

---

## 📋 **Available Intent Classification Datasets**

### **1. Core Datasets (Currently Integrated)**

#### **ATIS (Airline Travel Information System)**
- **Source**: `atis_intents` on Hugging Face
- **Size**: ~5,000 examples
- **Classes**: 21 intents
- **Language**: English
- **Quality**: High (human-annotated)
- **Usage**: Travel → Memory operations mapping
- **Status**: ✅ Implemented in dataset_builder.py

#### **BANKING77**
- **Source**: `banking77` on Hugging Face  
- **Size**: 13,083 examples
- **Classes**: 77 banking intents
- **Language**: English
- **Quality**: High (banking domain)
- **Usage**: Banking queries → Memory operations
- **Status**: ✅ Implemented in dataset_builder.py

#### **SNIPS NLU**
- **Source**: `snips_built_in_intents` on Hugging Face
- **Size**: ~16,000 examples
- **Classes**: 7 intents + slots
- **Language**: English
- **Quality**: Very High (voice assistants)
- **Usage**: Assistant intents → Memory triggers
- **Status**: ✅ Implemented in dataset_builder.py

#### **Synthetic Generation**
- **Source**: Custom SyntheticDataGenerator
- **Size**: Configurable (10K-50K+)
- **Classes**: 3 (SAVE_MEMORY, SEARCH_MEMORY, NO_ACTION)
- **Languages**: English, Italian
- **Quality**: High (template-based)
- **Usage**: Domain-specific memory triggers
- **Status**: ✅ Implemented in dataset_builder.py

---

## 🆕 **Additional Datasets to Integrate**

### **2. Large-Scale Intent Datasets**

#### **CLINC150** 
- **Source**: Facebook's Conversational AI dataset
- **Size**: 23,700 examples
- **Classes**: 150 intents across 10 domains
- **Language**: English
- **Quality**: Very High
- **Domains**: Banking, Travel, Utility, Work, Auto, etc.
- **HF Dataset**: `clinc_oos`
- **Priority**: 🔥 HIGH (large, diverse)

#### **TOP (Task-Oriented Parsing)**
- **Source**: Facebook Research
- **Size**: 44,873 examples
- **Classes**: 25+ intents
- **Language**: English
- **Quality**: Very High (compositional)
- **Features**: Complex nested intents
- **HF Dataset**: `facebook/top_v2`
- **Priority**: 🔥 HIGH (compositional reasoning)

#### **HWU64 (Hu et al.)**
- **Source**: Cambridge University
- **Size**: 25,716 examples
- **Classes**: 64 intents across 21 domains
- **Language**: English
- **Quality**: High (academic)
- **Domains**: IoT, News, Social, etc.
- **HF Dataset**: `hwu_64`
- **Priority**: 🔥 MEDIUM (good coverage)

#### **MultiWOZ 2.1**
- **Source**: Cambridge University
- **Size**: 10,000+ dialogs (100K+ turns)
- **Classes**: Multiple domains/intents
- **Language**: English
- **Quality**: Very High (multi-turn)
- **Features**: Context-aware conversations
- **HF Dataset**: `multi_woz_v22`
- **Priority**: 🔥 HIGH (conversational context)

### **3. Multilingual Datasets**

#### **MASSIVE (Amazon)**
- **Source**: Amazon Alexa
- **Size**: 1M+ examples
- **Classes**: 60 intents
- **Languages**: 51 languages (including Italian!)
- **Quality**: Very High
- **HF Dataset**: `AmazonScience/massive`
- **Priority**: 🔥 VERY HIGH (multilingual, massive scale)

#### **CrossNER**
- **Source**: Multilingual NER
- **Size**: 280K+ examples
- **Languages**: English, Spanish, Dutch, Chinese
- **Quality**: High
- **Features**: Cross-domain entities
- **HF Dataset**: `cross_ner`
- **Priority**: 🔥 MEDIUM (entity recognition)

### **4. Conversational & Dialog Datasets**

#### **PersonaChat**
- **Source**: Facebook Research
- **Size**: 164,356 utterances
- **Classes**: Conversational responses
- **Language**: English
- **Quality**: High
- **Features**: Personality-based conversations
- **HF Dataset**: `persona_chat`
- **Priority**: 🔥 MEDIUM (casual conversation patterns)

#### **DailyDialog**
- **Source**: Academic
- **Size**: 13,118 dialogs
- **Classes**: Daily conversation topics
- **Language**: English
- **Quality**: High
- **Features**: Multi-turn daily conversations
- **HF Dataset**: `daily_dialog`
- **Priority**: 🔥 MEDIUM (natural conversations)

### **5. Technical/Programming Datasets**

#### **CodeSearchNet**
- **Source**: GitHub
- **Size**: 6M+ functions
- **Classes**: Programming languages
- **Language**: Code + English comments
- **Quality**: High
- **Features**: Code documentation patterns
- **HF Dataset**: `code_search_net`
- **Priority**: 🔥 HIGH (technical content)

#### **The Stack**
- **Source**: BigCode
- **Size**: 6.4TB of code
- **Classes**: Programming languages
- **Language**: Code + comments
- **Quality**: Very High
- **Features**: Massive code repository
- **HF Dataset**: `bigcode/the-stack`
- **Priority**: 🔥 MEDIUM (code patterns)

---

## 🚀 **Implementation Plan**

### **Phase 1: Core Integration (Week 1)**
1. ✅ ATIS - Already integrated
2. ✅ BANKING77 - Already integrated  
3. ✅ SNIPS - Already integrated
4. 🔄 **CLINC150** - High priority addition
5. 🔄 **MASSIVE** - Multilingual support

**Target**: 60K examples

### **Phase 2: Scale-Up (Week 2)**
1. 🔄 **TOP Dataset** - Complex intents
2. 🔄 **MultiWOZ** - Conversational context
3. 🔄 **PersonaChat** - Casual conversation
4. 🔄 **DailyDialog** - Natural dialog patterns

**Target**: 80K examples

### **Phase 3: Specialization (Week 3)**
1. 🔄 **CodeSearchNet** - Technical content
2. 🔄 **HWU64** - Additional intent coverage
3. 🔄 **Enhanced Synthetic** - Domain-specific templates
4. 🔄 **Real User Data** - Beta user interactions

**Target**: 100K+ examples

---

## 🔧 **Dataset Integration Architecture**

### **Enhanced Dataset Builder**

```python
class ComprehensiveDatasetBuilder:
    """Enhanced builder for 100K+ examples"""
    
    def __init__(self):
        self.dataset_loaders = {
            # Core datasets (implemented)
            'atis': self.load_atis,
            'banking77': self.load_banking77, 
            'snips': self.load_snips,
            
            # New large-scale datasets
            'clinc150': self.load_clinc150,
            'massive': self.load_massive,
            'top': self.load_top,
            'multiwoz': self.load_multiwoz,
            
            # Conversational datasets
            'persona_chat': self.load_persona_chat,
            'daily_dialog': self.load_daily_dialog,
            
            # Technical datasets
            'code_search_net': self.load_code_search_net,
            'hwu64': self.load_hwu64,
            
            # Synthetic generation
            'synthetic': self.generate_synthetic
        }
    
    def build_massive_dataset(self, target_size=100000):
        """Build 100K+ training dataset"""
        
        # Distribution plan
        distribution = {
            'synthetic': 0.60,        # 60K synthetic
            'clinc150': 0.15,         # 15K from CLINC150
            'massive': 0.10,          # 10K from MASSIVE  
            'multiwoz': 0.05,         # 5K from MultiWOZ
            'banking77': 0.04,        # 4K from BANKING77
            'snips': 0.03,            # 3K from SNIPS
            'top': 0.02,              # 2K from TOP
            'persona_chat': 0.01      # 1K from PersonaChat
        }
        
        all_examples = []
        
        for dataset_name, ratio in distribution.items():
            target_samples = int(target_size * ratio)
            loader = self.dataset_loaders[dataset_name]
            examples = loader(target_samples)
            all_examples.extend(examples)
            
        return self.balance_and_split(all_examples)
```

### **Smart Intent Mapping**

```python
class IntentMapper:
    """Advanced intent mapping for multiple datasets"""
    
    def __init__(self):
        self.mapping_rules = {
            # SAVE_MEMORY patterns
            'save_triggers': [
                'add_to_playlist', 'create_reminder', 'book_restaurant',
                'transfer_money', 'make_payment', 'set_alarm',
                'create_account', 'update_profile', 'save_contact',
                # CLINC150 intents
                'create_list', 'reminder', 'calendar_set',
                # MASSIVE intents  
                'takeaway_order', 'recommendation_events'
            ],
            
            # SEARCH_MEMORY patterns
            'search_triggers': [
                'search_music', 'find_restaurant', 'get_weather',
                'balance_inquiry', 'transaction_history', 'find_flight',
                'play_music', 'search_creative_work', 'query_contact',
                # CLINC150 intents
                'restaurant_reviews', 'flight_status', 'find_phone',
                # MASSIVE intents
                'weather_query', 'music_query', 'general_quirky'
            ],
            
            # NO_ACTION patterns  
            'no_action_triggers': [
                'greetings', 'goodbye', 'thank_you', 'affirmation',
                'negation', 'maybe', 'unknown', 'out_of_scope',
                # Conversational
                'small_talk', 'personal_chat', 'casual_conversation'
            ]
        }
```

---

## 📈 **Expected Performance**

### **With 100K+ Examples:**
- **Accuracy**: >90%
- **F1-Score**: >88%
- **Multilingual**: English + Italian support
- **Domain Coverage**: 15+ domains
- **Robustness**: High variance in input patterns

### **Model Capabilities:**
- **Technical Content**: Code, documentation, tutorials
- **Conversational**: Natural dialog understanding  
- **Multilingual**: Cross-language generalization
- **Domain Transfer**: Banking → Programming → General

---

## 🔑 **Required Access & Setup**

### **Hugging Face Hub:**
1. **Account Setup**: Personal HF account with datasets access
2. **Dataset Access**: Some datasets may require approval
3. **Storage**: Hub storage for our compiled dataset
4. **API Tokens**: For programmatic access

### **Google Colab Pro:**
1. **A100 GPU**: For fast training (8-12 hours for 100K examples)
2. **High RAM**: 25GB+ for large dataset processing
3. **Drive Storage**: 15GB+ for dataset caching

### **Permissions Needed:**
```bash
# HF Token with read/write access
export HF_TOKEN="hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# Datasets that may need approval:
# - MASSIVE (Amazon)
# - The Stack (BigCode)  
# - Some academic datasets
```

---

## 🚀 **Next Steps**

### **Immediate Actions:**
1. **Setup HF Account** with dataset access permissions
2. **Implement Enhanced Dataset Builder** with all datasets
3. **Create 100K Dataset** and upload to your HF profile
4. **Setup Colab Training Environment** with A100

### **Implementation Order:**
1. **Dataset Integration** (2-3 days)
2. **Dataset Compilation** (1 day)
3. **HF Upload** (1 day)  
4. **Colab Training Setup** (1 day)
5. **Model Training** (1 day)
6. **Model Deployment** (1 day)

**Ready to start with dataset integration?** 🚀
