from typing import List, Optional
from dataclasses import dataclass
from enum import Enum


class FormatterType(Enum):
    """Available template formatter types."""

    BRACE = "brace"
    DOLLAR = "dollar"


@dataclass
class Argument:
    """Template argument for prompt substitution.

    Attributes:
        name: Parameter name for template substitution
        description: Human-readable description of the parameter
        default: Default value if parameter not provided
    """

    name: str
    description: str
    default: Optional[str] = None


@dataclass
class PromptData:
    """Complete prompt data loaded from markdown file.

    Attributes:
        name: Unique identifier for the prompt
        title: Display title for the prompt
        description: Brief description of prompt purpose
        arguments: Template arguments this prompt accepts
        content: Template content for variable substitution
    """

    name: str
    title: str
    description: str
    arguments: List[Argument]
    content: str
