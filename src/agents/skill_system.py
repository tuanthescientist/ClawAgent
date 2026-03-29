"""Skill system for dynamic agent capabilities."""

import json
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class Skill:
    """Represents an agent skill."""
    
    def __init__(
        self,
        name: str,
        description: str,
        instructions: str,
        examples: Optional[List[str]] = None,
        prerequisites: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict] = None
    ):
        self.name = name
        self.description = description
        self.instructions = instructions
        self.examples = examples or []
        self.prerequisites = prerequisites or []
        self.tags = tags or []
        self.metadata = metadata or {}
        self.created_at = datetime.now()
        self.usage_count = 0
        self.success_rate = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "instructions": self.instructions,
            "examples": self.examples,
            "prerequisites": self.prerequisites,
            "tags": self.tags,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "usage_count": self.usage_count,
            "success_rate": self.success_rate
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "Skill":
        """Create from dictionary."""
        skill = cls(
            name=data["name"],
            description=data["description"],
            instructions=data["instructions"],
            examples=data.get("examples", []),
            prerequisites=data.get("prerequisites", []),
            tags=data.get("tags", []),
            metadata=data.get("metadata", {})
        )
        skill.usage_count = data.get("usage_count", 0)
        skill.success_rate = data.get("success_rate", 1.0)
        return skill


