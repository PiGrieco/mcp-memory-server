# Watchdog Service - Auto-Restart on Keywords

The MCP Memory Server includes a powerful **Watchdog Service** that automatically restarts the server when deterministic keywords are detected in user input.

## 🎯 Overview

The Watchdog Service monitors for specific keywords that indicate the user wants to interact with the memory system. When these keywords are detected, it automatically restarts the server to ensure it's available for processing.

## 🚀 Quick Start

```bash
# Start server with watchdog (auto-restart on keywords)
./scripts/main.sh server watchdog

# Alternative command
./scripts/servers/start_server_with_watchdog.sh
```

## 🔑 Deterministic Keywords

The watchdog monitors for these trigger words:

### Italian Keywords
- `ricorda` - remember
- `importante` - important
- `nota` - note
- `salva` - save
- `memorizza` - memorize
- `riavvia` - restart

### English Keywords
- `remember` - remember something
- `save` - save something
- `note` - take a note
- `important` - mark as important
- `store` - store information
- `restart` - restart server

### Direct Commands
- `mcp start` - start MCP server
- `server start` - start server
- `wake up` - wake up server
- `restart server` - restart server

### Urgent Commands (faster restart)
- `emergency restart` - immediate restart
- `force restart` - force restart
- `restart now` - restart immediately

## 🛠️ How It Works

1. **Monitoring**: The watchdog service monitors stdin and optionally a trigger file
2. **Detection**: When keywords are detected, it analyzes the message
3. **Rate Limiting**: Prevents spam restarts with cooldown periods
4. **Restart**: Gracefully stops and restarts the server process
5. **Logging**: All actions are logged for debugging

## 📁 File Structure

```
logs/
├── watchdog.log          # Watchdog service logs
└── restart_triggers.txt  # Optional trigger file

src/services/
└── watchdog_service.py   # Main watchdog implementation

scripts/servers/
└── start_server_with_watchdog.sh  # Startup script
```

## ⚙️ Configuration

The watchdog can be configured via `WatchdogConfig`:

```python
config = WatchdogConfig(
    monitor_stdin=True,           # Monitor stdin input
    monitor_file=None,            # Optional file to monitor
    restart_script="main.py",     # Script to restart
    restart_delay=2.0,           # Delay before restart
    cooldown_period=30.0,        # Cooldown between restarts
    max_restarts_per_hour=10     # Rate limiting
)
```

## 📊 Rate Limiting

To prevent abuse, the watchdog includes rate limiting:

- **Maximum restarts**: 10 per hour by default
- **Cooldown period**: 30 seconds between restarts
- **Urgent restarts**: Bypass some delays but still rate limited

## 🔍 Monitoring Options

### 1. stdin Monitoring (Default)
```bash
# Type keywords directly in terminal
./scripts/main.sh server watchdog
# Then type: "ricorda questo" or "remember this"
```

### 2. File Monitoring
```bash
# Monitor a specific file for keywords
python3 -m src.services.watchdog_service --monitor-file /path/to/trigger.txt
```

### 3. Hybrid Monitoring
```bash
# Monitor both stdin and file
python3 -m src.services.watchdog_service --monitor-file logs/restart_triggers.txt
```

## 📝 Usage Examples

### Basic Usage
```bash
# Start watchdog service
./scripts/main.sh server watchdog

# In another terminal or the same terminal, type:
ricorda questa soluzione  # Italian - triggers restart
remember this solution    # English - triggers restart
restart server           # Direct command - triggers restart
```

### File-based Triggering
```bash
# Start with file monitoring
python3 -m src.services.watchdog_service --monitor-file triggers.txt

# In another terminal:
echo "ricorda questo" >> triggers.txt  # Triggers restart
echo "important note" >> triggers.txt  # Triggers restart
```

### Urgent Restart
```bash
# Type urgent commands for faster restart
emergency restart  # Restarts in 0.5 seconds instead of 2.0
force restart     # Immediate restart
restart now       # Immediate restart
```

## 🔧 Integration with Main Server

The watchdog integrates seamlessly with the main MCP server:

1. **Graceful Shutdown**: Uses SIGTERM for clean shutdown
2. **Process Management**: Tracks server PID and status
3. **Environment Setup**: Maintains Python path and environment
4. **Error Handling**: Logs errors and continues monitoring

## 📊 Logging

All watchdog activity is logged to `logs/watchdog.log`:

```
2024-01-15 10:30:00 - watchdog_service - INFO - 🐕 Starting Watchdog Service
2024-01-15 10:30:01 - watchdog_service - INFO - 👂 Monitoring stdin for restart keywords...
2024-01-15 10:30:05 - watchdog_service - INFO - 🔥 Restart trigger detected: keywords: ricorda
2024-01-15 10:30:05 - watchdog_service - INFO - 🚀 Initiating restart (delay: 2.0s)
2024-01-15 10:30:07 - watchdog_service - INFO - ✅ Server restart completed successfully
```

## 🚨 Troubleshooting

### Common Issues

1. **Server won't restart**
   - Check MongoDB is running
   - Verify Python environment
   - Check logs in `logs/watchdog.log`

2. **Keywords not detected**
   - Ensure exact keyword match
   - Check case sensitivity
   - Verify stdin monitoring is active

3. **Rate limiting**
   - Wait for cooldown period
   - Check `max_restarts_per_hour` setting
   - Review restart history in logs

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
./scripts/main.sh server watchdog
```

## 🎯 Use Cases

### 1. Development Workflow
- Server crashes during development
- Type "restart server" to quickly get back up
- Automatic recovery without manual intervention

### 2. Interactive Sessions
- User mentions wanting to save something important
- Type "ricorda questo" to ensure server is ready
- Seamless user experience

### 3. Remote Monitoring
- Use file monitoring for remote triggers
- Script can append to trigger file
- Automated restart based on external conditions

### 4. Emergency Recovery
- Server becomes unresponsive
- Use "emergency restart" for immediate recovery
- Faster response than manual restart

## 🔐 Security Considerations

- **Input Validation**: All input is validated before processing
- **Rate Limiting**: Prevents restart spam attacks
- **Process Isolation**: Watchdog runs separately from main server
- **Logging**: All actions are logged for audit trails

## 🚀 Advanced Usage

### Custom Keyword Detection
```python
# Extend KeywordDetector for custom keywords
class CustomKeywordDetector(KeywordDetector):
    def __init__(self):
        super().__init__()
        self.restart_keywords.extend([
            'custom_keyword',
            'special_trigger'
        ])
```

### Integration with Other Services
```python
# Use watchdog service in other applications
from src.services.watchdog_service import create_watchdog_service

watchdog = await create_watchdog_service(
    monitor_stdin=False,
    monitor_file="/app/triggers.txt"
)
await watchdog.start()
```

## 📈 Performance

- **Low overhead**: Minimal CPU usage when monitoring
- **Fast restart**: Typical restart time 2-5 seconds
- **Efficient monitoring**: Uses async I/O for scalability
- **Memory efficient**: Small memory footprint

The Watchdog Service ensures your MCP Memory Server is always ready to capture important information, providing a seamless and intelligent user experience.
