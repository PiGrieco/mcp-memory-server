# Replit + MCP Memory Server Setup

## Method 1: Cloud Deployment on Replit

### Step 1: Import Project to Replit
1. Go to [Replit.com](https://replit.com)
2. Click "Create Repl"
3. Choose "Import from GitHub"
4. Use: `https://github.com/AiGotsrl/mcp-memory-server`

### Step 2: Configure Replit Environment

Create `.replit` file:
```toml
run = "python main.py"
entrypoint = "main.py"

[nix]
channel = "stable-22_11"

[env]
MONGODB_URL = "your-mongodb-cloud-url"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
LOG_LEVEL = "INFO"
PYTHONPATH = "/home/runner/mcp-memory-server/src"

[deployment]
run = ["sh", "-c", "python main.py"]
deploymentTarget = "cloudrun"
```

### Step 3: Setup MongoDB Cloud
Since Replit doesn't support Docker, use MongoDB Atlas:

1. Go to [MongoDB Atlas](https://cloud.mongodb.com)
2. Create free cluster
3. Get connection string
4. Add to Replit Secrets:
   - Key: `MONGODB_URL`
   - Value: `mongodb+srv://username:password@cluster.mongodb.net/memory_db`

### Step 4: Install Dependencies
Create `replit.nix`:
```nix
{ pkgs }: {
  deps = [
    pkgs.python310Full
    pkgs.python310Packages.pip
    pkgs.python310Packages.setuptools
    pkgs.python310Packages.wheel
  ];
}
```

### Step 5: Configure for Production
Update `requirements-replit.txt`:
```
# Core MCP
mcp>=1.0.0

# Database (cloud-ready)
pymongo>=4.5.0
dnspython>=2.3.0

# Embedding Models (lightweight)
sentence-transformers>=2.2.0
torch>=2.0.0
transformers>=4.30.0

# Data Validation
pydantic>=2.0.0

# Utilities
numpy>=1.24.0
python-dotenv>=1.0.0

# Production web server
uvicorn>=0.23.0
fastapi>=0.100.0
```

### Step 6: Test Installation
```bash
python -m pip install -r requirements-replit.txt
python main.py
```

## Method 2: Replit AI Integration

### Step 1: Create Replit Plugin
Create `replit_plugin.py`:

```python
import requests
import json
from typing import Dict, List, Optional

class ReplitMemoryPlugin:
    def __init__(self, repl_url: str):
        self.base_url = repl_url.rstrip('/')
        self.project = "replit"
    
    async def save_memory(self, text: str, memory_type: str = "code") -> Dict:
        """Save memory to MCP server"""
        try:
            response = requests.post(f"{self.base_url}/save", json={
                "text": text,
                "memory_type": memory_type,
                "project": self.project,
                "importance": 0.7
            })
            return response.json()
        except Exception as e:
            print(f"Failed to save memory: {e}")
            return {"success": False, "error": str(e)}
    
    async def search_memory(self, query: str) -> Dict:
        """Search memories"""
        try:
            response = requests.post(f"{self.base_url}/search", json={
                "query": query,
                "project": self.project,
                "limit": 5
            })
            return response.json()
        except Exception as e:
            print(f"Failed to search memory: {e}")
            return {"success": False, "memories": []}

# Replit AI Hook
if hasattr(__builtins__, 'replit'):
    # Hook into Replit's AI system
    memory_plugin = ReplitMemoryPlugin("https://your-repl-name.username.repl.co")
    
    # Save code context automatically
    def on_code_change(file_path: str, content: str):
        memory_plugin.save_memory(
            f"File {file_path} contains: {content[:500]}...",
            "code_context"
        )
    
    # Enhance AI suggestions with memory
    def enhance_ai_prompt(original_prompt: str) -> str:
        memories = memory_plugin.search_memory(original_prompt)
        if memories.get("success") and memories.get("data", {}).get("memories"):
            context = "\n".join([m["text"] for m in memories["data"]["memories"][:3]])
            return f"{original_prompt}\n\nRelevant context:\n{context}"
        return original_prompt
```

### Step 3: Usage in Replit
```python
# In your Replit files
from replit_plugin import ReplitMemoryPlugin

memory = ReplitMemoryPlugin("https://your-repl.repl.co")

# Save important code patterns
await memory.save_memory("This React hook handles authentication", "pattern")

# Search for solutions
results = await memory.search_memory("React authentication")
```

## Method 3: Replit Database Integration

For simpler setup, use Replit's built-in database:

```python
# replit_simple.py
from replit import db
import json
from sentence_transformers import SentenceTransformer

class ReplitSimpleMemory:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
    
    def save_memory(self, text: str, memory_type: str = "note"):
        embedding = self.model.encode(text).tolist()
        memory_id = f"memory_{len(db.keys())}"
        
        db[memory_id] = {
            "text": text,
            "type": memory_type,
            "embedding": embedding,
            "timestamp": time.time()
        }
        return memory_id
    
    def search_memory(self, query: str, limit: int = 5):
        query_embedding = self.model.encode(query)
        results = []
        
        for key in db.keys():
            if key.startswith("memory_"):
                memory = db[key]
                similarity = cosine_similarity([query_embedding], [memory["embedding"]])[0][0]
                if similarity > 0.3:  # Threshold
                    results.append({
                        "text": memory["text"],
                        "type": memory["type"],
                        "similarity": float(similarity)
                    })
        
        return sorted(results, key=lambda x: x["similarity"], reverse=True)[:limit]

# Usage
memory = ReplitSimpleMemory()
memory.save_memory("Python list comprehensions are powerful", "tip")
results = memory.search_memory("Python lists")
```

## Deployment URLs

After deployment, your Replit will be available at:
- **Development**: `https://repl-name.username.repl.co`
- **Production**: `https://repl-name--username.repl.co`

## Testing Integration

```bash
# Test health endpoint
curl https://your-repl.repl.co/health

# Test save memory
curl -X POST https://your-repl.repl.co/save \
  -H "Content-Type: application/json" \
  -d '{"text": "Test memory", "project": "replit"}'

# Test search
curl -X POST https://your-repl.repl.co/search \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "project": "replit"}'
``` 