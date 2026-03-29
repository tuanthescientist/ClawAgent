"""Comprehensive examples showcasing Advanced ReAct and Powerful Tools."""

import asyncio
import logging
import os
import json

from src.agents.react_advanced import AdvancedReActAgent, AdvancedReActLoop, ActionType
from src.tools.function_calling import FunctionCallingAgent
from src.tools.advanced_tools import (
    WebSearchTool, FileSystemTool, DataAnalysisTool,
    CommandExecutionTool, APICallTool
)
from src.tools.code_executor import CodeExecutionTool, PythonREPLTool, DataProcessingTool
from src.llm.openai_client import OpenAILLMClient

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def example_1_advanced_react_visualization():
    """Example 1: Advanced ReAct with rich visualization."""
    logger.info("=" * 80)
    logger.info("EXAMPLE 1: Advanced ReAct with Rich Visualization")
    logger.info("=" * 80)
    
    loop = AdvancedReActLoop(
        name="VisualizationDemo",
        max_iterations=6,
        verbose=True
    )
    
    # Step 1: Analyze
    step1 = loop.add_step(
        thought="I need to build a data analysis pipeline to process customer data",
        action_type=ActionType.ANALYZE,
        action_details={"input": "Customer data analysis"},
        reasoning="Understanding requirements and data structure",
        confidence=0.95,
        next_steps=["Research tools", "Plan architecture", "Begin implementation"]
    )
    
    loop.set_observation(0, "Analysis complete: Need 3 main components - Data Input, Processing, Output")
    
    # Step 2: Plan
    if loop.should_continue():
        step2 = loop.add_step(
            thought="Creating detailed implementation plan with validation checkpoints",
            action_type=ActionType.PLAN,
            action_details={
                "components": ["data_loader", "processor", "analyzer"],
                "validation": ["format_check", "quality_check", "result_check"]
            },
            reasoning="Structured approach ensures reliability",
            confidence=0.90,
            next_steps=["Implement data_loader", "Implement processor"]
        )
        
        plan_text = """
        PLAN:
        1. Load and validate input data
        2. Apply transformations
        3. Run statistical analysis
        4. Generate report
        Validation at each step to catch errors early.
        """
        
        loop.set_observation(1, plan_text)
    
    # Step 3: Parallel tasks
    if loop.should_continue():
        step3 = loop.add_step(
            thought="Setting up parallel execution for data processing tasks",
            action_type=ActionType.PARALLEL_TASKS,
            action_details={
                "tasks": ["load_data", "prepare_schema", "create_output_dir"],
                "parallelization": "full"
            },
            reasoning="Parallel execution saves time for independent tasks",
            confidence=0.85
        )
        
        parallel_result = "✓ Task 1: Data loaded (1000 records)\n✓ Task 2: Schema prepared\n✓ Task 3: Output directory created"
        loop.set_observation(2, parallel_result, add_tokens=150)
    
    # Step 4: Tool usage
    if loop.should_continue():
        step4 = loop.add_step(
            thought="Using specialized tools for data processing",
            action_type=ActionType.TOOL_USE,
            action_details={"tools": ["data_processor", "analyzer", "formatter"]},
            reasoning="Tools provide optimized implementations",
            confidence=0.88
        )
        
        tool_result = "Data processing complete:\n- 1000 records processed\n- 5 anomalies detected\n- 3 transformations applied"
        loop.set_observation(3, tool_result, add_tokens=100)
    
    # Step 5: Reflection
    if loop.should_continue():
        step5 = loop.add_step(
            thought="Reflecting on results and identifying improvements",
            action_type=ActionType.REFLECTION,
            action_details={
                "checks": ["accuracy", "performance", "completeness"],
                "improvements": ["caching", "batching"]
            },
            reasoning="Learning from execution for future optimizations",
            confidence=0.92
        )
        
        reflection_text = "Results exceed expectations. Performance optimizations identified for future runs."
        loop.set_observation(4, reflection_text)
    
    # Step 6: Final response
    if loop.should_continue():
        step6 = loop.add_step(
            thought="Generating comprehensive final response with insights",
            action_type=ActionType.RESPONSE,
            action_details={"format": "comprehensive_report"},
            reasoning="Synthesizing all findings into actionable insights",
            confidence=0.95
        )
        
        loop.set_observation(5, "Report generated successfully")
    
    # Display results
    print(loop.get_visual_trace())
    print("\n" + loop.get_detailed_analysis())
    
    # Export traces
    loop.export_trace("example1_trace.json", format="json")
    logger.info("✓ Traces exported to example1_trace.json")


