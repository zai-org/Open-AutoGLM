# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- **Async/Await Support**: Complete async implementation for better performance
  - `AsyncPhoneAgent` for async task execution
  - Async ADB operations (`async_device.py`, `async_screenshot.py`)
  - Async model client (`async_client.py`)
  - Async example usage (`examples/async_usage.py`)
  - Async unit tests (`tests/test_async_agent.py`)
  - Backward compatible - sync versions still available

### Security
- **CRITICAL**: Fixed security vulnerability in `parse_action()` function by replacing `eval()` with safe AST-based parsing
  - Prevents code injection attacks
  - Maintains backward compatibility with existing action formats

### Added
- Comprehensive logging system with colored output (`phone_agent/utils/logger.py`)
- Input validation utilities (`phone_agent/utils/validation.py`)
  - Coordinate validation and clamping
  - App name validation
  - URL and port validation
- Retry logic for network operations and ADB commands (`phone_agent/utils/retry.py`)
  - Configurable retry attempts and delays
  - Exponential backoff support
  - Custom exception handling
- Unit test suite
  - Tests for action parsing (`tests/test_action_parser.py`)
  - Tests for validation utilities (`tests/test_validation.py`)
  - Tests for retry logic (`tests/test_retry.py`)
- Pytest configuration (`pytest.ini`)

### Changed
- Enhanced error handling throughout the codebase
- Improved logging in ADB operations (`phone_agent/adb/device.py`)
- Added retry logic to model client requests (`phone_agent/model/client.py`)
- Updated action handler to use validation utilities (`phone_agent/actions/handler.py`)

### Improved
- Better error messages and logging
- More robust ADB command execution with retry logic
- Input validation prevents invalid operations
- Type safety improvements

## [0.1.0] - Initial Release

- Initial release of Open-AutoGLM
- Basic phone automation functionality
- ADB integration
- Model client for AI inference

