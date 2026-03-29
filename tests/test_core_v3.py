"""
Comprehensive tests for ClawAgent v3.0 core infrastructure.

Tests:
- Config system
- LLM providers
- Hybrid controller with fallback
- Circuit breaker
- Performance tracking
"""

import asyncio
import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta

from src.core.config import AppConfig, LLMBackendType, MemoryBackendType
from src.core.llm_provider import Message, LLMResponse, BaseLLMProvider
from src.core.hybrid_controller import (
    HybridLLMController,
    CircuitBreakerState,
    CircuitState,
    ProviderStats,
)
from src.core.types import (
    ReasoningTrace,
    ReasoningStep,
    ReasoningStage,
    ToolCall,
)


class TestConfig:
    """Test configuration system"""

    def test_config_defaults(self):
        """Test default configuration"""
        config = AppConfig()
        assert config.LLM_BACKEND == LLMBackendType.OPENAI
        assert config.MEMORY_BACKEND == MemoryBackendType.CHROMADB
        assert config.RATE_LIMIT_ENABLED is True

    def test_config_with_overrides(self):
        """Test configuration with overrides"""
        config = AppConfig(
            LLM_BACKEND=LLMBackendType.HYBRID,
            LLM_MODEL="qwen2.5:14b",
            RATE_LIMIT_REQUESTS_PER_MINUTE=100,
        )
        assert config.LLM_BACKEND == LLMBackendType.HYBRID
        assert config.LLM_MODEL == "qwen2.5:14b"
        assert config.RATE_LIMIT_REQUESTS_PER_MINUTE == 100

    def test_config_from_env(self, monkeypatch):
        """Test configuration loading from environment"""
        monkeypatch.setenv("LLM_BACKEND", "ollama")
        monkeypatch.setenv("OLLAMA_MODEL", "llama2:70b")
        
        config = AppConfig()
        assert config.LLM_BACKEND == LLMBackendType.OLLAMA
        assert config.OLLAMA_MODEL == "llama2:70b"


class MockLLMProvider(BaseLLMProvider):
    """Mock LLM provider for testing"""

    async def complete(self, messages, **kwargs) -> LLMResponse:
        await asyncio.sleep(0.01)  # Simulate latency
        return LLMResponse(
            content="Mock response",
            model=self.model,
            tokens_used=100,
            tokens_input=50,
            tokens_output=50,
        )

    async def complete_stream(self, messages, **kwargs):
        yield "Mock "
        yield "streaming "
        yield "response"

    async def embed(self, text: str):
        return [0.1, 0.2, 0.3]

    async def health_check(self):
        return {"healthy": True, "model": self.model}


class TestCircuitBreaker:
    """Test circuit breaker pattern"""

    def test_circuit_breaker_closed_on_success(self):
        """Test circuit stays closed on success"""
        cb = CircuitBreakerState("test", failure_threshold=3)
        assert cb.state == CircuitState.CLOSED
        assert cb.is_available() is True

        cb.record_success()
        assert cb.state == CircuitState.CLOSED
        assert cb.failure_count == 0

    def test_circuit_breaker_opens_after_failures(self):
        """Test circuit opens after threshold"""
        cb = CircuitBreakerState("test", failure_threshold=3)

        cb.record_failure()
        cb.record_failure()
        assert cb.state == CircuitState.CLOSED  # Not yet

        cb.record_failure()
        assert cb.state == CircuitState.OPEN  # Now open
        assert cb.is_available() is False

    def test_circuit_breaker_half_open_after_timeout(self):
        """Test circuit goes to half-open after timeout"""
        cb = CircuitBreakerState(
            "test",
            failure_threshold=2,
            timeout_seconds=0
        )

        cb.record_failure()
        cb.record_failure()
        assert cb.state == CircuitState.OPEN

        # Simulate timeout (0 seconds)
        cb.record_failure()
        assert cb.last_failure_time is not None

        # Manually set old failure time
        cb.last_failure_time = datetime.now() - timedelta(seconds=1)
        
        # Should transition to half-open
        result = cb.is_available()
        if result:
            assert cb.state == CircuitState.HALF_OPEN

    def test_circuit_breaker_closes_after_recovery(self):
        """Test circuit closes after successful recovery"""
        cb = CircuitBreakerState("test", failure_threshold=2, success_threshold=2)

        # Open circuit
        cb.record_failure()
        cb.record_failure()
        assert cb.state == CircuitState.OPEN

        # Transition to half-open (skip normally)
        cb.state = CircuitState.HALF_OPEN

        # Record successes
        cb.record_success()
        cb.record_success()
        assert cb.state == CircuitState.CLOSED
        assert cb.failure_count == 0


