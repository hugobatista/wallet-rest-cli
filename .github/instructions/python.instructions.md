---
description: 'Python coding conventions and guidelines'
applyTo: '**/*.py'
---

# Python Coding Conventions

## Project structure, frameworks and libraries
- if implementing a web api, use FastAPI as the framework. FastAPI is a high-performance api framework that allows you to build APIs quickly and efficiently with Python. Always #fetch the latest documentation from https://fastapi.tiangolo.com/ 
- use pyproject.toml to specify project metadata and dependencies. This file should include information about the project, such as its name, version, and any required packages. 
- use uv to manage dependencies and run the project. 
- on uv make sure to exclude newer versions of dependencies for 30 days. Add this to the pyproject.toml file:

```toml
[tool.uv]
exclude-newer = "30 days"
```
- Packages are a good way to organize code and manage dependencies. Avoid monolithic files and break down the code into smaller, more manageable modules. Avoid modules > 500 lines of code and use packages instead of prefixing modules with the same name.

- use hatch when needed. Hatch is a modern Python package manager that provides a streamlined workflow for building, testing, and publishing Python packages. 


mandatory pyproject.toml sections:

```toml
name = "projectname"
version = "0.1.0" # replace with your project version
description = "A brief description of your project"
readme = "README.md"
requires-python = ">=3.11"


[project]
requires-python = ">=3.11"

[project.scripts]
# add any CLI entry points here, for example:
projectname = "projectname.cli:main"

[tool.uv]
exclude-newer = "30 days"


[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/projectname"]  # replace with your package name

[tool.hatch.envs.default]
features = ["dev"]

[tool.hatch.envs.default.scripts]
lint = "ruff check . --fix"
format = "black ."
format-check = "black --check ."
test = "pytest src tests --cov=src/projectname --cov-fail-under=100 -v"
typecheck = "mypy src --strict --no-incremental"
validate = ["lint", "format", "test", "typecheck"]
check = ["lint", "format", "test", "typecheck"]

[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]

[tool.coverage.run]
source = ["src/projectname"]  # replace with your package name
omit = [
    "*/__init__.py",
]

[tool.coverage.report]
show_missing = true
skip_covered = false
fail_under = 100

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
check_untyped_defs = true
no_implicit_optional = true
files = ["src"]
exclude = ["tests/"]

```



## Coverage and testing
- unit tests should always be included for new features and bug fixes. 
- coverage should be maintained at a high level, and always work for the 100% of the codebase.
- avoid "pragma: no cover" at all cost. If you find yourself needing to use it, consider refactoring the code to make it more testable instead.



## Python Instructions

- Write clear and concise comments for each function.
- Ensure functions have descriptive names and include type hints.
- Provide docstrings following PEP 257 conventions.
- Use the `typing` module for type annotations (e.g., `List[str]`, `Dict[str, int]`).
- Break down complex functions into smaller, more manageable functions.

## General Instructions

- even if the prompt is in another language, write code in English to ensure accessibility and maintainability.
- Always prioritize readability and clarity.
- For algorithm-related code, include explanations of the approach used.
- Write code with good maintainability practices, including comments on why certain design decisions were made.
- Handle edge cases and write clear exception handling.
- For libraries or external dependencies, mention their usage and purpose in comments.
- Use consistent naming conventions and follow language-specific best practices.
- Write concise, efficient, and idiomatic code that is also easily understandable.

## Code Style and Formatting

- Follow the **PEP 8** style guide for Python.
- Maintain proper indentation (use 4 spaces for each level of indentation).
- Ensure lines do not exceed 79 characters.
- Place function and class docstrings immediately after the `def` or `class` keyword.
- Use blank lines to separate functions, classes, and code blocks where appropriate.

## Edge Cases and Testing

- Always include test cases for critical paths of the application.
- Account for common edge cases like empty inputs, invalid data types, and large datasets.
- Include comments for edge cases and the expected behavior in those cases.
- Write unit tests for functions and document them with docstrings explaining the test cases.

## Example of Proper Documentation

```python
def calculate_area(radius: float) -> float:
    """
    Calculate the area of a circle given the radius.
    
    Parameters:
    radius (float): The radius of the circle.
    
    Returns:
    float: The area of the circle, calculated as π * radius^2.
    """
    import math
    return math.pi * radius ** 2
```
