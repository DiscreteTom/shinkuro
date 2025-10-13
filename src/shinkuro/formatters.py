"""Template formatters for different variable syntax."""

import re
import string
from typing import Protocol, Dict, Any
from .model import FormatterType

# Python identifier pattern for argument names and template variables
IDENTIFIER_PATTERN = r"^[a-zA-Z_][a-zA-Z0-9_]*$"


def validate_variable_name(name: str) -> bool:
    """Validate that a variable name is a valid Python identifier."""
    return bool(re.match(IDENTIFIER_PATTERN, name))


class FormatterInterface(Protocol):
    """Protocol for template formatters."""

    def extract_arguments(self, content: str) -> set[str]:
        """Extract and validate argument names from content."""
        ...

    def format(self, content: str, variables: Dict[str, Any]) -> str:
        """Format content with variables."""
        ...


class BraceFormatter:
    """Formatter for {var} syntax."""

    def extract_arguments(self, content: str) -> set[str]:
        formatter = string.Formatter()
        arguments = set()
        for _, field_name, _, _ in formatter.parse(content):
            if field_name:
                if not validate_variable_name(field_name):
                    raise ValueError(f"Invalid variable name: {field_name}")
                arguments.add(field_name)
        return arguments

    def format(self, content: str, variables: Dict[str, Any]) -> str:
        return content.format(**variables)


class DollarFormatter:
    """Formatter for $var syntax."""

    def extract_arguments(self, content: str) -> set[str]:
        try:
            template = string.Template(content)
            arguments = set()
            for match in template.pattern.finditer(content):
                if match.group("named"):
                    param = match.group("named")
                    if not validate_variable_name(param):
                        raise ValueError(f"Invalid variable name: {param}")
                    arguments.add(param)
            return arguments
        except ValueError as e:
            raise ValueError(f"Invalid template syntax: {e}")

    def format(self, content: str, variables: Dict[str, Any]) -> str:
        template = string.Template(content)
        return template.safe_substitute(variables)


def get_formatter(formatter_type: FormatterType) -> FormatterInterface:
    """Get formatter by type."""
    formatters = {
        FormatterType.BRACE: BraceFormatter(),
        FormatterType.DOLLAR: DollarFormatter(),
    }
    if formatter_type not in formatters:
        raise ValueError(f"Unknown formatter: {formatter_type}")
    return formatters[formatter_type]