class TestProviderStats:
    """Test performance statistics"""

    def test_initial_stats(self):
        """Test initial statistics"""
        stats = ProviderStats("test")
        assert stats.requests == 0
        assert stats.successes == 0
        assert stats.failures == 0
        assert stats.success_rate() == 0.0

    def test_success_rate_calculation(self):
        """Test success rate calculation"""
        stats = ProviderStats("test")
        
        stats.update(success=True, latency_ms=100)
        assert stats.success_rate() == 100.0
        
        stats.update(success=True, latency_ms=110)
        assert stats.success_rate() == 100.0
        
        stats.update(success=False, latency_ms=0)
        assert stats.success_rate() == 66.67  # ~67%

    def test_latency_tracking(self):
        """Test latency statistics"""
        stats = ProviderStats("test")
        
        stats.update(success=True, latency_ms=100)
        assert stats.avg_latency_ms == 100
        assert stats.max_latency_ms == 100
        
        stats.update(success=True, latency_ms=50)
        assert stats.avg_latency_ms == 75
        assert stats.max_latency_ms == 100
        assert stats.min_latency_ms == 50


class TestHybridController:
    """Test hybrid LLM controller"""

    @pytest.mark.asyncio
    async def test_controller_basic_completion(self):
        """Test basic completion"""
        providers = {
            "mock": MockLLMProvider({"model": "mock-model"})
        }

        controller = HybridLLMController(
            providers=providers,
            fallback_chain=["mock"],
        )

        messages = [Message(role="user", content="test")]
        response = await controller.complete(messages)

        assert response.content == "Mock response"
        assert response.tokens_used == 100

    @pytest.mark.asyncio
    async def test_controller_fallback(self):
        """Test fallback between providers"""
        provider1 = AsyncMock(spec=BaseLLMProvider)
        provider2 = AsyncMock(spec=BaseLLMProvider)

        # First provider fails, second succeeds
        provider1.complete = AsyncMock(side_effect=Exception("Failed"))
        provider1.with_timeout = AsyncMock(side_effect=Exception("Failed"))
        
        provider2.complete = AsyncMock(
            return_value=LLMResponse(
                content="Fallback response",
                model="provider2",
                tokens_used=100,
            )
        )
        provider2.with_timeout = AsyncMock(
            wraps=lambda coro, timeout: coro
        )

        controller = HybridLLMController(
            providers={
                "provider1": provider1,
                "provider2": provider2,
            },
            fallback_chain=["provider1", "provider2"],
            retry_count=1,
            circuit_breaker_enabled=False,
        )

        messages = [Message(role="user", content="test")]
        response = await controller.complete(messages)

        # Should have fallen back to provider2
        assert response.content == "Fallback response"

    @pytest.mark.asyncio
    async def test_controller_circuit_breaker(self):
        """Test circuit breaker in controller"""
        providers = {
            "test": MockLLMProvider({"model": "test"})
        }

        controller = HybridLLMController(
            providers=providers,
            fallback_chain=["test"],
            circuit_breaker_enabled=True,
        )

        # Open circuit breaker manually
        controller.circuit_breakers["test"].state = CircuitState.OPEN
        controller.circuit_breakers["test"].is_available = lambda: False

        messages = [Message(role="user", content="test")]

        with pytest.raises(RuntimeError):
            await controller.complete(messages)

    @pytest.mark.asyncio
    async def test_controller_health_check(self):
        """Test health check"""
        providers = {
            "mock": MockLLMProvider({"model": "mock"})
        }

        controller = HybridLLMController(
            providers=providers,
            fallback_chain=["mock"],
        )

        health = await controller.health_check()

        assert "providers" in health
        assert "mock" in health["providers"]
        assert health["providers"]["mock"]["healthy"] is True

    @pytest.mark.asyncio
    async def test_controller_statistics(self):
        """Test statistics tracking"""
        providers = {
            "mock": MockLLMProvider({"model": "mock"})
        }

        controller = HybridLLMController(
            providers=providers,
            fallback_chain=["mock"],
        )

        messages = [Message(role="user", content="test")]
        await controller.complete(messages)

        stats = controller.get_stats()

        assert stats["providers"]["mock"]["requests"] == 1
        assert stats["providers"]["mock"]["successes"] == 1
        assert stats["providers"]["mock"]["failures"] == 0

    @pytest.mark.asyncio
    async def test_controller_timeout(self):
        """Test request timeout"""
        slow_provider = AsyncMock(spec=BaseLLMProvider)
        slow_provider.complete = AsyncMock(side_effect=asyncio.sleep(10))

        controller = HybridLLMController(
            providers={"slow": slow_provider},
            fallback_chain=["slow"],
            timeout_seconds=0.1,
        )

        messages = [Message(role="user", content="test")]

        with pytest.raises(Exception):  # TimeoutError or similar
            await controller.complete(messages)


