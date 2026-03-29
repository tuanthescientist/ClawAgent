"""
Hybrid LLM Controller with fallback and circuit breaker.

Features:
- Multiple provider support with automatic fallback
- Circuit breaker pattern for reliability
- Performance tracking and metrics
- Retry logic with exponential backoff
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
import asyncio
from dataclasses import dataclass, field
from enum import Enum

from .llm_provider import BaseLLMProvider, LLMResponse, Message


class CircuitState(str, Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class CircuitBreakerState:
    """Tracks circuit breaker state for a provider"""
    name: str
    failure_threshold: int = 5
    timeout_seconds: int = 60
    success_threshold: int = 2

    failure_count: int = 0
    success_count: int = 0
    last_failure_time: Optional[datetime] = None
    state: CircuitState = CircuitState.CLOSED

    def record_success(self):
        """Record successful request"""
        self.failure_count = 0
        
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.success_threshold:
                self.state = CircuitState.CLOSED
                self.success_count = 0
                logging.info(f"Circuit breaker for {self.name}: CLOSED (recovered)")

    def record_failure(self):
        """Record failed request"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        self.success_count = 0
        
        if self.failure_count >= self.failure_threshold and self.state == CircuitState.CLOSED:
            self.state = CircuitState.OPEN
            logging.warning(
                f"Circuit breaker for {self.name}: OPEN "
                f"({self.failure_count} failures)"
            )

    def is_available(self) -> bool:
        """Check if provider is available"""
        if self.state == CircuitState.CLOSED:
            return True

        if self.state == CircuitState.OPEN:
            # Check if timeout has passed
            if self.last_failure_time:
                elapsed = (datetime.now() - self.last_failure_time).total_seconds()
                if elapsed > self.timeout_seconds:
                    self.state = CircuitState.HALF_OPEN
                    self.failure_count = 0
                    logging.info(f"Circuit breaker for {self.name}: HALF_OPEN (testing)")
                    return True
            return False

        # HALF_OPEN state
        return True

    def __repr__(self) -> str:
        return f"CircuitBreaker({self.name}, state={self.state.value})"


@dataclass
class ProviderStats:
    """Performance statistics for a provider"""
    name: str
    requests: int = 0
    successes: int = 0
    failures: int = 0
    avg_latency_ms: float = 0.0
    max_latency_ms: float = 0.0
    min_latency_ms: float = float('inf')
    total_tokens: int = 0

    def update(self, success: bool, latency_ms: float, tokens: int = 0):
        """Update statistics"""
        self.requests += 1
        if success:
            self.successes += 1
        else:
            self.failures += 1

        # Update latency stats
        self.max_latency_ms = max(self.max_latency_ms, latency_ms)
        self.min_latency_ms = min(self.min_latency_ms, latency_ms)

        # Rolling average for latency
        if self.requests == 1:
            self.avg_latency_ms = latency_ms
        else:
            self.avg_latency_ms = (
                (self.avg_latency_ms * (self.requests - 1) + latency_ms)
                / self.requests
            )

        self.total_tokens += tokens

    def success_rate(self) -> float:
        """Get success rate percentage"""
        if self.requests == 0:
            return 0.0
        return (self.successes / self.requests) * 100

    def __repr__(self) -> str:
        return (
            f"Stats({self.name}, "
            f"success_rate={self.success_rate():.1f}%, "
            f"avg_latency={self.avg_latency_ms:.0f}ms)"
        )


