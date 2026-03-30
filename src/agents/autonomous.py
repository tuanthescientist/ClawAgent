"""Autonomous Agent with Tool Calling."""

import json
import logging
from typing import Any, Dict, Optional

from .base import BaseAgent
from src.core.llm_provider import Message as ProviderMessage
from src.llm.openai_client import OpenAILLMClient
from src.tools.base import ToolRegistry

logger = logging.getLogger(__name__)


class AutonomousAgent(BaseAgent):
    """Agent that can autonomously call tools and decide actions."""
    
    def __init__(
        self,
        name: str,
        api_key: Optional[str] = None,
        model: str = "gpt-4",
        tool_registry: Optional[ToolRegistry] = None,
        llm_provider: Optional[Any] = None,
    ):
        self.tool_registry = tool_registry or ToolRegistry()
        super().__init__(name, model)
        self.llm_provider = llm_provider
        self.llm_client = OpenAILLMClient(api_key, model) if api_key else None
        self.max_iterations = 10  # Prevent infinite loops
        self.autonomous_mode = True

        if not self.llm_provider and not self.llm_client:
            raise ValueError("AutonomousAgent requires either api_key or llm_provider")
    
    def _get_system_prompt(self) -> str:
        """Get enhanced system prompt for tool-using agent."""
        tool_registry = getattr(self, "tool_registry", None)
        tool_names = ", ".join([t.name for t in tool_registry.list_tools()]) if tool_registry else "none"
        
        return f"""You are {self.name}, an autonomous AI agent with the ability to use tools.

Your capabilities:
- You can use the following tools: {tool_names}
- You should call tools when needed to accomplish tasks
- Always think step-by-step about what tools are needed
- Provide clear reasoning for tool usage
- Return the final result after using tools if necessary

When you need to use a tool, respond with:
TOOL: <tool_name>
ARGS: <json_args>

Be helpful, accurate, and use tools wisely."""
    
    async def _execute_tool_call(self, tool_name: str, args: Dict[str, Any]) -> str:
        """Execute a tool call."""
        logger.info(f"Executing tool: {tool_name} with args: {args}")
        
        tool = self.tool_registry.get_tool(tool_name)
        if not tool:
            return f"Error: Tool '{tool_name}' not found"
        
        try:
            result = await tool.execute(**args)
            logger.info(f"Tool result: {result}")
            return result
        except Exception as e:
            error_msg = f"Tool error: {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    def _parse_tool_call(self, response: str) -> Optional[tuple[str, Dict]]:
        """Parse tool call from response.
        
        Returns:
            (tool_name, args) or None if no tool call
        """
        lines = response.strip().split('\n')
        
        for i, line in enumerate(lines):
            if line.startswith('TOOL:'):
                tool_name = line.replace('TOOL:', '').strip()
                
                # Find ARGS line
                for j in range(i + 1, len(lines)):
                    if lines[j].startswith('ARGS:'):
                        args_str = lines[j].replace('ARGS:', '').strip()
                        try:
                            args = json.loads(args_str)
                            return tool_name, args
                        except json.JSONDecodeError:
                            logger.error(f"Failed to parse args: {args_str}")
                            return None
        
        return None
    
    async def process(self, user_input: str, max_iterations: Optional[int] = None) -> str:
        """Process user input with autonomous tool calling.
        
        Args:
            user_input: User's message
            max_iterations: Max autonomous iterations (overrides self.max_iterations)
            
        Returns:
            Final response
        """
        max_iter = max_iterations or self.max_iterations
        iteration = 0
        
        # Add user message
        self.add_message("user", user_input)

        if self.llm_provider is not None:
            try:
                provider_messages = [
                    ProviderMessage(role="system", content=self.system_prompt),
                    *[
                        ProviderMessage(role=message["role"], content=message["content"])
                        for message in self.get_conversation_history()
                    ],
                ]
                response = await self.llm_provider.complete(provider_messages)
                self.add_message("assistant", response.content)
                logger.info("Agent finished using configured provider")
                return response.content
            except Exception as e:
                error_msg = f"Error in autonomous loop: {str(e)}"
                logger.error(error_msg)
                self.add_message("assistant", error_msg)
                return error_msg
        
        while iteration < max_iter:
            iteration += 1
            logger.debug(f"Autonomous iteration {iteration}/{max_iter}")
            
            # Get response from LLM with tools
            messages = [
                {"role": "system", "content": self.system_prompt},
                *self.get_conversation_history()
            ]
            
            tools_schema = self.tool_registry.get_schemas() if self.tool_registry.list_tools() else None
            
            try:
                response_data = await self.llm_client.get_response(
                    messages=messages,
                    tools=tools_schema,
                    tool_choice="auto" if tools_schema else None
                )
                
                response_text = response_data.get("content", "")
                tool_calls = response_data.get("tool_calls", [])
                finish_reason = response_data.get("finish_reason", "stop")
                
                # Check for tool calls in response
                tool_call = self._parse_tool_call(response_text)
                
                if tool_call:
                    tool_name, args = tool_call
                    logger.info(f"Agent calling tool: {tool_name}")
                    
                    # Execute tool
                    tool_result = await self._execute_tool_call(tool_name, args)
                    
                    # Add to conversation
                    self.add_message("assistant", f"Using tool {tool_name}: {response_text}")
                    self.add_message("system", f"Tool result: {tool_result}")
                    
                    # Continue with next iteration
                    continue
                
                elif tool_calls:  # OpenAI native tool calling
                    for tool_call in tool_calls:
                        tool_name = tool_call.function.name
                        args = json.loads(tool_call.function.arguments)
                        
                        logger.info(f"Agent calling tool: {tool_name}")
                        tool_result = await self._execute_tool_call(tool_name, args)
                        
                        # Add tool result to conversation
                        self.add_message("assistant", response_text)
                        self.add_message("system", f"Tool {tool_name} result: {tool_result}")
                    
                    continue
                
                else:
                    # No tool call, finish response
                    self.add_message("assistant", response_text)
                    logger.info(f"Agent finished after {iteration} iteration(s)")
                    return response_text
            
            except Exception as e:
                error_msg = f"Error in autonomous loop: {str(e)}"
                logger.error(error_msg)
                self.add_message("assistant", error_msg)
                return error_msg
        
        # Max iterations reached
        error_msg = f"Max iterations ({max_iter}) reached"
        logger.warning(error_msg)
        self.add_message("assistant", error_msg)
        return error_msg


class MultiAgentOrchestrator:
    """Orchestrate multiple agents for complex tasks."""
    
    def __init__(self, agents: Dict[str, AutonomousAgent]):
        """Initialize multi-agent orchestrator.
        
        Args:
            agents: Dictionary of agent_name -> agent
        """
        self.agents = agents
        self.primary_agent = list(agents.values())[0] if agents else None
    
    async def delegate_task(self, task: str, agent_name: Optional[str] = None) -> str:
        """Delegate task to appropriate agent.
        
        Args:
            task: Task description
            agent_name: Specific agent name or None for primary
            
        Returns:
            Task result
        """
        agent = self.agents.get(agent_name or "") or self.primary_agent
        
        if not agent:
            return "Error: No agents available"
        
        logger.info(f"Delegating task to {agent.name}")
        return await agent.process(task)
