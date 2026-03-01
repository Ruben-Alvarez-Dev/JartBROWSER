"""
Window Persistence Service

Provides window state persistence, multi-window management, and window restore.
"""

import uuid
import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
from pathlib import Path


class WindowState(Enum):
    """Window states"""

    NORMAL = "normal"
    MINIMIZED = "minimized"
    MAXIMIZED = "maximized"
    FULLSCREEN = "fullscreen"
    CLOSED = "closed"


class WindowType(Enum):
    """Window types"""

    MAIN = "main"
    POPUP = "popup"
    PANEL = "panel"
    DIALOG = "dialog"
    SIDEBAR = "sidebar"


class MonitorInfo:
    """Monitor information"""

    def __init__(
        self,
        id: str,
        name: str,
        x: int,
        y: int,
        width: int,
        height: int,
        is_primary: bool = False,
    ):
        self.id = id
        self.name = name
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.is_primary = is_primary

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "isPrimary": self.is_primary,
        }


@dataclass
class WindowGeometry:
    """Window geometry"""

    x: int = 0
    y: int = 0
    width: int = 1024
    height: int = 768
    monitor_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "monitorId": self.monitor_id,
        }


@dataclass
class WindowProfile:
    """Window profile for persistence"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    window_type: WindowType = WindowType.MAIN
    state: WindowState = WindowState.NORMAL
    geometry: WindowGeometry = field(default_factory=WindowGeometry)
    is_visible: bool = True
    is_focused: bool = False
    is_always_on_top: bool = False
    is_fullscreen: bool = False
    title: str = ""
    url: str = ""
    favicon: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "windowType": self.window_type.value,
            "state": self.state.value,
            "geometry": self.geometry.to_dict(),
            "isVisible": self.is_visible,
            "isFocused": self.is_focused,
            "isAlwaysOnTop": self.is_always_on_top,
            "isFullscreen": self.is_fullscreen,
            "title": self.title,
            "url": self.url,
            "favicon": self.favicon,
            "metadata": self.metadata,
            "createdAt": self.created_at.isoformat(),
            "updatedAt": self.updated_at.isoformat(),
        }


@dataclass
class WindowGroup:
    """Group of related windows"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    window_ids: List[str] = field(default_factory=list)
    is_default: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "windowIds": self.window_ids,
            "isDefault": self.is_default,
            "createdAt": self.created_at.isoformat(),
            "metadata": self.metadata,
        }


