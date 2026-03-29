"""Advanced ClawAgent with ReAct and Powerful Tools Integration."""

import logging
from typing import Optional, List, Dict, Any, Tuple
from openai import AsyncOpenAI

from .base import BaseAgent
from .react_advanced import AdvancedReActAgent, AdvancedReActLoop, ActionType
from .skill_system import SkillLibrary, DEFAULT_SKILLS
from src.tools.function_calling import FunctionCallingAgent
from src.tools.advanced_tools import (
    WebSearchTool, FileSystemTool, DataAnalysisTool,
    CommandExecutionTool, APICallTool
)
from src.tools.code_executor import CodeExecutionTool, PythonREPLTool, DataProcessingTool
from src.llm.openai_client import OpenAILLMClient
from src.llm.local_providers import LocalLLMFactory
from src.utils.vector_memory import VectorMemory, SentenceTransformerEmbedding

logger = logging.getLogger(__name__)


class AdvancedClawAgent(BaseAgent):
    """Advanced ClawAgent with ReAct framework and powerful tools."""
    
    def __init__(
        self,
        name: str,
        api_key: Optional[str] = None,
        model: str = "gpt-4",
        enable_advanced_react: bool = True,
        enable_powerful_tools: bool = True,
        enable_code_execution: bool = False,  # Careful with this!
        enable_memory: bool = True,
        enable_skills: bool = True,
        enable_local_llm: bool = False,
        local_llm_url: Optional[str] = None,
        max_iterations: int = 15,
        verbose: bool = True
    ):
        """Initialize advanced agent.
        
        Args:
            name: Agent name
            api_key: OpenAI API key
            model: LLM model
            enable_advanced_react: Use advanced ReAct reasoning
            enable_powerful_tools: Enable powerful tools
            enable_code_execution: Enable Python code execution (WARNING: security)
            enable_memory: Enable vector memory
            enable_skills: Enable skill system
            enable_local_llm: Use local LLM
            local_llm_url: Local LLM endpoint
            max_iterations: Max ReAct iterations
            verbose: Verbose logging
        """
        super().__init__(name, model)
        
        self.enable_advanced_react = enable_advanced_react
        self.enable_powerful_tools = enable_powerful_tools
        self.enable_code_execution = enable_code_execution
        self.enable_memory = enable_memory
        self.enable_skills = enable_skills
        self.verbose = verbose
        self.max_iterations = max_iterations
        
        # Initialize LLM
        if enable_local_llm:
            self.llm_client = None
            self.local_llm_url = local_llm_url or "http://localhost:11434"
        else:
            self.llm_client = OpenAILLMClient(api_key=api_key, model=model)
        
        # Initialize components
        self.tools_agent: Optional[FunctionCallingAgent] = None
        self.react_agent: Optional[AdvancedReActAgent] = None
        self.vector_memory: Optional[VectorMemory] = None
        self.skill_library: Optional[SkillLibrary] = None
        
        self.reasoning_loops: List[AdvancedReActLoop] = []
        self.stats = {
            "messages_processed": 0,
            "reasoning_loops": 0,
            "tools_executed": 0
        }
        
        # Initialize subsystems
        if enable_powerful_tools:
            self._init_powerful_tools()
        
        if enable_memory:
            try:
                self._init_memory()
            except Exception as e:
                logger.warning(f"Memory init failed: {str(e)}")
        
        if enable_skills:
            self._init_skills()
    
    def _init_powerful_tools(self) -> None:
        """Initialize powerful tools."""
        self.tools_agent = FunctionCallingAgent(f"{self.name}_Tools")
        
        tools = [
            WebSearchTool(provider="duckduckgo"),
            FileSystemTool(safe_root="./", allow_write=True),
            DataAnalysisTool(),
            APICallTool(),
            DataProcessingTool(),
            PythonREPLTool()
        ]
        
        # Conditionally add code execution
        if self.enable_code_execution:
            logger.warning("⚠️ Code execution enabled - use with caution!")
            tools.append(CodeExecutionTool(timeout=10))
        
        # Conditionally add system command execution
        tools.append(CommandExecutionTool(
            timeout=30,
            allowed_commands=["python", "pip", "node", "npm", "git"]
        ))
        
        self.tools_agent.register_tools(tools)
        logger.info(f"✓ Initialized {len(tools)} powerful tools")
    
    def _init_memory(self) -> None:
        """Initialize vector memory."""
        try:
            embedding_model = SentenceTransformerEmbedding()
            self.vector_memory = VectorMemory(
                embedding_model=embedding_model,
                storage_path=f"./{self.name.lower()}_memory"
            )
            logger.info("✓ Initialized vector memory with embeddings")
        except ImportError:
            logger.warning("Sentence transformers not available, using text-based search")
            self.vector_memory = VectorMemory(
                embedding_model=None,
                storage_path=f"./{self.name.lower()}_memory"
            )
    
    def _init_skills(self) -> None:
        """Initialize skill library."""
        self.skill_library = SkillLibrary(storage_path=f"./{self.name.lower()}_skills")
        for skill in DEFAULT_SKILLS:
            self.skill_library.add_skill(skill)
        logger.info(f"✓ Initialized {len(DEFAULT_SKILLS)} built-in skills")
    
    async def _init_local_llm_if_needed(self) -> None:
        """Initialize local LLM if enabled."""
        if not self.llm_client and hasattr(self, 'local_llm_url'):
            provider = await LocalLLMFactory.create(
                "ollama",
                self.local_llm_url,
                "mistral"
            )
            if provider:
                self.llm_client = provider
                logger.info("✓ Connected to local LLM")
    
    async def process(self, user_input: str) -> str:
        """Process user input with advanced reasoning.
        
        Args:
            user_input: User message
            
        Returns:
            str: Response
        """
        await self._init_local_llm_if_needed()
        
        self.add_message("user", user_input)
        self.stats["messages_processed"] += 1
        
        # Determine if advanced ReAct should be used
        use_react = self.enable_advanced_react and self._should_use_advanced_react(user_input)
        
        try:
            if use_react:
                return await self._process_with_advanced_react(user_input)
            else:
                return await self._process_simple(user_input)
        except Exception as e:
            logger.error(f"Processing error: {str(e)}")
            return f"Error processing request: {str(e)}"
    
    def _should_use_advanced_react(self, user_input: str) -> bool:
        """Determine if advanced ReAct should be used."""
        complex_indicators = [
            "analyze", "break down", "design", "plan", "step by step",
            "how to", "solve", "complex", "multi", "architecture",
            "workflow", "process", "system", "research", "investigate"
        ]
        
        lower = user_input.lower()
        return (
            any(ind in lower for ind in complex_indicators) or
            len(user_input) > 150 or
            user_input.count("?") > 1
        )
    
    async def _process_with_advanced_react(self, user_input: str) -> str:
        """Process using advanced ReAct reasoning."""
        # Create ReAct agent if not exists
        if not self.react_agent:
            self.react_agent = AdvancedReActAgent(
                name=f"{self.name}_ReAct",
                llm_client=self.llm_client,
                tools=self.tools_agent,
                max_iterations=self.max_iterations,
                enable_dynamic_planning=True,
                enable_error_recovery=True
            )
        
        try:
            response, loop = await self.react_agent.process_with_advanced_reasoning(
                user_input,
                return_trace=True
            )
            
            self.reasoning_loops.append(loop)
            self.stats["reasoning_loops"] += 1
            
            if self.verbose:
                logger.info(f"ReAct trace:\n{loop.get_visual_trace()}")
            
            # Store findings in memory
            if self.vector_memory:
                try:
                    await self.vector_memory.add_memory(
                        content=f"Advanced reasoning: {user_input[:80]}...",
                        memory_type="learning",
                        metadata={"steps": len(loop.state.steps)}
                    )
                except Exception as e:
                    logger.debug(f"Memory storage failed: {str(e)}")
            
            self.add_message("assistant", response)
            return response
        
        except Exception as e:
            logger.error(f"Advanced ReAct failed: {str(e)}")
            return await self._process_simple(user_input)
    
    async def _process_simple(self, user_input: str) -> str:
        """Simple processing without ReAct."""
        # Get memory context
        context = ""
        if self.vector_memory:
            try:
                context = await self.vector_memory.get_context(user_input, max_results=2)
            except Exception as e:
                logger.debug(f"Memory retrieval failed: {str(e)}")
        
        # Build system prompt
        system_prompt = self.system_prompt
        if self.skill_library:
            relevant_skills = self.skill_library.get_relevant_skills(user_input, max_skills=2)
            if relevant_skills:
                system_prompt = self.skill_library.get_system_prompt_with_skills(
                    system_prompt, relevant_skills
                )
        
        if context:
            system_prompt += f"\n\n{context}"
        
        # Get tool schemas
        tool_schemas = None
        if self.tools_agent:
            tool_schemas = self.tools_agent.get_tools_schema(format="openai")
        
        # Prepare messages
        messages = [
            {"role": "system", "content": system_prompt},
            *self.get_conversation_history()
        ]
        
        # Call LLM
        try:
            response = await self.llm_client.get_response(messages, tools=tool_schemas)
            assistant_message = response.get("content", "")
            
            self.add_message("assistant", assistant_message)
            return assistant_message
        
        except Exception as e:
            logger.error(f"LLM call failed: {str(e)}")
            return f"Processing error: {str(e)}"
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get detailed statistics."""
        stats = {
            **self.stats,
            "features": {
                "advanced_react": self.enable_advanced_react,
                "powerful_tools": self.enable_powerful_tools,
                "code_execution": self.enable_code_execution,
                "memory": self.enable_memory,
                "skills": self.enable_skills
            }
        }
        
        if self.tools_agent:
            stats["tools_info"] = self.tools_agent.get_tool_info()
            stats["available_tools"] = list(self.tools_agent.tools.keys())
        
        if self.vector_memory:
            stats["memory_stats"] = self.vector_memory.get_stats()
        
        if self.reasoning_loops:
            stats["last_loop_summary"] = self.reasoning_loops[-1].get_summary()
        
        return stats
    
    def export_reasoning_traces(self, directory: str = "./reasoning_traces") -> None:
        """Export all reasoning traces."""
        from pathlib import Path
        Path(directory).mkdir(exist_ok=True)
        
        for i, loop in enumerate(self.reasoning_loops):
            filepath = f"{directory}/trace_{i+1}"
            loop.export_trace(f"{filepath}.json", format="json")
            loop.export_trace(f"{filepath}.md", format="markdown")
        
        logger.info(f"✓ Exported {len(self.reasoning_loops)} reasoning traces")
    
    def __repr__(self) -> str:
        features = []
        if self.enable_advanced_react:
            features.append("advanced-react")
        if self.enable_powerful_tools:
            features.append("powerful-tools")
        if self.enable_memory:
            features.append("memory")
        if self.enable_skills:
            features.append("skills")
        
        return f"<AdvancedClawAgent({self.name}, features={features})>"
