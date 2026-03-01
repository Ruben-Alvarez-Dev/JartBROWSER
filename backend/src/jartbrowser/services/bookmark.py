"""
Bookmark Service

Provides bookmark management functionality including CRUD operations,
folders, tags, search, and import/export.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any


@dataclass
class Bookmark:
    """Bookmark model"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    url: str = ""
    title: str = ""
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    folder_id: Optional[str] = None
    favicon: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    visit_count: int = 0
    last_visited: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "url": self.url,
            "title": self.title,
            "description": self.description,
            "tags": self.tags,
            "folder_id": self.folder_id,
            "favicon": self.favicon,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "visit_count": self.visit_count,
            "last_visited": self.last_visited.isoformat() if self.last_visited else None,
        }


@dataclass
class BookmarkFolder:
    """Bookmark folder model"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    parent_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "parent_id": self.parent_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class BookmarkService:
    """
    Service for managing bookmarks.

    Provides CRUD operations, folder organization, tagging,
    search, and import/export functionality.
    """

    def __init__(self):
        self._bookmarks: Dict[str, Bookmark] = {}
        self._folders: Dict[str, BookmarkFolder] = {}

    # ============== Bookmark CRUD ==============

    def create_bookmark(
        self,
        url: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        folder_id: Optional[str] = None,
    ) -> Bookmark:
        """Create a new bookmark"""
        bookmark = Bookmark(
            url=url,
            title=title or url,
            description=description,
            tags=tags or [],
            folder_id=folder_id,
        )

        self._bookmarks[bookmark.id] = bookmark
        return bookmark

    def get_bookmark(self, bookmark_id: str) -> Optional[Bookmark]:
        """Get a bookmark by ID"""
        return self._bookmarks.get(bookmark_id)

    def get_bookmarks(
        self,
        folder_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Bookmark]:
        """Get bookmarks with optional filtering"""
        results = list(self._bookmarks.values())

        # Filter by folder
        if folder_id is not None:
            results = [b for b in results if b.folder_id == folder_id]

        # Filter by tags
        if tags:
            results = [b for b in results if any(t in b.tags for t in tags)]

        # Sort by most recently used
        results.sort(key=lambda b: b.last_visited or b.created_at, reverse=True)

        return results[offset : offset + limit]

    def update_bookmark(
        self,
        bookmark_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        folder_id: Optional[str] = None,
    ) -> Optional[Bookmark]:
        """Update a bookmark"""
        bookmark = self._bookmarks.get(bookmark_id)
        if not bookmark:
            return None

        if title is not None:
            bookmark.title = title
        if description is not None:
            bookmark.description = description
        if tags is not None:
            bookmark.tags = tags
        if folder_id is not None:
            bookmark.folder_id = folder_id

        bookmark.updated_at = datetime.utcnow()
        return bookmark

    def delete_bookmark(self, bookmark_id: str) -> bool:
        """Delete a bookmark"""
        if bookmark_id in self._bookmarks:
            del self._bookmarks[bookmark_id]
            return True
        return False

    def visit_bookmark(self, bookmark_id: str) -> Optional[Bookmark]:
        """Record a bookmark visit"""
        bookmark = self._bookmarks.get(bookmark_id)
        if bookmark:
            bookmark.visit_count += 1
            bookmark.last_visited = datetime.utcnow()
        return bookmark

    # ============== Search ==============

    def search_bookmarks(self, query: str, limit: int = 50) -> List[Bookmark]:
        """Search bookmarks by query"""
        query_lower = query.lower()
        results = []

        for bookmark in self._bookmarks.values():
            # Search in title, URL, description, and tags
            searchable = " ".join(
                [bookmark.title, bookmark.url, bookmark.description or "", " ".join(bookmark.tags)]
            ).lower()

            if query_lower in searchable:
                results.append(bookmark)

        # Sort by relevance and recency
        results.sort(key=lambda b: (b.visit_count, b.last_visited or b.created_at), reverse=True)

        return results[:limit]

    def get_bookmarks_by_url(self, url: str) -> List[Bookmark]:
        """Get all bookmarks for a specific URL"""
        return [b for b in self._bookmarks.values() if b.url == url]

    def get_recent_bookmarks(self, limit: int = 10) -> List[Bookmark]:
        """Get recently visited bookmarks"""
        results = [b for b in self._bookmarks.values() if b.last_visited]
        results.sort(key=lambda b: b.last_visited or b.created_at, reverse=True)
        return results[:limit]

    def get_popular_bookmarks(self, limit: int = 10) -> List[Bookmark]:
        """Get most visited bookmarks"""
        results = list(self._bookmarks.values())
        results.sort(key=lambda b: b.visit_count, reverse=True)
        return results[:limit]

    # ============== Tags ==============

    def get_all_tags(self) -> List[str]:
        """Get all unique tags"""
        tags = set()
        for bookmark in self._bookmarks.values():
            tags.update(bookmark.tags)
        return sorted(list(tags))

    def get_bookmarks_by_tag(self, tag: str) -> List[Bookmark]:
        """Get bookmarks by tag"""
        return [b for b in self._bookmarks.values() if tag in b.tags]

    def add_tag(self, bookmark_id: str, tag: str) -> Optional[Bookmark]:
        """Add a tag to a bookmark"""
        bookmark = self._bookmarks.get(bookmark_id)
        if bookmark and tag not in bookmark.tags:
            bookmark.tags.append(tag)
            bookmark.updated_at = datetime.utcnow()
        return bookmark

    def remove_tag(self, bookmark_id: str, tag: str) -> Optional[Bookmark]:
        """Remove a tag from a bookmark"""
        bookmark = self._bookmarks.get(bookmark_id)
        if bookmark and tag in bookmark.tags:
            bookmark.tags.remove(tag)
            bookmark.updated_at = datetime.utcnow()
        return bookmark

    # ============== Folders ==============

    def create_folder(self, name: str, parent_id: Optional[str] = None) -> BookmarkFolder:
        """Create a new folder"""
        folder = BookmarkFolder(name=name, parent_id=parent_id)

        self._folders[folder.id] = folder
        return folder

    def get_folder(self, folder_id: str) -> Optional[BookmarkFolder]:
        """Get a folder by ID"""
        return self._folders.get(folder_id)

    def get_folders(self, parent_id: Optional[str] = None) -> List[BookmarkFolder]:
        """Get folders, optionally filtered by parent"""
        results = list(self._folders.values())

        if parent_id is not None:
            results = [f for f in results if f.parent_id == parent_id]

        return results

    def update_folder(
        self, folder_id: str, name: Optional[str] = None, parent_id: Optional[str] = None
    ) -> Optional[BookmarkFolder]:
        """Update a folder"""
        folder = self._folders.get(folder_id)
        if not folder:
            return None

        if name is not None:
            folder.name = name
        if parent_id is not None:
            folder.parent_id = parent_id

        folder.updated_at = datetime.utcnow()
        return folder

    def delete_folder(self, folder_id: str) -> bool:
        """Delete a folder (moves bookmarks to root)"""
        if folder_id not in self._folders:
            return False

        # Move bookmarks to root
        for bookmark in self._bookmarks.values():
            if bookmark.folder_id == folder_id:
                bookmark.folder_id = None

        # Move child folders to root
        for folder in self._folders.values():
            if folder.parent_id == folder_id:
                folder.parent_id = None

        del self._folders[folder_id]
        return True

    def get_folder_tree(self) -> Dict[str, Any]:
        """Get folder structure as a tree"""

        def build_tree(parent_id: Optional[str] = None) -> List[Dict]:
            result = []

            for folder in self._folders.values():
                if folder.parent_id == parent_id:
                    node = {"id": folder.id, "name": folder.name, "children": build_tree(folder.id)}
                    result.append(node)

            return result

        return {
            "folders": build_tree(),
            "root_bookmarks": [
                b.to_dict() for b in self._bookmarks.values() if b.folder_id is None
            ],
        }

    # ============== Import/Export ==============

    def export_bookmarks(self) -> List[Dict[str, Any]]:
        """Export all bookmarks"""
        return [b.to_dict() for b in self._bookmarks.values()]

    def import_bookmarks(self, bookmarks: List[Dict[str, Any]], merge: bool = True) -> int:
        """Import bookmarks"""
        imported = 0

        for data in bookmarks:
            # Check if already exists
            existing = self.get_bookmarks_by_url(data.get("url", ""))

            if existing and not merge:
                continue

            if not existing:
                self.create_bookmark(
                    url=data.get("url", ""),
                    title=data.get("title"),
                    description=data.get("description"),
                    tags=data.get("tags", []),
                    folder_id=data.get("folder_id"),
                )
                imported += 1

        return imported

    def export_html(self) -> str:
        """Export bookmarks as HTML (Netscape format)"""
        html = [
            "<!DOCTYPE NETSCAPE-Bookmark-file-1>",
            "<!-- This is an automatically generated file.",
            "     It will be read and overwritten.",
            "     DO NOT EDIT! -->",
            '<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">',
            "<TITLE>Bookmarks</TITLE>",
            "<H1>Bookmarks</H1>",
            "<DL><p>",
        ]

        # Add folders
        def add_folder_items(folder_id: Optional[str] = None, indent: int = 2):
            spaces = "  " * indent

            # Bookmarks in this folder
            for bookmark in self.get_bookmarks(folder_id=folder_id):
                html.append(
                    f'{spaces}<DT><A HREF="{bookmark.url}" ADD_DATE="{int(bookmark.created_at.timestamp())}">{bookmark.title}</A>'
                )
                if bookmark.description:
                    html.append(f"{spaces}<DD>{bookmark.description}")

            # Subfolders
            for folder in self.get_folders(parent_id=folder_id):
                html.append(
                    f'{spaces}<DT><H3 ADD_DATE="{int(folder.created_at.timestamp())}">{folder.name}</H3>'
                )
                html.append(f"{spaces}<DL><p>")
                add_folder_items(folder.id, indent + 1)
                html.append(f"{spaces}</DL><p>")

        add_folder_items()

        html.append("</DL><p>")
        return "\n".join(html)

    def import_html(self, html: str) -> int:
        """Import bookmarks from HTML (Netscape format)"""
        # Simplified HTML parser - in production would use proper HTML parsing
        imported = 0

        # Simple regex-based extraction
        import re

        # Extract bookmarks
        pattern = r'<A HREF="([^"]+)"[^>]*>([^<]+)</A>'
        matches = re.findall(pattern, html)

        for url, title in matches:
            existing = self.get_bookmarks_by_url(url)
            if not existing:
                self.create_bookmark(url=url, title=title)
                imported += 1

        return imported


# Singleton instance
_bookmark_service: Optional[BookmarkService] = None


def get_bookmark_service() -> BookmarkService:
    """Get the bookmark service instance"""
    global _bookmark_service
    if _bookmark_service is None:
        _bookmark_service = BookmarkService()
    return _bookmark_service
