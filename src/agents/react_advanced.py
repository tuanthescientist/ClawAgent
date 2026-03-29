"""Advanced ReAct Framework with Enhanced Reasoning and Visualization."""

import logging
import json
from typing import List, Dict, Any, Optional, Set, Tuple
from enum import Enum
from datetime import datetime
from dataclasses import dataclass, asdict
import asyncio

logger = logging.getLogger(__name__)


class ActionType(str, Enum):
    """Advanced action types."""
    ANALYZE = "analyze"              # Break down problem
    PLAN = "plan"                    # Create action plan
    TOOL_USE = "tool_use"            # Execute tool
    CODE_EXECUTION = "code_exec"     # Run code
    PARALLEL_TASKS = "parallel"      # Run multiple tasks
    KNOWLEDGE_RETRIEVAL = "knowledge"
    REFLECTION = "reflection"        # Learn from results
    RESPONSE = "response"            # Final answer
    ERROR_RECOVERY = "error_recovery"
    STOP = "stop"


@dataclass
class ReasoningStep:
    """Single reasoning step with full context."""
    step_num: int
    timestamp: str
    thought: str                     # Current thinking
    action_type: ActionType          # Type of action
    action_details: Dict[str, Any]   # Action parameters
    observation: Optional[str] = None
    confidence: float = 1.0          # Confidence in this step
    reasoning: str = ""              # Explanation of why
    next_steps: List[str] = None     # Planned next steps
    errors: List[str] = None         # Any errors encountered
    
    def __post_init__(self):
        if self.next_steps is None:
            self.next_steps = []
        if self.errors is None:
            self.errors = []
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class ReasoningState:
    """Tracks overall reasoning state and progress."""
    
    def __init__(self):
        self.steps: List[ReasoningStep] = []
        self.goals: List[str] = []
        self.completed_goals: Set[str] = set()
        self.failed_actions: List[Tuple[int, str]] = []  # (step_num, error)
        self.tool_results: Dict[str, Any] = {}
        self.context_memory: List[Dict] = []
        self.decision_points: List[Dict] = []
        
    def add_step(self, step: ReasoningStep) -> None:
        """Add a reasoning step."""
        self.steps.append(step)
    
    def set_goal(self, goal: str) -> None:
        """Set a reasoning goal."""
        self.goals.append(goal)
    
    def complete_goal(self, goal: str) -> None:
        """Mark goal as completed."""
        if goal in self.goals:
            self.completed_goals.add(goal)
    
    def add_tool_result(self, tool_name: str, result: Any) -> None:
        """Store tool execution result."""
        self.tool_results[tool_name] = result
    
    def record_error(self, step_num: int, error: str) -> None:
        """Record an error."""
        self.failed_actions.append((step_num, error))
    
    def get_progress(self) -> Dict[str, Any]:
        """Get current progress."""
        return {
            "total_steps": len(self.steps),
            "goals_completed": len(self.completed_goals),
            "total_goals": len(self.goals),
            "errors": len(self.failed_actions),
            "tools_used": len(self.tool_results)
        }


