"""
Complete example showcasing all new ClawAgent features:
- Enhanced tool calling with function schemas
- Local LLM support (Ollama, vLLM, LM Studio)
- ReAct framework with reasoning loops
- Vector memory & long-term memory
- Dynamic skill system
"""

import asyncio
import logging
from pathlib import Path

# Import new components
from src.tools.function_calling import FunctionCallingAgent, Parameter, ParameterType, ToolCall, ActionType
from src.tools.enhanced_builtin import (
    CalculatorTool, WebSearchTool, GetTimeTool, FileReadTool, JSONParseTool
)
from src.llm.local_providers import LocalLLMFactory, OllamaProvider, VLLMProvider
from src.agents.react_agent import ReActAgent
from src.agents.skill_system import SkillLibrary, Skill, DEFAULT_SKILLS
from src.utils.vector_memory import VectorMemory, SentenceTransformerEmbedding
from src.llm.openai_client import OpenAILLMClient

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def example_1_enhanced_tool_calling():
    """Example 1: Enhanced tool calling with function schemas."""
    logger.info("=" * 60)
    logger.info("EXAMPLE 1: Enhanced Tool Calling")
    logger.info("=" * 60)
    
    # Create agent with function calling support
    agent = FunctionCallingAgent(name="ToolAgent")
    
    # Register built-in tools
    tools = [
        CalculatorTool(),
        WebSearchTool(),
        GetTimeTool(),
        JSONParseTool(),
        FileReadTool()
    ]
    
    agent.register_tools(tools)
    
    # Show available tools
    print("\n📋 Registered Tools:")
    for name, tool in agent.tools.items():
        print(f"  • {name}: {tool.description}")
        print(f"    Parameters: {[p.name for p in tool.parameters]}")
    
    # Get OpenAI-compatible schemas
    schemas = agent.get_tools_schema(format="openai")
    print(f"\n✅ Generated {len(schemas)} tool schemas for OpenAI API")
    
    # Execute some tools
    print("\n🔧 Executing tools:")
    
    # Calculator tool
    calc_call = ToolCall(
        id="calc_1",
        name="calculator",
        arguments={"expression": "sqrt(16) + 2*3", "precision": 2}
    )
    result = await agent.execute_tool(calc_call)
    print(f"  Calculator: {calc_call.arguments}")
    print(f"  Result: {result.result}")
    
    # Time tool
    time_call = ToolCall(
        id="time_1",
        name="get_time",
        arguments={"timezone": "UTC", "format": "readable"}
    )
    result = await agent.execute_tool(time_call)
    print(f"  Time: {result.result}")
    
    print(f"\n📊 Tool Statistics: {agent.get_tool_info()}")


async def example_2_local_llm_support():
    """Example 2: Local LLM support with fallback."""
    logger.info("\n" + "=" * 60)
    logger.info("EXAMPLE 2: Local LLM Support (Ollama/vLLM/LM Studio)")
    logger.info("=" * 60)
    
    print("\n🔍 Checking available LLM providers...")
    
    # Try creating Ollama provider
    print("\n  Attempting Ollama connection (http://localhost:11434)...")
    ollama_provider = await LocalLLMFactory.create(
        provider="ollama",
        base_url="http://localhost:11434",
        model="mistral"
    )
    
    if ollama_provider:
        print("  ✅ Ollama is running!")
        
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is 2+2?"}
        ]
        
        response = await ollama_provider.generate(messages)
        print(f"\n  Response: {response['content'][:100]}...")
    else:
        print("  ❌ Ollama not available")
        print("\n  Start Ollama with: ollama run mistral")
    
    # Show alternative providers
    print("\n📌 Alternative Local LLM Providers:")
    print("  • vLLM: pip install vllm")
    print("  • LM Studio: https://lmstudio.ai/")
    print("  • ollama: https://ollama.ai/")
    
    print("\nProvider Comparison:")
    print("  Ollama         - Easy setup, slow (CPU)")
    print("  vLLM           - High performance, requires GPU")
    print("  LM Studio      - GUI, beginner-friendly")


