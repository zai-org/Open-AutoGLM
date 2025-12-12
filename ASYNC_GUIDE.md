# Async/Await Guide for Open-AutoGLM

This guide explains how to use the async/await API for better performance in Open-AutoGLM.

## Why Use Async?

The async API provides several benefits:

1. **Better Performance**: Non-blocking I/O operations allow better resource utilization
2. **Concurrent Operations**: Can handle multiple tasks simultaneously
3. **Scalability**: Better for applications that need to handle many operations

## Quick Start

### Basic Async Usage

```python
import asyncio
from phone_agent.async_agent import AsyncPhoneAgent
from phone_agent.model import ModelConfig

async def main():
    # Configure model
    model_config = ModelConfig(
        base_url="http://localhost:8000/v1",
        model_name="autoglm-phone-9b",
    )
    
    # Create async agent
    agent = AsyncPhoneAgent(model_config=model_config)
    
    # Run task
    result = await agent.run("打开微信发送消息")
    print(result)

# Run the async function
asyncio.run(main())
```

## Key Differences from Sync API

### 1. Import Statement

**Sync**:
```python
from phone_agent import PhoneAgent
```

**Async**:
```python
from phone_agent.async_agent import AsyncPhoneAgent
```

### 2. Method Calls

**Sync**:
```python
result = agent.run("task")
```

**Async**:
```python
result = await agent.run("task")
```

### 3. Configuration

**Sync**:
```python
from phone_agent.agent import AgentConfig
config = AgentConfig(max_steps=100)
```

**Async**:
```python
from phone_agent.async_agent import AsyncAgentConfig
config = AsyncAgentConfig(max_steps=100)
```

## Advanced Usage

### Step-by-Step Execution

```python
async def step_by_step():
    agent = AsyncPhoneAgent(model_config)
    
    # First step requires task
    result = await agent.step("打开微信")
    print(f"Step 1: {result.action}")
    
    # Subsequent steps don't need task
    if not result.finished:
        result = await agent.step()
        print(f"Step 2: {result.action}")
```

### Concurrent Tasks

```python
async def run_multiple_tasks():
    agent = AsyncPhoneAgent(model_config)
    
    # Run multiple tasks concurrently
    tasks = [
        agent.run("打开微信"),
        agent.run("打开QQ"),
        agent.run("打开微博"),
    ]
    
    results = await asyncio.gather(*tasks)
    for result in results:
        print(result)
```

### Custom Async Callbacks

```python
async def async_confirmation(message: str) -> bool:
    """Async confirmation callback."""
    # Can do async operations here
    response = await get_user_input_async(message)
    return response.lower() == "y"

async def async_takeover(message: str) -> None:
    """Async takeover callback."""
    await notify_user_async(message)
    await wait_for_user_completion_async()

agent = AsyncPhoneAgent(
    model_config=model_config,
    confirmation_callback=async_confirmation,
    takeover_callback=async_takeover,
)
```

## Performance Comparison

### Sync API
- Blocks on I/O operations
- Sequential execution
- Simple to use

### Async API
- Non-blocking I/O
- Can run operations concurrently
- Better for high-throughput scenarios

## Migration Guide

### From Sync to Async

1. **Change imports**:
   ```python
   # Before
   from phone_agent import PhoneAgent
   
   # After
   from phone_agent.async_agent import AsyncPhoneAgent
   ```

2. **Wrap in async function**:
   ```python
   # Before
   agent = PhoneAgent(model_config)
   result = agent.run("task")
   
   # After
   async def main():
       agent = AsyncPhoneAgent(model_config)
       result = await agent.run("task")
   
   asyncio.run(main())
   ```

3. **Update configuration**:
   ```python
   # Before
   from phone_agent.agent import AgentConfig
   
   # After
   from phone_agent.async_agent import AsyncAgentConfig
   ```

## Examples

See `examples/async_usage.py` for complete examples including:
- Basic async usage
- Step-by-step execution
- Error handling
- Custom callbacks

## Backward Compatibility

The sync API remains fully functional. You can use either:
- **Sync API**: `PhoneAgent` - Simple, blocking operations
- **Async API**: `AsyncPhoneAgent` - Advanced, non-blocking operations

Both APIs share the same underlying functionality and produce the same results.

## Troubleshooting

### Common Issues

1. **Forgetting `await`**:
   ```python
   # Wrong
   result = agent.run("task")
   
   # Correct
   result = await agent.run("task")
   ```

2. **Not using `asyncio.run()`**:
   ```python
   # Wrong
   main()  # This won't work
   
   # Correct
   asyncio.run(main())
   ```

3. **Mixing sync and async**:
   ```python
   # Avoid mixing sync and async in the same function
   # Use one or the other consistently
   ```

## Best Practices

1. **Use async for I/O-bound operations**: Screenshots, network requests
2. **Use sync for simple scripts**: If you don't need concurrency
3. **Handle errors properly**: Use try/except with async functions
4. **Use async context managers**: For resource cleanup when available

## API Reference

### AsyncPhoneAgent

- `run(task: str) -> str`: Execute a task asynchronously
- `step(task: str | None = None) -> AsyncStepResult`: Execute a single step
- `reset() -> None`: Reset agent state
- `context`: Get conversation context
- `step_count`: Get current step count

### AsyncAgentConfig

- `max_steps: int`: Maximum steps per task
- `device_id: str | None`: ADB device ID
- `lang: str`: Language (cn/en)
- `verbose: bool`: Verbose output
- `system_prompt: str | None`: Custom system prompt

## See Also

- `examples/async_usage.py` - Complete examples
- `tests/test_async_agent.py` - Test cases
- Main README.md for general usage

