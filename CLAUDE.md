# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Development Setup
```bash
# Install package with development dependencies using uv
uv pip install -e ".[dev]"

# Run all tests
uv run pytest

# Run tests with verbose output
uv run pytest -v

# Run a specific test file
uv run pytest tests/test_client.py

# Run a specific test class or method
uv run pytest tests/test_client.py::TestHexClient::test_client_initialization

# Run tests with coverage
uv run pytest --cov=src/hex_api --cov-report=html
```

### Code Quality
```bash
# Format code with Ruff
uv run ruff format src tests

# Lint with Ruff
uv run ruff check src tests

# Fix linting issues automatically (when possible)
uv run ruff check --fix src tests

# Type check with mypy
uv run mypy src

# Run all checks (format, lint, type check)
uv run ruff format src tests && uv run ruff check src tests && uv run mypy src
```

## Architecture

### Client-Resource Pattern
The SDK uses a client-resource pattern where the main `HexClient` class acts as the entry point and owns resource instances:

- `HexClient` (in `client.py`) - Main client that handles HTTP requests and authentication
- Resource classes (in `resources/`) - Domain-specific functionality attached to the client
  - `ProjectsResource` - Project operations (list, get, run)
  - `RunsResource` - Run monitoring and management
  - `EmbeddingResource` - Embedding URL generation
  - `SemanticModelsResource` - Semantic model operations

All resources inherit from `BaseResource` which provides common HTTP methods and response parsing.

### Model Organization
Models are organized by domain in the `models/` directory:
- All models inherit from `HexBaseModel` which configures Pydantic v2 settings
- Models use field aliases to map between Python snake_case and API camelCase
- Enums are used extensively for type safety (e.g., `RunStatus`, `ProjectType`)

### Error Handling
Custom exception hierarchy in `exceptions.py`:
- `HexAPIError` - Base exception with trace_id support
- Specialized exceptions for different HTTP status codes (401, 404, 422, 429, 5xx)
- Validation errors include details about invalid/missing parameters

### Configuration
`HexConfig` uses Pydantic for validation and supports:
- Environment variables (`HEX_API_KEY`, `HEX_API_BASE_URL`)
- Direct instantiation with overrides
- Automatic URL cleaning and validation

## Key Design Decisions

1. **Synchronous Only**: The SDK is synchronous-only for simplicity. Async was removed as it's overkill for most Hex API use cases.

2. **Pydantic v2**: Uses modern Pydantic v2 with `ConfigDict` and `field_validator` instead of deprecated v1 patterns.

3. **Type Safety**: Extensive use of type hints, enums, and Pydantic models for compile-time safety.

4. **Resource Methods**: Resources use method names that match the API actions (e.g., `projects.run()` not `projects.create_run()`).

## Testing

Tests use pytest with comprehensive mocking:
- `conftest.py` provides shared fixtures for mock clients and sample data
- Tests are organized to mirror the source structure
- Mock HTTP responses are used to avoid actual API calls
- Each resource and model has dedicated test files

## API Coverage

The SDK implements these Hex API endpoints:
- `GET/POST /v1/projects/*` - Project operations
- `GET/POST/DELETE /v1/projects/{id}/runs/*` - Run management  
- `POST /v1/embedding/createPresignedUrl/{id}` - Embedding
- `POST /v1/semantic-models/{id}/ingest` - Semantic models

Note: The semantic models ingest endpoint requires multipart file upload which is not yet implemented.