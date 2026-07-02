import logging
import httpx
from typing import Optional, List, Dict, Any
from abc import ABC, abstractmethod

logger = logging.getLogger("aether.integrations.llm_providers")

class LLMProvider(ABC):
    """Abstract Base Class for modular LLM providers."""
    
    @abstractmethod
    async def generate_text(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        """Generates text based on a prompt and optional system instruction."""
        pass


class MockLLMProvider(LLMProvider):
    """Fallback Mock LLM provider when no API keys are configured or for local testing."""
    
    async def generate_text(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        logger.info("Using Mock LLM Provider...")
        return (
            f"[Mock LLM Response]\n"
            f"System Instruction: {system_instruction or 'None'}\n"
            f"Prompt: {prompt[:100]}...\n\n"
            f"This is a simulated high-quality response from AETHER's Mock LLM integration."
        )


class GeminiLLMProvider(LLMProvider):
    """Google Gemini API Provider using raw HTTP requests (no SDK dependency)."""
    
    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash"):
        self.api_key = api_key
        self.model_name = model_name
        self.url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"

    async def generate_text(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        logger.info(f"Generating text via Gemini API ({self.model_name})...")
        
        payload: Dict[str, Any] = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ]
        }
        
        if system_instruction:
            payload["systemInstruction"] = {
                "parts": [{"text": system_instruction}]
            }
            
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(self.url, json=payload)
                response.raise_for_status()
                data = response.json()
                
                # Extract text from Gemini response structure
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                return text
        except Exception as e:
            logger.error(f"Gemini API call failed: {e}. Falling back to Mock response.", exc_info=True)
            mock = MockLLMProvider()
            return await mock.generate_text(prompt, system_instruction)


class OpenAILLMProvider(LLMProvider):
    """OpenAI API Provider using raw HTTP requests."""
    
    def __init__(self, api_key: str, model_name: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model_name = model_name
        self.url = "https://api.openai.com/v1/chat/completions"

    async def generate_text(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        logger.info(f"Generating text via OpenAI API ({self.model_name})...")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.model_name,
            "messages": messages
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(self.url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                
                text = data["choices"][0]["message"]["content"]
                return text
        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}. Falling back to Mock response.", exc_info=True)
            mock = MockLLMProvider()
            return await mock.generate_text(prompt, system_instruction)


def get_llm_provider() -> LLMProvider:
    """Factory function to instantiate the configured LLM provider based on settings."""
    from aether.core.config import settings
    
    gemini_key = settings.gemini_api_key.get_secret_value() if settings.gemini_api_key else None
    openai_key = settings.openai_api_key.get_secret_value() if settings.openai_api_key else None
    
    if gemini_key:
        logger.info("Initializing Gemini LLM Provider.")
        return GeminiLLMProvider(api_key=gemini_key)
    elif openai_key:
        logger.info("Initializing OpenAI LLM Provider.")
        return OpenAILLMProvider(api_key=openai_key)
    else:
        logger.warning("No LLM API keys configured. Initializing Mock LLM Provider.")
        return MockLLMProvider()
