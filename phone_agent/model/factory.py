"""Model client factory for creating different types of model clients."""

from typing import Type

from phone_agent.model.client import ModelClient, ModelConfig


class ModelClientFactory:
    """Factory for creating model clients based on configuration."""
    
    _client_registry: dict[str, Type[ModelClient]] = {}
    
    @classmethod
    def register_client(cls, name: str, client_class: Type[ModelClient]) -> None:
        """
        Register a model client class.
        
        Args:
            name: Client type name (e.g., 'openai', 'llama').
            client_class: Client class to register.
        """
        cls._client_registry[name] = client_class
    
    @classmethod
    def create_client(cls, client_type: str, config: ModelConfig) -> ModelClient:
        """
        Create a model client based on type.
        
        Args:
            client_type: Type of client to create ('openai', 'llama', 'auto').
            config: Model configuration.
            
        Returns:
            Model client instance.
            
        Raises:
            ValueError: If client type is not supported.
        """
        # Handle auto detection
        if client_type == "auto":
            client_type = cls._detect_client_type(config)
        
        # Get client class
        if client_type not in cls._client_registry:
            raise ValueError(f"Unsupported client type: {client_type}")
        
        client_class = cls._client_registry[client_type]
        return client_class(config)
    
    @classmethod
    def _detect_client_type(cls, config: ModelConfig) -> str:
        """
        Auto-detect client type based on configuration.
        
        Args:
            config: Model configuration.
            
        Returns:
            Detected client type.
        """
        base_url = config.base_url.lower()
        
        # Local server detection
        if "localhost" in base_url or "127.0.0.1" in base_url:
            return "llama"
        
        # OpenAI API detection
        if "openai.com" in base_url:
            return "openai"
        
        # Default to llama for other local-like URLs
        if base_url.startswith("http://"):
            return "llama"
        
        # Default to openai for HTTPS URLs
        return "openai"
    
    @classmethod
    def list_clients(cls) -> list[str]:
        """List all registered client types."""
        return list(cls._client_registry.keys())


# Register the default OpenAI client
ModelClientFactory.register_client("openai", ModelClient)

# LlamaModelClient will be registered when imported
try:
    from phone_agent.model.llama_client import LlamaModelClient
    ModelClientFactory.register_client("llama", LlamaModelClient)
except ImportError:
    # LlamaModelClient not available
    pass
