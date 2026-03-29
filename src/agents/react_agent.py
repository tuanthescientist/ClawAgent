"""ReAct framework for agents - Reasoning + Acting loops."""

import logging
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class ActionType(str, Enum):
    """Types of actions an agent can take."""
    TOOL_USE = "tool_use"
    KNOWLEDGE_RETRIEVAL = "knowledge_retrieval"
    REASONING = "reasoning"
    RESPONSE = "response"
    STOP = "stop"


class ThoughtAction:
    """A thought followed by an action."""
    
    def __init__(
        self,
        thought: str,
        action_type: ActionType,
        action_details: Dict[str, Any],
        step: int
    ):
        self.thought = thought
        self.action_type = action_type
        self.action_details = action_details
        self.step = step
        self.timestamp = datetime.now()
        self.observation = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "step": self.step,
            "thought": self.thought,
            "action_type": self.action_type.value,
            "action_details": self.action_details,
            "observation": self.observation,
            "timestamp": self.timestamp.isoformat()
        }


class ReActLoop:
    """ReAct reasoning and acting loop."""
    
    def __init__(
        self,
        max_iterations: int = 10,
        max_tokens_per_step: int = 1000,
        enable_reflection: bool = True
    ):
        self.max_iterations = max_iterations
        self.max_tokens_per_step = max_tokens_per_step
        self.enable_reflection = enable_reflection
        
        self.steps: List[ThoughtAction] = []
        self.iteration_count = 0
        self.total_tokens_used = 0
    
    def add_step(
        self,
        thought: str,
        action_type: ActionType,
        action_details: Dict[str, Any]
    ) -> ThoughtAction:
        """Add a thought-action step.
        
        Args:
            thought: Agent's reasoning
            action_type: Type of action
            action_details: Action parameters
            
        Returns:
            ThoughtAction: The added step
        """
        step = ThoughtAction(
            thought=thought,
            action_type=action_type,
            action_details=action_details,
            step=len(self.steps) + 1
        )
        self.steps.append(step)
        self.iteration_count += 1
        
        return step
    
    def set_observation(self, step_index: int, observation: str) -> None:
        """Set observation for a step.
        
        Args:
            step_index: Index of step
            observation: Observation result
        """
        if step_index < len(self.steps):
            self.steps[step_index].observation = observation
    
    def should_continue(self) -> bool:
        """Check if loop should continue.
        
        Returns:
            bool: True if should continue
        """
        if self.iteration_count >= self.max_iterations:
            logger.info(f"Max iterations ({self.max_iterations}) reached")
            return False
        
        if self.total_tokens_used >= self.max_tokens_per_step * self.max_iterations:
            logger.info("Token limit reached")
            return False
        
        # Check last action
        if self.steps and self.steps[-1].action_type in [ActionType.RESPONSE, ActionType.STOP]:
            return False
        
        return True
    
    def get_reasoning_trace(self) -> str:
        """Get formatted reasoning trace.
        
        Returns:
            str: Reasoning trace
        """
        parts = ["ReAct Reasoning Trace:"]
        
        for step in self.steps:
            parts.append(f"\nStep {step.step}:")
            parts.append(f"Thought: {step.thought}")
            parts.append(f"Action: {step.action_type.value} - {step.action_details}")
            if step.observation:
                parts.append(f"Observation: {step.observation}")
        
        return "\n".join(parts)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get loop execution summary.
        
        Returns:
            dict: Summary statistics
        """
        action_counts = {}
        for step in self.steps:
            action_counts[step.action_type.value] = action_counts.get(step.action_type.value, 0) + 1
        
        return {
            "total_steps": len(self.steps),
            "iterations": self.iteration_count,
            "action_distribution": action_counts,
            "tokens_used": self.total_tokens_used,
            "final_action": self.steps[-1].action_type.value if self.steps else None
        }
    
    def export_trace(self, filepath: str) -> None:
        """Export reasoning trace to file.
        
        Args:
            filepath: Output file path
        """
        try:
            trace_data = {
                "summary": self.get_summary(),
                "steps": [step.to_dict() for step in self.steps]
            }
            with open(filepath, "w") as f:
                json.dump(trace_data, f, indent=2)
            logger.info(f"Exported reasoning trace to {filepath}")
        except Exception as e:
            logger.error(f"Error exporting trace: {str(e)}")


class ReActAgent:
    """Agent with ReAct framework."""
    
    def __init__(
        self,
        name: str,
        llm_client: Any,  # LLM client (OpenAI, Local, etc.)
        tools: Optional[Any] = None,
        vector_memory: Optional[Any] = None,
        skill_library: Optional[Any] = None,
        max_iterations: int = 10
    ):
        self.name = name
        self.llm_client = llm_client
        self.tools = tools
        self.vector_memory = vector_memory
        self.skill_library = skill_library
        self.max_iterations = max_iterations
        
        self.conversation_history: List[Dict] = []
        self.system_prompt = self._build_system_prompt()
        self.loops: List[ReActLoop] = []
    
    def _build_system_prompt(self) -> str:
        """Build system prompt with skills and instructions.
        
        Returns:
            str: System prompt
        """
        base_prompt = f"""You are {self.name}, an AI assistant equipped with reasoning and action capabilities.