class HybridLLMController:
    """
    Manages multiple LLM providers with fallback support.

    Example:
        controller = HybridLLMController(
            providers={
                "openai": OpenAIProvider(openai_config),
                "ollama": OllamaProvider(ollama_config),
            },
            fallback_chain=["openai", "ollama"],
            retry_count=3
        )

        response = await controller.complete(messages)
    """

    def __init__(
        self,
        providers: Dict[str, BaseLLMProvider],
        fallback_chain: List[str],
        retry_count: int = 3,
        timeout_seconds: int = 30,
        circuit_breaker_enabled: bool = True,
    ):
        """
        Initialize hybrid controller.

        Args:
            providers: Dict of provider_name -> provider_instance
            fallback_chain: List of provider names in fallback order
            retry_count: Max retries per provider
            timeout_seconds: Timeout per request
            circuit_breaker_enabled: Enable circuit breaker pattern
        """
        self.providers = providers
        self.fallback_chain = fallback_chain
        self.retry_count = retry_count
        self.timeout_seconds = timeout_seconds
        self.circuit_breaker_enabled = circuit_breaker_enabled
        
        self.logger = logging.getLogger(self.__class__.__name__)

        # Initialize circuit breakers
        self.circuit_breakers: Dict[str, CircuitBreakerState] = {
            name: CircuitBreakerState(name)
            for name in providers.keys()
        }

        # Initialize statistics
        self.stats: Dict[str, ProviderStats] = {
            name: ProviderStats(name)
            for name in providers.keys()
        }

    async def complete(
        self,
        messages: List[Message],
        primary_provider: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Get completion with fallback support.

        Tries providers in order:
        1. Primary provider (if specified and available)
        2. Fallback chain (in order)

        Args:
            messages: Chat message history
            primary_provider: Provider to try first
            **kwargs: Additional provider-specific arguments

        Returns:
            LLMResponse with completion

        Raises:
            RuntimeError: If all providers fail
        """
        providers_to_try = []

        # Add primary provider first if specified
        if primary_provider and primary_provider in self.providers:
            if self._is_provider_available(primary_provider):
                providers_to_try.append(primary_provider)

        # Add fallback chain
        for provider_name in self.fallback_chain:
            if provider_name not in providers_to_try:
                if self._is_provider_available(provider_name):
                    providers_to_try.append(provider_name)

        if not providers_to_try:
            raise RuntimeError(
                "No LLM providers available. All circuit breakers are open."
            )

        last_error = None

        for provider_name in providers_to_try:
            provider = self.providers[provider_name]

            for attempt in range(self.retry_count):
                try:
                    self.logger.debug(
                        f"Attempting {provider_name} "
                        f"(attempt {attempt + 1}/{self.retry_count})"
                    )

                    # Execute with timeout
                    start_time = datetime.now()
                    response = await provider.with_timeout(
                        provider.complete(messages, **kwargs),
                        timeout=self.timeout_seconds
                    )
                    latency_ms = (datetime.now() - start_time).total_seconds() * 1000

                    # Update stats and circuit breaker
                    self.stats[provider_name].update(
                        success=True,
                        latency_ms=latency_ms,
                        tokens=response.tokens_used
                    )
                    self.circuit_breakers[provider_name].record_success()

                    self.logger.info(
                        f"✓ {provider_name} success "
                        f"(latency: {latency_ms:.0f}ms, tokens: {response.tokens_used})"
                    )

                    return response

                except Exception as e:
                    last_error = e
                    error_msg = str(e)
                    self.logger.warning(
                        f"✗ {provider_name} failed: {error_msg} "
                        f"(attempt {attempt + 1}/{self.retry_count})"
                    )

                    # Update stats
                    self.stats[provider_name].update(success=False, latency_ms=0)

                    # Only record circuit breaker failure on last attempt
                    if attempt == self.retry_count - 1:
                        self.circuit_breakers[provider_name].record_failure()

                    # Exponential backoff between retries
                    if attempt < self.retry_count - 1:
                        backoff_ms = 100 * (2 ** attempt)
                        await asyncio.sleep(backoff_ms / 1000)

        # All providers failed
        raise RuntimeError(
            f"All LLM providers failed after {len(providers_to_try)} tries. "
            f"Last error: {last_error}"
        )

    def _is_provider_available(self, provider_name: str) -> bool:
        """Check if provider is available"""
        if provider_name not in self.providers:
            return False

        if not self.circuit_breaker_enabled:
            return True

        return self.circuit_breakers[provider_name].is_available()

    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics"""
        return {
            "timestamp": datetime.now().isoformat(),
            "providers": {
                name: {
                    "requests": stats.requests,
                    "successes": stats.successes,
                    "failures": stats.failures,
                    "success_rate": f"{stats.success_rate():.1f}%",
                    "avg_latency_ms": f"{stats.avg_latency_ms:.0f}",
                    "max_latency_ms": f"{stats.max_latency_ms:.0f}",
                    "min_latency_ms": f"{stats.min_latency_ms:.0f}",
                    "total_tokens": stats.total_tokens,
                    "circuit_breaker": {
                        "state": self.circuit_breakers[name].state.value,
                        "failure_count": self.circuit_breakers[name].failure_count,
                    }
                }
                for name, stats in self.stats.items()
            }
        }

    def reset_stats(self):
        """Reset all statistics"""
        for stats in self.stats.values():
            stats.requests = 0
            stats.successes = 0
            stats.failures = 0
            stats.avg_latency_ms = 0.0
            stats.total_tokens = 0

    async def health_check(self) -> Dict[str, Any]:
        """Check health of all providers"""
        health = {
            "timestamp": datetime.now().isoformat(),
            "overall_healthy": True,
            "providers": {}
        }

        for name, provider in self.providers.items():
            try:
                status = await provider.with_timeout(provider.health_check())
                health["providers"][name] = {
                    "healthy": status.get("healthy", False),
                    "latency_ms": status.get("latency_ms", 0),
                    "model": status.get("model", "unknown"),
                }
            except Exception as e:
                health["overall_healthy"] = False
                health["providers"][name] = {
                    "healthy": False,
                    "error": str(e),
                }

        return health

    def __repr__(self) -> str:
        return (
            f"HybridLLMController("
            f"providers={list(self.providers.keys())}, "
            f"fallback_chain={self.fallback_chain})"
        )
