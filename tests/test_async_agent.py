"""Tests for async agent functionality."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from phone_agent.async_agent import AsyncAgentConfig, AsyncPhoneAgent, AsyncStepResult
from phone_agent.model import ModelConfig


@pytest.mark.asyncio
class TestAsyncPhoneAgent:
    """Test cases for AsyncPhoneAgent."""

    @pytest.fixture
    def model_config(self):
        """Create a test model config."""
        return ModelConfig(
            base_url="http://localhost:8000/v1",
            model_name="test-model",
        )

    @pytest.fixture
    def agent_config(self):
        """Create a test agent config."""
        return AsyncAgentConfig(
            max_steps=10,
            verbose=False,
        )

    @pytest.fixture
    def agent(self, model_config, agent_config):
        """Create a test async agent."""
        return AsyncPhoneAgent(
            model_config=model_config,
            agent_config=agent_config,
        )

    def test_agent_initialization(self, agent):
        """Test agent initializes correctly."""
        assert agent.model_config is not None
        assert agent.agent_config is not None
        assert agent.step_count == 0
        assert len(agent.context) == 0

    def test_reset(self, agent):
        """Test agent reset functionality."""
        agent._step_count = 5
        agent._context = [{"test": "data"}]
        agent.reset()
        assert agent.step_count == 0
        assert len(agent.context) == 0

    @pytest.mark.asyncio
    async def test_step_requires_task_on_first_call(self, agent):
        """Test that first step requires a task."""
        with pytest.raises(ValueError, match="Task is required"):
            await agent.step()

    @pytest.mark.asyncio
    async def test_step_with_task(self, agent):
        """Test step execution with task."""
        with patch("phone_agent.async_agent.get_screenshot_async") as mock_screenshot, \
             patch("phone_agent.async_agent.get_current_app_async") as mock_app, \
             patch.object(agent.model_client, "request") as mock_request, \
             patch.object(agent.action_handler, "execute") as mock_execute:

            # Setup mocks
            from phone_agent.adb.async_screenshot import Screenshot
            mock_screenshot.return_value = Screenshot(
                base64_data="test", width=1080, height=1920
            )
            mock_app.return_value = "微信"
            
            from phone_agent.model.client import ModelResponse
            mock_request.return_value = ModelResponse(
                thinking="Test thinking",
                action='do(action="Tap", element=[100, 200])',
                raw_content="test",
            )
            
            from phone_agent.actions.handler import ActionResult
            mock_execute.return_value = ActionResult(
                success=True, should_finish=False
            )

            result = await agent.step("Test task")
            
            assert isinstance(result, AsyncStepResult)
            assert result.action is not None
            assert agent.step_count == 1

    def test_context_property(self, agent):
        """Test context property returns a copy."""
        agent._context = [{"test": "data"}]
        context = agent.context
        assert context == [{"test": "data"}]
        # Modify copy - original should not change
        context.append({"new": "data"})
        assert len(agent.context) == 1

    def test_step_count_property(self, agent):
        """Test step_count property."""
        agent._step_count = 5
        assert agent.step_count == 5


@pytest.mark.asyncio
class TestAsyncAgentConfig:
    """Test cases for AsyncAgentConfig."""

    def test_default_config(self):
        """Test default configuration values."""
        config = AsyncAgentConfig()
        assert config.max_steps == 100
        assert config.device_id is None
        assert config.lang == "cn"
        assert config.verbose is True
        assert config.system_prompt is not None

    def test_custom_config(self):
        """Test custom configuration values."""
        config = AsyncAgentConfig(
            max_steps=50,
            device_id="test-device",
            lang="en",
            verbose=False,
        )
        assert config.max_steps == 50
        assert config.device_id == "test-device"
        assert config.lang == "en"
        assert config.verbose is False

