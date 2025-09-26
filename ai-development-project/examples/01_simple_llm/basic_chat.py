#!/usr/bin/env python3
"""
Simple LLM Chat Example
=======================

A basic chatbot demonstrating LLM integration and prompt engineering.
This example works with both local (Ollama) and API-based LLMs.

Based on the ai-flight-tracker implementation from the main repository.
"""

import requests
import json
import os
from typing import Optional
import asyncio


class SimpleLLMChat:
    """Simple chatbot using LLM integration"""
    
    def __init__(self, model_type: str = "ollama", model_name: str = "llama3.1:8b"):
        self.model_type = model_type
        self.model_name = model_name
        self.conversation_history = []
        
    async def ask_question(self, question: str, context: str = "") -> str:
        """
        Ask a question to the LLM with optional context.
        
        Args:
            question: The user's question
            context: Additional context to provide to the LLM
            
        Returns:
            The LLM's response
        """
        
        # Build the prompt with context and conversation history
        prompt = self._build_prompt(question, context)
        
        try:
            if self.model_type == "ollama":
                response = await self._call_ollama(prompt)
            elif self.model_type == "openai":
                response = await self._call_openai(prompt)
            else:
                response = "Unsupported model type. Use 'ollama' or 'openai'"
            
            # Store in conversation history
            self.conversation_history.append({
                "question": question,
                "response": response,
                "context": context
            })
            
            return response
            
        except Exception as e:
            error_msg = f"Error getting response: {str(e)}"
            print(f"❌ {error_msg}")
            return error_msg
    
    def _build_prompt(self, question: str, context: str = "") -> str:
        """Build a well-structured prompt"""
        
        prompt_parts = []
        
        # System prompt
        prompt_parts.append("You are a helpful AI assistant. Provide accurate, helpful, and concise responses.")
        
        # Context if provided
        if context:
            prompt_parts.append(f"\nContext: {context}")
        
        # Conversation history (last 3 interactions)
        if self.conversation_history:
            prompt_parts.append("\nPrevious conversation:")
            for entry in self.conversation_history[-3:]:
                prompt_parts.append(f"Human: {entry['question']}")
                prompt_parts.append(f"Assistant: {entry['response']}")
        
        # Current question
        prompt_parts.append(f"\nHuman: {question}")
        prompt_parts.append("Assistant:")
        
        return "\n".join(prompt_parts)
    
    async def _call_ollama(self, prompt: str) -> str:
        """Call Ollama local API"""
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "max_tokens": 500
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "No response generated.")
            else:
                return f"Ollama API error: {response.status_code}"
                
        except requests.exceptions.ConnectionError:
            return "❌ Cannot connect to Ollama. Make sure it's running:\n" \
                   "1. Install: curl -fsSL https://ollama.ai/install.sh | sh\n" \
                   "2. Start: ollama serve\n" \
                   "3. Download model: ollama pull llama3.1:8b"
        except requests.exceptions.Timeout:
            return "❌ Request timed out. The model might be processing..."
        except Exception as e:
            return f"❌ Unexpected error: {str(e)}"
    
    async def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return "❌ OpenAI API key not found. Set OPENAI_API_KEY environment variable."
        
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 500,
                "temperature": 0.7
            }
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                return f"OpenAI API error: {response.status_code} - {response.text}"
                
        except Exception as e:
            return f"❌ OpenAI API error: {str(e)}"
    
    def get_conversation_summary(self) -> str:
        """Get a summary of the conversation"""
        if not self.conversation_history:
            return "No conversation history yet."
        
        summary = f"Conversation Summary ({len(self.conversation_history)} exchanges):\n"
        summary += "=" * 50 + "\n"
        
        for i, entry in enumerate(self.conversation_history[-5:], 1):  # Last 5 exchanges
            summary += f"\n{i}. Q: {entry['question'][:80]}{'...' if len(entry['question']) > 80 else ''}\n"
            summary += f"   A: {entry['response'][:80]}{'...' if len(entry['response']) > 80 else ''}\n"
        
        return summary


async def interactive_chat():
    """Run an interactive chat session"""
    print("🤖 Simple LLM Chat Demo")
    print("=" * 40)
    print("Available models:")
    print("1. Ollama (local) - Default")
    print("2. OpenAI (API key required)")
    print()
    
    # Model selection
    choice = input("Select model (1 for Ollama, 2 for OpenAI) [1]: ").strip()
    if choice == "2":
        chat = SimpleLLMChat(model_type="openai")
        print("Using OpenAI GPT-3.5-turbo")
    else:
        chat = SimpleLLMChat(model_type="ollama")
        print("Using Ollama llama3.1:8b")
    
    print("\nChat started! Type 'quit' to exit, 'history' to see conversation summary.")
    print("-" * 60)
    
    while True:
        try:
            # Get user input
            user_input = input("\n🧑 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break
            elif user_input.lower() == 'history':
                print("\n" + chat.get_conversation_summary())
                continue
            elif not user_input:
                continue
            
            # Get AI response
            print("🤖 Assistant: ", end="", flush=True)
            response = await chat.ask_question(user_input)
            print(response)
            
        except KeyboardInterrupt:
            print("\n\n👋 Chat interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


async def demo_examples():
    """Run some demo examples"""
    print("🚀 Running Demo Examples")
    print("=" * 40)
    
    chat = SimpleLLMChat()
    
    # Example 1: Simple question
    print("\n📝 Example 1: Simple Question")
    print("-" * 30)
    response = await chat.ask_question("What is Python?")
    print(f"Q: What is Python?")
    print(f"A: {response[:200]}{'...' if len(response) > 200 else ''}")
    
    # Example 2: Question with context
    print("\n📝 Example 2: Question with Context")
    print("-" * 30)
    context = "We're building a trading application with real-time market data."
    response = await chat.ask_question("What security considerations should we have?", context)
    print(f"Q: What security considerations should we have?")
    print(f"Context: {context}")
    print(f"A: {response[:200]}{'...' if len(response) > 200 else ''}")
    
    # Example 3: Follow-up question (uses conversation history)
    print("\n📝 Example 3: Follow-up Question")
    print("-" * 30)
    response = await chat.ask_question("Can you give me 3 specific examples?")
    print(f"Q: Can you give me 3 specific examples?")
    print(f"A: {response[:200]}{'...' if len(response) > 200 else ''}")
    
    # Show conversation summary
    print("\n📊 Conversation Summary:")
    print(chat.get_conversation_summary())


if __name__ == "__main__":
    print("🎯 Simple LLM Integration Example")
    print("=" * 50)
    print("This example demonstrates:")
    print("✅ Basic LLM integration (Ollama + OpenAI)")
    print("✅ Prompt engineering techniques")
    print("✅ Conversation memory")
    print("✅ Error handling")
    print("✅ Context management")
    print()
    
    mode = input("Run in (1) Demo mode or (2) Interactive mode? [1]: ").strip()
    
    if mode == "2":
        asyncio.run(interactive_chat())
    else:
        asyncio.run(demo_examples())