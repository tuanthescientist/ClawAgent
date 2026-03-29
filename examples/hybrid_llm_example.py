"""
Example: Using ClawAgent v3.0 with Hybrid LLM Backend

This example shows how to:
1. Configure multiple LLM providers
2. Setup the hybrid controller with fallback
3. Use the agent with automatic provider selection
4. Monitor performance and health
"""

import asyncio
import logging
from typing import List

from src.core.config import AppConfig, LLMBackendType
from src.core.llm_provider import Message
from src.core.hybrid_controller import HybridLLMController
from src.llm.openai_provider import OpenAIProvider
from src.llm.ollama_provider import OllamaProvider

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def example_hybrid_llm():
    """Example: Hybrid LLM with fallback"""
    
    logger.info("=" * 60)
    logger.info("ClawAgent v3.0 - Hybrid LLM Example")
    logger.info("=" * 60)

    # ===== Setup Configuration =====
    config = AppConfig(
        LLM_BACKEND=LLMBackendType.HYBRID,
        FALLBACK_CHAIN=[
            LLMBackendType.OPENAI,
            LLMBackendType.GROQ,
            LLMBackendType.OLLAMA,
        ],
        OPENAI_API_KEY="sk-...",  # Your key
        OLLAMA_HOST="http://localhost:11434",
        OLLAMA_MODEL="qwen2.5:14b",
    )

    logger.info(f"Config: {config.LLM_BACKEND} with fallback chain {config.FALLBACK_CHAIN}")

    # ===== Setup Providers =====
    providers = {}

    # OpenAI Provider
    try:
        providers["openai"] = OpenAIProvider({
            "api_key": config.OPENAI_API_KEY,
            "model": "gpt-4-turbo",
            "temperature": 0.7,
            "max_tokens": 2000,
            "timeout": 30,
        })
        logger.info("✓ OpenAI provider initialized")
    except Exception as e:
        logger.warning(f"✗ OpenAI provider failed: {e}")

    # Ollama Provider (local)
    try:
        providers["ollama"] = OllamaProvider({
            "host": config.OLLAMA_HOST,
            "model": config.OLLAMA_MODEL,
            "temperature": 0.7,
            "max_tokens": 2000,
            "timeout": 60,
        })
        logger.info("✓ Ollama provider initialized")
    except Exception as e:
        logger.warning(f"✗ Ollama provider failed: {e}")

    if not providers:
        logger.error("❌ No providers available!")
        return

    # ===== Setup Hybrid Controller =====
    controller = HybridLLMController(
        providers=providers,
        fallback_chain=["openai", "ollama"],
        retry_count=2,
        timeout_seconds=30,
        circuit_breaker_enabled=True,
    )
    logger.info(f"Hybrid controller initialized: {controller}")

    # ===== Health Check =====
    logger.info("\n--- Health Check ---")
    health = await controller.health_check()
    for provider_name, status in health["providers"].items():
        symbol = "✓" if status.get("healthy") else "✗"
        logger.info(f"{symbol} {provider_name}: {status}")

    # ===== Test Completion =====
    logger.info("\n--- Testing Completion ---")

    messages = [
        Message(role="system", content="You are a helpful assistant."),
        Message(role="user", content="Explain machine learning in 2 sentences.")
    ]

    try:
        logger.info("Requesting completion...")
        response = await controller.complete(messages)

        logger.info(f"\n✓ Completion successful!")
        logger.info(f"  Model: {response.model}")
        logger.info(f"  Tokens: {response.tokens_used} (input: {response.tokens_input}, output: {response.tokens_output})")
        logger.info(f"  Content: {response.content[:100]}...")

    except Exception as e:
        logger.error(f"❌ Completion failed: {e}")

    # ===== Test Streaming =====
    logger.info("\n--- Testing Streaming ---")

    try:
        logger.info("Requesting streaming completion...")
        print("\nStreaming output: ", end="", flush=True)

        async for chunk in providers["openai"].complete_stream(messages):
            print(chunk, end="", flush=True)

        print("\n✓ Streaming completed")

    except Exception as e:
        logger.warning(f"⚠️  Streaming failed: {e}")

    # ===== Statistics =====
    logger.info("\n--- Performance Statistics ---")
    stats = controller.get_stats()

    for provider_name, provider_stats in stats["providers"].items():
        logger.info(f"\n{provider_name}:")
        logger.info(f"  Requests: {provider_stats['requests']}")
        logger.info(f"  Success rate: {provider_stats['success_rate']}")
        logger.info(f"  Avg latency: {provider_stats['avg_latency_ms']:.0f}ms")
        logger.info(f"  Total tokens: {provider_stats['total_tokens']}")
        logger.info(f"  Circuit breaker: {provider_stats['circuit_breaker']['state']}")

    # ===== Test Fallback (Optional) =====
    logger.info("\n--- Testing Fallback Chain ---")
    logger.info("To test fallback:")
    logger.info("1. Stop your OpenAI API or set invalid API key")
    logger.info("2. Make sure Ollama is running locally")
    logger.info("3. Run this example again")
    logger.info("4. Watch as controller automatically falls back to Ollama")


