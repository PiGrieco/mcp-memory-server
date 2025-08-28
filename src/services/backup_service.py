"""
Backup service for MCP Memory Server
"""

import asyncio
import logging
import json
import shutil
from datetime import datetime, timedelta
from typing import Dict, Any, List
from pathlib import Path
import threading
import tarfile
import time

# Optional schedule import - gracefully handle missing dependency
try:
    import schedule
    SCHEDULE_AVAILABLE = True
except ImportError:
    schedule = None
    SCHEDULE_AVAILABLE = False

from ..config.settings import Settings
from ..utils.exceptions import BackupServiceError


class BackupService:
    """Backup service for automatic data backup"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.backup_dir = Path(self.settings.backup.storage["path"])
        self._initialized = False
        self._scheduler_thread = None
        self._stop_scheduler = False
        
        self.logger = logging.getLogger(__name__)
    
    async def initialize(self) -> None:
        """Initialize backup service"""
        if self._initialized:
            return
        
        try:
            # Create backup directory
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Start backup scheduler if enabled
            if self.settings.backup.enabled:
                await self._start_backup_scheduler()
            
            self._initialized = True
            self.logger.info("Backup service initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize backup service: {e}")
            raise BackupServiceError(f"Backup service initialization failed: {e}")
    
    async def _start_backup_scheduler(self) -> None:
        """Start backup scheduler"""
        if not SCHEDULE_AVAILABLE:
            self.logger.warning("Schedule library not available - automatic backups disabled")
            return
            
        try:
            # Parse cron schedule
            schedule_str = self.settings.backup.schedule
            
            # Schedule backup job
            if schedule_str == "0 2 * * *":  # Daily at 2 AM
                schedule.every().day.at("02:00").do(self._run_backup_job)
            elif schedule_str == "0 */6 * * *":  # Every 6 hours
                schedule.every(6).hours.do(self._run_backup_job)
            elif schedule_str == "0 */12 * * *":  # Every 12 hours
                schedule.every(12).hours.do(self._run_backup_job)
            else:
                # Default to daily at 2 AM
                schedule.every().day.at("02:00").do(self._run_backup_job)
            
            # Start scheduler thread
            self._scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
            self._scheduler_thread.start()
            
            self.logger.info(f"Backup scheduler started with schedule: {schedule_str}")
            
        except Exception as e:
            self.logger.error(f"Failed to start backup scheduler: {e}")
            raise
    
    def _scheduler_loop(self) -> None:
        """Scheduler loop"""
        if not SCHEDULE_AVAILABLE:
            return
            
        while not self._stop_scheduler:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                self.logger.error(f"Scheduler loop error: {e}")
                time.sleep(60)
    
    def _run_backup_job(self) -> None:
        """Run backup job"""
        try:
            asyncio.run(self.create_backup())
        except Exception as e:
            self.logger.error(f"Backup job failed: {e}")
    
    async def create_backup(self, backup_type: str = "full") -> Dict[str, Any]:
        """Create a backup"""
        try:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_{backup_type}_{timestamp}"
            backup_path = self.backup_dir / backup_name
            
            # Create backup directory
            backup_path.mkdir(parents=True, exist_ok=True)
            
            # Backup metadata
            metadata = {
                "backup_type": backup_type,
                "created_at": datetime.utcnow().isoformat(),
                "version": self.settings.server.version,
                "settings": self._get_backup_settings()
            }
            
            # Save metadata
            metadata_file = backup_path / "metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            # Backup data files
            await self._backup_data_files(backup_path)
            
            # Backup configuration
            await self._backup_configuration(backup_path)
            
            # Compress backup if enabled
            if self.settings.backup.compression:
                await self._compress_backup(backup_path)
            
            # Cleanup old backups
            await self._cleanup_old_backups()
            
            self.logger.info(f"Backup created successfully: {backup_name}")
            
            return {
                "success": True,
                "backup_name": backup_name,
                "backup_path": str(backup_path),
                "size": await self._get_backup_size(backup_path),
                "created_at": metadata["created_at"]
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create backup: {e}")
            raise BackupServiceError(f"Backup creation failed: {e}")
    
    async def _backup_data_files(self, backup_path: Path) -> None:
        """Backup data files"""
        try:
            data_dir = Path(self.settings.paths.data_dir)
            if data_dir.exists():
                # Copy data directory
                backup_data_dir = backup_path / "data"
                shutil.copytree(data_dir, backup_data_dir)
                
                self.logger.debug(f"Backed up data directory: {data_dir}")
            
        except Exception as e:
            self.logger.error(f"Failed to backup data files: {e}")
            raise
    
    async def _backup_configuration(self, backup_path: Path) -> None:
        """Backup configuration files"""
        try:
            config_dir = Path("config")
            if config_dir.exists():
                # Copy config directory
                backup_config_dir = backup_path / "config"
                shutil.copytree(config_dir, backup_config_dir)
                
                self.logger.debug(f"Backed up config directory: {config_dir}")
            
        except Exception as e:
            self.logger.error(f"Failed to backup configuration: {e}")
            raise
    
    async def _compress_backup(self, backup_path: Path) -> None:
        """Compress backup directory"""
        try:
            # Create tar.gz archive
            archive_path = backup_path.parent / f"{backup_path.name}.tar.gz"
            
            with tarfile.open(archive_path, "w:gz") as tar:
                tar.add(backup_path, arcname=backup_path.name)
            
            # Remove uncompressed directory
            shutil.rmtree(backup_path)
            
            self.logger.debug(f"Compressed backup: {archive_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to compress backup: {e}")
            raise
    
    async def _cleanup_old_backups(self) -> None:
        """Clean up old backups based on retention policy"""
        try:
            retention_days = self.settings.backup.retention_days
            cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
            
            # Find old backups
            old_backups = []
            for backup_file in self.backup_dir.glob("*"):
                if backup_file.is_file() or backup_file.is_dir():
                    # Try to get creation time
                    try:
                        if backup_file.is_file():
                            stat = backup_file.stat()
                        else:
                            stat = backup_file.stat()
                        
                        creation_time = datetime.fromtimestamp(stat.st_ctime)
                        if creation_time < cutoff_date:
                            old_backups.append(backup_file)
                    except Exception:
                        continue
            
            # Remove old backups
            for old_backup in old_backups:
                try:
                    if old_backup.is_file():
                        old_backup.unlink()
                    else:
                        shutil.rmtree(old_backup)
                    
                    self.logger.debug(f"Removed old backup: {old_backup}")
                except Exception as e:
                    self.logger.warning(f"Failed to remove old backup {old_backup}: {e}")
            
            if old_backups:
                self.logger.info(f"Cleaned up {len(old_backups)} old backups")
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup old backups: {e}")
    
    async def _get_backup_size(self, backup_path: Path) -> int:
        """Get backup size in bytes"""
        try:
            if backup_path.is_file():
                return backup_path.stat().st_size
            else:
                total_size = 0
                for file_path in backup_path.rglob("*"):
                    if file_path.is_file():
                        total_size += file_path.stat().st_size
                return total_size
        except Exception:
            return 0
    
    def _get_backup_settings(self) -> Dict[str, Any]:
        """Get backup settings for metadata"""
        return {
            "enabled": self.settings.backup.enabled,
            "schedule": self.settings.backup.schedule,
            "retention_days": self.settings.backup.retention_days,
            "compression": self.settings.backup.compression,
            "storage_type": self.settings.backup.storage["type"]
        }
    
    async def list_backups(self) -> List[Dict[str, Any]]:
        """List all backups"""
        try:
            backups = []
            
            for backup_file in self.backup_dir.glob("*"):
                if backup_file.is_file() or backup_file.is_dir():
                    try:
                        if backup_file.is_file():
                            stat = backup_file.stat()
                        else:
                            stat = backup_file.stat()
                        
                        creation_time = datetime.fromtimestamp(stat.st_ctime)
                        size = await self._get_backup_size(backup_file)
                        
                        backups.append({
                            "name": backup_file.name,
                            "path": str(backup_file),
                            "size": size,
                            "created_at": creation_time.isoformat(),
                            "type": "compressed" if backup_file.suffix == ".gz" else "directory"
                        })
                    except Exception as e:
                        self.logger.warning(f"Failed to get backup info for {backup_file}: {e}")
            
            # Sort by creation time (newest first)
            backups.sort(key=lambda x: x["created_at"], reverse=True)
            
            return backups
            
        except Exception as e:
            self.logger.error(f"Failed to list backups: {e}")
            return []
    
    async def restore_backup(self, backup_name: str) -> Dict[str, Any]:
        """Restore from backup"""
        try:
            backup_path = self.backup_dir / backup_name
            
            if not backup_path.exists():
                raise BackupServiceError(f"Backup not found: {backup_name}")
            
            # Check if it's a compressed backup
            if backup_path.suffix == ".gz":
                # Extract compressed backup
                extracted_path = backup_path.parent / backup_path.stem
                with tarfile.open(backup_path, "r:gz") as tar:
                    tar.extractall(backup_path.parent)
                backup_path = extracted_path
            
            # Read metadata
            metadata_file = backup_path / "metadata.json"
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
            else:
                metadata = {}
            
            # Restore data files
            await self._restore_data_files(backup_path)
            
            # Restore configuration
            await self._restore_configuration(backup_path)
            
            self.logger.info(f"Backup restored successfully: {backup_name}")
            
            return {
                "success": True,
                "backup_name": backup_name,
                "restored_at": datetime.utcnow().isoformat(),
                "metadata": metadata
            }
            
        except Exception as e:
            self.logger.error(f"Failed to restore backup: {e}")
            raise BackupServiceError(f"Backup restoration failed: {e}")
    
    async def _restore_data_files(self, backup_path: Path) -> None:
        """Restore data files"""
        try:
            backup_data_dir = backup_path / "data"
            if backup_data_dir.exists():
                data_dir = Path(self.settings.paths.data_dir)
                
                # Remove existing data directory
                if data_dir.exists():
                    shutil.rmtree(data_dir)
                
                # Restore data directory
                shutil.copytree(backup_data_dir, data_dir)
                
                self.logger.debug(f"Restored data directory: {data_dir}")
            
        except Exception as e:
            self.logger.error(f"Failed to restore data files: {e}")
            raise
    
    async def _restore_configuration(self, backup_path: Path) -> None:
        """Restore configuration files"""
        try:
            backup_config_dir = backup_path / "config"
            if backup_config_dir.exists():
                config_dir = Path("config")
                
                # Remove existing config directory
                if config_dir.exists():
                    shutil.rmtree(config_dir)
                
                # Restore config directory
                shutil.copytree(backup_config_dir, config_dir)
                
                self.logger.debug(f"Restored config directory: {config_dir}")
            
        except Exception as e:
            self.logger.error(f"Failed to restore configuration: {e}")
            raise
    
    async def get_backup_status(self) -> Dict[str, Any]:
        """Get backup service status"""
        try:
            backups = await self.list_backups()
            
            return {
                "enabled": self.settings.backup.enabled,
                "schedule": self.settings.backup.schedule,
                "retention_days": self.settings.backup.retention_days,
                "compression": self.settings.backup.compression,
                "total_backups": len(backups),
                "total_size": sum(b["size"] for b in backups),
                "last_backup": backups[0]["created_at"] if backups else None,
                "backup_directory": str(self.backup_dir),
                "status": "healthy" if self._initialized else "not_initialized"
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check"""
        try:
            if not self._initialized:
                return {"status": "not_initialized"}
            
            # Check backup directory
            if not self.backup_dir.exists():
                return {
                    "status": "unhealthy",
                    "error": "Backup directory does not exist"
                }
            
            # Check scheduler
            scheduler_ok = self._scheduler_thread is not None and self._scheduler_thread.is_alive()
            
            return {
                "status": "healthy" if scheduler_ok else "unhealthy",
                "backup_directory": str(self.backup_dir),
                "scheduler_running": scheduler_ok,
                "enabled": self.settings.backup.enabled
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def stop(self) -> None:
        """Stop backup service"""
        try:
            self._stop_scheduler = True
            
            if self._scheduler_thread and self._scheduler_thread.is_alive():
                self._scheduler_thread.join(timeout=5)
            
            self._initialized = False
            self.logger.info("Backup service stopped")
            
        except Exception as e:
            self.logger.error(f"Failed to stop backup service: {e}") 