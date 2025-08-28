"""
Watchdog Service for Auto-Restart on Deterministic Keywords
Monitors for deterministic keywords and restarts the server when detected
"""

import asyncio
import os
import signal
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass

from ..utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class WatchdogConfig:
    """Configuration for watchdog service"""
    monitor_file: Optional[str] = None  # File to monitor for input
    monitor_stdin: bool = True  # Monitor stdin
    restart_script: str = "main.py"  # Script to restart
    restart_delay: float = 2.0  # Delay before restart
    cooldown_period: float = 30.0  # Cooldown between restarts
    max_restarts_per_hour: int = 10  # Rate limiting
    log_file: str = "logs/watchdog.log"


class KeywordDetector:
    """Detects deterministic keywords for restart triggers"""
    
    def __init__(self):
        # Core deterministic keywords that should trigger restart
        self.restart_keywords = [
            # Italian
            'ricorda', 'importante', 'nota', 'salva', 'memorizza',
            'riavvia', 'restart', 'ripartire', 'ricomincia',
            
            # English  
            'remember', 'save', 'note', 'important', 'store',
            'restart', 'reboot', 'start again', 'wake up',
            
            # Commands
            'mcp start', 'server start', 'memory start',
            'attiva server', 'avvia server'
        ]
        
        # Patterns that indicate urgent restart need
        self.urgent_patterns = [
            'emergency restart', 'force restart', 'restart now',
            'riavvio di emergenza', 'riavvio forzato', 'riavvia subito'
        ]
    
    def should_restart(self, message: str) -> Dict[str, any]:
        """Check if message contains restart triggers"""
        message_lower = message.lower().strip()
        
        # Check for urgent patterns first
        for pattern in self.urgent_patterns:
            if pattern in message_lower:
                return {
                    "should_restart": True,
                    "reason": f"urgent_pattern: {pattern}",
                    "priority": "high",
                    "delay": 0.5  # Fast restart for urgent
                }
        
        # Check for regular restart keywords
        triggered_keywords = []
        for keyword in self.restart_keywords:
            if keyword in message_lower:
                triggered_keywords.append(keyword)
        
        if triggered_keywords:
            return {
                "should_restart": True,
                "reason": f"keywords: {', '.join(triggered_keywords)}",
                "priority": "normal",
                "delay": 2.0,
                "keywords": triggered_keywords
            }
        
        return {"should_restart": False}


class ServerProcess:
    """Manages the server process lifecycle"""
    
    def __init__(self, script_path: str, project_root: str):
        self.script_path = script_path
        self.project_root = project_root
        self.process: Optional[subprocess.Popen] = None
        self.start_time: Optional[datetime] = None
        
    def is_running(self) -> bool:
        """Check if server process is running"""
        if self.process is None:
            return False
        return self.process.poll() is None
    
    async def start(self) -> bool:
        """Start the server process"""
        if self.is_running():
            logger.warning("Server process is already running")
            return True
        
        try:
            logger.info(f"🚀 Starting server: {self.script_path}")
            
            # Set up environment
            env = os.environ.copy()
            env['PYTHONPATH'] = f"{self.project_root}:{env.get('PYTHONPATH', '')}"
            
            # Start process
            self.process = subprocess.Popen(
                [sys.executable, self.script_path],
                cwd=self.project_root,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE
            )
            
            self.start_time = datetime.now()
            
            # Give it a moment to start
            await asyncio.sleep(1)
            
            if self.is_running():
                logger.info(f"✅ Server started successfully (PID: {self.process.pid})")
                return True
            else:
                logger.error("❌ Server failed to start")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error starting server: {e}")
            return False
    
    async def stop(self) -> bool:
        """Stop the server process"""
        if not self.is_running():
            return True
        
        try:
            logger.info(f"🛑 Stopping server (PID: {self.process.pid})")
            
            # Try graceful shutdown first
            self.process.send_signal(signal.SIGTERM)
            
            # Wait for graceful shutdown
            try:
                await asyncio.wait_for(
                    asyncio.create_task(self._wait_for_exit()),
                    timeout=5.0
                )
                logger.info("✅ Server stopped gracefully")
                return True
            except asyncio.TimeoutError:
                # Force kill if graceful shutdown fails
                logger.warning("⚠️ Graceful shutdown timeout, forcing kill")
                self.process.kill()
                await self._wait_for_exit()
                logger.info("✅ Server force stopped")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error stopping server: {e}")
            return False
    
    async def restart(self, delay: float = 2.0) -> bool:
        """Restart the server process"""
        logger.info(f"🔄 Restarting server (delay: {delay}s)")
        
        # Stop current process
        if self.is_running():
            await self.stop()
        
        # Wait for delay
        if delay > 0:
            await asyncio.sleep(delay)
        
        # Start new process
        return await self.start()
    
    async def _wait_for_exit(self):
        """Wait for process to exit (async wrapper)"""
        while self.process.poll() is None:
            await asyncio.sleep(0.1)


