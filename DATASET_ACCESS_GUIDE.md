# 🔑 Dataset Access Guide & Setup Instructions

## 📋 **Complete Dataset List (All 10+ Sources)**

### **✅ Currently Available (No Permission Required)**

#### **1. ATIS** 
- **HF ID**: `atis_intents`
- **Size**: ~5,000 examples
- **Access**: ✅ Public
- **Usage**: `load_dataset("atis_intents")`

#### **2. BANKING77**
- **HF ID**: `banking77`
- **Size**: 13,083 examples  
- **Access**: ✅ Public
- **Usage**: `load_dataset("banking77")`

#### **3. SNIPS**
- **HF ID**: `snips_built_in_intents`
- **Size**: ~16,000 examples
- **Access**: ✅ Public
- **Usage**: `load_dataset("snips_built_in_intents")`

#### **4. CLINC150**
- **HF ID**: `clinc_oos`
- **Size**: 23,700 examples
- **Access**: ✅ Public
- **Usage**: `load_dataset("clinc_oos", "imbalanced")`
- **Note**: Requires config parameter

#### **5. HWU64**
- **HF ID**: `hwu_64`
- **Size**: 25,716 examples
- **Access**: ✅ Public
- **Usage**: `load_dataset("hwu_64")`

### **🔐 Requires Approval/Token (High Value)**

#### **6. MASSIVE (Amazon)**
- **HF ID**: `AmazonScience/massive`
- **Size**: 1M+ examples (51 languages!)
- **Access**: 🔐 Requires approval
- **Languages**: English, Italian + 49 others
- **Priority**: 🔥 VERY HIGH (multilingual, massive scale)
- **Request**: https://huggingface.co/datasets/AmazonScience/massive

#### **7. TOP (Facebook)**
- **HF ID**: `facebook/top_v2`
- **Size**: 44,873 examples
- **Access**: 🔐 May require approval
- **Features**: Compositional semantic parsing
- **Priority**: 🔥 HIGH

#### **8. MultiWOZ**
- **HF ID**: `multi_woz_v22`
- **Size**: 10,000+ dialogs (100K+ turns)
- **Access**: 🔐 May require approval
- **Features**: Multi-turn conversations
- **Priority**: 🔥 HIGH

### **🎯 Conversational (Public)**

#### **9. PersonaChat**
- **HF ID**: `persona_chat`
- **Size**: 164,356 utterances
- **Access**: ✅ Public
- **Usage**: `load_dataset("persona_chat")`

#### **10. DailyDialog**
- **HF ID**: `daily_dialog`
- **Size**: 13,118 dialogs
- **Access**: ✅ Public
- **Usage**: `load_dataset("daily_dialog")`

### **💻 Technical/Code (Large Scale)**

#### **11. CodeSearchNet**
- **HF ID**: `code_search_net`
- **Size**: 6M+ functions
- **Access**: ✅ Public
- **Features**: Code + documentation
- **Usage**: `load_dataset("code_search_net")`

#### **12. The Stack**
- **HF ID**: `bigcode/the-stack`
- **Size**: 6.4TB of code
- **Access**: 🔐 Requires agreement
- **Priority**: 🔥 MEDIUM (massive but specialized)

---

## 🚀 **Setup Instructions**

### **Step 1: Hugging Face Account Setup**

```bash
# Install Hugging Face CLI
pip install huggingface_hub

# Login to Hugging Face
huggingface-cli login
# Enter your token when prompted
```

### **Step 2: Token Configuration**

1. **Get HF Token**: https://huggingface.co/settings/tokens
2. **Create token** with `read` and `write` permissions
3. **Set environment variable**:

```bash
export HF_TOKEN="hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

### **Step 3: Request Dataset Access**

For datasets requiring approval:

#### **MASSIVE Dataset (Priority 1)**
1. Go to: https://huggingface.co/datasets/AmazonScience/massive
2. Click "Request Access"
3. Fill out the form:
   - **Purpose**: "Academic research on conversational AI auto-trigger systems"
   - **Organization**: "Independent Research"
   - **Use Case**: "Training intent classification model for memory management system"

#### **TOP Dataset**
1. Go to: https://huggingface.co/datasets/facebook/top_v2
2. Request access if required
3. Mention research purpose

#### **MultiWOZ Dataset**
1. Go to: https://huggingface.co/datasets/multi_woz_v22
2. Request access if required

---

## 📊 **Dataset Usage Strategy**

### **Phase 1: Public Datasets (Immediate)**
Target: 60K examples
```python
datasets_phase1 = [
    ("clinc_oos", 15000),
    ("banking77", 4000), 
    ("snips_built_in_intents", 3000),
    ("hwu_64", 2000),
    ("persona_chat", 1000),
    ("daily_dialog", 1000),
    ("synthetic", 35000)  # Fill remainder
]
```

### **Phase 2: With Approvals (Optimal)**
Target: 100K examples
```python
datasets_phase2 = [
    ("AmazonScience/massive", 25000),  # Multilingual boost
    ("facebook/top_v2", 5000),        # Compositional reasoning
    ("multi_woz_v22", 10000),         # Conversational context
    ("clinc_oos", 15000),
    ("banking77", 4000),
    ("snips_built_in_intents", 3000),
    ("synthetic", 38000)              # Fill remainder
]
```

---

## 🔧 **Implementation Scripts**

### **Test Dataset Access**

```python
#!/usr/bin/env python3
"""Test access to all datasets"""

