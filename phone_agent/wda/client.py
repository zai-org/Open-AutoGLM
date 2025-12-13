"""WebDriverAgent HTTP client for iOS device communication."""

import logging
import requests
from dataclasses import dataclass, field
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class WDAClient:
    """
    HTTP client for WebDriverAgent.
    
    Provides a simple interface to communicate with WDA running on iOS devices.
    WDA requires a session for most commands (tap, type, swipe, etc.).
    
    Args:
        base_url: WDA server URL (e.g., http://localhost:8100)
        timeout: Request timeout in seconds
    """
    
    base_url: str = "http://localhost:8100"
    timeout: int = 30
    _session: requests.Session = field(default=None, repr=False)
    _wda_session_id: str = field(default=None, repr=False)
    
    def __post_init__(self):
        self._session = requests.Session()
        # Set default headers
        self._session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
        })
        self._wda_session_id = None
    
    @property
    def session_id(self) -> Optional[str]:
        """Get the current WDA session ID, creating one if needed."""
        if self._wda_session_id is None:
            self._create_session()
        return self._wda_session_id
    
    def _create_session(self) -> bool:
        """
        Create a new WDA session.
        
        Returns:
            True if session created successfully, False otherwise
        """
        try:
            url = f"{self.base_url}/session"
            resp = self._session.post(url, json={"capabilities": {}}, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
            
            # Extract session ID from response
            if "value" in data and "sessionId" in data["value"]:
                self._wda_session_id = data["value"]["sessionId"]
            elif "sessionId" in data:
                self._wda_session_id = data["sessionId"]
            
            if self._wda_session_id:
                logger.debug(f"WDA session created: {self._wda_session_id[:8]}...")
                return True
            return False
        except Exception as e:
            logger.warning(f"Failed to create WDA session: {e}")
            return False
    
    def _invalidate_session(self) -> None:
        """Invalidate the current session, forcing creation of a new one on next request."""
        self._wda_session_id = None
    
    def _session_path(self, path: str) -> str:
        """
        Convert a path to session-scoped path if needed.
        
        Args:
            path: Original API path (e.g., /wda/tap)
            
        Returns:
            Session-scoped path (e.g., /session/{id}/wda/tap)
        """
        # Paths that require session
        session_required_prefixes = ["/wda/tap", "/wda/keys", "/wda/swipe", "/wda/doubleTap",
                                      "/wda/touchAndHold", "/wda/scroll", "/wda/drag",
                                      "/wda/dragfromtoforduration", "/wda/pressAndDragWithVelocity",
                                      "/wda/pinch", "/wda/rotate", "/wda/forceTouch",
                                      "/wda/pickerwheel", "/wda/homescreen", "/wda/pressButton",
                                      "/wda/lock", "/wda/unlock", "/wda/locked",
                                      "/wda/keyboard",  # keyboard/dismiss, keyboard/shown
                                      "/element", "/actions", "/wda/apps/", "/window/"]
        
        # Check if path needs session
        needs_session = any(path.startswith(p) for p in session_required_prefixes)
        
        if needs_session and self.session_id:
            return f"/session/{self.session_id}{path}"
        return path
    
    def get(self, path: str, use_session: bool = True, **kwargs) -> dict:
        """
        Send GET request to WDA.
        
        Args:
            path: API endpoint path (e.g., /screenshot)
            use_session: Whether to prepend session path (default True)
            **kwargs: Additional arguments for requests.get
            
        Returns:
            JSON response as dictionary
        """
        if use_session:
            path = self._session_path(path)
        url = f"{self.base_url}{path}"
        try:
            resp = self._session.get(url, timeout=self.timeout, **kwargs)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.JSONDecodeError:
            # Some endpoints return plain text
            return {"value": resp.text}
        except Exception as e:
            logger.error(f"WDA GET {path} error: {e}")
            return {"error": str(e)}
    
    def post(self, path: str, data: dict = None, use_session: bool = True, **kwargs) -> dict:
        """
        Send POST request to WDA.
        
        Args:
            path: API endpoint path (e.g., /wda/tap)
            data: JSON payload
            use_session: Whether to prepend session path (default True)
            **kwargs: Additional arguments for requests.post
            
        Returns:
            JSON response as dictionary
        """
        original_path = path
        if use_session:
            path = self._session_path(path)
        url = f"{self.base_url}{path}"
        
        for attempt in range(2):  # Try up to 2 times
            try:
                resp = self._session.post(url, json=data or {}, timeout=self.timeout, **kwargs)
                
                # Check for 404 which might indicate session expired
                if resp.status_code == 404 and "/session/" in path and attempt == 0:
                    # Session might have expired, invalidate and retry
                    self._invalidate_session()
                    path = self._session_path(original_path)
                    url = f"{self.base_url}{path}"
                    continue
                
                resp.raise_for_status()
                return resp.json()
            except requests.exceptions.JSONDecodeError:
                return {"value": resp.text}
            except requests.exceptions.HTTPError as e:
                # On 404 with session path, try recreating session
                if resp.status_code == 404 and "/session/" in path and attempt == 0:
                    self._invalidate_session()
                    path = self._session_path(original_path)
                    url = f"{self.base_url}{path}"
                    continue
                logger.error(f"WDA POST {path} error: {e}")
                return {"error": str(e)}
            except Exception as e:
                logger.error(f"WDA POST {path} error: {e}")
                return {"error": str(e)}
        
        return {"error": "Request failed after retry"}
    
    def delete(self, path: str, **kwargs) -> dict:
        """Send DELETE request to WDA."""
        url = f"{self.base_url}{path}"
        try:
            resp = self._session.delete(url, timeout=self.timeout, **kwargs)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error(f"WDA DELETE {path} error: {e}")
            return {"error": str(e)}
    
    def health_check(self) -> bool:
        """
        Check if WDA is running and responsive.
        
        Returns:
            True if WDA is healthy, False otherwise
        """
        try:
            resp = self.get("/status")
            return "error" not in resp
        except Exception as e:
            logger.debug(f"WDA health check failed: {e}")
            return False
    
    def get_screen_info(self) -> dict:
        """
        Get screen dimensions and scale.
        
        Returns:
            Dict with screenSize, statusBarSize, and scale
        """
        return self.get("/wda/screen")


# Global client instance management
_client: Optional[WDAClient] = None
_client_url: Optional[str] = None


def get_client(base_url: str = None) -> WDAClient:
    """
    Get or create WDA client instance.
    
    Args:
        base_url: WDA server URL. If None, uses default or cached URL.
        
    Returns:
        WDAClient instance
    """
    global _client, _client_url
    
    # Determine URL to use
    import os
    url = base_url or os.environ.get("PHONE_AGENT_WDA_URL", "http://localhost:8100")
    
    # Normalize URL (handle device_id being passed as URL or IP:PORT)
    if url and not url.startswith("http"):
        url = f"http://{url}"
    
    # Create new client if needed
    if _client is None or _client_url != url:
        _client = WDAClient(base_url=url)
        _client_url = url
    
    return _client


def set_wda_url(url: str) -> None:
    """
    Set the global WDA URL.
    
    Args:
        url: WDA server URL
    """
    global _client, _client_url
    _client = None
    _client_url = None
    import os
    os.environ["PHONE_AGENT_WDA_URL"] = url
