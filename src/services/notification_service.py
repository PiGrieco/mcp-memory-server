"""
Notification service for MCP Memory Server
"""

import asyncio
import logging
import json
import smtplib
import aiohttp
from datetime import datetime
from typing import Dict, Any, List, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dataclasses import dataclass

from ..config.settings import Settings
from ..utils.exceptions import NotificationServiceError


@dataclass
class NotificationMessage:
    """Notification message"""
    title: str
    content: str
    level: str = "info"  # info, warning, error, success
    recipients: List[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.recipients is None:
            self.recipients = []
        if self.metadata is None:
            self.metadata = {}


class NotificationService:
    """Notification service for sending alerts and notifications"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self._initialized = False
        self._notification_queue = asyncio.Queue()
        self._worker_task = None
        
        self.logger = logging.getLogger(__name__)
    
    async def initialize(self) -> None:
        """Initialize notification service"""
        if self._initialized:
            return
        
        try:
            # Start notification worker if enabled
            if self.settings.notifications.enabled:
                self._worker_task = asyncio.create_task(self._notification_worker())
            
            self._initialized = True
            self.logger.info("Notification service initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize notification service: {e}")
            raise NotificationServiceError(f"Notification service initialization failed: {e}")
    
    async def _notification_worker(self) -> None:
        """Background worker for processing notifications"""
        while True:
            try:
                # Get notification from queue
                notification = await self._notification_queue.get()
                
                # Process notification
                await self._process_notification(notification)
                
                # Mark as done
                self._notification_queue.task_done()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Notification worker error: {e}")
                await asyncio.sleep(1)
    
    async def _process_notification(self, notification: NotificationMessage) -> None:
        """Process a notification message"""
        try:
            # Send via email if enabled
            if self.settings.notifications.providers["email"]["enabled"]:
                await self._send_email_notification(notification)
            
            # Send via webhook if enabled
            if self.settings.notifications.providers["webhook"]["enabled"]:
                await self._send_webhook_notification(notification)
            
            self.logger.debug(f"Processed notification: {notification.title}")
            
        except Exception as e:
            self.logger.error(f"Failed to process notification: {e}")
    
    async def _send_email_notification(self, notification: NotificationMessage) -> None:
        """Send email notification"""
        try:
            email_config = self.settings.notifications.providers["email"]
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = email_config["username"]
            msg['To'] = ", ".join(notification.recipients)
            msg['Subject'] = f"[MCP Memory Server] {notification.title}"
            
            # Create HTML content
            html_content = self._create_email_html(notification)
            msg.attach(MIMEText(html_content, 'html'))
            
            # Send email
            with smtplib.SMTP(email_config["smtp_host"], email_config["smtp_port"]) as server:
                server.starttls()
                server.login(email_config["username"], email_config["password"])
                server.send_message(msg)
            
            self.logger.debug(f"Email notification sent to {len(notification.recipients)} recipients")
            
        except Exception as e:
            self.logger.error(f"Failed to send email notification: {e}")
            raise
    
    async def _send_webhook_notification(self, notification: NotificationMessage) -> None:
        """Send webhook notification"""
        try:
            webhook_config = self.settings.notifications.providers["webhook"]
            
            # Prepare payload
            payload = {
                "title": notification.title,
                "content": notification.content,
                "level": notification.level,
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": notification.metadata
            }
            
            # Add custom headers
            headers = {
                "Content-Type": "application/json",
                **webhook_config.get("headers", {})
            }
            
            # Send webhook
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    webhook_config["url"],
                    json=payload,
                    headers=headers
                ) as response:
                    if response.status >= 400:
                        raise NotificationServiceError(f"Webhook failed with status {response.status}")
            
            self.logger.debug(f"Webhook notification sent to {webhook_config['url']}")
            
        except Exception as e:
            self.logger.error(f"Failed to send webhook notification: {e}")
            raise
    
    def _create_email_html(self, notification: NotificationMessage) -> str:
        """Create HTML email content"""
        level_colors = {
            "info": "#3498db",
            "warning": "#f39c12",
            "error": "#e74c3c",
            "success": "#27ae60"
        }
        
        color = level_colors.get(notification.level, "#3498db")
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; }}
                .header {{ background-color: {color}; color: white; padding: 20px; border-radius: 5px 5px 0 0; }}
                .content {{ background-color: #f8f9fa; padding: 20px; border-radius: 0 0 5px 5px; }}
                .footer {{ text-align: center; margin-top: 20px; color: #6c757d; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>{notification.title}</h2>
                </div>
                <div class="content">
                    <p>{notification.content}</p>
                    {self._format_metadata_html(notification.metadata)}
                </div>
                <div class="footer">
                    <p>MCP Memory Server Notification</p>
                    <p>Sent at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _format_metadata_html(self, metadata: Dict[str, Any]) -> str:
        """Format metadata as HTML"""
        if not metadata:
            return ""
        
        html = "<h3>Details:</h3><ul>"
        for key, value in metadata.items():
            html += f"<li><strong>{key}:</strong> {value}</li>"
        html += "</ul>"
        
        return html
    
    async def send_notification(
        self,
        title: str,
        content: str,
        level: str = "info",
        recipients: List[str] = None,
        metadata: Dict[str, Any] = None
    ) -> bool:
        """Send a notification"""
        try:
            if not self._initialized:
                self.logger.warning("Notification service not initialized")
                return False
            
            # Create notification message
            notification = NotificationMessage(
                title=title,
                content=content,
                level=level,
                recipients=recipients or [],
                metadata=metadata or {}
            )
            
            # Add to queue
            await self._notification_queue.put(notification)
            
            self.logger.debug(f"Notification queued: {title}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send notification: {e}")
            return False
    
    async def send_memory_created_notification(self, memory: Any, context: Dict[str, Any] = None) -> bool:
        """Send notification when memory is created"""
        try:
            title = "New Memory Created"
            content = f"A new memory has been created in project '{memory.project}'"
            
            metadata = {
                "memory_id": memory.id,
                "project": memory.project,
                "importance": memory.importance,
                "created_at": memory.created_at.isoformat()
            }
            
            if context:
                metadata.update(context)
            
            return await self.send_notification(
                title=title,
                content=content,
                level="info",
                metadata=metadata
            )
            
        except Exception as e:
            self.logger.error(f"Failed to send memory created notification: {e}")
            return False
    
    async def send_error_notification(self, error: str, context: Dict[str, Any] = None) -> bool:
        """Send error notification"""
        try:
            title = "System Error"
            content = f"An error occurred: {error}"
            
            metadata = {
                "error": error,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            if context:
                metadata.update(context)
            
            return await self.send_notification(
                title=title,
                content=content,
                level="error",
                metadata=metadata
            )
            
        except Exception as e:
            self.logger.error(f"Failed to send error notification: {e}")
            return False
    
    async def send_backup_notification(self, backup_info: Dict[str, Any]) -> bool:
        """Send backup notification"""
        try:
            title = "Backup Completed"
            content = f"Backup '{backup_info['backup_name']}' has been completed successfully"
            
            metadata = {
                "backup_name": backup_info["backup_name"],
                "backup_size": backup_info.get("size", 0),
                "created_at": backup_info.get("created_at", ""),
                "backup_path": backup_info.get("backup_path", "")
            }
            
            return await self.send_notification(
                title=title,
                content=content,
                level="success",
                metadata=metadata
            )
            
        except Exception as e:
            self.logger.error(f"Failed to send backup notification: {e}")
            return False
    
    async def send_health_check_notification(self, health_status: Dict[str, Any]) -> bool:
        """Send health check notification"""
        try:
            status = health_status.get("status", "unknown")
            
            if status == "unhealthy":
                title = "System Health Check Failed"
                content = "The system health check has failed"
                level = "error"
            else:
                title = "System Health Check Passed"
                content = "The system health check has passed"
                level = "success"
            
            return await self.send_notification(
                title=title,
                content=content,
                level=level,
                metadata=health_status
            )
            
        except Exception as e:
            self.logger.error(f"Failed to send health check notification: {e}")
            return False
    
    async def get_notification_status(self) -> Dict[str, Any]:
        """Get notification service status"""
        try:
            return {
                "enabled": self.settings.notifications.enabled,
                "queue_size": self._notification_queue.qsize(),
                "worker_running": self._worker_task is not None and not self._worker_task.done(),
                "email_enabled": self.settings.notifications.providers["email"]["enabled"],
                "webhook_enabled": self.settings.notifications.providers["webhook"]["enabled"],
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
            
            # Check worker task
            worker_ok = self._worker_task is not None and not self._worker_task.done()
            
            # Check providers
            email_ok = True
            webhook_ok = True
            
            if self.settings.notifications.providers["email"]["enabled"]:
                try:
                    # Test email connection
                    email_config = self.settings.notifications.providers["email"]
                    with smtplib.SMTP(email_config["smtp_host"], email_config["smtp_port"]) as server:
                        server.starttls()
                        server.login(email_config["username"], email_config["password"])
                except Exception as e:
                    email_ok = False
            
            if self.settings.notifications.providers["webhook"]["enabled"]:
                try:
                    # Test webhook connection
                    webhook_config = self.settings.notifications.providers["webhook"]
                    async with aiohttp.ClientSession() as session:
                        async with session.get(webhook_config["url"]) as response:
                            webhook_ok = response.status < 500
                except Exception:
                    webhook_ok = False
            
            overall_status = "healthy" if worker_ok else "unhealthy"
            
            return {
                "status": overall_status,
                "worker_running": worker_ok,
                "email_provider": "healthy" if email_ok else "unhealthy",
                "webhook_provider": "healthy" if webhook_ok else "unhealthy",
                "queue_size": self._notification_queue.qsize()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def stop(self) -> None:
        """Stop notification service"""
        try:
            if self._worker_task:
                self._worker_task.cancel()
                try:
                    await self._worker_task
                except asyncio.CancelledError:
                    pass
            
            self._initialized = False
            self.logger.info("Notification service stopped")
            
        except Exception as e:
            self.logger.error(f"Failed to stop notification service: {e}") 