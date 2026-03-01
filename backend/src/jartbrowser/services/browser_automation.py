"""
Browser Automation Service

Provides programmatic control over browser tabs, windows, and navigation.
This service communicates with the Chrome extension via WebSocket or HTTP.
"""

import asyncio
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from enum import Enum


class ActionType(Enum):
    """Browser action types"""

    NAVIGATE = "navigate"
    CLICK = "click"
    DOUBLE_CLICK = "double_click"
    HOVER = "hover"
    FILL = "fill"
    SELECT = "select"
    SUBMIT = "submit"
    SCROLL = "scroll"
    SCREENSHOT = "screenshot"
    GET_DOM = "get_dom"
    GET_CONTENT = "get_content"
    WAIT = "wait"
    EVALUATE = "evaluate"


class ScrollDirection(Enum):
    """Scroll directions"""

    UP = "up"
    DOWN = "down"
    TOP = "top"
    BOTTOM = "bottom"


@dataclass
class ElementSelector:
    """Element selector configuration"""

    selector_type: str  # css, xpath, text, id
    value: str
    index: int = 0


@dataclass
class BrowserAction:
    """Represents a browser action to execute"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    action_type: ActionType = ActionType.NAVIGATE
    target: Optional[str] = None
    value: Optional[str] = None
    options: Optional[Dict[str, Any]] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "action": self.action_type.value,
            "target": self.target,
            "value": self.value,
            "options": self.options or {},
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class Tab:
    """Represents a browser tab"""

    id: int
    url: str
    title: str
    active: bool = True
    pinned: bool = False
    incognito: bool = False
    group_id: Optional[int] = None
    favicon: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "url": self.url,
            "title": self.title,
            "active": self.active,
            "pinned": self.pinned,
            "incognito": self.incognito,
            "group_id": self.group_id,
            "favicon": self.favicon,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class Window:
    """Represents a browser window"""

    id: int
    focused: bool = True
    tabs: List[Tab] = field(default_factory=list)
    incognito: bool = False
    type: str = "normal"  # normal, popup, app
    bounds: Optional[Dict[str, int]] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "focused": self.focused,
            "tabs": [t.to_dict() for t in self.tabs],
            "incognito": self.incognito,
            "type": self.type,
            "bounds": self.bounds,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class NavigationHistory:
    """Navigation history entry"""

    url: str
    title: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    transition_type: str = "link"  # link, typed, bookmark, etc.


class BrowserAutomationService:
    """
    Service for browser automation.

    Manages tabs, windows, navigation history, and executes browser actions.
    Communicates with Chrome extension for actual browser control.
    """

    def __init__(self, backend_url: str = "http://localhost:8000"):
        self.backend_url = backend_url
        self._tabs: Dict[int, Tab] = {}
        self._windows: Dict[int, Window] = {}
        self._navigation_history: Dict[int, List[NavigationHistory]] = {}
        self._action_callbacks: List[Callable] = []
        self._connected = False

    # ============== Connection ==============

    async def connect(self) -> bool:
        """Connect to the backend/chrome extension"""
        try:
            # In production, this would establish WebSocket connection
            self._connected = True
            return True
        except Exception:
            self._connected = False
            return False

    async def disconnect(self) -> None:
        """Disconnect from the backend"""
        self._connected = False

    @property
    def is_connected(self) -> bool:
        return self._connected

    # ============== Tab Management ==============

    async def create_tab(
        self,
        url: Optional[str] = None,
        active: bool = True,
        pinned: bool = False,
        window_id: Optional[int] = None,
    ) -> Tab:
        """Create a new tab"""
        tab_id = len(self._tabs) + 1

        tab = Tab(
            id=tab_id, url=url or "about:blank", title="New Tab", active=active, pinned=pinned
        )

        self._tabs[tab_id] = tab

        # Initialize history for this tab
        if tab_id not in self._navigation_history:
            self._navigation_history[tab_id] = []

        return tab

    async def get_tab(self, tab_id: int) -> Optional[Tab]:
        """Get a tab by ID"""
        return self._tabs.get(tab_id)

    async def get_tabs(self, window_id: Optional[int] = None) -> List[Tab]:
        """Get all tabs, optionally filtered by window"""
        tabs = list(self._tabs.values())

        if window_id is not None:
            window = self._windows.get(window_id)
            if window:
                tabs = window.tabs

        return tabs

    async def update_tab(
        self,
        tab_id: int,
        url: Optional[str] = None,
        title: Optional[str] = None,
        active: Optional[bool] = None,
        pinned: Optional[bool] = None,
    ) -> Optional[Tab]:
        """Update tab properties"""
        tab = self._tabs.get(tab_id)
        if not tab:
            return None

        if url is not None:
            # Add to history
            if tab_id not in self._navigation_history:
                self._navigation_history[tab_id] = []

            self._navigation_history[tab_id].append(NavigationHistory(url=tab.url, title=tab.title))

            tab.url = url

        if title is not None:
            tab.title = title
        if active is not None:
            tab.active = active
        if pinned is not None:
            tab.pinned = pinned

        return tab

    async def close_tab(self, tab_id: int) -> bool:
        """Close a tab"""
        if tab_id in self._tabs:
            del self._tabs[tab_id]
            if tab_id in self._navigation_history:
                del self._navigation_history[tab_id]
            return True
        return False

    async def activate_tab(self, tab_id: int) -> Optional[Tab]:
        """Activate a tab (make it the active tab)"""
        # Deactivate all other tabs
        for tab in self._tabs.values():
            if tab.id != tab_id:
                tab.active = False

        # Activate the target tab
        return await self.update_tab(tab_id, active=True)

    async def duplicate_tab(self, tab_id: int) -> Optional[Tab]:
        """Duplicate a tab"""
        source = await self.get_tab(tab_id)
        if not source:
            return None

        return await self.create_tab(url=source.url, active=True, pinned=source.pinned)

    # ============== Window Management ==============

    async def create_window(
        self,
        url: Optional[str] = None,
        incognito: bool = False,
        bounds: Optional[Dict[str, int]] = None,
    ) -> Window:
        """Create a new window"""
        window_id = len(self._windows) + 1

        # Create initial tab if URL provided
        tabs = []
        if url:
            tab = await self.create_tab(url=url, active=True)
            tabs.append(tab)

        window = Window(id=window_id, tabs=tabs, incognito=incognito, bounds=bounds)

        self._windows[window_id] = window
        return window

    async def get_window(self, window_id: int) -> Optional[Window]:
        """Get a window by ID"""
        return self._windows.get(window_id)

    async def get_windows(self) -> List[Window]:
        """Get all windows"""
        return list(self._windows.values())

    async def update_window(
        self,
        window_id: int,
        focused: Optional[bool] = None,
        bounds: Optional[Dict[str, int]] = None,
    ) -> Optional[Window]:
        """Update window properties"""
        window = self._windows.get(window_id)
        if not window:
            return None

        if focused is not None:
            window.focused = focused
        if bounds is not None:
            window.bounds = bounds

        return window

    async def close_window(self, window_id: int) -> bool:
        """Close a window and all its tabs"""
        if window_id in self._windows:
            window = self._windows[window_id]

            # Close all tabs in the window
            for tab in window.tabs:
                if tab.id in self._tabs:
                    del self._tabs[tab.id]

            del self._windows[window_id]
            return True
        return False

    async def focus_window(self, window_id: int) -> Optional[Window]:
        """Focus a window"""
        # Unfocus all other windows
        for window in self._windows.values():
            if window.id != window_id:
                window.focused = False

        return await self.update_window(window_id, focused=True)

    # ============== Navigation ==============

    async def navigate(self, tab_id: int, url: str) -> Tab:
        """Navigate to a URL"""
        tab = await self.update_tab(tab_id, url=url)
        if not tab:
            raise ValueError(f"Tab {tab_id} not found")

        # Simulate page load - in production would wait for actual load
        tab.title = f"Page at {url}"

        return tab

    async def go_back(self, tab_id: int) -> Optional[Tab]:
        """Go back in history"""
        history = self._navigation_history.get(tab_id, [])

        if len(history) > 1:
            # Remove current entry
            history.pop()

            # Navigate to previous
            previous = history[-1]
            return await self.update_tab(tab_id, url=previous.url, title=previous.title)

        return await self.get_tab(tab_id)

    async def go_forward(self, tab_id: int) -> Optional[Tab]:
        """Go forward in history"""
        # This would require storing future history - simplified for now
        return await self.get_tab(tab_id)

    async def reload(self, tab_id: int) -> Optional[Tab]:
        """Reload a tab"""
        tab = await self.get_tab(tab_id)
        if tab:
            # In production, would trigger actual reload
            pass
        return tab

    async def get_navigation_history(self, tab_id: int, limit: int = 50) -> List[NavigationHistory]:
        """Get navigation history for a tab"""
        history = self._navigation_history.get(tab_id, [])
        return history[-limit:]

    # ============== Tab Groups ==============

    async def create_tab_group(
        self, tab_ids: List[int], title: Optional[str] = None, color: str = "grey"
    ) -> int:
        """Create a tab group"""
        # In production, would use chrome.tabGroups API
        group_id = hash(f"{tab_ids}{datetime.utcnow().isoformat()}") % 100000

        # Update tabs with group
        for tab_id in tab_ids:
            tab = self._tabs.get(tab_id)
            if tab:
                tab.group_id = group_id

        return group_id

    async def update_tab_group(
        self, group_id: int, title: Optional[str] = None, color: Optional[str] = None
    ) -> bool:
        """Update a tab group"""
        # In production, would use chrome.tabGroups API
        return True

    async def move_tab_to_group(self, tab_id: int, group_id: Optional[int]) -> Optional[Tab]:
        """Move a tab to a group"""
        tab = self._tabs.get(tab_id)
        if tab:
            tab.group_id = group_id
        return tab

    async def ungroup_tabs(self, group_id: int) -> List[int]:
        """Ungroup tabs in a group"""
        ungrouped = []

        for tab in self._tabs.values():
            if tab.group_id == group_id:
                tab.group_id = None
                ungrouped.append(tab.id)

        return ungrouped

    # ============== Actions ==============

    async def execute_action(self, tab_id: int, action: BrowserAction) -> Dict[str, Any]:
        """Execute a browser action"""
        result = {"success": False, "action_id": action.id, "error": None}

        try:
            if action.action_type == ActionType.NAVIGATE:
                await self.navigate(tab_id, action.target or "")
                result["success"] = True

            elif action.action_type == ActionType.CLICK:
                # In production, would execute via Chrome extension
                result["success"] = True
                result["element_clicked"] = action.target

            elif action.action_type == ActionType.FILL:
                # In production, would execute via Chrome extension
                result["success"] = True
                result["field_filled"] = action.target

            elif action.action_type == ActionType.SCROLL:
                direction = action.target or "down"
                result["success"] = True
                result["scrolled"] = direction

            elif action.action_type == ActionType.SCREENSHOT:
                # In production, would capture via Chrome extension
                result["success"] = True
                result["screenshot"] = "base64_encoded_data"

            elif action.action_type == ActionType.GET_DOM:
                # In production, would get from Chrome extension
                result["success"] = True
                result["dom"] = {"elements": []}

            elif action.action_type == ActionType.GET_CONTENT:
                # In production, would get from Chrome extension
                result["success"] = True
                result["content"] = "page text content"

            else:
                result["error"] = f"Unknown action type: {action.action_type}"

        except Exception as e:
            result["error"] = str(e)

        # Notify callbacks
        for callback in self._action_callbacks:
            try:
                callback(action, result)
            except Exception:
                pass

        return result

    async def click(self, tab_id: int, selector: str) -> Dict[str, Any]:
        """Click an element"""
        action = BrowserAction(action_type=ActionType.CLICK, target=selector)
        return await self.execute_action(tab_id, action)

    async def fill(self, tab_id: int, selector: str, value: str) -> Dict[str, Any]:
        """Fill a form field"""
        action = BrowserAction(action_type=ActionType.FILL, target=selector, value=value)
        return await self.execute_action(tab_id, action)

    async def scroll(
        self, tab_id: int, direction: str = "down", amount: int = 300
    ) -> Dict[str, Any]:
        """Scroll the page"""
        action = BrowserAction(action_type=ActionType.SCROLL, target=direction, value=str(amount))
        return await self.execute_action(tab_id, action)

    async def scroll_to_element(self, tab_id: int, selector: str) -> Dict[str, Any]:
        """Scroll to a specific element"""
        action = BrowserAction(action_type=ActionType.SCROLL, target=f"element:{selector}")
        return await self.execute_action(tab_id, action)

    # ============== Content Extraction ==============

    async def get_page_content(self, tab_id: int) -> str:
        """Get page text content"""
        action = BrowserAction(action_type=ActionType.GET_CONTENT)
        result = await self.execute_action(tab_id, action)
        return result.get("content", "")

    async def get_dom_snapshot(self, tab_id: int, include_html: bool = True) -> Dict[str, Any]:
        """Get DOM snapshot"""
        action = BrowserAction(
            action_type=ActionType.GET_DOM, options={"include_html": include_html}
        )
        result = await self.execute_action(tab_id, action)
        return result.get("dom", {})

    async def get_interactive_elements(self, tab_id: int) -> List[Dict[str, Any]]:
        """Get list of interactive elements"""
        # In production, would parse DOM
        return []

    # ============== Screenshot ==============

    async def take_screenshot(self, tab_id: int, full_page: bool = False) -> str:
        """Take a screenshot"""
        action = BrowserAction(action_type=ActionType.SCREENSHOT, options={"full_page": full_page})
        result = await self.execute_action(tab_id, action)
        return result.get("screenshot", "")

    # ============== Events ==============

    def on_action(self, callback: Callable[[BrowserAction, Dict], None]) -> None:
        """Register an action callback"""
        self._action_callbacks.append(callback)

    def remove_action_callback(self, callback: Callable) -> None:
        """Remove an action callback"""
        if callback in self._action_callbacks:
            self._action_callbacks.remove(callback)


# Singleton instance
_browser_service: Optional[BrowserAutomationService] = None


def get_browser_service() -> BrowserAutomationService:
    """Get the browser automation service instance"""
    global _browser_service
    if _browser_service is None:
        _browser_service = BrowserAutomationService()
    return _browser_service
