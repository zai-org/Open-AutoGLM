# iOS Apps Configuration

## Overview

The `apps_ios.py` module provides iOS Bundle ID mappings for supported applications, based on the approach from [iOS-app-info](https://github.com/WengYuehTing/iOS-app-info).

## File Structure

- **`apps.py`**: Android package names (for Android devices)
- **`apps_ios.py`**: iOS Bundle IDs (for iOS devices)

## iOS Bundle ID Format

iOS Bundle IDs follow the format: `com.company.appName`

Examples:
- WeChat (微信): `com.tencent.xin`
- Safari: `com.apple.mobilesafari`
- Gmail: `com.google.Gmail`

## Usage

### In Python Code

```python
from phone_agent.config.apps_ios import (
    get_bundle_id,
    get_app_name,
    list_supported_apps,
    check_app_installed,
    get_app_info_from_itunes
)

# Get Bundle ID for an app
bundle_id = get_bundle_id("微信")  # Returns: com.tencent.xin

# Get app name from Bundle ID
app_name = get_app_name("com.tencent.xin")  # Returns: 微信

# List all supported apps
apps = list_supported_apps()

# Check if app is installed (queries iTunes API)
is_installed = check_app_installed("微信")

# Get detailed app info from iTunes
info = get_app_info_from_itunes("com.tencent.xin")
```

### Command Line

```bash
# List all supported iOS apps
python ios.py --list-apps
```

## Adding New Apps

To add a new iOS app, you need to find its Bundle ID:

### Method 1: Using iTunes API

For apps available on the App Store:

```bash
# Search by app name (example: WeChat)
curl "https://itunes.apple.com/search?term=wechat&entity=software&country=cn"

# Look for "bundleId" in the response
```

### Method 2: Using URL Scheme (if app is installed)

If you have the app installed:

1. Open Xcode
2. Window → Devices and Simulators
3. Select your device
4. Find the app under "Installed Apps"
5. The Bundle ID will be shown

### Method 3: From App Store URL

If you know the App Store URL:
- URL format: `https://apps.apple.com/cn/app/wechat/id414478124`
- The number after `id` is the App Store ID
- Query: `https://itunes.apple.com/lookup?id=414478124`

### Adding to `apps_ios.py`

Once you have the Bundle ID, add it to the `APP_PACKAGES_IOS` dictionary:

```python
APP_PACKAGES_IOS: dict[str, str] = {
    # ... existing apps ...
    "Your App Name": "com.company.appname",
    "你的应用名称": "com.company.appname",  # Support multiple languages
}
```

## Integration with WebDriverAgent

The `apps_ios.py` module is automatically used by:

1. **`phone_agent/xctest/device.py`**: For launching apps via WebDriverAgent
2. **`phone_agent/actions/handler_ios.py`**: For iOS action handling
3. **`ios.py`**: Main CLI for iOS automation

Example of app launching:

```python
from phone_agent.xctest import launch_app

# Launch WeChat by name (Bundle ID is resolved automatically)
success = launch_app("微信", wda_url="http://localhost:8100")
```

## Key Functions

### `get_bundle_id(app_name: str) -> str | None`
Get the iOS Bundle ID for an app by its display name.

### `get_app_name(bundle_id: str) -> str | None`
Get the app's display name from its Bundle ID.

### `list_supported_apps() -> list[str]`
Get a list of all supported app names.

### `check_app_installed(app_name: str, wda_url: str) -> bool`
Check if an app is available (queries iTunes API).

### `get_app_info_from_itunes(bundle_id: str) -> dict | None`
Get detailed app information from the iTunes API.

### `get_app_info_by_id(app_store_id: str) -> dict | None`
Get app information using the App Store ID.

## Notes

- iOS Bundle IDs are case-sensitive
- Some apps have different Bundle IDs between regions (China vs. Global)
- System apps (Settings, Safari, etc.) use `com.apple.*` Bundle IDs
- The iTunes API is used for app information lookup but doesn't guarantee the app is installed on the device

## Differences from Android

| Feature | Android (`apps.py`) | iOS (`apps_ios.py`) |
|---------|---------------------|---------------------|
| Identifier Format | `com.company.app` | `com.company.app` |
| Example | `com.tencent.xin` | `com.tencent.xin` |
| System Apps | `com.android.*` | `com.apple.*` |
| Launch Method | ADB intent | WDA Bundle ID |
| API Lookup | Google Play (limited) | iTunes API |

## References

- [iOS-app-info GitHub Repository](https://github.com/WengYuehTing/iOS-app-info)
- [iTunes Search API](https://developer.apple.com/library/archive/documentation/AudioVideo/Conceptual/iTuneSearchAPI/)
- [WebDriverAgent Documentation](https://github.com/appium/WebDriverAgent)
