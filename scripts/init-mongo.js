// MongoDB initialization script
db = db.getSiblingDB('memory_db');

// Create collection
db.createCollection('memories');

// Create indexes for optimal performance
db.memories.createIndex({ "project": 1 });
db.memories.createIndex({ "type": 1 });
db.memories.createIndex({ "created_at": -1 });
db.memories.createIndex({ "importance": -1 });
db.memories.createIndex({ 
    "project": 1, 
    "type": 1, 
    "created_at": -1 
});
db.memories.createIndex({ 
    "project": 1, 
    "importance": -1, 
    "created_at": -1 
});

// Text search index
db.memories.createIndex({ "text": "text" });

// Vector search index (for embeddings)
db.memories.createIndex({ "embedding": "2dsphere" });

print("MongoDB database initialized successfully!");
print("Collection 'memories' created with indexes."); 