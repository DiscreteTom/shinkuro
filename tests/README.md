# Shinkuro Test Suite

This directory contains the comprehensive test suite for Shinkuro, focusing on security validation and core functionality.

## Running Tests

### Run All Tests
```fish
uv run pytest
```

### Run with Verbose Output
```fish
uv run pytest -v
```

### Run Specific Test File
```fish
uv run pytest tests/test_security.py
```

### Run Specific Test Class or Function
```fish
uv run pytest tests/test_security.py::TestValidateSafePath
uv run pytest tests/test_security.py::TestValidateSafePath::test_path_traversal_blocked_with_base
```

### Run with Coverage Report
```fish
uv run pytest --cov=shinkuro --cov-report=html
```

The coverage report will be generated in `htmlcov/index.html`.

## Test Organization

### `test_security.py` - Security Validation Tests (14 tests)

Tests for the security validation functions in `src/shinkuro/security.py`:

- **`TestValidateSafePath`** - Path traversal prevention
  - Valid absolute and relative paths
  - Path traversal blocking with base path boundary
  - Symlink escape prevention

- **`TestValidatePythonIdentifier`** - Python identifier validation
  - Valid identifier patterns
  - Invalid patterns (numeric start, special chars)
  - Dangerous identifier blocking (`__import__`, `eval`, `exec`, etc.)
  - Dunder method prevention

