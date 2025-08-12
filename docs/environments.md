# 🌍 **Environment Configurations - MCP Memory Server**

## 📖 **Overview**

The MCP Memory Server supports multiple environment configurations for different usage scenarios. Each environment has configurations optimized for its specific purpose.

## 🎯 **Available Environments**

### **1. Development**
- **Purpose**: Local development and debugging
- **File**: `config/environments/development.yaml`
- **Characteristics**:
  - Debug mode enabled
  - Verbose logging (DEBUG level)
  - Local cache only
  - Backups disabled
  - Notifications disabled
  - Development tools enabled

### **2. Testing**
- **Purpose**: Automated tests and CI/CD
- **File**: `config/environments/testing.yaml`
- **Characteristics**:
  - Complete isolation
  - Separate database
  - Cache disabled
  - Plugins disabled
  - Reduced timeouts
  - Automatic data cleanup

### **3. Staging**
- **Purpose**: Pre-production testing
- **File**: `config/environments/staging.yaml`
- **Characteristics**:
  - Production-like configuration
  - Limited notifications
  - Feature flags enabled
  - Performance testing enabled
  - Anonymized data

### **4. Production**
- **Purpose**: Production environment
- **File**: `config/environments/production.yaml`
- **Characteristics**:
  - Optimized performance
  - Maximum security
  - Complete monitoring
  - Automatic backup
  - High availability
  - Structured logging

## 🔧 **Environment Management**

### **Management Script**

The project includes a script to manage environments:

```bash
# List available environments
./scripts/manage_environments.sh list

# Show current environment
./scripts/manage_environments.sh current

# Switch to specific environment
./scripts/manage_environments.sh switch development
./scripts/manage_environments.sh switch production

# Validate environment configuration
./scripts/manage_environments.sh validate production

# Compare environments
./scripts/manage_environments.sh diff development production

# Create new environment
./scripts/manage_environments.sh create custom

# Backup and restore
./scripts/manage_environments.sh backup
./scripts/manage_environments.sh restore backup_file.yaml
```

### **Available Commands**

| Command | Description |
|---------|-------------|
| `list` | List all available environments |
| `current` | Show current environment |
| `switch <env>` | Switch to specified environment |
| `validate <env>` | Validate environment configuration |
| `backup` | Backup current environment |
| `restore <file>` | Restore environment from backup |
| `diff <env1> <env2>` | Compare two environments |
| `create <name>` | Create new environment |
| `delete <name>` | Remove custom environment |

## 📋 **Environment-Specific Configurations**

### **Development**

```yaml
# config/environments/development.yaml
environment:
  name: "development"
  debug: true
  log_level: "DEBUG"

server:
  host: "0.0.0.0"
  port: 8000
  reload: true
  workers: 1

database:
  mongodb:
    uri: "mongodb://localhost:27017"
    database: "mcp_memory_dev"
    collection: "memories"
    max_pool_size: 5
    min_pool_size: 1

memory:
  auto_save: true
  storage: "mongodb"
  ml_triggers: true
  trigger_threshold: 0.6
  min_text_length: 20
  max_text_length: 5000

embedding:
  model: "sentence-transformers/all-MiniLM-L6-v2"
  cache_enabled: false
  batch_size: 32

cache:
  enabled: true
  type: "memory"
  ttl: 3600

plugins:
  enabled: true
  auto_load: true
  plugins: ["memory_analytics"]

backup:
  enabled: false
  schedule: "0 2 * * *"
  retention_days: 7

notifications:
  enabled: false
  channels: ["email", "webhook"]

monitoring:
  enabled: true
  metrics: true
  health_checks: true
```

### **Testing**

```yaml
# config/environments/testing.yaml
environment:
  name: "testing"
  debug: false
  log_level: "WARNING"

server:
  host: "127.0.0.1"
  port: 8001
  reload: false
  workers: 1

database:
  mongodb:
    uri: "mongodb://localhost:27017"
    database: "mcp_memory_test"
    collection: "memories"
    max_pool_size: 2
    min_pool_size: 1

memory:
  auto_save: false
  storage: "mongodb"
  ml_triggers: false
  trigger_threshold: 0.8
  min_text_length: 10
  max_text_length: 1000

embedding:
  model: "sentence-transformers/all-MiniLM-L6-v2"
  cache_enabled: false
  batch_size: 16

cache:
  enabled: false
  type: "memory"
  ttl: 300

plugins:
  enabled: false
  auto_load: false
  plugins: []

backup:
  enabled: false
  schedule: "0 0 * * *"
  retention_days: 1

notifications:
  enabled: false
  channels: []

monitoring:
  enabled: false
  metrics: false
  health_checks: true
```

