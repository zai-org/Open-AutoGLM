"""UI Hierarchy utilities for Android UI element detection and interaction.

This module provides functionality to:
1. Dump UI hierarchy from Android devices using uiautomator
2. Parse XML to extract clickable/interactive elements
3. Find elements by text, content-desc, or resource-id
4. Calculate element center coordinates for precise tapping
"""

import subprocess
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import List, Optional, Tuple


@dataclass
class UIElement:
    """Represents a UI element on the screen."""
    
    index: int  # Sequential index for easy reference
    text: str  # Element text content
    content_desc: str  # Accessibility description
    resource_id: str  # Resource identifier
    class_name: str  # Android class name (e.g., android.widget.Button)
    bounds: Tuple[int, int, int, int]  # (left, top, right, bottom)
    clickable: bool
    enabled: bool
    focused: bool
    selected: bool
    
    @property
    def center(self) -> Tuple[int, int]:
        """Calculate the center point of the element."""
        left, top, right, bottom = self.bounds
        return ((left + right) // 2, (top + bottom) // 2)
    
    @property
    def width(self) -> int:
        return self.bounds[2] - self.bounds[0]
    
    @property
    def height(self) -> int:
        return self.bounds[3] - self.bounds[1]
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "index": self.index,
            "text": self.text,
            "content_desc": self.content_desc,
            "resource_id": self.resource_id,
            "class_name": self.class_name,
            "bounds": self.bounds,
            "center": self.center,
            "clickable": self.clickable,
            "enabled": self.enabled,
        }
    
    def __str__(self) -> str:
        """Human-readable representation."""
        label = self.text or self.content_desc or self.resource_id or self.class_name
        return f"[{self.index}] {label} @ {self.center}"


