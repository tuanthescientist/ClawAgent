"""Tests for Advanced ClawAgent features."""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock

from src.agents.advanced_claw_agent import AdvancedClawAgent
from src.agents.react_advanced import AdvancedReActAgent, AdvancedReActLoop, ActionType
from src.tools.advanced_tools import (
    WebSearchTool, FileSystemTool, DataAnalysisTool,
    APICallTool, CommandExecutionTool
)
from src.agents.skill_system import Skill, SkillLibrary


class TestAdvancedClawAgent:
    """Test AdvancedClawAgent initialization and features."""
    
    @pytest.fixture
    def agent(self):
        """Create test agent."""
        return AdvancedClawAgent(
            name="TestAgent",
            model="gpt-4",
            enable_advanced_react=True,
            enable_powerful_tools=True,
            enable_memory=False,  # Disable for testing
            enable_skills=True,
            verbose=False
        )
    
    def test_agent_initialization(self, agent):
        """Test agent initializes with all components."""
        assert agent.name == "TestAgent"
        assert agent.enable_advanced_react is True
        assert agent.enable_powerful_tools is True
        assert agent.enable_skills is True
        assert agent.max_iterations == 15
        assert agent.stats["messages_processed"] == 0
    
    def test_agent_representation(self, agent):
        """Test agent string representation."""
        repr_str = repr(agent)
        assert "AdvancedClawAgent" in repr_str
        assert "TestAgent" in repr_str
        assert "advanced-react" in repr_str
    
    def test_get_statistics(self, agent):
        """Test statistics collection."""
        stats = agent.get_statistics()
        
        assert "messages_processed" in stats
        assert "reasoning_loops" in stats
        assert "tools_executed" in stats
        assert "features" in stats
        assert stats["features"]["advanced_react"] is True
        assert stats["features"]["powerful_tools"] is True
    
    def test_should_use_advanced_react(self, agent):
        """Test ReAct routing decision."""
        # Should use ReAct for complex queries
        complex_query = "Analyze and break down the complete workflow for building a machine learning pipeline"
        assert agent._should_use_advanced_react(complex_query) is True
        
        # Should not use for simple queries
        simple_query = "Hello"
        assert agent._should_use_advanced_react(simple_query) is False
        
        # Should use for multiple questions
        multi_question = "What is machine learning? How does it work? What are the applications?"
        assert agent._should_use_advanced_react(multi_question) is True


class TestAdvancedReActLoop:
    """Test Advanced ReAct reasoning loop."""
    
    @pytest.fixture
    def react_loop(self):
        """Create test ReAct loop."""
        return AdvancedReActLoop(
            task="Test task",
            initial_context="Test context"
        )
    
    def test_loop_initialization(self, react_loop):
        """Test loop initializes properly."""
        assert react_loop.task == "Test task"
        assert react_loop.state.current_step == 0
        assert len(react_loop.state.steps) == 0
        assert react_loop.state.status == "understand"
    
    def test_add_step(self, react_loop):
        """Test adding steps to loop."""
        react_loop.add_step(
            action_type=ActionType.REASON,
            content="Initial understanding",
            tool_used=None,
            result=None
        )
        
        assert len(react_loop.state.steps) == 1
        assert react_loop.state.steps[0]["action_type"] == ActionType.REASON
        assert react_loop.state.steps[0]["content"] == "Initial understanding"
    
    def test_get_visual_trace(self, react_loop):
        """Test visual trace generation."""
        react_loop.add_step(ActionType.REASON, "Step 1")
        react_loop.add_step(ActionType.PLAN, "Step 2")
        
        trace = react_loop.get_visual_trace()
        assert "Step 1" in trace
        assert "Step 2" in trace
        assert "→" in trace or "REASON" in trace
    
    def test_loop_summary(self, react_loop):
        """Test loop summary generation."""
        react_loop.add_step(ActionType.REASON, "Understanding")
        react_loop.add_step(ActionType.EXECUTE, "Running tool", tool_used="WebSearch")
        
        summary = react_loop.get_summary()
        
        assert summary["total_steps"] == 2
        assert len(summary["tools_used"]) > 0


class TestPowerfulTools:
    """Test powerful tools."""
    
    @pytest.mark.asyncio
    async def test_web_search_tool(self):
        """Test web search tool initialization."""
        tool = WebSearchTool(provider="duckduckgo")
        
        assert tool.name == "web_search"
        assert "query" in tool.parameters
        assert "provider" in tool.metadata
    
    def test_file_system_tool(self):
        """Test file system tool."""
        tool = FileSystemTool(safe_root="./data", allow_write=False)
        
        assert tool.name == "filesystem"
        assert tool.safe_root == "./data"
        assert tool.allow_write is False
    
    def test_data_analysis_tool(self):
        """Test data analysis tool."""
        tool = DataAnalysisTool()
        
        assert tool.name == "data_analysis"
        assert "method" in tool.parameters
        assert tool.metadata["framework"] == "pandas"
    
    def test_api_call_tool(self):
        """Test API call tool."""
        tool = APICallTool()
        
        assert tool.name == "api_call"
        assert "url" in tool.parameters
        assert "method" in tool.parameters
        assert tool.timeout == 10
    
    def test_command_execution_tool(self):
        """Test command execution tool."""
        tool = CommandExecutionTool(timeout=30)
        
        assert tool.name == "execute_command"
        assert "command" in tool.parameters
        assert tool.timeout == 30
        assert "python" in tool.allowed_commands