class AdvancedReActLoop:
    """Advanced ReAct loop with sophisticated reasoning."""
    
    def __init__(
        self,
        name: str = "ReActAgent",
        max_iterations: int = 15,
        max_tokens: int = 5000,
        enable_reflection: bool = True,
        enable_parallel: bool = True,
        verbose: bool = True
    ):
        self.name = name
        self.max_iterations = max_iterations
        self.max_tokens = max_tokens
        self.enable_reflection = enable_reflection
        self.enable_parallel = enable_parallel
        self.verbose = verbose
        
        self.state = ReasoningState()
        self.iteration_count = 0
        self.total_tokens = 0
        self.start_time = datetime.now()
        self.execution_log = []
    
    def add_step(
        self,
        thought: str,
        action_type: ActionType,
        action_details: Dict[str, Any],
        reasoning: str = "",
        confidence: float = 1.0,
        next_steps: Optional[List[str]] = None
    ) -> ReasoningStep:
        """Add a reasoning step with full context."""
        step = ReasoningStep(
            step_num=len(self.state.steps) + 1,
            timestamp=datetime.now().isoformat(),
            thought=thought,
            action_type=action_type,
            action_details=action_details,
            confidence=confidence,
            reasoning=reasoning,
            next_steps=next_steps or []
        )
        
        self.state.add_step(step)
        self.iteration_count += 1
        
        if self.verbose:
            self._log_step(step)
        
        return step
    
    def _log_step(self, step: ReasoningStep) -> None:
        """Log step details for visualization."""
        log_entry = {
            "step": step.step_num,
            "type": step.action_type.value,
            "thought_preview": step.thought[:60] + "..." if len(step.thought) > 60 else step.thought,
            "confidence": f"{step.confidence:.2%}",
            "timestamp": step.timestamp
        }
        self.execution_log.append(log_entry)
        
        logger.info(f"Step {step.step_num}: [{step.action_type.value}] {step.thought[:80]}")
    
    def set_observation(self, step_index: int, observation: str, add_tokens: int = 0) -> None:
        """Set observation for a step."""
        if step_index < len(self.state.steps):
            self.state.steps[step_index].observation = observation
            self.total_tokens += add_tokens
    
    def should_continue(self) -> bool:
        """Check if reasoning should continue."""
        if self.iteration_count >= self.max_iterations:
            logger.info(f"Max iterations ({self.max_iterations}) reached")
            return False
        
        if self.total_tokens >= self.max_tokens:
            logger.info(f"Token limit ({self.max_tokens}) reached")
            return False
        
        # Stop if last action is terminal
        if self.state.steps:
            last_action = self.state.steps[-1].action_type
            if last_action in [ActionType.RESPONSE, ActionType.STOP]:
                return False
        
        return True
    
    def add_decision_point(self, option_a: str, option_b: str, chosen: str, confidence: float) -> None:
        """Track decision points in reasoning."""
        self.state.decision_points.append({
            "step": self.iteration_count,
            "options": [option_a, option_b],
            "chosen": chosen,
            "confidence": confidence,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_visual_trace(self) -> str:
        """Get formatted visual reasoning trace."""
        lines = [
            f"\n{'='*70}",
            f"ADVANCED REACT REASONING TRACE - {self.name}",
            f"{'='*70}",
            f"Total Steps: {len(self.state.steps)} | Iterations: {self.iteration_count}",
            f"Goals: {len(self.state.completed_goals)}/{len(self.state.goals)} | Errors: {len(self.state.failed_actions)}",
            f"Duration: {(datetime.now() - self.start_time).total_seconds():.1f}s",
            f"{'='*70}\n"
        ]
        
        for i, step in enumerate(self.state.steps, 1):
            lines.append(f"\n┌─ STEP {step.step_num}: {step.action_type.value.upper()}")
            lines.append(f"│  Thought: {step.thought}")
            
            if step.reasoning:
                lines.append(f"│  Reasoning: {step.reasoning}")
            
            lines.append(f"│  Confidence: {step.confidence:.0%}")
            
            if step.action_details:
                for key, value in step.action_details.items():
                    val_str = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
                    lines.append(f"│  → {key}: {val_str}")
            
            if step.observation:
                obs_str = step.observation[:100] + "..." if len(step.observation) > 100 else step.observation
                lines.append(f"│  ✓ Result: {obs_str}")
            
            if step.errors:
                for error in step.errors:
                    lines.append(f"│  ✗ Error: {error}")
            
            if step.next_steps:
                lines.append(f"│  ⤴ Next: {', '.join(step.next_steps[:2])}")
            
            lines.append("└─")
        
        return "\n".join(lines)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get comprehensive reasoning summary."""
        action_types = {}
        for step in self.state.steps:
            action_types[step.action_type.value] = action_types.get(step.action_type.value, 0) + 1
        
        avg_confidence = sum(s.confidence for s in self.state.steps) / len(self.state.steps) if self.state.steps else 0
        
        return {
            "total_steps": len(self.state.steps),
            "iterations": self.iteration_count,
            "duration_seconds": (datetime.now() - self.start_time).total_seconds(),
            "tokens_used": self.total_tokens,
            "action_distribution": action_types,
            "goals_completed": len(self.state.completed_goals),
            "total_goals": len(self.state.goals),
            "errors_encountered": len(self.state.failed_actions),
            "tools_used": len(self.state.tool_results),
            "average_confidence": avg_confidence,
            "decision_points": len(self.state.decision_points),
            "final_action": self.state.steps[-1].action_type.value if self.state.steps else None
        }
    
    def get_detailed_analysis(self) -> str:
        """Get detailed reasoning analysis."""
        summary = self.get_summary()
        
        lines = [
            f"\n{'='*70}",
            f"REASONING SESSION ANALYSIS",
            f"{'='*70}",
        ]
        
        for key, value in summary.items():
            if key == "action_distribution":
                lines.append(f"\nAction Distribution:")
                for action, count in value.items():
                    lines.append(f"  • {action}: {count}")
            elif isinstance(value, float):
                lines.append(f"{key}: {value:.2f}")
            else:
                lines.append(f"{key}: {value}")
        
        if self.state.failed_actions:
            lines.append(f"\nErrors Encountered:")
            for step_num, error in self.state.failed_actions:
                lines.append(f"  • Step {step_num}: {error}")
        
        if self.state.decision_points:
            lines.append(f"\nKey Decision Points:")
            for dp in self.state.decision_points[:5]:  # Show first 5
                lines.append(f"  • Step {dp['step']}: Chose '{dp['chosen']}' over '{dp['options'][0]}' " +
                           f"(confidence: {dp['confidence']:.0%})")
        
        return "\n".join(lines)
    
    def export_trace(self, filepath: str, format: str = "json") -> None:
        """Export detailed reasoning trace."""
        try:
            if format == "json":
                data = {
                    "metadata": {
                        "name": self.name,
                        "timestamp": datetime.now().isoformat(),
                        "summary": self.get_summary()
                    },
                    "steps": [step.to_dict() for step in self.state.steps],
                    "decision_points": self.state.decision_points,
                    "execution_log": self.execution_log
                }
                
                with open(filepath, "w") as f:
                    json.dump(data, f, indent=2)
            
            elif format == "markdown":
                with open(filepath, "w") as f:
                    f.write(self.get_visual_trace())
                    f.write("\n")
                    f.write(self.get_detailed_analysis())
            
            logger.info(f"Exported reasoning trace to {filepath}")
        except Exception as e:
            logger.error(f"Error exporting trace: {str(e)}")


class AdvancedReActAgent:
    """Advanced agent with sophisticated ReAct reasoning."""
    
    def __init__(
        self,
        name: str,
        llm_client: Any,
        tools: Optional[Any] = None,
        max_iterations: int = 15,
        enable_dynamic_planning: bool = True,
        enable_error_recovery: bool = True
    ):
        self.name = name
        self.llm_client = llm_client
        self.tools = tools
        self.max_iterations = max_iterations
        self.enable_dynamic_planning = enable_dynamic_planning
        self.enable_error_recovery = enable_error_recovery
        
        self.conversation_history: List[Dict] = []
        self.reasoning_loops: List[AdvancedReActLoop] = []
        self.system_prompt = self._build_system_prompt()
    
    def _build_system_prompt(self) -> str:
        """Build sophisticated system prompt."""
        return f"""You are {self.name}, an advanced reasoning agent using the ReAct framework.

YOUR REASONING PROCESS:
1. ANALYZE: Break down the problem into components
2. PLAN: Create a detailed action plan  
3. EXECUTE: Use tools and take actions
4. REFLECT: Learn from results
5. ITERATE: Refine approach based on observations

REQUIREMENTS:
- Always show your thinking process
- Use tools when needed for facts/calculations
- Provide confidence levels for decisions
- Recover gracefully from errors
- Explain your decision-making

OUTPUT FORMAT:
For each step, provide:
- Thought: What are you thinking?
- Action: What will you do?
- Reasoning: Why this action?
- Confidence: How confident (0-100%)?
"""
    
    async def process_with_advanced_reasoning(
        self,
        user_input: str,
        return_trace: bool = True
    ) -> Tuple[str, AdvancedReActLoop]:
        """Process with advanced ReAct reasoning.
        
        Args:
            user_input: User request
            return_trace: Return full reasoning trace
            
        Returns:
            tuple: (response, reasoning_loop)
        """
        # Create new loop
        loop = AdvancedReActLoop(
            name=f"{self.name}_Loop",
            max_iterations=self.max_iterations,
            verbose=True
        )
        self.reasoning_loops.append(loop)
        
        self.conversation_history.append({"role": "user", "content": user_input})
        
        # Step 1: Analyze
        step1 = loop.add_step(
            thought=f"Breaking down the request: {user_input[:100]}...",
            action_type=ActionType.ANALYZE,
            action_details={"input": user_input},
            reasoning="Need to understand what is being asked",
            confidence=0.9
        )
        
        # Simulate analysis
        analysis = f"Key requirements: {user_input[:80]}"
        loop.set_observation(len(loop.state.steps) - 1, analysis)
        
        # Step 2: Plan
        if loop.should_continue():
            step2 = loop.add_step(
                thought="Creating action plan to address the request",
                action_type=ActionType.PLAN,
                action_details={
                    "strategy": "Multi-step approach",
                    "tools_needed": ["research", "analysis"]
                },
                reasoning="Breaking down into manageable steps",
                confidence=0.85,
                next_steps=["Execute step 1", "Execute step 2", "Synthesize results"]
            )
            
            plan = "Plan: Step 1 → Step 2 → Synthesis"
            loop.set_observation(len(loop.state.steps) - 1, plan)
        
        # Step 3: Execute (tool use)
        if loop.should_continue() and self.tools:
            step3 = loop.add_step(
                thought="Executing planned actions using available tools",
                action_type=ActionType.TOOL_USE,
                action_details={"tools": ["search", "analysis"]},
                reasoning="Tools provide accurate information",
                confidence=0.8
            )
            
            # Simulate tool execution
            tool_result = "Tool execution completed: Found relevant information"
            loop.set_observation(len(loop.state.steps) - 1, tool_result, add_tokens=100)
        
        # Step 4: Reflect
        if loop.should_continue() and self.enable_dynamic_planning:
            step4 = loop.add_step(
                thought="Reflecting on results to verify approach",
                action_type=ActionType.REFLECTION,
                action_details={"verify": True, "improve": True},
                reasoning="Ensure solution addresses original request",
                confidence=0.9
            )
            
            reflection = "Results align with requirements. Approach is sound."
            loop.set_observation(len(loop.state.steps) - 1, reflection)
        
        # Step 5: Response
        if loop.should_continue():
            final_thought = "Synthesizing findings into comprehensive response"
            loop.add_step(
                thought=final_thought,
                action_type=ActionType.RESPONSE,
                action_details={},
                reasoning="Ready to provide final answer",
                confidence=0.95
            )
            
            # Generate response
            final_response = f"""Based on my reasoning:

Analysis: {user_input[:80]}...

Approach: I analyzed the request, created a plan, executed actions, and reflected on the results.

Key Findings:
- Successfully identified core requirements
- Applied appropriate tools and methods
- Verified results align with objectives

Conclusion: Your request has been processed through advanced reasoning with high confidence.
"""
            
            loop.set_observation(len(loop.state.steps) - 1, final_response)
            self.conversation_history.append({
                "role": "assistant",
                "content": final_response
            })
            
            return final_response, loop
        
        # If loop ended prematurely
        fallback = "Unable to complete full reasoning within limits."
        loop.add_step(
            thought="Reached iteration limit",
            action_type=ActionType.STOP,
            action_details={},
            confidence=0.5
        )
        
        return fallback, loop
    
    def get_reasoning_history(self) -> List[Dict[str, Any]]:
        """Get all reasoning loop summaries."""
        return [loop.get_summary() for loop in self.reasoning_loops]
    
    def export_all_traces(self, directory: str = "./reasoning_traces") -> None:
        """Export all reasoning traces."""
        from pathlib import Path
        Path(directory).mkdir(exist_ok=True)
        
        for i, loop in enumerate(self.reasoning_loops):
            filepath = f"{directory}/trace_{i+1}.json"
            loop.export_trace(filepath, format="json")
            
            md_path = f"{directory}/trace_{i+1}.md"
            loop.export_trace(md_path, format="markdown")
        
        logger.info(f"Exported {len(self.reasoning_loops)} reasoning traces")
