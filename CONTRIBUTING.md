# Contributing to Open-AutoGLM

Thank you for your interest in contributing to Open-AutoGLM! This document outlines the improvements and contributions made to enhance the codebase.

## Recent Contributions

### 🔒 Security Improvements

1. **Fixed Critical Security Vulnerability**
   - **Issue**: The `parse_action()` function used `eval()` which is a security risk
   - **Solution**: Replaced `eval()` with safe AST-based parsing and regex fallback
   - **Files**: `phone_agent/actions/handler.py`
   - **Impact**: Prevents code injection attacks while maintaining functionality

### 🛠️ Code Quality Improvements

2. **Comprehensive Logging System**
   - **Added**: Professional logging infrastructure with colored output
   - **Files**: `phone_agent/utils/logger.py`
   - **Features**:
     - Colored console output for better readability
     - Configurable log levels
     - Structured logging format
   - **Usage**: Replace `print()` statements with `logger.info()`, `logger.error()`, etc.

3. **Input Validation Utilities**
   - **Added**: Comprehensive validation functions
   - **Files**: `phone_agent/utils/validation.py`
   - **Features**:
     - Coordinate validation and clamping
     - App name validation
     - URL validation
     - Port number validation
   - **Impact**: Prevents invalid inputs and improves error messages

4. **Retry Logic for Network Operations**
   - **Added**: Automatic retry mechanism with exponential backoff
   - **Files**: `phone_agent/utils/retry.py`
   - **Features**:
     - Configurable retry attempts and delays
     - Exponential backoff support
     - Custom exception handling
     - Retry callbacks
   - **Usage**: Applied to ADB commands and model API calls

### 🧪 Testing Infrastructure

5. **Unit Tests**
   - **Added**: Comprehensive test suite
   - **Files**: 
     - `tests/test_action_parser.py` - Tests for action parsing
     - `tests/test_validation.py` - Tests for validation utilities
     - `tests/test_retry.py` - Tests for retry logic
   - **Configuration**: `pytest.ini` for test configuration
   - **Coverage**: Core functionality is now tested

### 📝 Code Improvements

6. **Enhanced Error Handling**
   - Improved error messages throughout the codebase
   - Better exception handling in ADB operations
   - More informative error logging

7. **Type Safety**
   - Improved type hints consistency
   - Better type annotations for better IDE support

## Running Tests

To run the test suite:

```bash
# Install test dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run with coverage
pytest --cov=phone_agent --cov-report=html

# Run specific test file
pytest tests/test_action_parser.py
```

## Code Style

This project follows PEP 8 style guidelines. We use:
- `black` for code formatting
- `mypy` for type checking
- `pytest` for testing

## Async/Await Support

The project now includes async versions of key components for better performance:

### AsyncPhoneAgent

Use `AsyncPhoneAgent` for async operations:

```python
import asyncio
from phone_agent.async_agent import AsyncPhoneAgent
from phone_agent.model import ModelConfig

async def main():
    model_config = ModelConfig(base_url="http://localhost:8000/v1")
    agent = AsyncPhoneAgent(model_config=model_config)
    result = await agent.run("Open WeChat and send a message")
    print(result)

asyncio.run(main())
```

### Benefits

- **Better Performance**: Non-blocking I/O operations
- **Concurrent Operations**: Can handle multiple tasks concurrently
- **Backward Compatible**: Sync versions still available

### Files

- `phone_agent/async_agent.py` - Async agent implementation
- `phone_agent/adb/async_device.py` - Async device operations
- `phone_agent/adb/async_screenshot.py` - Async screenshot capture
- `phone_agent/model/async_client.py` - Async model client
- `examples/async_usage.py` - Usage examples

## Future Improvements

Potential areas for future contributions:

1. **Configuration Files**: Support for YAML/JSON configuration files
2. **More Tests**: Expand test coverage to 90%+
3. **Documentation**: Enhanced API documentation
4. **Performance**: Further optimize screenshot and ADB operations
5. **Batch Operations**: Support for batch task execution

## How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass (`pytest`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## Questions?

Feel free to open an issue for questions or discussions about contributions.

