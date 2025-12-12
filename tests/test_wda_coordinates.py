#!/usr/bin/env python3
"""
Test script for iOS WDA coordinate system.

This script helps verify that the coordinate conversion is working correctly.

Usage:
    python test_wda_coordinates.py [--wda-url URL]

Prerequisites:
    1. WebDriverAgent must be running
    2. iproxy 8100 8100 should be active
"""

import argparse
import requests
import sys


def get_wda_info(wda_url: str):
    """Get WDA device and screen information."""
    print("=" * 60)
    print("🔍 WDA Device Information")
    print("=" * 60)
    
    # Status
    try:
        resp = requests.get(f"{wda_url}/status", timeout=5)
        data = resp.json()
        print(f"\n✅ WDA Status: Connected")
        
        # Device info
        if "value" in data:
            value = data["value"]
            if "ios" in value:
                ios_info = value["ios"]
                print(f"   iOS Version: {ios_info.get('sdkVersion', 'unknown')}")
                print(f"   Device Name: {ios_info.get('name', 'unknown')}")
    except Exception as e:
        print(f"❌ WDA Status: Failed - {e}")
        return False
    
    # Screen info
    try:
        resp = requests.get(f"{wda_url}/wda/screen", timeout=5)
        data = resp.json()
        value = data.get("value", {})
        
        screen_size = value.get("screenSize", {})
        scale = value.get("scale", 3.0)
        
        width_pt = screen_size.get("width", 0)
        height_pt = screen_size.get("height", 0)
        width_px = int(width_pt * scale)
        height_px = int(height_pt * scale)
        
        print(f"\n📱 Screen Information:")
        print(f"   Scale Factor: {scale}x")
        print(f"   Points: {width_pt} x {height_pt}")
        print(f"   Pixels: {width_px} x {height_px}")
        print("-" * 60)
        
    except Exception as e:
        print(f"⚠️  Could not get screen info: {e}")
    
    return True


def test_tap(wda_url: str, x_px: int, y_px: int):
    """Test tap at specific pixel coordinates."""
    print(f"\n🎯 Testing Tap at Pixel ({x_px}, {y_px})")
    print("-" * 60)
    
    # Get scale factor
    try:
        resp = requests.get(f"{wda_url}/wda/screen", timeout=5)
        data = resp.json()
        scale = data.get("value", {}).get("scale", 3.0)
    except:
        scale = 3.0
    
    # Convert to points
    x_pt = x_px / scale
    y_pt = y_px / scale
    
    print(f"   Pixel coordinates: ({x_px}, {y_px})")
    print(f"   Scale factor: {scale}")
    print(f"   Point coordinates: ({x_pt:.1f}, {y_pt:.1f})")
    
    # Create session if needed
    try:
        session_resp = requests.post(f"{wda_url}/session", json={"capabilities": {}}, timeout=10)
        session_data = session_resp.json()
        session_id = session_data.get("value", {}).get("sessionId") or session_data.get("sessionId")
        print(f"   Session ID: {session_id[:8] if session_id else 'none'}...")
    except Exception as e:
        print(f"   ⚠️  Session creation: {e}")
        session_id = None
    
    # Perform tap
    try:
        if session_id:
            tap_url = f"{wda_url}/session/{session_id}/wda/tap"
        else:
            tap_url = f"{wda_url}/wda/tap"
        
        print(f"\n   Sending tap to: {tap_url}")
        print(f"   Payload: {{'x': {x_pt:.1f}, 'y': {y_pt:.1f}}}")
        
        resp = requests.post(tap_url, json={"x": x_pt, "y": y_pt}, timeout=10)
        
        if resp.status_code in (200, 201):
            print(f"   ✅ Tap successful!")
        else:
            print(f"   ❌ Tap failed: {resp.status_code} - {resp.text[:100]}")
            
    except Exception as e:
        print(f"   ❌ Tap error: {e}")


def test_coordinate_scenarios(wda_url: str):
    """Test common coordinate scenarios."""
    print("\n" + "=" * 60)
    print("🧪 Coordinate Conversion Examples")
    print("=" * 60)
    
    # Get actual screen dimensions
    try:
        resp = requests.get(f"{wda_url}/wda/screen", timeout=5)
        data = resp.json()
        value = data.get("value", {})
        scale = value.get("scale", 3.0)
        screen_w = value.get("screenSize", {}).get("width", 393)
        screen_h = value.get("screenSize", {}).get("height", 852)
    except:
        scale = 3.0
        screen_w = 393
        screen_h = 852
    
    # Example: Model outputs [500, 500] (0-1000 relative)
    # Screenshot size from WDA
    screenshot_w = int(screen_w * scale)  # e.g., 1179
    screenshot_h = int(screen_h * scale)  # e.g., 2556
    
    print(f"\n📊 Example: Model outputs relative coordinates [500, 300]")
    print(f"   Screenshot size: {screenshot_w} x {screenshot_h} pixels")
    
    # Convert 0-1000 relative to pixels
    rel_x, rel_y = 500, 300
    px_x = int(rel_x / 1000 * screenshot_w)
    px_y = int(rel_y / 1000 * screenshot_h)
    
    print(f"   Relative [0-1000]: ({rel_x}, {rel_y})")
    print(f"   Converted to pixels: ({px_x}, {px_y})")
    
    # Convert pixels to points
    pt_x = px_x / scale
    pt_y = px_y / scale
    
    print(f"   Converted to points: ({pt_x:.1f}, {pt_y:.1f})")
    print(f"\n   ➡️  This should tap at approximately the center-left of the screen")
    
    # Another example
    print(f"\n📊 Example: Tap center of screen")
    center_x = screenshot_w // 2
    center_y = screenshot_h // 2
    pt_cx = center_x / scale
    pt_cy = center_y / scale
    print(f"   Center pixels: ({center_x}, {center_y})")
    print(f"   Center points: ({pt_cx:.1f}, {pt_cy:.1f})")


def main():
    parser = argparse.ArgumentParser(description="Test WDA coordinate system")
    parser.add_argument(
        "--wda-url",
        default="http://localhost:8100",
        help="WebDriverAgent URL"
    )
    parser.add_argument(
        "--tap",
        nargs=2,
        type=int,
        metavar=("X", "Y"),
        help="Test tap at pixel coordinates X Y"
    )
    args = parser.parse_args()
    
    # Test connection and get info
    if not get_wda_info(args.wda_url):
        sys.exit(1)
    
    # Show coordinate examples
    test_coordinate_scenarios(args.wda_url)
    
    # Test tap if coordinates provided
    if args.tap:
        test_tap(args.wda_url, args.tap[0], args.tap[1])
    else:
        print("\n💡 To test tap, run:")
        print(f"   python {__file__} --tap 590 1278")
        print("   (This would tap at approximately the middle of the screen)")
    
    print("\n" + "=" * 60)
    print("✅ Coordinate system test complete!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