def get_ui_hierarchy_xml(device_id: str | None = None, timeout: int = 10) -> str:
    """
    Dump UI hierarchy XML from the device.
    
    Args:
        device_id: Optional ADB device ID for multi-device setups.
        timeout: Timeout in seconds for the dump operation.
    
    Returns:
        XML string of the UI hierarchy.
    """
    adb_prefix = _get_adb_prefix(device_id)
    
    # Dump UI hierarchy to device
    subprocess.run(
        adb_prefix + ["shell", "uiautomator", "dump", "/sdcard/ui_dump.xml"],
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    
    # Pull the XML content
    result = subprocess.run(
        adb_prefix + ["shell", "cat", "/sdcard/ui_dump.xml"],
        capture_output=True,
        text=True,
        timeout=5,
    )
    
    return result.stdout


def parse_ui_elements(
    xml_content: str,
    clickable_only: bool = True,
    include_all_with_text: bool = True,
) -> List[UIElement]:
    """
    Parse UI hierarchy XML and extract elements.
    
    Args:
        xml_content: XML string from uiautomator dump.
        clickable_only: If True, only return clickable elements.
        include_all_with_text: If True, also include non-clickable elements that have text.
    
    Returns:
        List of UIElement objects.
    """
    elements = []
    
    try:
        root = ET.fromstring(xml_content)
    except ET.ParseError:
        return elements
    
    index = 0
    for node in root.iter("node"):
        # Parse attributes
        text = node.get("text", "")
        content_desc = node.get("content-desc", "")
        resource_id = node.get("resource-id", "")
        class_name = node.get("class", "")
        clickable = node.get("clickable", "false") == "true"
        enabled = node.get("enabled", "true") == "true"
        focused = node.get("focused", "false") == "true"
        selected = node.get("selected", "false") == "true"
        
        # Parse bounds: "[left,top][right,bottom]"
        bounds_str = node.get("bounds", "[0,0][0,0]")
        bounds = _parse_bounds(bounds_str)
        
        # Skip elements with zero size
        if bounds[2] <= bounds[0] or bounds[3] <= bounds[1]:
            continue
        
        # Filter logic
        has_identifier = bool(text or content_desc or resource_id)
        
        if clickable_only:
            # Include if clickable, or if it has text/desc (useful for labels)
            if not clickable and not (include_all_with_text and has_identifier):
                continue
        
        # Skip if no useful identifier at all
        if not has_identifier and not clickable:
            continue
        
        element = UIElement(
            index=index,
            text=text,
            content_desc=content_desc,
            resource_id=resource_id,
            class_name=class_name,
            bounds=bounds,
            clickable=clickable,
            enabled=enabled,
            focused=focused,
            selected=selected,
        )
        elements.append(element)
        index += 1
    
    return elements


def get_ui_elements(
    device_id: str | None = None,
    clickable_only: bool = True,
    timeout: int = 10,
) -> List[UIElement]:
    """
    Get all UI elements from the current screen.
    
    Args:
        device_id: Optional ADB device ID for multi-device setups.
        clickable_only: If True, only return clickable/interactive elements.
        timeout: Timeout in seconds.
    
    Returns:
        List of UIElement objects.
    """
    xml_content = get_ui_hierarchy_xml(device_id, timeout)
    return parse_ui_elements(xml_content, clickable_only)


def find_element_by_text(
    elements: List[UIElement],
    text: str,
    exact_match: bool = False,
) -> Optional[UIElement]:
    """
    Find an element by its text content.
    
    Args:
        elements: List of UIElement objects.
        text: Text to search for.
        exact_match: If True, require exact match; otherwise, partial match.
    
    Returns:
        The matching UIElement, or None if not found.
    """
    text_lower = text.lower()
    
    for element in elements:
        element_text = element.text.lower()
        element_desc = element.content_desc.lower()
        
        if exact_match:
            if element_text == text_lower or element_desc == text_lower:
                return element
        else:
            if text_lower in element_text or text_lower in element_desc:
                return element
    
    return None


def find_element_by_resource_id(
    elements: List[UIElement],
    resource_id: str,
    partial_match: bool = True,
) -> Optional[UIElement]:
    """
    Find an element by its resource ID.
    
    Args:
        elements: List of UIElement objects.
        resource_id: Resource ID to search for.
        partial_match: If True, match if resource_id is contained in element's resource_id.
    
    Returns:
        The matching UIElement, or None if not found.
    """
    for element in elements:
        if partial_match:
            if resource_id in element.resource_id:
                return element
        else:
            if element.resource_id == resource_id:
                return element
    
    return None


def find_element_by_index(
    elements: List[UIElement],
    index: int,
) -> Optional[UIElement]:
    """
    Find an element by its index.
    
    Args:
        elements: List of UIElement objects.
        index: Index of the element.
    
    Returns:
        The matching UIElement, or None if index is out of range.
    """
    for element in elements:
        if element.index == index:
            return element
    return None


def format_elements_for_llm(elements: List[UIElement], max_elements: int = 50) -> str:
    """
    Format UI elements as a string suitable for LLM consumption.
    
    Args:
        elements: List of UIElement objects.
        max_elements: Maximum number of elements to include.
    
    Returns:
        Formatted string describing the elements.
    """
    if not elements:
        return "No interactive elements found on screen."
    
    lines = ["Interactive elements on screen:"]
    lines.append("=" * 50)
    
    for element in elements[:max_elements]:
        # Build description
        parts = []
        if element.text:
            parts.append(f'text="{element.text}"')
        if element.content_desc:
            parts.append(f'desc="{element.content_desc}"')
        if element.resource_id:
            # Simplify resource ID (remove package prefix)
            simple_id = element.resource_id.split("/")[-1] if "/" in element.resource_id else element.resource_id
            parts.append(f'id="{simple_id}"')
        
        # Add class type hint
        class_hint = element.class_name.split(".")[-1] if element.class_name else ""
        if class_hint:
            parts.append(f"({class_hint})")
        
        # Add clickable indicator
        if element.clickable:
            parts.append("[clickable]")
        
        desc = " ".join(parts) if parts else f"({element.class_name})"
        lines.append(f"[{element.index}] {desc}")
    
    if len(elements) > max_elements:
        lines.append(f"... and {len(elements) - max_elements} more elements")
    
    lines.append("=" * 50)
    lines.append("Use tap_element with index=N or text='...' to interact.")
    
    return "\n".join(lines)


def _parse_bounds(bounds_str: str) -> Tuple[int, int, int, int]:
    """
    Parse bounds string from uiautomator.
    
    Args:
        bounds_str: String in format "[left,top][right,bottom]"
    
    Returns:
        Tuple of (left, top, right, bottom)
    """
    try:
        # Remove brackets and split
        # "[0,0][1080,2400]" -> "0,0", "1080,2400"
        parts = bounds_str.replace("][", ",").strip("[]").split(",")
        if len(parts) == 4:
            return (int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3]))
    except (ValueError, IndexError):
        pass
    
    return (0, 0, 0, 0)


def _get_adb_prefix(device_id: str | None) -> list:
    """Get ADB command prefix with optional device specifier."""
    if device_id:
        return ["adb", "-s", device_id]
    return ["adb"]