### **Staging**

```yaml
# config/environments/staging.yaml
environment:
  name: "staging"
  debug: false
  log_level: "INFO"

server:
  host: "0.0.0.0"
  port: 8000
  reload: false
  workers: 4

database:
  mongodb:
    uri: "mongodb://staging-mongo:27017"
    database: "mcp_memory_staging"
    collection: "memories"
    max_pool_size: 10
    min_pool_size: 2

memory:
  auto_save: true
  storage: "mongodb"
  ml_triggers: true
  trigger_threshold: 0.7
  min_text_length: 20
  max_text_length: 5000

embedding:
  model: "sentence-transformers/all-MiniLM-L6-v2"
  cache_enabled: true
  batch_size: 64

cache:
  enabled: true
  type: "redis"
  redis:
    host: "staging-redis"
    port: 6379
    db: 0
  ttl: 3600

plugins:
  enabled: true
  auto_load: true
  plugins: ["memory_analytics", "backup_manager"]

backup:
  enabled: true
  schedule: "0 2 * * *"
  retention_days: 30

notifications:
  enabled: true
  channels: ["webhook"]
  webhook_url: "https://staging-webhook.example.com"

monitoring:
  enabled: true
  metrics: true
  health_checks: true
```

### **Production**

```yaml
# config/environments/production.yaml
environment:
  name: "production"
  debug: false
  log_level: "WARNING"

server:
  host: "0.0.0.0"
  port: 8000
  reload: false
  workers: 8

database:
  mongodb:
    uri: "mongodb://prod-mongo:27017"
    database: "mcp_memory_prod"
    collection: "memories"
    max_pool_size: 20
    min_pool_size: 5

memory:
  auto_save: true
  storage: "mongodb"
  ml_triggers: true
  trigger_threshold: 0.6
  min_text_length: 20
  max_text_length: 10000

embedding:
  model: "sentence-transformers/all-MiniLM-L6-v2"
  cache_enabled: true
  batch_size: 128

cache:
  enabled: true
  type: "redis"
  redis:
    host: "prod-redis"
    port: 6379
    db: 0
    max_connections: 20
  ttl: 7200

plugins:
  enabled: true
  auto_load: true
  plugins: ["memory_analytics", "backup_manager", "notification_service"]

backup:
  enabled: true
  schedule: "0 2 * * *"
  retention_days: 90
  compression: true
  encryption: true

notifications:
  enabled: true
  channels: ["email", "webhook", "slack"]
  email:
    smtp_host: "smtp.production.com"
    smtp_port: 587
    username: "notifications@production.com"
  webhook_url: "https://webhook.production.com"
  slack_webhook: "https://hooks.slack.com/services/..."

monitoring:
  enabled: true
  metrics: true
  health_checks: true
  alerting: true
  prometheus: true
  grafana: true
```

## 🔄 **Environment Switching**

### **Automatic Switching**

The server automatically detects the environment based on:

1. **Environment Variable**: `ENVIRONMENT`
2. **Configuration File**: `config/settings.yaml`
3. **Default**: `development`

```bash
# Set environment variable
export ENVIRONMENT=production

# Start server
python main.py
```

### **Manual Switching**

```bash
# Switch to development
./scripts/manage_environments.sh switch development

# Switch to production
./scripts/manage_environments.sh switch production

# Verify current environment
./scripts/manage_environments.sh current
```

## 🔍 **Environment Validation**

### **Validation Process**

The environment management script validates configurations:

```bash
# Validate specific environment
./scripts/manage_environments.sh validate production

# Validate all environments
./scripts/manage_environments.sh validate all
```

### **Validation Checks**

1. **Configuration Structure**: Valid YAML format
2. **Required Fields**: All required fields present
3. **Field Types**: Correct data types
4. **Value Ranges**: Values within acceptable ranges
5. **Dependencies**: Required services configured
6. **Security**: Security settings appropriate

### **Validation Output**