- **`TestValidatePathComponent`** - Path component validation
  - Valid components (usernames, repo names)
  - Empty component blocking
  - Dot traversal prevention (`.`, `..`)
  - Path separator blocking (`/`, `\`)
  - Null byte prevention

### `test_server.py` - Server and Formatting Tests (15 tests)

Tests for safe string formatting and prompt function creation:

- **`TestSafeFormatter`** - Format string security
  - Basic and multiple variable substitution
  - Attribute access blocking (`{obj.__class__}`)
  - Item access blocking (`{data[key]}`)
  - Method call blocking (`{name.upper()}`)
  - Missing key error handling

- **`TestCreatePromptFunction`** - Dynamic prompt generation
  - Prompts without arguments
  - Prompts with valid arguments
  - Dangerous argument name rejection
  - Invalid identifier rejection
  - Default value handling
  - Multiple argument support

### `test_git.py` - Git URL Validation Tests (13 tests)

Tests for git URL parsing and security validation:

- **`TestExtractUserRepo`** - URL parsing and validation
  - GitHub HTTPS and SSH URL parsing
  - GitLab URL support
  - URLs without `.git` extension
  - Missing user/repo detection
  - Path traversal attack prevention
  - Legitimate special characters (dots, hyphens, underscores)
  - Null byte blocking

### `test_file.py` - File Scanning Tests (11 tests)

Tests for markdown file scanning and error handling:

- **`TestScanMarkdownFiles`** - Markdown processing
  - Valid markdown files
  - Frontmatter parsing (name, title, description, arguments)
  - Multiple and nested file scanning
  - Nonexistent directory handling
  - Malformed markdown logging
  - Invalid frontmatter type handling
  - Empty files
  - Default argument values
  - Non-markdown file filtering

### `test_integration.py` - Integration Tests (11 tests)

End-to-end tests for server creation and functionality:

- **`TestServerIntegration`** - Full workflow testing
  - Simple prompt loading
  - Parameterized prompts with arguments
  - Mixed prompt types
  - Invalid prompt skipping
  - Nested directory support
  - Empty directory handling
  - Multiple argument prompts
  - Content preservation
  - Special character handling
  - SafeFormatter integration

## Test Fixtures

### `conftest.py` - Shared Fixtures

- **`sample_prompts_dir(tmp_path)`** - Creates a directory with sample markdown prompts:
  - Simple prompt without arguments
  - Prompt with frontmatter and arguments
  - Prompt with default arguments

- **`empty_dir(tmp_path)`** - Creates an empty temporary directory

### Helper Functions

- **`get_prompt_count(mcp: FastMCP) -> int`** - Synchronously retrieves the number of registered prompts from a FastMCP instance (in `test_server.py` and `test_integration.py`)

## Writing New Tests

### Test Structure

```python
import pytest
from shinkuro.module import function_to_test


class TestFunctionName:
    """Tests for function_to_test."""

    def test_expected_behavior(self):
        """Test that function works with valid input."""
        result = function_to_test("valid_input")
        assert result == "expected_output"

    def test_invalid_input_raises_error(self):
        """Test that function raises error with invalid input."""
        with pytest.raises(ValueError, match="error message pattern"):
            function_to_test("invalid_input")
```

### Using Fixtures

```python
def test_with_temp_directory(tmp_path):
    """pytest automatically provides tmp_path fixture."""
    test_file = tmp_path / "test.md"
    test_file.write_text("content")
    assert test_file.exists()

def test_with_custom_fixture(sample_prompts_dir):
    """Use custom fixture from conftest.py."""
    prompts = list(scan_markdown_files(str(sample_prompts_dir)))
    assert len(prompts) == 3
```

### Testing Error Conditions

```python
# Test specific exception type
with pytest.raises(ValueError):
    dangerous_function()

# Test exception message pattern
with pytest.raises(ValueError, match="path traversal"):
    dangerous_function("../etc")

# Test multiple exception types
with pytest.raises((ValueError, AttributeError)):
    function_that_may_raise_different_errors()
```

### Capturing Output

```python
def test_error_logging(tmp_path, capsys):
    """Test that errors are logged to stderr."""
    # ... perform operation that logs to stderr ...

    captured = capsys.readouterr()
    assert "Warning:" in captured.err
    assert "error details" in captured.err
```

## Security Test Guidelines

When writing security tests:

1. **Test the Attack** - Verify that actual attack patterns are blocked:
   ```python
   def test_attribute_access_blocked(self):
       formatter = SafeFormatter()
       with pytest.raises(ValueError):
           formatter.format("{obj.__class__}", obj=object())
   ```

2. **Test Valid Input** - Ensure legitimate use cases still work:
   ```python
   def test_valid_identifier(self):
       validate_python_identifier("valid_name")  # Should not raise
   ```

3. **Test Boundaries** - Check edge cases:
   ```python
   def test_single_underscore_allowed(self):
       validate_python_identifier("_private")  # Single underscore OK

   def test_dunder_methods_blocked(self):
       with pytest.raises(ValueError):
           validate_python_identifier("__custom__")  # Double underscore blocked
   ```

4. **Document Attack Vectors** - Explain what you're testing:
   ```python
   def test_symlink_escape_blocked(self, tmp_path):
       """Test that symlinks escaping base are blocked.

       Attack: Create symlink inside base pointing outside base,
       then try to access it. This should be blocked.
       """
   ```

## Test Coverage Goals

Aim for comprehensive coverage of:

- ✅ All security validation functions (100%)
- ✅ Error handling paths
- ✅ Edge cases and boundary conditions
- ✅ Attack vector prevention
- ✅ Integration between components
- ⚠️ Async operations (currently minimal)
- ⚠️ Git clone/update operations (requires mocking)

## Continuous Integration

Tests should be run:
- Before committing changes
- In CI/CD pipeline
- Before merging pull requests

All tests must pass before code can be merged.

## Debugging Failed Tests

### Show Full Traceback
```fish
uv run pytest --tb=long
```

### Show Only Failed Tests
```fish
uv run pytest --lf  # last failed
uv run pytest --ff  # failed first
```

### Drop into Debugger on Failure
```fish
uv run pytest --pdb
```

### Verbose Output with Print Statements
```fish
uv run pytest -v -s
```

## Dependencies

Test dependencies are defined in `pyproject.toml`:
- `pytest>=8.3.4` - Testing framework
- `pytest-cov>=6.0.0` - Coverage reporting

Install with:
```fish
uv sync --dev
```