async def example_3_skill_system():
    """Example 3: Dynamic skill system."""
    logger.info("\n" + "=" * 60)
    logger.info("EXAMPLE 3: Dynamic Skill System")
    logger.info("=" * 60)
    
    # Initialize skill library
    skill_lib = SkillLibrary(storage_path="./skills")
    
    # Add default skills
    for skill in DEFAULT_SKILLS:
        skill_lib.add_skill(skill)
    
    print(f"\n📚 Loaded {len(skill_lib.list_skills())} default skills")
    
    # List all skills
    print("\nAvailable Skills:")
    for skill in skill_lib.list_skills():
        print(f"  • {skill.name}: {skill.description}")
        print(f"    Tags: {', '.join(skill.tags)}")
    
    # Add a custom skill
    custom_skill = Skill(
        name="document_analysis",
        description="Analyze documents for key information",
        instructions="1. Read document\n2. Extract key points\n3. Summarize findings",
        examples=["Contract review", "Research paper analysis"],
        tags=["analysis", "document"]
    )
    skill_lib.add_skill(custom_skill)
    print(f"\n✅ Added custom skill: {custom_skill.name}")
    
    # Find relevant skills for a query
    query = "I need to analyze a research paper"
    relevant = skill_lib.get_relevant_skills(query, max_skills=3)
    print(f"\n🎯 Skills relevant to '{query}':")
    for skill in relevant:
        print(f"  • {skill.name}")
    
    # Build system prompt with skills
    base_prompt = "You are a helpful assistant."
    enhanced_prompt = skill_lib.get_system_prompt_with_skills(
        base_prompt,
        skills=[skill_lib.get_skill("document_analysis")]
    )
    print(f"\n✨ System prompt with skills ({len(enhanced_prompt)} chars)")
    
    # Record skill usage
    skill_lib.record_skill_usage("document_analysis", success=True)
    print(f"✅ Recorded skill usage")


async def example_4_vector_memory():
    """Example 4: Vector memory with semantic search."""
    logger.info("\n" + "=" * 60)
    logger.info("EXAMPLE 4: Vector Memory & Long-term Memory")
    logger.info("=" * 60)
    
    try:
        # Initialize vector memory with embeddings
        print("\n🔄 Loading embedding model (sentence-transformers)...")
        embedding_model = SentenceTransformerEmbedding()
        vector_mem = VectorMemory(
            embedding_model=embedding_model,
            storage_path="./long_term_memory"
        )
        print("✅ Vector memory initialized with embeddings")
        
        # Add some memories
        memories_to_add = [
            ("User prefers concise responses", "fact"),
            ("Python is a popular programming language", "fact"),
            ("The user asked about machine learning basics", "conversation"),
            ("System should use semantic search for retrieval", "learning"),
        ]
        
        print("\n📝 Adding memories:")
        for content, mem_type in memories_to_add:
            mem_id = await vector_mem.add_memory(content, memory_type=mem_type)
            print(f"  ✅ Added: {content[:50]}...")
        
        # Semantic search
        print("\n🔍 Semantic Search Examples:")
        
        queries = [
            "Tell me about Python",
            "What does the user like?",
            "machine learning"
        ]
        
        for query in queries:
            results = await vector_mem.search(query, limit=2)
            print(f"\n  Query: '{query}'")
            for memory, score in results:
                print(f"    • {memory.content[:50]}... (score: {score:.2f})")
        
        # Get context for LLM
        context = await vector_mem.get_context(
            "Tell me about programming",
            max_results=2
        )
        print(f"\n📌 Retrieved context:\n{context}")
        
        # Print stats
        stats = vector_mem.get_stats()
        print(f"\n📊 Memory Statistics:")
        print(f"  Total memories: {stats['total_memories']}")
        print(f"  Type distribution: {stats['type_distribution']}")
        print(f"  Average importance: {stats['average_importance']:.2f}")
        
    except ImportError:
        print("\n⚠️  sentence-transformers not installed")
        print("  Virtual memory (without embeddings) is still functional")


