from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import torch  # runtime dep for HF model

app = FastAPI(
    title="MCP Memory Server - HTTP",
    version=os.getenv("APP_VERSION", "0.1.0"),
)

# Lazy-load HF model
_MODEL = None
_TOKENIZER = None
_CLASS_NAMES = ["SAVE_MEMORY", "SEARCH_MEMORY", "NO_ACTION"]  # order per model card

def _load_model():
    global _MODEL, _TOKENIZER
    if _MODEL is not None:
        return
    model_name = os.getenv("AUTO_TRIGGER_MODEL", "PiGrieco/mcp-memory-auto-trigger-model")
    try:
        from transformers import AutoTokenizer, AutoModelForSequenceClassification
    except Exception as e:
        raise RuntimeError(f"Missing ML deps: {e}. Install 'transformers' and 'torch'.")
    _TOKENIZER = AutoTokenizer.from_pretrained(model_name)
    _MODEL = AutoModelForSequenceClassification.from_pretrained(model_name)

class Message(BaseModel):
    role: str
    content: str

class AnalyzeRequest(BaseModel):
    messages: List[Message]
    scope: str = "last"   # "last" | "all"

class AnalyzeResponse(BaseModel):
    action: str
    confidence: float
    scope: str

@app.get("/health")
def health():
    loaded = _MODEL is not None
    return {
        "status": "ok",
        "model_loaded": loaded,
        "model_name": os.getenv("AUTO_TRIGGER_MODEL", "PiGrieco/mcp-memory-auto-trigger-model"),
    }

@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest):
    _load_model()
    text = req.messages[-1].content if req.scope == "last" else "\n".join(m.content for m in req.messages)
    inputs = _TOKENIZER(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        outputs = _MODEL(**inputs)
        probs = torch.nn.functional.softmax(outputs.logits, dim=-1)[0]
        idx = int(probs.argmax().item())
        conf = float(probs[idx].item())
    return AnalyzeResponse(action=_CLASS_NAMES[idx], confidence=conf, scope=req.scope)

class SaveRequest(BaseModel):
    key: str
    value: str
    metadata: Optional[Dict[str, Any]] = None

@app.post("/save")
def save_memory(_: SaveRequest):
    # Wire this to Mongo/embeddings when ready
    raise HTTPException(status_code=501, detail="Memory persistence not wired yet in 'main'.")

class SearchRequest(BaseModel):
    query: str
    top_k: int = 5

@app.post("/search")
def search_memory(_: SearchRequest):
    # Wire this to semantic search when ready
    raise HTTPException(status_code=501, detail="Semantic search not wired yet in 'main'.")
