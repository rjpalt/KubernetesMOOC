"""Image service for business logic operations."""
import logging
from typing import Dict, Any

from ..core.cache import ImageCacheManager
from ..models.image import ImageInfo, FetchResult
from ..config.settings import settings

logger = logging.getLogger(__name__)


class ImageService:
    """Service layer for image operations."""
    
    def __init__(self, cache_manager: ImageCacheManager):
        self.cache_manager = cache_manager
    
    async def get_image_info(self) -> ImageInfo:
        """Get information about the current image."""
        return await self.cache_manager.get_current_image_info()
    
    async def fetch_new_image(self, force: bool = False) -> FetchResult:
        """Fetch a new image."""
        logger.info(f"Image fetch requested (force={force})")
        return await self.cache_manager.fetch_new_image(force=force)
    
    def get_image_path(self):
        """Get the current image file path."""
        return self.cache_manager.current_image_file
    
    def format_image_status(self, image_info: ImageInfo) -> str:
        """Format image status for display."""
        if image_info.status != "available":
            return "No image available"
        
        status = f"Image loaded ({image_info.file_size} bytes)"
        if image_info.last_fetch_time:
            from datetime import datetime
            fetch_time = datetime.fromisoformat(image_info.last_fetch_time.replace("Z", "+00:00"))
            status += f" - Last updated: {fetch_time.strftime('%H:%M:%S UTC')}"
        
        return status
    
    def get_config_for_template(self) -> Dict[str, Any]:
        """Get configuration data for template rendering."""
        return {
            "cache_path": str(settings.image_cache_path),
            "update_interval": settings.image_update_interval_minutes,
            "picsum_url": settings.picsum_url,
        }
