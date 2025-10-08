#!/usr/bin/env python3
"""
Synchronous AI API Calls
=========================

This example demonstrates synchronous AI API calls using the requests library.
Suitable for simple scripts, testing, and learning.
"""

import os
import time
import requests
from typing import List, Dict, Optional


class SyncAIClient:
    """Synchronous AI client for simple use cases"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: str = "http://localhost:11434"):
        """
        Initialize sync AI client
        
        Args:
            api_key: API key (not needed for Ollama)
            base_url: Base URL for API (default: Ollama local)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = base_url
        self.is_ollama = "11434" in base_url or "ollama" in base_url.lower()
    
    def generate_text(
        self,
        prompt: str,
        model: str = "llama3.1:8b",
        max_tokens: int = 500,
        temperature: float = 0.7
    ) -> Dict:
        """
        Generate text synchronously
        
        Args:
            prompt: Input prompt
            model: Model name
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Dictionary with response and metadata
        """
        start_time = time.time()
        
        try:
            if self.is_ollama:
                response = self._call_ollama(prompt, model)
            else:
                response = self._call_openai(prompt, model, max_tokens, temperature)
            
            elapsed = time.time() - start_time
            
            return {
                "success": True,
                "response": response,
                "elapsed_time": elapsed,
                "model": model
            }
        
        except Exception as e:
            elapsed = time.time() - start_time
            return {
                "success": False,
                "error": str(e),
                "elapsed_time": elapsed,
                "model": model
            }
    
    def _call_ollama(self, prompt: str, model: str) -> str:
        """Call Ollama API"""
        url = f"{self.base_url}/api/generate"
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        
        return response.json()["response"]
    
    def _call_openai(
        self,
        prompt: str,
        model: str,
        max_tokens: int,
        temperature: float
    ) -> str:
        """Call OpenAI API"""
        url = f"{self.base_url}/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        return response.json()["choices"][0]["message"]["content"]


# ============================================================================
# EXAMPLE 1: Single Request
# ============================================================================

def example_single_request():
    """Example: Single AI request"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Single Synchronous Request")
    print("="*60)
    
    client = SyncAIClient()
    
    prompt = "Explain what an async function is in one sentence."
    print(f"\n📝 Prompt: {prompt}")
    
    result = client.generate_text(prompt)
    
    if result["success"]:
        print(f"\n✅ Response: {result['response']}")
        print(f"⏱️  Time: {result['elapsed_time']:.2f}s")
    else:
        print(f"\n❌ Error: {result['error']}")


# ============================================================================
# EXAMPLE 2: Multiple Sequential Requests
# ============================================================================

def example_sequential_requests():
    """Example: Multiple requests processed sequentially"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Multiple Sequential Requests")
    print("="*60)
    
    client = SyncAIClient()
    
    prompts = [
        "What is Python?",
        "What is async programming?",
        "What is an event loop?"
    ]
    
    print(f"\n📝 Processing {len(prompts)} prompts sequentially...")
    
    start_time = time.time()
    results = []
    
    for i, prompt in enumerate(prompts, 1):
        print(f"\n🔄 Request {i}/{len(prompts)}: {prompt}")
        result = client.generate_text(prompt)
        results.append(result)
        
        if result["success"]:
            print(f"   ✅ Completed in {result['elapsed_time']:.2f}s")
        else:
            print(f"   ❌ Failed: {result['error']}")
    
    total_time = time.time() - start_time
    
    print(f"\n📊 Summary:")
    print(f"   Total time: {total_time:.2f}s")
    print(f"   Average time per request: {total_time/len(prompts):.2f}s")
    print(f"   Successful: {sum(1 for r in results if r['success'])}/{len(results)}")


# ============================================================================
# EXAMPLE 3: Batch Processing with Progress
# ============================================================================

