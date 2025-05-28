# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Development Setup
```bash
# Install package with development dependencies using uv
uv pip install -e ".[dev]"
```

### Code Quality
```bash
# Format code with Ruff
uv run ruff format src tests

# Lint with Ruff
uv run ruff check src tests

# Fix linting issues automatically (when possible)
uv run ruff check --fix src tests

# Run all checks (format, lint)
uv run ruff format src tests && uv run ruff check src tests
```

## Architecture

### Client-Resource Pattern
The SDK uses a simple client-resource pattern where the main `HexClient` class acts as the entry point and owns resource instances:

- `HexClient` (in `client.py`) - Main client that handles HTTP requests and authentication
- Resource classes (in `resources/`) - Domain-specific functionality attached to the client
  - `ProjectsResource` - Project operations (list, get, run)
  - `RunsResource` - Run monitoring and management
  - `EmbeddingResource` - Embedding URL generation
  - `SemanticModelsResource` - Semantic model operations

All resources inherit from `BaseResource` which provides common HTTP methods. Resources return plain Python dicts and lists.

### Response Format
All API responses are returned as plain Python dictionaries. This makes the SDK simple and flexible:
- No model classes to learn
- Direct access to response data
- Easy to work with using standard Python dict operations
- Field names match the API's camelCase format (e.g., `projectId`, `runUrl`)

### Error Handling
Custom exception hierarchy in `exceptions.py`:
- `HexAPIError` - Base exception with trace_id support
- Specialized exceptions for different HTTP status codes (401, 404, 422, 429, 5xx)
- Validation errors include details about invalid/missing parameters

### Configuration
`HexConfig` is a simple class that supports:
- Environment variables (`HEX_API_KEY`, `HEX_API_BASE_URL`)
- Direct instantiation with parameters
- Basic validation (API key required)

## Key Design Decisions

1. **Synchronous Only**: The SDK is synchronous-only for simplicity. Async was removed as it's overkill for most Hex API use cases.

2. **No Type System**: No Pydantic, no type hints, no model classes. Just simple Python with dicts and lists.

3. **Direct API Mapping**: Response fields use the same names as the API (camelCase) for transparency.

4. **Resource Methods**: Resources use method names that match the API actions (e.g., `projects.run()` not `projects.create_run()`).

## Testing

Tests use pytest with comprehensive mocking and OpenAPI validation:
- `conftest.py` provides shared fixtures for mock clients and sample data
- Tests are organized to mirror the source structure
- Mock HTTP responses are used to avoid actual API calls
- Each resource and model has dedicated test files
- **OpenAPI Validation**: Mock data is automatically validated against the OpenAPI spec
- **Integration Tests**: Optional tests that use the real API (marked with `@pytest.mark.integration`)

### Running Tests
```bash
# Run unit tests only (default)
uv run pytest

# Run tests with verbose output
uv run pytest -v

# Run a specific test file
uv run pytest tests/test_client.py

# Run a specific test class or method
uv run pytest tests/test_client.py::TestHexClient::test_client_initialization

# Run tests with coverage
uv run pytest --cov=src/hex_toolkit --cov-report=html

# Run all tests including integration tests
uv run pytest -m ""

# Run only integration tests (requires HEX_API_KEY in environment)
uv run pytest -m integration
```

## API Coverage

The SDK implements these Hex API endpoints:
- `GET/POST /v1/projects/*` - Project operations
- `GET/POST/DELETE /v1/projects/{id}/runs/*` - Run management  
- `POST /v1/embedding/createPresignedUrl/{id}` - Embedding
- `POST /v1/semantic-models/{id}/ingest` - Semantic models

Note: The semantic models ingest endpoint requires multipart file upload which is not yet implemented.

## Maintaining the SDK

### Workflow for API Updates
When the Hex API changes, follow this workflow:

1. **Update the OpenAPI spec**:
   ```bash
   # Download latest spec or copy from source
   curl -o hex-openapi.json https://api.hex.tech/openapi.json
   ```

2. **Run tests to detect breaking changes**:
   ```bash
   uv run pytest
   # Validation errors will show exactly what changed
   ```

3. **Fix validation errors**:
   - Update mock data in `conftest.py` for new/changed fields
   - Update resource methods if needed
   - The error messages tell you exactly what needs fixing

4. **Verify with integration test**:
   ```bash
   # Quick smoke test with real API
   uv run python tests/test_integration.py
   ```

5. **Run code quality checks**:
   ```bash
   uv run ruff format src tests && uv run ruff check src tests
   ```

The OpenAPI validation ensures your SDK stays in sync with the API with minimal effort.