class WindowPersistenceService:
    """
    Service for window persistence.

    Provides:
    - Window state persistence
    - Window position and size
    - Multiple monitor support
    - Window restore on startup
    - Multi-window management
    """

    def __init__(self, storage_path: Optional[str] = None):
        self._windows: Dict[str, WindowProfile] = {}
        self._groups: Dict[str, WindowGroup] = {}
        self._monitors: Dict[str, MonitorInfo] = {}
        self._storage_path = storage_path
        self._default_window_id: Optional[str] = None
        self._auto_save = True
        self._save_debounce_seconds = 2

    def set_storage_path(self, path: str) -> None:
        """Set storage path"""
        self._storage_path = path
        Path(path).mkdir(parents=True, exist_ok=True)

    # ============== Window Management ==============

    def create_window(
        self,
        name: str,
        window_type: WindowType = WindowType.MAIN,
        geometry: Optional[WindowGeometry] = None,
        title: str = "",
        url: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> WindowProfile:
        """Create a window profile"""
        window = WindowProfile(
            name=name,
            window_type=window_type,
            geometry=geometry or WindowGeometry(),
            title=title,
            url=url,
            metadata=metadata or {},
        )

        self._windows[window.id] = window

        if window_type == WindowType.MAIN:
            self._default_window_id = window.id

        return window

    def get_window(self, window_id: str) -> Optional[WindowProfile]:
        """Get a window"""
        return self._windows.get(window_id)

    def get_windows(
        self,
        window_type: Optional[WindowType] = None,
        include_closed: bool = False,
        limit: int = 50,
    ) -> List[WindowProfile]:
        """Get windows"""
        results = list(self._windows.values())

        if window_type:
            results = [w for w in results if w.window_type == window_type]

        if not include_closed:
            results = [w for w in results if w.state != WindowState.CLOSED]

        return results[:limit]

    def update_window(
        self,
        window_id: str,
        name: Optional[str] = None,
        state: Optional[WindowState] = None,
        geometry: Optional[WindowGeometry] = None,
        is_visible: Optional[bool] = None,
        is_focused: Optional[bool] = None,
        is_always_on_top: Optional[bool] = None,
        title: Optional[str] = None,
        url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[WindowProfile]:
        """Update a window"""
        window = self._windows.get(window_id)
        if not window:
            return None

        if name is not None:
            window.name = name
        if state is not None:
            window.state = state
        if geometry is not None:
            window.geometry = geometry
        if is_visible is not None:
            window.is_visible = is_visible
        if is_focused is not None:
            window.is_focused = is_focused
        if is_always_on_top is not None:
            window.is_always_on_top = is_always_on_top
        if title is not None:
            window.title = title
        if url is not None:
            window.url = url
        if metadata is not None:
            window.metadata.update(metadata)

        window.updated_at = datetime.utcnow()
        return window

    def delete_window(self, window_id: str) -> bool:
        """Delete a window"""
        if window_id in self._windows:
            del self._windows[window_id]
            if self._default_window_id == window_id:
                self._default_window_id = None
            return True
        return False

    def close_window(self, window_id: str) -> bool:
        """Close a window"""
        window = self._windows.get(window_id)
        if not window:
            return False

        window.state = WindowState.CLOSED
        window.updated_at = datetime.utcnow()
        return True

    def restore_window(self, window_id: str) -> bool:
        """Restore a closed window"""
        window = self._windows.get(window_id)
        if not window:
            return False

        window.state = WindowState.NORMAL
        window.updated_at = datetime.utcnow()
        return True

    # ============== Window Groups ==============

    def create_group(
        self,
        name: str,
        description: str = "",
        is_default: bool = False,
    ) -> WindowGroup:
        """Create a window group"""
        group = WindowGroup(
            name=name,
            description=description,
            is_default=is_default,
        )

        self._groups[group.id] = group

        if is_default:
            # Unset other defaults
            for g in self._groups.values():
                if g.id != group.id:
                    g.is_default = False

        return group

    def get_group(self, group_id: str) -> Optional[WindowGroup]:
        """Get a window group"""
        return self._groups.get(group_id)

    def get_groups(self) -> List[WindowGroup]:
        """Get all window groups"""
        return list(self._groups.values())

    def add_window_to_group(self, group_id: str, window_id: str) -> bool:
        """Add window to group"""
        group = self._groups.get(group_id)
        if not group:
            return False

        if window_id not in group.window_ids:
            group.window_ids.append(window_id)

        return True

    def remove_window_from_group(self, group_id: str, window_id: str) -> bool:
        """Remove window from group"""
        group = self._groups.get(group_id)
        if not group:
            return False

        if window_id in group.window_ids:
            group.window_ids.remove(window_id)

        return True

    def get_default_group(self) -> Optional[WindowGroup]:
        """Get default window group"""
        return next((g for g in self._groups.values() if g.is_default), None)

    def delete_group(self, group_id: str) -> bool:
        """Delete a window group"""
        if group_id in self._groups:
            del self._groups[group_id]
            return True
        return False

    # ============== Monitor Management ==============

    def register_monitor(
        self,
        id: str,
        name: str,
        x: int,
        y: int,
        width: int,
        height: int,
        is_primary: bool = False,
    ) -> MonitorInfo:
        """Register a monitor"""
        monitor = MonitorInfo(id, name, x, y, width, height, is_primary)
        self._monitors[id] = monitor
        return monitor

    def get_monitor(self, monitor_id: str) -> Optional[MonitorInfo]:
        """Get a monitor"""
        return self._monitors.get(monitor_id)

    def get_monitors(self) -> List[MonitorInfo]:
        """Get all monitors"""
        return list(self._monitors.values())

    def get_primary_monitor(self) -> Optional[MonitorInfo]:
        """Get primary monitor"""
        return next((m for m in self._monitors.values() if m.is_primary), None)

    def find_monitor_for_position(self, x: int, y: int) -> Optional[MonitorInfo]:
        """Find monitor that contains the given position"""
        for monitor in self._monitors.values():
            if (
                monitor.x <= x < monitor.x + monitor.width
                and monitor.y <= y < monitor.y + monitor.height
            ):
                return monitor
        return self.get_primary_monitor()

    # ============== Persistence ==============

    async def save_to_disk(self) -> bool:
        """Save window state to disk"""
        if not self._storage_path:
            return False

        try:
            path = Path(self._storage_path)
            path.mkdir(parents=True, exist_ok=True)

            # Save windows
            windows_data = {wid: window.to_dict() for wid, window in self._windows.items()}

            with open(path / "windows.json", "w") as f:
                json.dump(windows_data, f, indent=2)

            # Save groups
            groups_data = {gid: group.to_dict() for gid, group in self._groups.items()}

            with open(path / "window_groups.json", "w") as f:
                json.dump(groups_data, f, indent=2)

            # Save monitors
            monitors_data = {mid: monitor.to_dict() for mid, monitor in self._monitors.items()}

            with open(path / "monitors.json", "w") as f:
                json.dump(monitors_data, f, indent=2)

            # Save default window ID
            with open(path / "default_window.json", "w") as f:
                json.dump({"defaultWindowId": self._default_window_id}, f)

            return True
        except Exception:
            return False

    async def load_from_disk(self) -> bool:
        """Load window state from disk"""
        if not self._storage_path:
            return False

        try:
            path = Path(self._storage_path)
            if not path.exists():
                return False

            # Load windows
            windows_file = path / "windows.json"
            if windows_file.exists():
                with open(windows_file, "r") as f:
                    windows_data = json.load(f)

                for wid, data in windows_data.items():
                    window = WindowProfile(
                        id=data["id"],
                        name=data["name"],
                        window_type=WindowType(data["windowType"]),
                        state=WindowState(data["state"]),
                        geometry=WindowGeometry(**data["geometry"]),
                        is_visible=data["isVisible"],
                        is_focused=data["isFocused"],
                        is_always_on_top=data["isAlwaysOnTop"],
                        is_fullscreen=data["isFullscreen"],
                        title=data["title"],
                        url=data["url"],
                        favicon=data.get("favicon"),
                        metadata=data.get("metadata", {}),
                        created_at=datetime.fromisoformat(data["createdAt"]),
                        updated_at=datetime.fromisoformat(data["updatedAt"]),
                    )
                    self._windows[wid] = window

            # Load groups
            groups_file = path / "window_groups.json"
            if groups_file.exists():
                with open(groups_file, "r") as f:
                    groups_data = json.load(f)

                for gid, data in groups_data.items():
                    group = WindowGroup(
                        id=data["id"],
                        name=data["name"],
                        description=data["description"],
                        window_ids=data["windowIds"],
                        is_default=data["isDefault"],
                        created_at=datetime.fromisoformat(data["createdAt"]),
                        metadata=data.get("metadata", {}),
                    )
                    self._groups[gid] = group

            # Load monitors
            monitors_file = path / "monitors.json"
            if monitors_file.exists():
                with open(monitors_file, "r") as f:
                    monitors_data = json.load(f)

                for mid, data in monitors_data.items():
                    monitor = MonitorInfo(
                        id=data["id"],
                        name=data["name"],
                        x=data["x"],
                        y=data["y"],
                        width=data["width"],
                        height=data["height"],
                        is_primary=data["isPrimary"],
                    )
                    self._monitors[mid] = monitor

            # Load default window ID
            default_file = path / "default_window.json"
            if default_file.exists():
                with open(default_file, "r") as f:
                    data = json.load(f)
                    self._default_window_id = data.get("defaultWindowId")

            return True
        except Exception:
            return False

    # ============== Window Layouts ==============

    def save_layout(
        self,
        name: str,
        window_ids: Optional[List[str]] = None,
    ) -> Optional[str]:
        """Save current window layout"""
        if window_ids is None:
            window_ids = [w.id for w in self._windows.values() if w.state != WindowState.CLOSED]

        if not window_ids:
            return None

        group = self.create_group(
            name=f"Layout: {name}",
            description=f"Saved layout: {name}",
        )

        group.window_ids = window_ids
        return group.id

    def load_layout(self, group_id: str) -> List[WindowProfile]:
        """Load a saved layout"""
        group = self._groups.get(group_id)
        if not group:
            return []

        windows = []
        for window_id in group.window_ids:
            window = self._windows.get(window_id)
            if window:
                windows.append(window)

        return windows

    def get_layouts(self) -> List[WindowGroup]:
        """Get all saved layouts"""
        return [g for g in self._groups.values() if g.name.startswith("Layout: ")]

    # ============== Utility ==============

    def get_default_window(self) -> Optional[WindowProfile]:
        """Get default window"""
        if self._default_window_id:
            return self._windows.get(self._default_window_id)
        return next((w for w in self._windows.values() if w.window_type == WindowType.MAIN), None)

    def arrange_windows(
        self,
        arrangement: str = "tile_horizontal",
        window_ids: Optional[List[str]] = None,
    ) -> Dict[str, WindowGeometry]:
        """Arrange windows (tile_horizontal, tile_vertical, cascade, etc.)"""
        if window_ids is None:
            window_ids = [w.id for w in self._windows.values() if w.state != WindowState.CLOSED]

        windows = [self._windows[wid] for wid in window_ids if wid in self._windows]

        if not windows:
            return {}

        monitor = self.get_primary_monitor() or MonitorInfo("default", "Default", 0, 0, 1920, 1080)

        result = {}

        if arrangement == "tile_horizontal":
            width = monitor.width // len(windows)
            for i, window in enumerate(windows):
                result[window.id] = WindowGeometry(
                    x=monitor.x + i * width,
                    y=monitor.y,
                    width=width,
                    height=monitor.height,
                    monitor_id=monitor.id,
                )

        elif arrangement == "tile_vertical":
            height = monitor.height // len(windows)
            for i, window in enumerate(windows):
                result[window.id] = WindowGeometry(
                    x=monitor.x,
                    y=monitor.y + i * height,
                    width=monitor.width,
                    height=height,
                    monitor_id=monitor.id,
                )

        elif arrangement == "cascade":
            offset = 30
            for i, window in enumerate(windows):
                result[window.id] = WindowGeometry(
                    x=monitor.x + i * offset,
                    y=monitor.y + i * offset,
                    width=min(800, monitor.width - i * offset),
                    height=min(600, monitor.height - i * offset),
                    monitor_id=monitor.id,
                )

        # Apply geometries
        for window_id, geometry in result.items():
            self.update_window(window_id, geometry=geometry)

        return result


# Singleton
_window_persistence: Optional[WindowPersistenceService] = None


def get_window_persistence() -> WindowPersistenceService:
    """Get the window persistence service instance"""
    global _window_persistence
    if _window_persistence is None:
        _window_persistence = WindowPersistenceService()
    return _window_persistence