async def example_2_powerful_tools():
    """Example 2: Showcase all powerful tools."""
    logger.info("\n" + "=" * 80)
    logger.info("EXAMPLE 2: Powerful Tools Demonstration")
    logger.info("=" * 80)
    
    agent = FunctionCallingAgent("ToolMaster")
    
    # Register all powerful tools
    tools = [
        WebSearchTool(provider="duckduckgo"),
        FileSystemTool(safe_root="./", allow_write=True),
        DataAnalysisTool(),
        CommandExecutionTool(timeout=30, allowed_commands=["python", "pip", "git"]),
        APICallTool(),
        CodeExecutionTool(timeout=10),
        PythonREPLTool(max_history=20),
        DataProcessingTool()
    ]
    
    agent.register_tools(tools)
    
    print(f"\n📋 Registered {len(tools)} Powerful Tools:")
    print("=" * 50)
    
    for tool in tools:
        print(f"\n✓ {tool.name.upper()}")
        print(f"  Description: {tool.description}")
        print(f"  Category: {tool.category}")
        print(f"  Parameters: {', '.join([p.name for p in tool.parameters])}")
    
    # Tool info
    info = agent.get_tool_info()
    print(f"\n\nDetailed Tool Information:")
    print("=" * 50)
    print(json.dumps(info, indent=2)[:500] + "...")
    
    # Get schemas
    schemas = agent.get_tools_schema(format="openai")
    print(f"\n\nGenerated {len(schemas)} OpenAI-compatible tool schemas")
    print(json.dumps(schemas[0], indent=2)[:400] + "...")


async def example_3_web_search():
    """Example 3: Web search tool in action."""
    logger.info("\n" + "=" * 80)
    logger.info("EXAMPLE 3: Web Search Tool")
    logger.info("=" * 80)
    
    search_tool = WebSearchTool(provider="duckduckgo")
    
    print("\n🔍 Web Search Demonstration:")
    print("=" * 50)
    
    # Create tool call
    from src.tools.function_calling import ToolCall
    
    queries = [
        "What is artificial intelligence?",
        "Python programming best practices",
        "Machine learning recent advances"
    ]
    
    for query in queries:
        print(f"\n📝 Query: {query}")
        
        result = await search_tool.execute(
            query=query,
            num_results=3
        )
        
        try:
            result_data = json.loads(result)
            if "results" in result_data:
                for i, res in enumerate(result_data["results"][:2], 1):
                    print(f"  {i}. {res.get('title', 'N/A')}")
                    print(f"     {res.get('snippet', 'N/A')[:80]}...")
        except:
            print(f"  Result: {result[:100]}")