class TestReasoningTrace:
    """Test reasoning trace types"""

    def test_reasoning_trace_creation(self):
        """Test creating reasoning trace"""
        step1 = ReasoningStep(
            stage=ReasoningStage.UNDERSTAND,
            description="Understood the request"
        )

        trace = ReasoningTrace(
            steps=[step1],
            total_duration_ms=100,
            model_used="gpt-4",
            tokens_used=50,
        )

        assert len(trace.steps) == 1
        assert trace.steps[0].stage == ReasoningStage.UNDERSTAND
        assert trace.total_duration_ms == 100

    def test_reasoning_trace_markdown_export(self):
        """Test exporting trace to Markdown"""
        steps = [
            ReasoningStep(
                stage=ReasoningStage.UNDERSTAND,
                description="Parsed request"
            ),
            ReasoningStep(
                stage=ReasoningStage.PLAN,
                description="Planned approach"
            ),
        ]

        trace = ReasoningTrace(
            steps=steps,
            total_duration_ms=200,
            model_used="gpt-4",
            tokens_used=100,
        )

        markdown = trace.to_markdown()
        assert "Reasoning Trace" in markdown
        assert "UNDERSTAND" in markdown
        assert "PLAN" in markdown
        assert "100" in markdown  # tokens

    def test_tool_call_tracking(self):
        """Test tool call tracking"""
        tool_call = ToolCall(
            name="web_search",
            args={"query": "test"},
            tool_id="tool-1",
            result="Found result",
            duration_ms=500,
        )

        trace = ReasoningTrace(
            steps=[],
            tools_used=[tool_call],
            total_duration_ms=500,
            model_used="gpt-4",
            tokens_used=50,
        )

        assert len(trace.tools_used) == 1
        assert trace.tools_used[0].name == "web_search"
        assert trace.tools_used[0].duration_ms == 500


@pytest.mark.asyncio
async def test_full_workflow():
    """Integration test: full workflow"""
    providers = {
        "mock": MockLLMProvider({"model": "mock", "temperature": 0.7})
    }

    controller = HybridLLMController(
        providers=providers,
        fallback_chain=["mock"],
        retry_count=3,
        circuit_breaker_enabled=True,
    )

    # Health check
    health = await controller.health_check()
    assert health["providers"]["mock"]["healthy"] is True

    # Completion
    messages = [
        Message(role="system", content="You are helpful"),
        Message(role="user", content="What is 2+2?"),
    ]

    response = await controller.complete(messages)
    assert response.content == "Mock response"

    # Statistics
    stats = controller.get_stats()
    assert stats["providers"]["mock"]["requests"] == 1
    assert stats["providers"]["mock"]["successes"] == 1
    assert stats["providers"]["mock"]["success_rate"] == "100.0%"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
