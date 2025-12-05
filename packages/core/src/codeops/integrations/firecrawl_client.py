"""FireCrawl Client - Web scraping integration"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
import aiohttp
from urllib.parse import urljoin

from ..error_handling import (
    FireCrawlException,
    async_error_handler,
    validate_input,
    ErrorSeverity,
)

logger = logging.getLogger(__name__)


class FireCrawlClient:
    """FireCrawl web scraping client with advanced features"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.api_endpoint = config.get("api_endpoint", "http://localhost:3000")
        self.timeout = config.get("timeout", 30000)
        self.max_depth = config.get("max_depth", 2)
        self.api_key = config.get("api_key", "default-key")
        self.session = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    @async_error_handler(max_retries=3)
    async def crawl_multiple(
        self, 
        urls: List[str],
        parallel: bool = True,
        max_concurrent: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Crawl multiple URLs with optional parallelization
        
        Args:
            urls: List of URLs to crawl
            parallel: Whether to crawl in parallel
            max_concurrent: Maximum concurrent crawls
            
        Returns:
            List of crawl results
        """
        logger.info(f"🌐 Crawling {len(urls)} URLs (parallel={parallel})")
        
        if not parallel:
            return await self._crawl_sequential(urls)
        
        return await self._crawl_parallel(urls, max_concurrent)
    
    async def _crawl_sequential(self, urls: List[str]) -> List[Dict[str, Any]]:
        """Crawl URLs sequentially"""
        results = []
        
        for url in urls:
            try:
                result = await self.crawl(url)
                results.extend(result)
            except FireCrawlException as e:
                logger.warning(f"FireCrawl error for {url}: {e.message}")
            except Exception as e:
                logger.error(f"Unexpected error crawling {url}: {e}")
        
        return results
    
    async def _crawl_parallel(self, urls: List[str], max_concurrent: int) -> List[Dict[str, Any]]:
        """Crawl URLs in parallel with semaphore"""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def crawl_with_semaphore(url):
            async with semaphore:
                try:
                    return await self.crawl(url)
                except Exception as e:
                    logger.warning(f"Error crawling {url}: {e}")
                    return []
        
        results = await asyncio.gather(*[crawl_with_semaphore(url) for url in urls])
        return [item for sublist in results for item in sublist]
    
    @validate_input(url=lambda x: x.startswith("http"))
    @async_error_handler(max_retries=2)
    async def crawl(
        self,
        url: str,
        depth: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Crawl single URL
        
        Args:
            url: URL to crawl
            depth: Crawl depth (optional)
            
        Returns:
            List of extracted data
            
        Raises:
            FireCrawlException: If crawl fails
        """
        logger.info(f"🌐 Crawling: {url} (depth={depth or self.max_depth})")
        
        try:
            # TODO: Implement actual FireCrawl API call
            # This would use aiohttp to call FireCrawl API
            
            # Simulated response
            return [
                {
                    "keyword": "anime nft trending",
                    "volume": 1500,
                    "sentiment": 0.8,
                    "source": self._extract_source(url),
                    "url": url,
                    "depth": depth or self.max_depth
                },
                {
                    "keyword": "rare anime collectibles",
                    "volume": 800,
                    "sentiment": 0.75,
                    "source": self._extract_source(url),
                    "url": url,
                    "depth": depth or self.max_depth
                }
            ]
            
        except Exception as e:
            raise FireCrawlException(
                f"Failed to crawl {url}: {str(e)}",
                ErrorSeverity.ERROR
            )
    
    async def search(
        self,
        query: str,
        num_results: int = 10
    ) -> List[Dict[str, Any]]:
        """Search across multiple sources"""
        logger.info(f"🔍 Searching for: {query}")
        
        # TODO: Implement search across multiple platforms
        return []
    
    def _extract_source(self, url: str) -> str:
        """Extract source from URL"""
        if "twitter" in url:
            return "twitter"
        elif "reddit" in url:
            return "reddit"
        elif "youtube" in url:
            return "youtube"
        else:
            return "unknown"