```bash
✅ Environment 'development' is valid
✅ Environment 'testing' is valid
✅ Environment 'staging' is valid
✅ Environment 'production' is valid

All environments are valid!
```

## 📊 **Environment Comparison**

### **Compare Configurations**

```bash
# Compare development and production
./scripts/manage_environments.sh diff development production
```

### **Comparison Output**

```bash
Comparing development vs production:

🔧 Server Configuration:
  - workers: 1 → 8
  - reload: true → false

🗄️ Database Configuration:
  - database: mcp_memory_dev → mcp_memory_prod
  - max_pool_size: 5 → 20

🧠 Memory Configuration:
  - max_text_length: 5000 → 10000

⚡ Cache Configuration:
  - type: memory → redis
  - ttl: 3600 → 7200

🔌 Plugin Configuration:
  - plugins: ["memory_analytics"] → ["memory_analytics", "backup_manager", "notification_service"]
```

## 🛠️ **Custom Environments**

### **Creating Custom Environment**

```bash
# Create custom environment
./scripts/manage_environments.sh create custom_prod

# Edit custom environment
nano config/environments/custom_prod.yaml
```

### **Custom Environment Template**

```yaml
# config/environments/custom_prod.yaml
environment:
  name: "custom_prod"
  debug: false
  log_level: "INFO"

server:
  host: "0.0.0.0"
  port: 8000
  reload: false
  workers: 4

database:
  mongodb:
    uri: "mongodb://custom-mongo:27017"
    database: "mcp_memory_custom"
    collection: "memories"
    max_pool_size: 10
    min_pool_size: 2

# ... other configurations
```

## 🔒 **Security Considerations**

### **Environment-Specific Security**

1. **Development**: Minimal security for easy debugging
2. **Testing**: Isolated environment with test data
3. **Staging**: Production-like security with test data
4. **Production**: Maximum security with real data

### **Security Features**

```yaml
security:
  enabled: true
  auth_type: "jwt"  # or "basic"
  jwt_secret: "your-secret-key"
  session_timeout: 3600
  rate_limit:
    enabled: true
    requests_per_minute: 100
  cors:
    enabled: true
    origins: ["https://your-domain.com"]
    methods: ["GET", "POST", "PUT", "DELETE"]
```

## 📈 **Performance Tuning**

### **Environment-Specific Performance**

1. **Development**: Optimized for debugging
2. **Testing**: Optimized for speed
3. **Staging**: Production-like performance
4. **Production**: Maximum performance

### **Performance Settings**

```yaml
performance:
  cache:
    enabled: true
    ttl: 3600
    max_size: 1000
  database:
    connection_pool: 20
    query_timeout: 30
  embedding:
    batch_size: 128
    cache_enabled: true
  memory:
    max_concurrent_operations: 100
    operation_timeout: 60
```

## 🚨 **Troubleshooting**

### **Common Issues**

#### **1. Environment Not Found**
```bash
# Check available environments
./scripts/manage_environments.sh list

# Check current environment
./scripts/manage_environments.sh current
```

#### **2. Configuration Validation Failed**
```bash
# Validate configuration
./scripts/manage_environments.sh validate production

# Check configuration file
cat config/environments/production.yaml
```

#### **3. Environment Variable Issues**
```bash
# Check environment variable
echo $ENVIRONMENT

# Set environment variable
export ENVIRONMENT=development
```

### **Debug Commands**

```bash
# Show environment details
./scripts/manage_environments.sh info production

# Show configuration differences
./scripts/manage_environments.sh diff development production

# Backup and restore
./scripts/manage_environments.sh backup
./scripts/manage_environments.sh restore backup_2024-01-01.yaml
```

## 📚 **Best Practices**

### **1. Environment Management**
- Always validate configurations before switching
- Use descriptive environment names
- Keep environment files in version control
- Document environment-specific requirements

### **2. Security**
- Use different credentials for each environment
- Limit access to production configurations
- Regularly rotate secrets and keys
- Monitor environment access

### **3. Performance**
- Optimize configurations for each environment's purpose
- Monitor performance metrics
- Adjust settings based on usage patterns
- Plan for scaling

### **4. Maintenance**
- Regularly update environment configurations
- Clean up unused environments
- Backup important configurations
- Test environment switches

---

**For more information, see the [Configuration Guide](docs/configuration.md)** 