class RestartRateLimiter:
    """Rate limits restart attempts to prevent spam"""
    
    def __init__(self, max_restarts: int = 10, window_hours: int = 1):
        self.max_restarts = max_restarts
        self.window_hours = window_hours
        self.restart_history: List[datetime] = []
    
    def can_restart(self) -> bool:
        """Check if restart is allowed within rate limits"""
        now = datetime.now()
        cutoff = now - timedelta(hours=self.window_hours)
        
        # Remove old entries
        self.restart_history = [
            restart_time for restart_time in self.restart_history
            if restart_time > cutoff
        ]
        
        return len(self.restart_history) < self.max_restarts
    
    def record_restart(self):
        """Record a restart attempt"""
        self.restart_history.append(datetime.now())


class WatchdogService:
    """Main watchdog service that monitors and restarts server"""
    
    def __init__(self, config: WatchdogConfig = None):
        self.config = config or WatchdogConfig()
        self.keyword_detector = KeywordDetector()
        self.rate_limiter = RestartRateLimiter(
            max_restarts=self.config.max_restarts_per_hour
        )
        
        # Set up project paths
        project_root = str(Path(__file__).parent.parent.parent)
        self.server_process = ServerProcess(
            script_path=os.path.join(project_root, self.config.restart_script),
            project_root=project_root
        )
        
        self.running = False
        self.last_restart = None
        
        # Set up logging
        self._setup_logging()
    
    def _setup_logging(self):
        """Set up watchdog-specific logging"""
        log_dir = Path(self.config.log_file).parent
        log_dir.mkdir(exist_ok=True)
        
        handler = logging.FileHandler(self.config.log_file)
        handler.setFormatter(
            logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        )
        logger.addHandler(handler)
    
    async def start(self):
        """Start the watchdog service"""
        logger.info("🐕 Starting Watchdog Service")
        self.running = True
        
        # Start monitoring tasks
        tasks = []
        
        if self.config.monitor_stdin:
            tasks.append(asyncio.create_task(self._monitor_stdin()))
        
        if self.config.monitor_file:
            tasks.append(asyncio.create_task(self._monitor_file()))
        
        # Start server status monitoring
        tasks.append(asyncio.create_task(self._monitor_server_status()))
        
        try:
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            logger.info("🛑 Watchdog service interrupted")
        finally:
            await self.stop()
    
    async def stop(self):
        """Stop the watchdog service"""
        logger.info("🛑 Stopping Watchdog Service")
        self.running = False
        
        # Stop server if running
        if self.server_process.is_running():
            await self.server_process.stop()
    
    async def _monitor_stdin(self):
        """Monitor stdin for restart keywords"""
        logger.info("👂 Monitoring stdin for restart keywords...")
        
        while self.running:
            try:
                # Use a thread to read stdin without blocking
                loop = asyncio.get_event_loop()
                line = await loop.run_in_executor(None, sys.stdin.readline)
                
                if line:
                    await self._process_input(line.strip())
                
            except Exception as e:
                logger.error(f"Error monitoring stdin: {e}")
                await asyncio.sleep(1)
    
    async def _monitor_file(self):
        """Monitor a file for restart keywords"""
        if not self.config.monitor_file:
            return
        
        logger.info(f"👂 Monitoring file: {self.config.monitor_file}")
        
        try:
            # Create file if it doesn't exist
            Path(self.config.monitor_file).touch()
            
            with open(self.config.monitor_file, 'r') as f:
                # Seek to end of file
                f.seek(0, 2)
                
                while self.running:
                    line = f.readline()
                    if line:
                        await self._process_input(line.strip())
                    else:
                        await asyncio.sleep(0.1)
                        
        except Exception as e:
            logger.error(f"Error monitoring file: {e}")
    
    async def _monitor_server_status(self):
        """Monitor server status and log changes"""
        last_status = None
        
        while self.running:
            try:
                current_status = self.server_process.is_running()
                
                if current_status != last_status:
                    if current_status:
                        logger.info("✅ Server is running")
                    else:
                        logger.warning("❌ Server is not running")
                    last_status = current_status
                
                await asyncio.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                logger.error(f"Error monitoring server status: {e}")
                await asyncio.sleep(5)
    
    async def _process_input(self, message: str):
        """Process input message for restart triggers"""
        if not message:
            return
        
        logger.debug(f"Processing input: {message[:100]}...")
        
        # Check for restart triggers
        result = self.keyword_detector.should_restart(message)
        
        if result["should_restart"]:
            await self._handle_restart_trigger(message, result)
    
    async def _handle_restart_trigger(self, message: str, trigger_result: Dict):
        """Handle restart trigger"""
        logger.info(f"🔥 Restart trigger detected: {trigger_result['reason']}")
        
        # Check rate limiting
        if not self.rate_limiter.can_restart():
            logger.warning("⚠️ Restart rate limit exceeded, ignoring trigger")
            return
        
        # Check cooldown
        if self.last_restart:
            elapsed = datetime.now() - self.last_restart
            if elapsed.total_seconds() < self.config.cooldown_period:
                logger.warning(f"⚠️ Restart cooldown active ({elapsed.total_seconds():.1f}s elapsed)")
                return
        
        # Perform restart
        try:
            delay = trigger_result.get("delay", self.config.restart_delay)
            
            logger.info(f"🚀 Initiating restart (delay: {delay}s)")
            logger.info(f"📝 Trigger message: {message[:200]}")
            
            # Record restart attempt
            self.rate_limiter.record_restart()
            self.last_restart = datetime.now()
            
            # Restart server
            success = await self.server_process.restart(delay)
            
            if success:
                logger.info("✅ Server restart completed successfully")
            else:
                logger.error("❌ Server restart failed")
                
        except Exception as e:
            logger.error(f"❌ Error during restart: {e}")


async def create_watchdog_service(
    monitor_stdin: bool = True,
    monitor_file: Optional[str] = None,
    restart_script: str = "main.py"
) -> WatchdogService:
    """Factory function to create watchdog service"""
    config = WatchdogConfig(
        monitor_stdin=monitor_stdin,
        monitor_file=monitor_file,
        restart_script=restart_script
    )
    
    return WatchdogService(config)


async def main():
    """Main entry point for watchdog service"""
    import argparse
    
    parser = argparse.ArgumentParser(description="MCP Server Watchdog Service")
    parser.add_argument("--no-stdin", action="store_true", help="Don't monitor stdin")
    parser.add_argument("--monitor-file", type=str, help="File to monitor for keywords")
    parser.add_argument("--restart-script", type=str, default="main.py", help="Script to restart")
    
    args = parser.parse_args()
    
    watchdog = await create_watchdog_service(
        monitor_stdin=not args.no_stdin,
        monitor_file=args.monitor_file,
        restart_script=args.restart_script
    )
    
    try:
        await watchdog.start()
    except KeyboardInterrupt:
        print("\n🛑 Watchdog service stopped")


if __name__ == "__main__":
    asyncio.run(main())
