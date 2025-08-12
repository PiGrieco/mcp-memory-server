db = db.getSiblingDB('mcp_memory_production');

// Create collections
db.createCollection('memories');
db.createCollection('analytics');
db.createCollection('backups');

// Create indexes
db.memories.createIndex({ "content": "text" });
db.memories.createIndex({ "project": 1 });
db.memories.createIndex({ "created_at": -1 });
db.memories.createIndex({ "user_id": 1 });

// Create user for the application
db.createUser({
  user: "mcp_user",
  pwd: "mcp_password",
  roles: [
    { role: "readWrite", db: "mcp_memory_production" }
  ]
});

print("MongoDB initialization completed");
