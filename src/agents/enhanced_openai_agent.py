"""Enhanced OpenAI Agent with all new features integrated."""

import logging
from typing import Optional, List, Dict, Any, Tuple
from openai import AsyncOpenAI

from .base import BaseAgent
from .react_agent import ReActAgent
from .skill_system import SkillLibrary, DEFAULT_SKILLS
from src.tools.function_calling import FunctionCallingAgent
from src.tools.enhanced_builtin import (
    CalculatorTool, WebSearchTool, GetTimeTool, 
    FileReadTool, JSONParseTool
)
from src.utils.vector_memory import VectorMemory, SentenceTransformerEmbedding
from src.llm.openai_client import OpenAILLMClient
from src.llm.local_providers import LocalLLMFactory

logger = logging.getLogger(__name__)


class EnhancedOpenAIAgent(BaseAgent):
    """Enhanced OpenAI Agent with integrated new features."""
    
    def __init__(
        self,
        name: str,
        api_key: str,
        model: str = "gpt-4",
        enable_local_llm: bool = False,
        local_llm_url: Optional[str] = None,
        local_llm_model: Optional[str] = None,
        enable_tools: bool = True,
        enable_memory: bool = True,
        enable_skills: bool = True,
        enable_react: bool = False,
        max_iterations: int = 10
    ):
        """Initialize enhanced agent.
        
        Args:
            name: Agent name
            api_key: OpenAI API key
            model: Model name
            enable_local_llm: Use local LLM instead of OpenAI
            local_llm_url: Local LLM URL
            local_llm_model: Local LLM model name
            enable_tools: Enable function calling tools
            enable_memory: Enable vector memory
            enable_skills: Enable skill library
            enable_react: Enable ReAct framework
            max_iterations: Max reasoning iterations
        """
        super().__init__(name, model)
        
        self.enable_local_llm = enable_local_llm
        self.enable_tools = enable_tools
        self.enable_memory = enable_memory
        self.enable_skills = enable_skills
        self.enable_react = enable_react
        
        # Initialize LLM client
        if enable_local_llm:
            logger.info("Initializing with local LLM support")
            self.llm_client = None  # Will be set in async init
            self.local_llm_url = local_llm_url or "http://localhost:11434"
            self.local_llm_model = local_llm_model or "mistral"
        else:
            self.llm_client = OpenAILLMClient(api_key=api_key, model=model)
            self.local_llm_url = None
            self.local_llm_model = None
        
        # Initialize components
        self.tools_agent: Optional[FunctionCallingAgent] = None
        self.vector_memory: Optional[VectorMemory] = None
        self.skill_library: Optional[SkillLibrary] = None
        self.react_agent: Optional[ReActAgent] = None
        
        if enable_tools:
            self._init_tools()
        
        if enable_memory:
            try:
                self._init_memory()
            except Exception as e:
                logger.warning(f"Could not initialize memory: {str(e)}")
        
        if enable_skills:
            self._init_skills()
        
        # Track execution
        self.tool_calls_executed = 0
        self.reasoning_loops_completed = 0
    
    def _init_tools(self) -> None:
        """Initialize tool calling system."""
        self.tools_agent = FunctionCallingAgent(f"{self.name}_Tools")
        
        # Register built-in tools
        tools = [
            CalculatorTool(),
            WebSearchTool(),
            GetTimeTool(),
            FileReadTool(),
            JSONParseTool()
        ]
        
        self.tools_agent.register_tools(tools)
        logger.info(f"Initialized {len(tools)} tools")
    
    def _init_memory(self) -> None:
        """Initialize vector memory."""
        try:
            embedding_model = SentenceTransformerEmbedding()
            self.vector_memory = VectorMemory(
                embedding_model=embedding_model,
                storage_path=f"./{self.name.lower()}_memory"
            )
            logger.info("Initialized vector memory with embeddings")
        except ImportError:
            logger.warning("sentence-transformers not available, using text-based search")
            self.vector_memory = VectorMemory(
                embedding_model=None,
                storage_path=f"./{self.name.lower()}_memory"
            )
    
    def _init_skills(self) -> None:
        """Initialize skill library."""
        self.skill_library = SkillLibrary(storage_path=f"./{self.name.lower()}_skills")
        
        # Add default skills
        for skill in DEFAULT_SKILLS:
            self.skill_library.add_skill(skill)
        
        logger.info(f"Initialized skill library with {len(DEFAULT_SKILLS)} default skills")
    
    async def _init_local_llm(self) -> None:
        """Initialize local LLM connection."""
        if self.enable_local_llm and not self.llm_client:
            logger.info(f"Connecting to local LLM at {self.local_llm_url}")
            
            provider = await LocalLLMFactory.create(
                provider="ollama",  # Could be made configurable
                base_url=self.local_llm_url,
                model=self.local_llm_model
            )
            
            if provider:
                self.llm_client = provider
                logger.info(f"Connected to {provider.__class__.__name__}")
            else:
                logger.error("Could not connect to local LLM, falling back to OpenAI")
                self.enable_local_llm = False
    
    async def process(self, user_input: str) -> str:
        """Process user input with enhanced features.
        
        Args:
            user_input: User message
            
        Returns:
            str: Assistant response
        """
        if self.enable_local_llm and not self.llm_client:
            await self._init_local_llm()
        
        # Add to history
        self.add_message("user", user_input)
        
        try:
            # Check if ReAct should be used (for complex queries)
            if self.enable_react and self._should_use_react(user_input):
                return await self._process_with_react(user_input)
            else:
                return await self._process_normal(user_input)
        
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            error_response = f"Error: {str(e)}"
            self.add_message("assistant", error_response)
            return error_response
    
    def _should_use_react(self, user_input: str) -> bool:
        """Determine if query should use ReAct.
        
        Heuristics:
        - Complex keywords: "how", "analyze", "why", "steps"
        - Length > 100 chars
        - Multiple questions
        """
        lower = user_input.lower()
        complex_indicators = ["how", "analyze", "why", "steps", "complex", 
                             "problem", "design", "solve", "implement"]
        
        has_complex_indicator = any(ind in lower for ind in complex_indicators)
        is_long = len(user_input) > 100
        has_multiple_questions = user_input.count("?") > 1
        
        return has_complex_indicator or is_long or has_multiple_questions
    
    async def _process_normal(self, user_input: str) -> str:
        """Normal processing with optional tools and memory context."""
        # Retrieve memory context
        context = ""
        if self.vector_memory:
            try:
                context = await self.vector_memory.get_context(user_input, max_results=3)
                logger.debug("Retrieved memory context")
            except Exception as e:
                logger.debug(f"Error retrieving memory: {str(e)}")
        
        # Build system prompt with skills
        system_prompt = self.system_prompt
        if self.skill_library:
            relevant_skills = self.skill_library.get_relevant_skills(user_input, max_skills=3)
            if relevant_skills:
                system_prompt = self.skill_library.get_system_prompt_with_skills(
                    system_prompt, relevant_skills
                )
        
        # Add context to system prompt
        if context:
            system_prompt += f"\n\n{context}"
        
        # Get available tools schemas
        tool_schemas = None
        if self.tools_agent:
            tool_schemas = self.tools_agent.get_tools_schema(format="openai")
        
        # Prepare messages
        messages = [
            {"role": "system", "content": system_prompt},
            *self.get_conversation_history()
        ]
        
        # Call LLM
        if self.enable_local_llm:
            # For local LLM (Ollama, vLLM, etc.)
            response = await self.llm_client.generate(messages, tools=tool_schemas)
            assistant_message = response.get("content", "")
        else:
            # For OpenAI
            response = await self.llm_client.get_response(messages, tools=tool_schemas)
            assistant_message = response.get("content", "")
            
            # Handle tool calls if present
            if response.get("tool_calls"):
                tool_results = await self._handle_tool_calls(response["tool_calls"])
                
                # Add tool results to conversation
                messages.append({"role": "assistant", "content": assistant_message})
                messages.append({"role": "system", "content": f"Tool results: {tool_results}"})
                
                # Get final response
                final_response = await self.llm_client.get_response(messages)
                assistant_message = final_response.get("content", "")
        
        # Store memory if enabled
        if self.vector_memory:
            try:
                await self.vector_memory.add_memory(
                    content=f"Q: {user_input}\nA: {assistant_message[:100]}...",
                    memory_type="conversation",
                    metadata={"user_input": user_input}
                )
            except Exception as e:
                logger.debug(f"Error storing memory: {str(e)}")
        
        # Add to history
        self.add_message("assistant", assistant_message)
        
        return assistant_message
    
    async def _process_with_react(self, user_input: str) -> str:
        """Process with ReAct framework for complex reasoning."""
        if not self.react_agent:
            self.react_agent = ReActAgent(
                name=f"{self.name}_ReAct",
                llm_client=self.llm_client,
                tools=self.tools_agent,
                vector_memory=self.vector_memory,
                skill_library=self.skill_library,
                max_iterations=10
            )
        
        try:
            response, loop = await self.react_agent.process_with_reasoning(user_input)
            
            # Track reasoning
            self.reasoning_loops_completed += 1
            
            # Log reasoning trace in debug
            logger.debug(f"Reasoning trace:\n{loop.get_reasoning_trace()}")
            
            # Store reasoning metadata
            if self.vector_memory:
                try:
                    await self.vector_memory.add_memory(
                        content=f"ReAct loop: {len(loop.steps)} steps for: {user_input[:50]}...",
                        memory_type="learning",
                        metadata={"reasoning_steps": len(loop.steps)}
                    )
                except Exception as e:
                    logger.debug(f"Error storing reasoning: {str(e)}")
            
            return response
        
        except Exception as e:
            logger.error(f"ReAct processing failed: {str(e)}")
            return await self._process_normal(user_input)
    
    async def _handle_tool_calls(self, tool_calls: List[Dict]) -> str:
        """Handle tool calls from LLM response.
        
        Args:
            tool_calls: List of tool calls from LLM
            
        Returns:
            str: Tool execution results
        """
        if not self.tools_agent:
            return "Tools not available"
        
        results = []
        
        for tool_call in tool_calls:
            try:
                # Execute tool
                from src.tools.function_calling import ToolCall
                
                tc = ToolCall(
                    id=tool_call.get("id", ""),
                    name=tool_call.get("function", {}).get("name", ""),
                    arguments=tool_call.get("function", {}).get("arguments", {})
                )
                
                result = await self.tools_agent.execute_tool(tc)
                self.tool_calls_executed += 1
                
                results.append({
                    "tool": tc.name,
                    "result": result.result,
                    "success": result.success
                })
                
                logger.info(f"Executed tool: {tc.name}")
            
            except Exception as e:
                logger.error(f"Tool execution error: {str(e)}")
                results.append({"error": str(e)})
        
        return str(results)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get agent statistics.
        
        Returns:
            dict: Statistics
        """
        stats = {
            "name": self.name,
            "model": self.model,
            "messages_processed": len(self.conversation_history),
            "tools_executed": self.tool_calls_executed,
            "reasoning_loops": self.reasoning_loops_completed,
            "features": {
                "tools": self.enable_tools,
                "memory": self.enable_memory,
                "skills": self.enable_skills,
                "react": self.enable_react,
                "local_llm": self.enable_local_llm
            }
        }
        
        if self.vector_memory:
            stats["memory_stats"] = self.vector_memory.get_stats()
        
        if self.tools_agent:
            stats["tools_info"] = self.tools_agent.get_tool_info()
        
        return stats
    
    def __repr__(self) -> str:
        features = []
        if self.enable_tools:
            features.append("tools")
        if self.enable_memory:
            features.append("memory")
        if self.enable_skills:
            features.append("skills")
        if self.enable_react:
            features.append("react")
        
        return f"<EnhancedOpenAIAgent({self.name}, features={features})>"
