"""Memory Client - Persistent context storage"""

import json
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)


class MemoryClient:
    """Persistent memory and context storage"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.storage_dir = Path(config.get("storage_dir", "./memory"))
        self.storage_dir.mkdir(exist_ok=True)
    
    async def save_context(self, key: str, context: Dict[str, Any]) -> None:
        """Save execution context"""
        file_path = self.storage_dir / f"{key}.json"
        logger.info(f"💾 Saving memory: {key}")
        
        with open(file_path, 'w') as f:
            json.dump(context, f, indent=2, default=str)
    
    async def load_context(self, key: str) -> Dict[str, Any]:
        """Load execution context"""
        file_path = self.storage_dir / f"{key}.json"
        
        if not file_path.exists():
            logger.warning(f"Memory not found: {key}")
            return {}
        
        logger.info(f"📖 Loading memory: {key}")
        with open(file_path, 'r') as f:
            return json.load(f)
    
    async def list_contexts(self) -> list:
        """List all saved contexts"""
        return [f.stem for f in self.storage_dir.glob("*.json")]
    
    async def memory_bank(self) -> Dict[str, Any]:
        """Get all memory contexts"""
        contexts = {}
        for file_path in self.storage_dir.glob("*.json"):
            with open(file_path, 'r') as f:
                contexts[file_path.stem] = json.load(f)
        
        return contexts