async def example_4_code_execution():
    """Example 4: Python code execution."""
    logger.info("\n" + "=" * 80)
    logger.info("EXAMPLE 4: Safe Python Code Execution")
    logger.info("=" * 80)
    
    code_tool = CodeExecutionTool(timeout=10)
    
    print("\n💻 Code Execution Examples:")
    print("=" * 50)
    
    # Example 1: Math calculation
    code1 = """
import math
result = math.factorial(5)
print(f"5! = {result}")

# Calculate some statistics
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
print(f"Sum: {sum(numbers)}")
print(f"Average: {sum(numbers) / len(numbers)}")
print(f"Max: {max(numbers)}")
"""
    
    print("\n📌 Code 1: Math and Statistics")
    result = await code_tool.execute(code=code1)
    result_data = json.loads(result)
    print(f"Output:\n{result_data.get('stdout', 'No output')}")
    
    # Example 2: List comprehension
    code2 = """
# List operations
squares = [x**2 for x in range(10)]
print(f"Squares: {squares}")

# Filter even numbers
evens = [x for x in range(20) if x % 2 == 0]
print(f"Even numbers: {evens}")
"""
    
    print("\n📌 Code 2: List Comprehensions")
    result = await code_tool.execute(code=code2)
    result_data = json.loads(result)
    print(f"Output:\n{result_data.get('stdout', 'No output')}")
    
    # Example 3: Error demonstration
    code3 = "x = 1 / 0  # This will error"
    
    print("\n📌 Code 3: Error Handling")
    result = await code_tool.execute(code=code3)
    result_data = json.loads(result)
    print(f"Success: {result_data.get('success', False)}")
    print(f"Error: {result_data.get('error', 'N/A')}")


async def example_5_file_operations():
    """Example 5: File system operations."""
    logger.info("\n" + "=" * 80)
    logger.info("EXAMPLE 5: File System Operations")
    logger.info("=" * 80)
    
    fs_tool = FileSystemTool(safe_root="./", allow_write=True)
    
    print("\n📁 File System Operations:")
    print("=" * 50)
    
    # Create test file
    print("\n1️⃣ Write file")
    result = await fs_tool.execute(
        operation="write",
        path="./test_file.txt",
        content="This is test content for the file system tool.\nLine 2\nLine 3"
    )
    print(f"Result: {json.loads(result).get('status', 'Unknown')}")
    
    # Read file
    print("\n2️⃣ Read file")
    result = await fs_tool.execute(
        operation="read",
        path="./test_file.txt"
    )
    result_data = json.loads(result)
    print(f"Content preview: {result_data.get('content', 'N/A')[:100]}")
    
    # List directory
    print("\n3️⃣ List directory")
    result = await fs_tool.execute(
        operation="list",
        path="./"
    )
    result_data = json.loads(result)
    count = result_data.get('count', 0)
    print(f"Found {count} items in current directory (showing first 5):")
    for item in result_data.get('items', [])[:5]:
        print(f"  • {item.get('name')} ({item.get('type')})")
    
    # Cleanup
    print("\n4️⃣ Delete file")
    result = await fs_tool.execute(
        operation="delete",
        path="./test_file.txt"
    )
    print(f"Result: {json.loads(result).get('status', 'Unknown')}")


async def example_6_data_processing():
    """Example 6: Data processing and transformation."""
    logger.info("\n" + "=" * 80)
    logger.info("EXAMPLE 6: Data Processing")
    logger.info("=" * 80)
    
    data_tool = DataProcessingTool()
    
    print("\n🔄 Data Processing Examples:")
    print("=" * 50)
    
    # JSON parsing
    print("\n1️⃣ Parse and format JSON")
    json_data = '{"name":"John","age":30,"city":"NYC","hobbies":["reading","coding"]}'
    result = await data_tool.execute(operation="parse_json", data=json_data)
    result_data = json.loads(result)
    print(f"Parsed: {result_data.get('data', {})}")
    
    # Format JSON
    print("\n2️⃣ Format JSON with indentation")
    result = await data_tool.execute(operation="format", data=json_data)
    result_data = json.loads(result)
    formatted = result_data.get('formatted', 'N/A')
    print(f"Formatted:\n{formatted[:200]}")
    
    # CSV parsing
    print("\n3️⃣ Parse CSV data")
    csv_data = """name,age,city
John,30,NYC
Jane,28,LA
Bob,35,Chicago"""
    result = await data_tool.execute(operation="parse_csv", data=csv_data)
    result_data = json.loads(result)
    print(f"Parsed {result_data.get('count', 0)} CSV rows")