async def example_conversation_with_trace():
    """Example: Multi-turn conversation with reasoning trace"""
    
    logger.info("\n" + "=" * 60)
    logger.info("ClawAgent v3.0 - Conversation Example")
    logger.info("=" * 60)

    # Setup (simplified)
    try:
        provider = OpenAIProvider({
            "api_key": "sk-...",
            "model": "gpt-4-turbo",
        })
    except Exception as e:
        logger.error(f"Provider initialization failed: {e}")
        return

    # Simulate a conversation
    messages = [
        Message(role="system", content="You are a helpful programming assistant."),
        Message(role="user", content="Write a simple Python function to reverse a string."),
    ]

    try:
        response = await provider.complete(messages)
        logger.info(f"\nAssistant: {response.content[:200]}...")

        # Add assistant response
        messages.append(Message(role="assistant", content=response.content))

        # Follow-up question
        messages.append(Message(role="user", content="Can you add error handling?"))

        response2 = await provider.complete(messages)
        logger.info(f"\nAssistant: {response2.content[:200]}...")

    except Exception as e:
        logger.error(f"Conversation failed: {e}")


async def example_benchmark():
    """Example: Benchmark different providers"""
    
    logger.info("\n" + "=" * 60)
    logger.info("ClawAgent v3.0 - Provider Benchmark")
    logger.info("=" * 60)

    benchmark_messages = [
        Message(role="user", content="What is 2+2?"),
    ]

    providers_to_test = {
        "openai": {
            "class": OpenAIProvider,
            "config": {
                "api_key": "sk-...",
                "model": "gpt-4-turbo",
            }
        },
        "ollama": {
            "class": OllamaProvider,
            "config": {
                "host": "http://localhost:11434",
                "model": "qwen2.5:14b",
            }
        }
    }

    results = {}

    for provider_name, provider_info in providers_to_test.items():
        try:
            logger.info(f"\nTesting {provider_name}...")
            
            provider = provider_info["class"](provider_info["config"])
            
            # Run health check
            health = await provider.health_check()
            logger.info(f"  Health: {health.get('healthy', False)}")
            logger.info(f"  Latency: {health.get('latency_ms', 'N/A')}ms")
            
            if not health.get("healthy"):
                logger.warning(f"  ⚠️  {provider_name} is not healthy")
                continue
            
            # Run completion
            response = await provider.complete(benchmark_messages)
            logger.info(f"  Response: {response.content[:50]}...")
            logger.info(f"  Tokens: {response.tokens_used}")
            
            results[provider_name] = {
                "healthy": True,
                "response_time_ms": response.latency_ms,
                "tokens": response.tokens_used,
            }

        except Exception as e:
            logger.error(f"  ✗ Error: {e}")
            results[provider_name] = {"healthy": False, "error": str(e)}

    logger.info("\n" + "=" * 40)
    logger.info("Benchmark Results:")
    for provider, result in results.items():
        if result["healthy"]:
            logger.info(f"  {provider}: {result['response_time_ms']:.0f}ms, {result['tokens']} tokens")
        else:
            logger.info(f"  {provider}: FAILED ({result.get('error', 'unknown')})")


async def main():
    """Run all examples"""
    
    # Run examples
    await example_hybrid_llm()
    # await example_conversation_with_trace()
    # await example_benchmark()

    logger.info("\n" + "=" * 60)
    logger.info("Examples completed!")
    logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