You use the ReAct framework:
1. Think: Analyze the user's request and plan your approach
2. Act: Execute actions using available tools or provide responses
3. Observe: Analyze the results
4. Reflect: Learn from observations for next steps

Be concise, accurate, and logical in your reasoning.
Always explain your thinking process before taking actions."""
        
        if self.skill_library:
            base_prompt = self.skill_library.get_system_prompt_with_skills(base_prompt)
        
        return base_prompt
    
    async def process_with_reasoning(self, user_input: str) -> Tuple[str, ReActLoop]:
        """Process input using ReAct loop.
        
        Args:
            user_input: User's request
            
        Returns:
            tuple: (response, reasoning_loop)
        """
        # Create new ReAct loop
        loop = ReActLoop(max_iterations=self.max_iterations)
        self.loops.append(loop)
        
        # Add user message
        self.conversation_history.append({"role": "user", "content": user_input})
        
        # Initial thought
        thought = f"The user is asking: {user_input[:100]}... Let me break this down and determine the best approach."
        loop.add_step(thought, ActionType.REASONING, {})
        
        # Retrieve relevant context from memory
        if self.vector_memory:
            try:
                context = await self.vector_memory.get_context(user_input)
                first_step = loop.steps[-1]
                first_step.observation = context
                
                thought = f"Retrieved relevant context. Now let me proceed with the solution."
                loop.add_step(thought, ActionType.KNOWLEDGE_RETRIEVAL, {"query": user_input})
            except Exception as e:
                logger.error(f"Error retrieving memory: {str(e)}")
        
        # Main reasoning loop
        while loop.should_continue():
            try:
                # Get LLM reasoning
                response = await self._get_llm_reasoning(user_input, loop)
                
                if response.get("action_type") == "tool_use":
                    # Execute tool
                    step = loop.add_step(
                        response.get("thought", ""),
                        ActionType.TOOL_USE,
                        response.get("action_details", {})
                    )
                    
                    # Execute tool and set observation
                    if self.tools:
                        tool_name = response["action_details"].get("tool")
                        tool_input = response["action_details"].get("input", {})
                        
                        try:
                            # TODO: Execute actual tool
                            observation = f"Tool '{tool_name}' executed with result"
                            loop.set_observation(len(loop.steps) - 1, observation)
                        except Exception as e:
                            loop.set_observation(len(loop.steps) - 1, f"Tool error: {str(e)}")
                
                elif response.get("action_type") == "response":
                    # Provide final response
                    step = loop.add_step(
                        response.get("thought", ""),
                        ActionType.RESPONSE,
                        {}
                    )
                    
                    final_response = response.get("response", "")
                    step.observation = final_response
                    
                    # Add to conversation history
                    self.conversation_history.append({
                        "role": "assistant",
                        "content": final_response
                    })
                    
                    return final_response, loop
                
                else:
                    # Continue reasoning
                    step = loop.add_step(
                        response.get("thought", ""),
                        ActionType.REASONING,
                        response.get("action_details", {})
                    )
            
            except Exception as e:
                logger.error(f"Error in reasoning loop: {str(e)}")
                break
        
        # Max iterations reached, provide best response
        final_response = "I've reached the maximum reasoning iterations. Based on my analysis, " + \
                        ("I need more information to provide a complete answer." if not loop.steps \
                         else "Here's what I've determined so far.")
        
        self.conversation_history.append({
            "role": "assistant",
            "content": final_response
        })
        
        return final_response, loop
    
    async def _get_llm_reasoning(self, user_input: str, loop: ReActLoop) -> Dict[str, Any]:
        """Get reasoning from LLM.
        
        Args:
            user_input: Original user input
            loop: Current ReAct loop
            
        Returns:
            dict: Reasoning response
        """
        # Build context from loop steps
        trace_context = loop.get_reasoning_trace()
        
        reasoning_prompt = f"""{trace_context}

Based on the above reasoning, what should be the next step?
Respond in JSON format with:
{{
    "thought": "your next thought",
    "action_type": "reasoning" | "tool_use" | "response",
    "action_details": {{}},
    "response": "final response if action_type is response"
}}"""
        
        # Call LLM
        try:
            # This is a simplified version - adapt to your LLM client
            result = await self.llm_client.get_response(
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    *self.conversation_history
                ]
            )
            
            # Parse response
            try:
                response_data = json.loads(result.get("content", "{}"))
                return response_data
            except json.JSONDecodeError:
                return {
                    "thought": result.get("content", ""),
                    "action_type": "response",
                    "response": result.get("content", "")
                }
        
        except Exception as e:
            logger.error(f"Error getting LLM reasoning: {str(e)}")
            return {
                "thought": f"Error in reasoning: {str(e)}",
                "action_type": "response",
                "response": f"I encountered an error during reasoning: {str(e)}"
            }
    
    def get_reasoning_history(self) -> List[Dict[str, Any]]:
        """Get all reasoning loops.
        
        Returns:
            list: Summary of reasoning loops
        """
        return [loop.get_summary() for loop in self.loops]
    
    def clear_history(self) -> None:
        """Clear conversation and reasoning history."""
        self.conversation_history = []
        self.loops = []
        logger.info(f"Cleared history for {self.name}")
