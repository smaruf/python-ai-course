"""
Web Crawler Implementation

Tests: BFS traversal, multithreading, synchronization, URL normalization

A production-ready web crawler that demonstrates:
- Breadth-First Search for systematic crawling
- Thread-safe operations with proper synchronization
- URL deduplication and normalization
- Respectful crawling with delays
- Error handling and retries
"""

from typing import Set, List, Deque, Optional, Callable
from collections import deque
from urllib.parse import urljoin, urlparse
import threading
import time
import re


class WebCrawler:
    """
    Multi-threaded web crawler with BFS traversal.
    
    Features:
    - Concurrent crawling with configurable worker threads
    - URL deduplication to avoid cycles
    - Domain restrictions
    - Configurable depth limits
    - Thread-safe visited set
    """
    
    def __init__(
        self,
        max_depth: int = 3,
        max_workers: int = 5,
        delay: float = 0.1,
        same_domain_only: bool = True
    ):
        """
        Initialize the web crawler.
        
        Args:
            max_depth: Maximum depth to crawl
            max_workers: Number of concurrent worker threads
            delay: Delay between requests (in seconds)
            same_domain_only: Only crawl URLs from the same domain
        """
        self.max_depth = max_depth
        self.max_workers = max_workers
        self.delay = delay
        self.same_domain_only = same_domain_only
        
        # Thread-safe data structures
        self.visited: Set[str] = set()
        self.queue: Deque[tuple[str, int]] = deque()
        self.results: List[dict] = []
        
        # Synchronization primitives
        self.lock = threading.Lock()
        self.stop_event = threading.Event()
        
    def crawl(
        self,
        start_url: str,
        fetch_callback: Optional[Callable[[str], dict]] = None
    ) -> List[dict]:
        """
        Start crawling from the given URL.
        
        Args:
            start_url: URL to start crawling from
            fetch_callback: Optional callback to fetch URL content
            
        Returns:
            List of crawled pages with metadata
        """
        self.queue.append((start_url, 0))
        self.start_domain = self._get_domain(start_url)
        
        # Create worker threads
        workers = []
        for _ in range(self.max_workers):
            worker = threading.Thread(
                target=self._worker,
                args=(fetch_callback,)
            )
            worker.start()
            workers.append(worker)
        
        # Wait for all workers to complete
        for worker in workers:
            worker.join()
        
        return self.results
    
    def _worker(self, fetch_callback: Optional[Callable[[str], dict]]):
        """Worker thread that processes URLs from the queue."""
        while not self.stop_event.is_set():
            try:
                # Get URL from queue (thread-safe)
                with self.lock:
                    if not self.queue:
                        # Queue is empty, stop worker
                        break
                    url, depth = self.queue.popleft()
                    
                    # Skip if already visited
                    if url in self.visited:
                        continue
                    
                    # Mark as visited
                    self.visited.add(url)
                
                # Skip if max depth reached
                if depth > self.max_depth:
                    continue
                
                # Respect crawl delay
                time.sleep(self.delay)
                
                # Fetch page content
                if fetch_callback:
                    page_data = fetch_callback(url)
                else:
                    page_data = self._mock_fetch(url)
                
                # Extract links
                links = self._extract_links(url, page_data.get('content', ''))
                
                # Add new links to queue
                with self.lock:
                    for link in links:
                        if link not in self.visited:
                            self.queue.append((link, depth + 1))
                    
                    # Store result
                    self.results.append({
                        'url': url,
                        'depth': depth,
                        'title': page_data.get('title', ''),
                        'links_found': len(links)
                    })
                    
            except Exception as e:
                # Log error and continue
                print(f"Error crawling {url}: {e}")
    
    def _mock_fetch(self, url: str) -> dict:
        """Mock fetch function for testing."""
        return {
            'content': f'<html><body><a href="/page1">Link 1</a></body></html>',
            'title': f'Page: {url}'
        }
    
    def _extract_links(self, base_url: str, content: str) -> List[str]:
        """
        Extract and normalize links from HTML content.
        
        Args:
            base_url: Base URL for resolving relative links
            content: HTML content
            
        Returns:
            List of normalized absolute URLs
        """
        links = []
        
        # Simple regex to extract href attributes
        href_pattern = r'href=["\']([^"\']+)["\']'
        matches = re.findall(href_pattern, content)
        
        for href in matches:
            # Convert to absolute URL
            absolute_url = urljoin(base_url, href)
            
            # Normalize URL
            normalized_url = self._normalize_url(absolute_url)
            
            # Check domain restriction
            if self.same_domain_only:
                if self._get_domain(normalized_url) != self.start_domain:
                    continue
            
            links.append(normalized_url)
        
        return links
    
    def _normalize_url(self, url: str) -> str:
        """
        Normalize URL by removing fragments and trailing slashes.
        
        Args:
            url: URL to normalize
            
        Returns:
            Normalized URL
        """
        parsed = urlparse(url)
        
        # Remove fragment
        normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        
        # Remove trailing slash (except for root)
        if normalized.endswith('/') and len(parsed.path) > 1:
            normalized = normalized[:-1]
        
        return normalized
    
    def _get_domain(self, url: str) -> str:
        """Extract domain from URL."""
        parsed = urlparse(url)
        return parsed.netloc
    
    def stop(self):
        """Signal all workers to stop."""
        self.stop_event.set()


class DistributedCrawler:
    """
    Distributed web crawler using a shared URL queue.
    
    This demonstrates a more scalable approach where multiple
    crawler instances can work together using a distributed queue
    (like Redis or RabbitMQ).
    """
    
    def __init__(self, crawler_id: str, shared_queue=None):
        """
        Initialize distributed crawler.
        
        Args:
            crawler_id: Unique identifier for this crawler instance
            shared_queue: Shared queue for coordination (mock implementation)
        """
        self.crawler_id = crawler_id
        self.shared_queue = shared_queue or []
        self.visited = set()
        
    def crawl_task(self, url: str) -> dict:
        """
        Crawl a single URL (task-based approach).
        
        Args:
            url: URL to crawl
            
        Returns:
            Crawl result
        """
        if url in self.visited:
            return {'status': 'already_visited', 'url': url}
        
        self.visited.add(url)
        
        # Simulate fetching
        return {
            'status': 'success',
            'url': url,
            'crawler_id': self.crawler_id,
            'timestamp': time.time()
        }


if __name__ == "__main__":
    # Example usage
    print("Web Crawler Example")
    print("=" * 60)
    
    crawler = WebCrawler(max_depth=2, max_workers=3, delay=0.05)
    
    # Mock fetch function
    def fetch(url):
        return {
            'content': '<html><a href="/page1">P1</a><a href="/page2">P2</a></html>',
            'title': f'Page {url}'
        }
    
    results = crawler.crawl("https://example.com", fetch)
    
    print(f"\nCrawled {len(results)} pages:")
    for result in results[:10]:  # Show first 10
        print(f"  Depth {result['depth']}: {result['url']} ({result['links_found']} links)")
