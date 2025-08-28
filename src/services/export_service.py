"""
Export service for MCP Memory Server
"""

import logging
import json
import gzip
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
import pandas as pd

from ..config.settings import Settings
from ..utils.exceptions import ExportServiceError


class ExportService:
    """Export service for data export functionality"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.export_dir = Path(self.settings.paths.exports_dir)
        self._initialized = False
        
        self.logger = logging.getLogger(__name__)
    
    async def initialize(self) -> None:
        """Initialize export service"""
        if self._initialized:
            return
        
        try:
            # Create export directory
            self.export_dir.mkdir(parents=True, exist_ok=True)
            
            self._initialized = True
            self.logger.info("Export service initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize export service: {e}")
            raise ExportServiceError(f"Export service initialization failed: {e}")
    
    async def export_memories(
        self,
        memories: List[Any],
        format: str = "json",
        filename: Optional[str] = None,
        include_embeddings: Optional[bool] = None
    ) -> Dict[str, Any]:
        """Export memories to specified format"""
        try:
            if not memories:
                return {
                    "success": False,
                    "error": "No memories to export"
                }
            
            # Use settings default if not specified
            if include_embeddings is None:
                include_embeddings = self.settings.export.include_embeddings
            
            # Generate filename if not provided
            if not filename:
                timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
                filename = f"memories_export_{timestamp}.{format}"
            
            # Prepare export data
            export_data = await self._prepare_memories_data(memories, include_embeddings)
            
            # Export based on format
            if format == "json":
                result = await self._export_json(export_data, filename)
            elif format == "csv":
                result = await self._export_csv(export_data, filename)
            elif format == "markdown":
                result = await self._export_markdown(export_data, filename)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported format: {format}"
                }
            
            # Compress if enabled
            if self.settings.export.compression:
                result = await self._compress_export(result["file_path"])
            
            return {
                "success": True,
                "format": format,
                "filename": filename,
                "file_path": str(result["file_path"]),
                "size": result["size"],
                "memory_count": len(memories),
                "created_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to export memories: {e}")
            raise ExportServiceError(f"Export failed: {e}")
    
    async def _prepare_memories_data(self, memories: List[Any], include_embeddings: bool) -> List[Dict[str, Any]]:
        """Prepare memories data for export"""
        try:
            export_data = []
            
            for memory in memories:
                memory_data = {
                    "id": memory.id,
                    "project": memory.project,
                    "content": memory.content,
                    "memory_type": memory.memory_type.value,
                    "importance": memory.importance,
                    "tags": memory.tags,
                    "metadata": memory.metadata,
                    "context": memory.context,
                    "created_at": memory.created_at.isoformat(),
                    "updated_at": memory.updated_at.isoformat(),
                    "access_count": memory.access_count,
                    "last_accessed": memory.last_accessed.isoformat() if memory.last_accessed else None
                }
                
                # Include embeddings if requested
                if include_embeddings and memory.embedding:
                    memory_data["embedding"] = memory.embedding
                
                export_data.append(memory_data)
            
            return export_data
            
        except Exception as e:
            self.logger.error(f"Failed to prepare memories data: {e}")
            raise
    
    async def _export_json(self, data: List[Dict[str, Any]], filename: str) -> Dict[str, Any]:
        """Export data to JSON format"""
        try:
            file_path = self.export_dir / filename
            
            # Create export structure
            export_structure = {
                "export_info": {
                    "created_at": datetime.utcnow().isoformat(),
                    "version": self.settings.server.version,
                    "format": "json",
                    "memory_count": len(data)
                },
                "memories": data
            }
            
            # Write JSON file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_structure, f, indent=2, ensure_ascii=False)
            
            size = file_path.stat().st_size
            
            return {
                "file_path": file_path,
                "size": size
            }
            
        except Exception as e:
            self.logger.error(f"Failed to export JSON: {e}")
            raise
    
    async def _export_csv(self, data: List[Dict[str, Any]], filename: str) -> Dict[str, Any]:
        """Export data to CSV format"""
        try:
            file_path = self.export_dir / filename
            
            if not data:
                return {
                    "file_path": file_path,
                    "size": 0
                }
            
            # Convert to DataFrame
            df = pd.DataFrame(data)
            
            # Flatten nested structures
            df = self._flatten_dataframe(df)
            
            # Write CSV file
            df.to_csv(file_path, index=False, encoding='utf-8')
            
            size = file_path.stat().st_size
            
            return {
                "file_path": file_path,
                "size": size
            }
            
        except Exception as e:
            self.logger.error(f"Failed to export CSV: {e}")
            raise
    
    async def _export_markdown(self, data: List[Dict[str, Any]], filename: str) -> Dict[str, Any]:
        """Export data to Markdown format"""
        try:
            file_path = self.export_dir / filename
            
            # Create markdown content
            markdown_content = self._create_markdown_content(data)
            
            # Write markdown file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            size = file_path.stat().st_size
            
            return {
                "file_path": file_path,
                "size": size
            }
            
        except Exception as e:
            self.logger.error(f"Failed to export Markdown: {e}")
            raise
    
    def _flatten_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Flatten nested structures in DataFrame"""
        try:
            # Handle list columns
            for col in df.columns:
                if df[col].dtype == 'object':
                    # Check if column contains lists
                    if df[col].apply(lambda x: isinstance(x, list)).any():
                        df[col] = df[col].apply(lambda x: ', '.join(map(str, x)) if isinstance(x, list) else x)
                    
                    # Check if column contains dictionaries
                    elif df[col].apply(lambda x: isinstance(x, dict)).any():
                        df[col] = df[col].apply(lambda x: json.dumps(x) if isinstance(x, dict) else x)
            
            return df
            
        except Exception as e:
            self.logger.error(f"Failed to flatten DataFrame: {e}")
            return df
    
    def _create_markdown_content(self, data: List[Dict[str, Any]]) -> str:
        """Create markdown content from data"""
        try:
            content = f"""# MCP Memory Server Export

**Export Date:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC  
**Total Memories:** {len(data)}  
**Format:** Markdown

---

"""
            
            for i, memory in enumerate(data, 1):
                content += f"""## Memory {i}: {memory['id']}

**Project:** {memory['project']}  
**Type:** {memory['memory_type']}  
**Importance:** {memory['importance']}  
**Created:** {memory['created_at']}  
**Updated:** {memory['updated_at']}  
**Access Count:** {memory['access_count']}

**Tags:** {', '.join(memory['tags']) if memory['tags'] else 'None'}

**Content:**
```
{memory['content']}
```

"""
                
                # Add metadata if present
                if memory['metadata']:
                    content += "**Metadata:**\n"
                    for key, value in memory['metadata'].items():
                        content += f"- {key}: {value}\n"
                    content += "\n"
                
                # Add context if present
                if memory['context']:
                    content += "**Context:**\n"
                    for key, value in memory['context'].items():
                        content += f"- {key}: {value}\n"
                    content += "\n"
                
                content += "---\n\n"
            
            return content
            
        except Exception as e:
            self.logger.error(f"Failed to create markdown content: {e}")
            raise
    
    async def _compress_export(self, file_path: Path) -> Dict[str, Any]:
        """Compress export file"""
        try:
            compressed_path = file_path.with_suffix(file_path.suffix + '.gz')
            
            with open(file_path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb') as f_out:
                    f_out.writelines(f_in)
            
            # Remove original file
            file_path.unlink()
            
            size = compressed_path.stat().st_size
            
            return {
                "file_path": compressed_path,
                "size": size
            }
            
        except Exception as e:
            self.logger.error(f"Failed to compress export: {e}")
            raise
    
    async def get_export_status(self) -> Dict[str, Any]:
        """Get export service status"""
        try:
            exports = await self.list_exports()
            
            return {
                "enabled": True,
                "export_directory": str(self.export_dir),
                "total_exports": len(exports),
                "total_size": sum(e["size"] for e in exports),
                "supported_formats": self.settings.export.formats,
                "compression_enabled": self.settings.export.compression,
                "include_embeddings": self.settings.export.include_embeddings,
                "batch_size": self.settings.export.batch_size,
                "status": "healthy" if self._initialized else "not_initialized"
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def list_exports(self) -> List[Dict[str, Any]]:
        """List all export files"""
        try:
            exports = []
            
            for export_file in self.export_dir.glob("*"):
                if export_file.is_file():
                    try:
                        stat = export_file.stat()
                        creation_time = datetime.fromtimestamp(stat.st_ctime)
                        
                        exports.append({
                            "name": export_file.name,
                            "path": str(export_file),
                            "size": stat.st_size,
                            "created_at": creation_time.isoformat(),
                            "format": export_file.suffix.lstrip('.'),
                            "compressed": export_file.suffix.endswith('.gz')
                        })
                    except Exception as e:
                        self.logger.warning(f"Failed to get export info for {export_file}: {e}")
            
            # Sort by creation time (newest first)
            exports.sort(key=lambda x: x["created_at"], reverse=True)
            
            return exports
            
        except Exception as e:
            self.logger.error(f"Failed to list exports: {e}")
            return []
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check"""
        try:
            if not self._initialized:
                return {"status": "not_initialized"}
            
            # Check export directory
            if not self.export_dir.exists():
                return {
                    "status": "unhealthy",
                    "error": "Export directory does not exist"
                }
            
            # Test write permission
            test_file = self.export_dir / "health_check_test.txt"
            try:
                test_file.write_text("health check")
                test_file.unlink()
            except Exception as e:
                return {
                    "status": "unhealthy",
                    "error": f"No write permission to export directory: {e}"
                }
            
            return {
                "status": "healthy",
                "export_directory": str(self.export_dir),
                "writable": True
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            } 