async def example_5_react_framework():
    """Example 5: ReAct framework with reasoning loops."""
    logger.info("\n" + "=" * 60)
    logger.info("EXAMPLE 5: ReAct Framework (Reasoning + Acting)")
    logger.info("=" * 60)
    
    print("\n🧠 ReAct Framework Overview:")
    print("""
    ReAct combines Reasoning and Acting:
    1. THOUGHT: Agent analyzes the problem
    2. ACTION: Agent chooses action (tool, search, think, respond)
    3. OBSERVATION: Agent observes results
    4. REFLECTION: Agent learns and plans next step
    """)
    
    # Initialize ReAct agent (requires LLM)
    print("\nTo use ReAct with your LLM:")
    print("  1. Set OPENAI_API_KEY in .env for OpenAI")
    print("  2. Or start Ollama: ollama run mistral")
    print("  3. Update .env to use local LLM if desired")
    
    print("""
    Example usage:
    ```python
    # OpenAI-based
    llm_client = OpenAILLMClient(api_key="sk-...")
    
    # Or local LLM
    llm_client = await LocalLLMFactory.create(
        "ollama", "http://localhost:11434", "mistral"
    )
    
    agent = ReActAgent(
        name="Reasoner",
        llm_client=llm_client,
        max_iterations=5
    )
    
    response, loop = await agent.process_with_reasoning(
        "Solve this complex problem..."
    )
    
    print(loop.get_reasoning_trace())
    ```
    """)


async def example_6_full_integration():
    """Example 6: Full integration of all features."""
    logger.info("\n" + "=" * 60)
    logger.info("EXAMPLE 6: Full Integration - Advanced Agent")
    logger.info("=" * 60)
    
    print("""
    Complete integration example:
    
    ```python
    # 1. Setup tools with function calling
    agent = FunctionCallingAgent("SuperAgent")
    agent.register_tools([
        CalculatorTool(),
        WebSearchTool(),
        # ... more tools
    ])
    
    # 2. Initialize memory and skills
    embedding_model = SentenceTransformerEmbedding()
    vector_memory = VectorMemory(embedding_model=embedding_model)
    skill_library = SkillLibrary()
    for skill in DEFAULT_SKILLS:
        skill_library.add_skill(skill)
    
    # 3. Setup LLM (OpenAI or Local)
    llm_client = OpenAILLMClient(api_key=os.getenv("OPENAI_API_KEY"))
    # or: 
    # llm_client = await LocalLLMFactory.create("ollama", ...)
    
    # 4. Create ReAct agent
    react_agent = ReActAgent(
        name="IntelligentAgent",
        llm_client=llm_client,
        tools=agent,
        vector_memory=vector_memory,
        skill_library=skill_library,
        max_iterations=10
    )
    
    # 5. Process with full reasoning
    response, reasoning_loop = await react_agent.process_with_reasoning(
        user_input="Complex task requiring reasoning and tools"
    )
    
    # View reasoning trace
    print(reasoning_loop.get_reasoning_trace())
    ```
    """)


async def main():
    """Run all examples."""
    print("""
╔════════════════════════════════════════════════════════════╗
║       ClawAgent Upgrade Examples - All New Features        ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    # Run examples
    await example_1_enhanced_tool_calling()
    await example_2_local_llm_support()
    await example_3_skill_system()
    await example_4_vector_memory()
    await example_5_react_framework()
    await example_6_full_integration()
    
    print("""
╔════════════════════════════════════════════════════════════╗
║                   Examples Complete!                       ║
╚════════════════════════════════════════════════════════════╝

Next steps:
1. Install dependencies: pip install -r requirements.txt
2. Set up local LLM (Ollama/vLLM/LM Studio)
3. Configure .env file with API keys
4. Check src/agents/openai_agent.py for integration
5. Review documentation in UPGRADE_GUIDE.md
    """)


if __name__ == "__main__":
    asyncio.run(main())