class TestSkillSystem:
    """Test skill system."""
    
    def test_skill_creation(self):
        """Test creating custom skill."""
        skill = Skill(
            name="test_skill",
            category="testing",
            system_prompt="Test system prompt",
            keywords=["test", "verify"]
        )
        
        assert skill.name == "test_skill"
        assert skill.category == "testing"
        assert "test" in skill.keywords
    
    def test_skill_library_initialization(self):
        """Test skill library creation."""
        library = SkillLibrary()
        
        assert len(library.skills) > 0
        assert "code_generation" in [s.name for s in library.skills]
    
    def test_skill_relevance(self):
        """Test skill relevance scoring."""
        library = SkillLibrary()
        
        # Check code-related skills are relevant
        relevant = library.get_relevant_skills(
            "Write a Python function to calculate Fibonacci",
            max_skills=1
        )
        
        assert len(relevant) > 0


class TestVectorMemory:
    """Test vector memory system."""
    
    @pytest.mark.asyncio
    async def test_memory_functionality(self):
        """Test memory basic operations."""
        try:
            from src.utils.vector_memory import VectorMemory
            
            memory = VectorMemory(storage_path="./.test_memory")
            
            # Add memory
            await memory.add_memory(
                content="User likes technical discussions",
                memory_type="preference"
            )
            
            # Test added memory
            stats = memory.get_stats()
            assert stats["total_memories"] >= 1
            
        except ImportError:
            pytest.skip("Vector dependencies not installed")


class TestIntegration:
    """Integration tests."""
    
    @pytest.mark.asyncio
    async def test_agent_with_mock_llm(self):
        """Test agent with mocked LLM."""
        agent = AdvancedClawAgent(
            name="TestAgent",
            enable_memory=False,
            verbose=False
        )
        
        with patch('src.llm.openai_client.OpenAILLMClient.get_response') as mock_llm:
            mock_llm.return_value = {
                "content": "Mocked response"
            }
            
            # Note: This would need proper async mocking in real tests
            # For now just test that agent processes
            stats = agent.get_statistics()
            assert stats["messages_processed"] == 0
    
    @pytest.mark.asyncio
    async def test_tools_registration(self):
        """Test tool registration."""
        agent = AdvancedClawAgent(
            name="TestAgent",
            enable_powerful_tools=True,
            enable_memory=False
        )
        
        assert agent.tools_agent is not None
        
        tools = list(agent.tools_agent.tools.keys())
        
        assert "web_search" in tools
        assert "filesystem" in tools
        assert "data_analysis" in tools


class TestErrorHandling:
    """Test error handling."""
    
    def test_agent_graceful_degradation(self):
        """Test agent degrades gracefully."""
        agent = AdvancedClawAgent(
            name="TestAgent",
            enable_memory=False,
            verbose=False
        )
        
        # Verify features gracefully handle missing components
        stats = agent.get_statistics()
        assert "features" in stats
    
    def test_invalid_configuration(self):
        """Test agent with invalid configuration."""
        # Should not raise during init
        agent = AdvancedClawAgent(
            name="TestAgent",
            enable_advanced_react=False,
            enable_powerful_tools=False,
            enable_memory=False,
            enable_skills=False
        )
        
        assert agent is not None
        assert agent.tools_agent is None


class TestPerformance:
    """Performance tests."""
    
    def test_agent_statistics_performance(self):
        """Test statistics generation is fast."""
        agent = AdvancedClawAgent(
            name="TestAgent",
            enable_memory=False
        )
        
        import time
        
        start = time.time()
        for _ in range(100):
            agent.get_statistics()
        elapsed = time.time() - start
        
        # Should complete 100 iterations in < 1 second
        assert elapsed < 1.0
    
    def test_routing_decision_performance(self):
        """Test routing decision is fast."""
        agent = AdvancedClawAgent(name="TestAgent", enable_memory=False)
        
        import time
        
        test_queries = [
            "Hello",
            "What is machine learning?",
            "Design a complete system architecture with microservices"
        ]
        
        start = time.time()
        for query in test_queries * 10:
            agent._should_use_advanced_react(query)
        elapsed = time.time() - start
        
        # Should complete 30 routing decisions in < 100ms
        assert elapsed < 0.1


# Run tests with: pytest tests/test_advanced_features.py -v
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