async def example_7_advanced_agent_flow():
    """Example 7: Full advanced agent workflow."""
    logger.info("\n" + "=" * 80)
    logger.info("EXAMPLE 7: Advanced Agent Workflow")
    logger.info("=" * 80)
    
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║     Advanced ReAct Agent with Powerful Tools Workflow       ║
    ╚════════════════════════════════════════════════════════════╝
    
    This demonstrates a complete workflow:
    1. User gives complex task
    2. Agent analyzes requirements
    3. Agent creates detailed plan
    4. Agent uses available tools
    5. Agent reflects on results
    6. Agent provides comprehensive response
    
    Complete workflow would include:
    
    STEP 1: ANALYZE
    ├─ Understand requirements
    ├─ Identify data needs
    └─ Determine tools needed
    
    STEP 2: PLAN
    ├─ Create action sequence
    ├─ Define success criteria
    └─ Identify decision points
    
    STEP 3: EXECUTE
    ├─ Search for information    [WebSearchTool]
    ├─ Process data              [DataProcessingTool]
    ├─ Run analysis              [CodeExecutionTool]
    ├─ Call external APIs        [APICallTool]
    └─ Save results              [FileSystemTool]
    
    STEP 4: REFLECT
    ├─ Validate results
    ├─ Identify improvements
    └─ Learn from execution
    
    STEP 5: RESPONSE
    └─ Synthesize findings into comprehensive answer
    
    Benefits of Advanced ReAct:
    ✓ Clear reasoning visibility
    ✓ Parallel task execution
    ✓ Error recovery
    ✓ Decision tracking
    ✓ Performance optimization
    ✓ Learning from results
    """)
    
    # Create mock advanced agent scenario
    loop = AdvancedReActLoop(name="ComplexTask")
    
    print("\n📊 Simulated Advanced Agent Execution:")
    
    # Add multiple steps showing the full workflow
    tasks = [
        (ActionType.ANALYZE, "Break down the data analysis task", 0.95),
        (ActionType.PLAN, "Create multi-phased execution plan", 0.90),
        (ActionType.TOOL_USE, "Search for relevant data sources", 0.85),
        (ActionType.TOOL_USE, "Execute data processing", 0.88),
        (ActionType.PARALLEL_TASKS, "Run parallel analyses", 0.82),
        (ActionType.REFLECTION, "Review results and optimize", 0.91),
        (ActionType.RESPONSE, "Generate comprehensive report", 0.94)
    ]
    
    for i, (action_type, thought, confidence) in enumerate(tasks, 1):
        loop.add_step(
            thought=thought,
            action_type=action_type,
            action_details={"step": i},
            confidence=confidence
        )
        loop.set_observation(i-1, f"✓ Completed: {thought[:50]}...")
    
    summary = loop.get_summary()
    print(f"\n✓ Completed {summary['total_steps']} steps")
    print(f"✓ Average confidence: {summary['average_confidence']:.2%}")
    print(f"✓ Duration: {summary['duration_seconds']:.2f}s")


async def main():
    """Run all examples."""
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║  Advanced ReAct Framework & Powerful Tools - Complete Examples & Demo      ║
╚════════════════════════════════════════════════════════════════════════════╝
    """)
    
    # Run examples
    try:
        await example_1_advanced_react_visualization()
        await example_2_powerful_tools()
        await example_3_web_search()
        await example_4_code_execution()
        await example_5_file_operations()
        await example_6_data_processing()
        await example_7_advanced_agent_flow()
        
    except Exception as e:
        logger.error(f"Example error: {str(e)}", exc_info=True)
    
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                        Examples Complete! ✓                                ║
╚════════════════════════════════════════════════════════════════════════════╝

Key Improvements:
1. ✓ Advanced ReAct with detailed visualization
2. ✓ Rich reasoning traces with decision tracking
3. ✓ Parallel task execution support
4. ✓ 8 new powerful tools added
5. ✓ Safe Python code execution
6. ✓ Web search with multiple providers
7. ✓ File system operations
8. ✓ Data processing and transformation

Next Steps:
- Integrate into your agent for complex reasoning
- Use tools for real-world automation tasks
- Export reasoning traces for analysis
- Customize tools for your domain
    """)


if __name__ == "__main__":
    asyncio.run(main())