def example_batch_processing():
    """Example: Processing a batch of items"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Batch Processing")
    print("="*60)
    
    client = SyncAIClient()
    
    # Create a batch of items to analyze
    topics = [
        "artificial intelligence",
        "machine learning",
        "neural networks",
        "deep learning",
        "natural language processing"
    ]
    
    print(f"\n📝 Analyzing {len(topics)} topics...")
    
    start_time = time.time()
    results = []
    
    for i, topic in enumerate(topics, 1):
        prompt = f"Define {topic} in one sentence."
        print(f"\n[{i}/{len(topics)}] Analyzing: {topic}")
        
        result = client.generate_text(prompt)
        results.append({
            "topic": topic,
            "result": result
        })
        
        if result["success"]:
            response = result["response"]
            # Truncate long responses for display
            display_response = response[:100] + "..." if len(response) > 100 else response
            print(f"   ✅ {display_response}")
        else:
            print(f"   ❌ Error: {result['error']}")
    
    total_time = time.time() - start_time
    successful = sum(1 for r in results if r["result"]["success"])
    
    print(f"\n📊 Batch Processing Summary:")
    print(f"   Total items: {len(topics)}")
    print(f"   Successful: {successful}")
    print(f"   Failed: {len(topics) - successful}")
    print(f"   Total time: {total_time:.2f}s")
    print(f"   Average per item: {total_time/len(topics):.2f}s")


# ============================================================================
# EXAMPLE 4: Simple Error Handling
# ============================================================================

def example_error_handling():
    """Example: Handling API errors"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Error Handling")
    print("="*60)
    
    # Create client with invalid endpoint to simulate error
    client = SyncAIClient(base_url="http://localhost:99999")
    
    print("\n🔄 Attempting request to invalid endpoint...")
    
    result = client.generate_text("Test prompt")
    
    if result["success"]:
        print(f"✅ Response: {result['response']}")
    else:
        print(f"❌ Error handled gracefully: {result['error']}")
        print(f"⏱️  Failed after {result['elapsed_time']:.2f}s")


# ============================================================================
# EXAMPLE 5: Simple Retry Logic
# ============================================================================

def example_retry_logic():
    """Example: Simple retry logic for failed requests"""
    print("\n" + "="*60)
    print("EXAMPLE 5: Retry Logic")
    print("="*60)
    
    def make_request_with_retry(
        client: SyncAIClient,
        prompt: str,
        max_retries: int = 3
    ) -> Dict:
        """Make request with simple retry logic"""
        
        for attempt in range(max_retries):
            print(f"\n🔄 Attempt {attempt + 1}/{max_retries}")
            
            result = client.generate_text(prompt)
            
            if result["success"]:
                print("   ✅ Success!")
                return result
            else:
                print(f"   ❌ Failed: {result['error']}")
                
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    print(f"   ⏳ Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
        
        print(f"\n❌ All {max_retries} attempts failed")
        return result
    
    # Test with a valid client
    client = SyncAIClient()
    prompt = "What is a coroutine?"
    
    result = make_request_with_retry(client, prompt, max_retries=3)
    
    if result["success"]:
        print(f"\n✅ Final result: {result['response'][:100]}...")


# ============================================================================
# COMPARISON: Why This Might Be Slow
# ============================================================================

def comparison_sync_performance():
    """Show why sync can be slow for multiple requests"""
    print("\n" + "="*60)
    print("PERFORMANCE ANALYSIS: Synchronous Approach")
    print("="*60)
    
    client = SyncAIClient()
    
    # Simulate making 5 requests
    num_requests = 5
    avg_request_time = 2.0  # seconds
    
    print(f"\n📊 Making {num_requests} requests synchronously")
    print(f"   Average request time: {avg_request_time}s")
    print(f"   Expected total time: {num_requests * avg_request_time}s")
    
    print("\n⏱️  Timeline:")
    for i in range(1, num_requests + 1):
        print(f"   Request {i}: {'█' * 10} ({avg_request_time}s)")
    
    print(f"\n   Total: {num_requests * avg_request_time}s")
    
    print("\n💡 With async programming:")
    print(f"   All {num_requests} requests could run concurrently")
    print(f"   Total time: ~{avg_request_time}s (just one request time)")
    print(f"   Speedup: {num_requests}x faster! 🚀")


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Run all examples"""
    print("🔄 Synchronous AI API Calls Examples\n")
    print("This demonstrates sync AI integration patterns.")
    print("Sync is good for: scripts, testing, simple use cases")
    
    try:
        # Run examples
        example_single_request()
        example_sequential_requests()
        example_batch_processing()
        example_error_handling()
        example_retry_logic()
        comparison_sync_performance()
        
        print("\n" + "="*60)
        print("✅ All examples completed!")
        print("="*60)
        
        print("\n💡 When to use sync AI calls:")
        print("   ✅ Simple scripts and one-off tasks")
        print("   ✅ Testing and experimentation")
        print("   ✅ Sequential processing requirements")
        print("   ✅ Single-user applications")
        
        print("\n⚠️  Limitations of sync approach:")
        print("   ❌ Cannot handle concurrent requests efficiently")
        print("   ❌ Slow for processing multiple items")
        print("   ❌ Not suitable for web servers")
        print("   ❌ Blocks during I/O operations")
        
        print("\n📚 Next: Check out async examples for better performance!")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