class SkillLibrary:
    """Manages agent skills."""
    
    def __init__(self, storage_path: Optional[str] = None):
        self.skills: Dict[str, Skill] = {}
        self.storage_path = Path(storage_path) if storage_path else Path("./skills")
        self.storage_path.mkdir(exist_ok=True)
        self._load_skills()
    
    def add_skill(self, skill: Skill) -> None:
        """Add a skill to library.
        
        Args:
            skill: Skill instance
        """
        if skill.name in self.skills:
            logger.warning(f"Skill {skill.name} already exists, overwriting")
        
        self.skills[skill.name] = skill
        self._save_skill(skill)
        logger.info(f"Added skill: {skill.name}")
    
    def remove_skill(self, skill_name: str) -> bool:
        """Remove a skill.
        
        Args:
            skill_name: Name of skill to remove
            
        Returns:
            bool: True if removed
        """
        if skill_name in self.skills:
            del self.skills[skill_name]
            skill_file = self.storage_path / f"{skill_name}.json"
            if skill_file.exists():
                skill_file.unlink()
            logger.info(f"Removed skill: {skill_name}")
            return True
        return False
    
    def get_skill(self, skill_name: str) -> Optional[Skill]:
        """Get a skill by name.
        
        Args:
            skill_name: Skill name
            
        Returns:
            Skill or None
        """
        return self.skills.get(skill_name)
    
    def list_skills(self, tag: Optional[str] = None) -> List[Skill]:
        """List all skills, optionally filtered by tag.
        
        Args:
            tag: Optional tag filter
            
        Returns:
            list: List of skills
        """
        if tag:
            return [s for s in self.skills.values() if tag in s.tags]
        return list(self.skills.values())
    
    def get_relevant_skills(self, query: str, max_skills: int = 5) -> List[Skill]:
        """Get skills relevant to a query.
        
        Args:
            query: Query string
            max_skills: Maximum skills to return
            
        Returns:
            list: Relevant skills
        """
        query_lower = query.lower()
        scores = []
        
        for skill in self.skills.values():
            score = 0
            
            # Check description match
            if query_lower in skill.description.lower():
                score += 3
            
            # Check tags match
            for tag in skill.tags:
                if query_lower in tag.lower():
                    score += 2
            
            # Check name match
            if query_lower in skill.name.lower():
                score += 1
            
            # Weight by usage and success
            score *= (1 + skill.usage_count * 0.1) * skill.success_rate
            
            if score > 0:
                scores.append((skill, score))
        
        # Sort by score
        scores.sort(key=lambda x: x[1], reverse=True)
        return [s[0] for s in scores[:max_skills]]
    
    def get_system_prompt_with_skills(
        self,
        base_prompt: str,
        skills: Optional[List[Skill]] = None
    ) -> str:
        """Build system prompt including skills.
        
        Args:
            base_prompt: Base system prompt
            skills: Optional list of skills to include
            
        Returns:
            str: Enhanced system prompt
        """
        if skills is None:
            skills = list(self.skills.values())
        
        prompt_parts = [base_prompt]
        
        if skills:
            prompt_parts.append("\n\n## Available Skills:")
            for skill in skills:
                prompt_parts.append(f"\n### {skill.name}")
                prompt_parts.append(f"Description: {skill.description}")
                prompt_parts.append(f"Instructions: {skill.instructions}")
                
                if skill.examples:
                    prompt_parts.append("Examples:")
                    for example in skill.examples:
                        prompt_parts.append(f"  - {example}")
        
        return "\n".join(prompt_parts)
    
    def record_skill_usage(self, skill_name: str, success: bool = True) -> None:
        """Record skill usage.
        
        Args:
            skill_name: Skill name
            success: Whether usage was successful
        """
        if skill_name in self.skills:
            skill = self.skills[skill_name]
            skill.usage_count += 1
            
            # Update success rate (exponential moving average)
            alpha = 0.1
            skill.success_rate = alpha * (1.0 if success else 0.0) + (1 - alpha) * skill.success_rate
            
            self._save_skill(skill)
    
    def _load_skills(self) -> None:
        """Load skills from disk."""
        try:
            for skill_file in self.storage_path.glob("*.json"):
                with open(skill_file, "r") as f:
                    skill_data = json.load(f)
                    skill = Skill.from_dict(skill_data)
                    self.skills[skill.name] = skill
            
            logger.info(f"Loaded {len(self.skills)} skills")
        except Exception as e:
            logger.error(f"Error loading skills: {str(e)}")
    
    def _save_skill(self, skill: Skill) -> None:
        """Save a skill to disk."""
        try:
            skill_file = self.storage_path / f"{skill.name}.json"
            with open(skill_file, "w") as f:
                json.dump(skill.to_dict(), f, indent=2)
        except Exception as e:
            logger.error(f"Error saving skill {skill.name}: {str(e)}")
    
    def export_all(self, filepath: str) -> None:
        """Export all skills to file.
        
        Args:
            filepath: Output file path
        """
        try:
            skills_data = [skill.to_dict() for skill in self.skills.values()]
            with open(filepath, "w") as f:
                json.dump(skills_data, f, indent=2)
            logger.info(f"Exported {len(skills_data)} skills to {filepath}")
        except Exception as e:
            logger.error(f"Error exporting skills: {str(e)}")


# Built-in Skills
DEFAULT_SKILLS = [
    Skill(
        name="reasoning",
        description="Break down complex problems into steps",
        instructions="1. Identify the problem\n2. Break into subtasks\n3. Solve each step\n4. Verify solution",
        examples=["Complex math problems", "Multi-step planning"],
        tags=["problem-solving", "planning"]
    ),
    Skill(
        name="web_search",
        description="Search for current information online",
        instructions="Use web search to find current information, then synthesize results",
        examples=["Current events", "Recent research"],
        tags=["information", "research"]
    ),
    Skill(
        name="code_generation",
        description="Write and debug code",
        instructions="Generate clean, documented code with error handling",
        examples=["Python scripts", "API integrations"],
        tags=["programming", "development"]
    ),
    Skill(
        name="summarization",
        description="Summarize long text concisely",
        instructions="Extract key points while maintaining meaning",
        examples=["Document summaries", "Meeting notes"],
        tags=["text", "analysis"]
    ),
    Skill(
        name="creative_writing",
        description="Generate creative content",
        instructions="Generate original, engaging content in specified style",
        examples=["Stories", "Poetry", "Marketing copy"],
        tags=["creative", "writing"]
    ),
]
