"""
Shared type definitions for ClawAgent v3.0

Includes:
- Tool call structures
- Reasoning trace components
- Message structures
- Agent responses
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class ReasoningStage(str, Enum):
    """ReAct reasoning stages"""
    UNDERSTAND = "understand"
    PLAN = "plan"
    EXECUTE = "execute"
    OBSERVE = "observe"
    REASON = "reason"
    FINALIZE = "finalize"


class ToolCall(BaseModel):
    """Tool invocation record"""
    name: str = Field(..., description="Tool name")
    args: Dict[str, Any] = Field(..., description="Tool arguments")
    tool_id: str = Field(..., description="Unique tool call ID")
    result: Optional[str] = None
    error: Optional[str] = None
    duration_ms: float = 0.0
    timestamp: datetime = Field(default_factory=datetime.now)


class ReasoningStep(BaseModel):
    """Single step in reasoning trace"""
    stage: ReasoningStage
    description: str = Field(..., description="Step description")
    details: Dict[str, Any] = Field(default_factory=dict)
    tools_used: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.now)
    duration_ms: Optional[float] = None


class ReasoningTrace(BaseModel):
    """Complete reasoning trace for one request"""
    steps: List[ReasoningStep] = Field(default_factory=list)
    tools_used: List[ToolCall] = Field(default_factory=list)
    total_duration_ms: float
    model_used: str
    tokens_used: int
    tokens_input: int = 0
    tokens_output: int = 0
    success: bool = True
    error: Optional[str] = None
    conversation_id: Optional[str] = None
    user_id: Optional[str] = None

    def to_markdown(self) -> str:
        """Export trace to Markdown format"""
        lines = [
            "# Reasoning Trace",
            f"- Model: {self.model_used}",
            f"- Tokens: {self.tokens_used} (input: {self.tokens_input}, output: {self.tokens_output})",
            f"- Duration: {self.total_duration_ms:.2f}ms",
            f"- Status: {'✓ Success' if self.success else '✗ Failed'}",
            "",
            "## Reasoning Steps",
        ]

        for i, step in enumerate(self.steps, 1):
            lines.append(f"\n### Step {i}: {step.stage.value.upper()}")
            lines.append(f"{step.description}")
            if step.details:
                lines.append("**Details:**")
                for key, value in step.details.items():
                    lines.append(f"- {key}: {value}")

        if self.tools_used:
            lines.append("\n## Tools Used")
            for tool in self.tools_used:
                lines.append(f"\n### {tool.name}")
                lines.append(f"Args: {tool.args}")
                if tool.result:
                    lines.append(f"Result: {tool.result}")
                if tool.error:
                    lines.append(f"Error: {tool.error}")

        if self.error:
            lines.append(f"\n## Error\n{self.error}")

        return "\n".join(lines)

    def to_json(self) -> Dict[str, Any]:
        """Export trace to JSON"""
        return self.model_dump_json()


class UserMessage(BaseModel):
    """User message with metadata"""
    user_id: str = Field(..., description="User ID")
    content: str = Field(..., description="Message content")
    conversation_id: str = Field(..., description="Conversation ID")
    message_type: str = Field(default="text", description="Message type")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)


class AgentResponse(BaseModel):
    """Agent response with reasoning trace"""
    content: str = Field(..., description="Response content")
    reasoning_trace: Optional[ReasoningTrace] = None
    tools_used: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)
    user_id: Optional[str] = None
    conversation_id: Optional[str] = None


class ConversationMessage(BaseModel):
    """Message in a conversation"""
    role: str = Field(..., description="'user' or 'assistant'")
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Conversation(BaseModel):
    """Conversation history"""
    conversation_id: str
    user_id: str
    messages: List[ConversationMessage] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def add_message(self, role: str, content: str, metadata: Dict = None):
        """Add message to conversation"""
        self.messages.append(
            ConversationMessage(
                role=role,
                content=content,
                metadata=metadata or {}
            )
        )
        self.updated_at = datetime.now()

    def get_messages(self) -> List[Dict[str, str]]:
        """Get messages in format for LLM"""
        return [
            {"role": m.role, "content": m.content}
            for m in self.messages
        ]


class ToolDefinition(BaseModel):
    """Tool definition for function calling"""
    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    parameters: Dict[str, Any] = Field(..., description="JSON schema for parameters")
    required: List[str] = Field(default_factory=list, description="Required parameters")
    category: str = Field(default="general", description="Tool category")
    enabled: bool = True


class ExecutionContext(BaseModel):
    """Context for tool/code execution"""
    user_id: str
    conversation_id: str
    request_id: str
    timeout_seconds: int = 30
    environment: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ToolExecutionResult(BaseModel):
    """Result from tool execution"""
    tool_name: str
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    duration_ms: float
    tokens_used: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    """Standardized error response"""
    error: str = Field(..., description="Error message")
    error_code: str = Field(..., description="Error code")
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    request_id: Optional[str] = None


class HealthStatus(BaseModel):
    """Health check status"""
    status: str = Field(..., description="'healthy' or 'unhealthy'")
    components: Dict[str, dict] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)
    uptime_seconds: float = 0.0


# Type aliases
Message = Dict[str, str]  # {"role": str, "content": str}
Messages = List[Message]