from datasets import load_dataset
import os

# Set token
os.environ["HF_TOKEN"] = "your_token_here"

datasets_to_test = [
    # Public datasets
    ("atis_intents", "Public"),
    ("banking77", "Public"),
    ("snips_built_in_intents", "Public"), 
    ("clinc_oos", "Public"),
    ("hwu_64", "Public"),
    ("persona_chat", "Public"),
    ("daily_dialog", "Public"),
    
    # Approval required
    ("AmazonScience/massive", "Approval"),
    ("facebook/top_v2", "Approval"),
    ("multi_woz_v22", "Approval"),
]

for dataset_id, access_type in datasets_to_test:
    try:
        dataset = load_dataset(dataset_id)
        print(f"✅ {dataset_id} - Loaded successfully")
        print(f"   Splits: {list(dataset.keys())}")
        if 'train' in dataset:
            print(f"   Train size: {len(dataset['train']):,}")
    except Exception as e:
        print(f"❌ {dataset_id} - Failed: {e}")
    print()
```

### **Build Dataset Without Approvals**

```bash
# Run with public datasets only
python scripts/prepare_massive_dataset.py \
  --hf-token "your_token" \
  --target-size 60000 \
  --repo-name "mcp-memory-auto-trigger-dataset-v1"
```

### **Build Complete Dataset (With Approvals)**

```bash
# Run with all datasets
python scripts/prepare_massive_dataset.py \
  --hf-token "your_token" \
  --target-size 100000 \
  --repo-name "mcp-memory-auto-trigger-dataset-v2"
```

---

## 🎯 **Priority Action Plan**

### **Immediate (Today)**
1. ✅ **Setup HF account** and get token
2. ✅ **Test public datasets** with the script above
3. ✅ **Build 60K dataset** with public sources
4. ✅ **Upload to your HF profile**

### **Short Term (1-2 days)**
1. 🔐 **Request MASSIVE access** (most important)
2. 🔐 **Request TOP and MultiWOZ access**
3. ⏳ **Wait for approvals** (usually 1-3 days)

### **Once Approved (3-5 days)**
1. 📊 **Build complete 100K dataset**
2. 🚀 **Train on Google Colab A100**
3. 🤗 **Deploy model to Hugging Face**

---

## 💡 **Tips for Approval**

### **For MASSIVE Dataset:**
```
Subject: Research Access Request - Conversational AI Intent Classification

Dear Amazon Science Team,

I am requesting access to the MASSIVE dataset for academic research on 
conversational AI auto-trigger systems. 

Project: MCP Memory Server Auto-Trigger System
Purpose: Training multilingual intent classification models for automatic 
memory management in conversational interfaces.

The MASSIVE dataset's multilingual coverage (51 languages) and scale (1M+ examples) 
would significantly improve our model's capability to understand user intents 
across languages, particularly for memory save/search/no-action classification.

This is for open-source research with results published on Hugging Face Hub.

Thank you for considering this request.

Best regards,
[Your Name]
```

### **For Academic Datasets:**
- Mention "research" and "academic" purposes
- Specify the exact use case (intent classification)
- Promise to cite the dataset in publications
- Mention open-source nature of the project

---

## 🚨 **Backup Plan (If No Approvals)**

Even with just public datasets, we can still achieve excellent results:

### **60K Examples Distribution:**
- **CLINC150**: 15K (diverse intents)
- **Synthetic**: 35K (domain-specific) 
- **BANKING77**: 4K (financial domain)
- **SNIPS**: 3K (voice assistant)
- **HWU64**: 2K (IoT/tech domain)
- **PersonaChat**: 1K (casual conversation)

### **Expected Performance:**
- **Accuracy**: >87% (vs >90% with full dataset)
- **F1-Score**: >85% (vs >88% with full dataset)
- **Still excellent** for production use!

---

## ✅ **Ready to Start?**

1. **Get your HF token**: https://huggingface.co/settings/tokens
2. **Test dataset access**: Run the test script above
3. **Build initial dataset**: Use public datasets (60K examples)
4. **Request approvals**: While building, request access to premium datasets
5. **Train on Colab**: Use the provided notebook
6. **Deploy model**: Push to Hugging Face Hub

**Let's build the most comprehensive auto-trigger dataset! 🚀**
