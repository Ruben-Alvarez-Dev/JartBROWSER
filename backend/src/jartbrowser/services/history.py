"""
History Service

Provides browsing history management including search,
filtering, and statistics.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any


@dataclass
class HistoryEntry:
    """Browsing history entry"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    url: str = ""
    title: str = ""
    visit_count: int = 1
    last_visit: datetime = field(default_factory=datetime.utcnow)
    created_at: datetime = field(default_factory=datetime.utcnow)
    typed_count: int = 0
    bookmark_id: Optional[str] = None

    # Parsed URL components
    domain: str = ""
    scheme: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "url": self.url,
            "title": self.title,
            "visit_count": self.visit_count,
            "last_visit": self.last_visit.isoformat(),
            "created_at": self.created_at.isoformat(),
            "typed_count": self.typed_count,
            "bookmark_id": self.bookmark_id,
            "domain": self.domain,
            "scheme": self.scheme,
        }


class HistoryService:
    """
    Service for managing browsing history.

    Provides visit tracking, search, filtering,
    and statistics.
    """

    def __init__(self):
        self._history: Dict[str, HistoryEntry] = {}
        self._url_index: Dict[str, str] = {}  # URL -> entry ID

    def _parse_url(self, url: str) -> tuple[str, str]:
        """Parse URL to get scheme and domain"""
        try:
            from urllib.parse import urlparse

            parsed = urlparse(url)
            return parsed.scheme, parsed.netloc
        except Exception:
            return "", ""

    def _normalize_url(self, url: str) -> str:
        """Normalize URL for comparison"""
        # Remove trailing slashes, fragments
        url = url.rstrip("/")
        if "#" in url:
            url = url.split("#")[0]
        return url.lower()

    # ============== Visit Tracking ==============

    def add_visit(self, url: str, title: str = "", transition_type: str = "link") -> HistoryEntry:
        """Record a page visit"""
        normalized = self._normalize_url(url)

        # Check if entry exists
        entry_id = self._url_index.get(normalized)

        if entry_id and entry_id in self._history:
            # Update existing entry
            entry = self._history[entry_id]
            entry.visit_count += 1
            entry.last_visit = datetime.utcnow()
            entry.title = title or entry.title

            if transition_type == "typed":
                entry.typed_count += 1

            # Update URL index if URL changed
            if url != normalized:
                self._url_index[normalized] = entry_id

            return entry

        # Create new entry
        scheme, domain = self._parse_url(url)

        entry = HistoryEntry(url=url, title=title or url, domain=domain, scheme=scheme)

        self._history[entry.id] = entry
        self._url_index[normalized] = entry.id

        return entry

    def get_entry(self, entry_id: str) -> Optional[HistoryEntry]:
        """Get a history entry by ID"""
        return self._history.get(entry_id)

    def get_entry_by_url(self, url: str) -> Optional[HistoryEntry]:
        """Get history entry by URL"""
        normalized = self._normalize_url(url)
        entry_id = self._url_index.get(normalized)

        if entry_id:
            return self._history.get(entry_id)

        return None

    def delete_entry(self, entry_id: str) -> bool:
        """Delete a history entry"""
        if entry_id not in self._history:
            return False

        entry = self._history[entry_id]
        normalized = self._normalize_url(entry.url)

        del self._history[entry_id]

        if normalized in self._url_index:
            del self._url_index[normalized]

        return True

    def delete_by_url(self, url: str) -> bool:
        """Delete history entry by URL"""
        entry = self.get_entry_by_url(url)
        if entry:
            return self.delete_entry(entry.id)
        return False

    # ============== Queries ==============

    def get_history(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        domain: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[HistoryEntry]:
        """Get history entries with optional filtering"""
        results = list(self._history.values())

        # Filter by date range
        if start_date:
            results = [e for e in results if e.last_visit >= start_date]

        if end_date:
            results = [e for e in results if e.last_visit <= end_date]

        # Filter by domain
        if domain:
            results = [e for e in results if domain.lower() in e.domain.lower()]

        # Sort by most recent
        results.sort(key=lambda e: e.last_visit, reverse=True)

        return results[offset : offset + limit]

    def search(self, query: str, limit: int = 50) -> List[HistoryEntry]:
        """Search history by query"""
        query_lower = query.lower()
        results = []

        for entry in self._history.values():
            searchable = " ".join([entry.title, entry.url, entry.domain]).lower()

            if query_lower in searchable:
                results.append(entry)

        # Sort by relevance and recency
        results.sort(key=lambda e: (e.visit_count, e.last_visit), reverse=True)

        return results[:limit]

    def get_recent(self, limit: int = 50) -> List[HistoryEntry]:
        """Get recently visited pages"""
        results = list(self._history.values())
        results.sort(key=lambda e: e.last_visit, reverse=True)
        return results[:limit]

    def get_most_visited(self, limit: int = 50) -> List[HistoryEntry]:
        """Get most visited pages"""
        results = list(self._history.values())
        results.sort(key=lambda e: e.visit_count, reverse=True)
        return results[:limit]

    def get_today(self) -> List[HistoryEntry]:
        """Get today's history"""
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        return self.get_history(start_date=today)

    def get_by_date(self, date: datetime) -> List[HistoryEntry]:
        """Get history for a specific date"""
        start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
        return self.get_history(start_date=start, end_date=end)

    def get_by_domain(self, domain: str) -> List[HistoryEntry]:
        """Get history for a specific domain"""
        return self.get_history(domain=domain)

    # ============== Statistics ==============

    def get_stats(self) -> Dict[str, Any]:
        """Get history statistics"""
        total_visits = sum(e.visit_count for e in self._history.values())
        unique_urls = len(self._history)

        # Top domains
        domain_counts: Dict[str, int] = {}
        for entry in self._history.values():
            if entry.domain:
                domain_counts[entry.domain] = domain_counts.get(entry.domain, 0) + entry.visit_count

        top_domains = sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)[:10]

        # Date range
        if self._history:
            dates = [e.last_visit for e in self._history.values()]
            oldest = min(dates)
            newest = max(dates)
        else:
            oldest = newest = datetime.utcnow()

        return {
            "total_visits": total_visits,
            "unique_urls": unique_urls,
            "top_domains": [{"domain": d, "visits": v} for d, v in top_domains],
            "oldest_entry": oldest.isoformat(),
            "newest_entry": newest.isoformat(),
        }

    def get_top_domains(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most visited domains"""
        domain_counts: Dict[str, int] = {}

        for entry in self._history.values():
            if entry.domain:
                domain_counts[entry.domain] = domain_counts.get(entry.domain, 0) + entry.visit_count

        results = sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)[:limit]

        return [{"domain": d, "visits": v} for d, v in results]

    def get_visit_times(self) -> Dict[int, int]:
        """Get visit counts by hour of day"""
        hours = {h: 0 for h in range(24)}

        for entry in self._history.values():
            hour = entry.last_visit.hour
            hours[hour] += entry.visit_count

        return hours

    # ============== Bulk Operations ==============

    def delete_range(self, start_date: datetime, end_date: datetime) -> int:
        """Delete history entries in date range"""
        to_delete = []

        for entry in self._history.values():
            if start_date <= entry.last_visit <= end_date:
                to_delete.append(entry.id)

        for entry_id in to_delete:
            self.delete_entry(entry_id)

        return len(to_delete)

    def delete_by_domain(self, domain: str) -> int:
        """Delete all history for a domain"""
        to_delete = []

        for entry in self._history.values():
            if domain.lower() in entry.domain.lower():
                to_delete.append(entry.id)

        for entry_id in to_delete:
            self.delete_entry(entry_id)

        return len(to_delete)

    def clear_all(self) -> int:
        """Clear all history"""
        count = len(self._history)
        self._history.clear()
        self._url_index.clear()
        return count

    def delete_older_than(self, days: int) -> int:
        """Delete history older than N days"""
        cutoff = datetime.utcnow() - timedelta(days=days)

        to_delete = [
            entry_id for entry_id, entry in self._history.items() if entry.last_visit < cutoff
        ]

        for entry_id in to_delete:
            self.delete_entry(entry_id)

        return len(to_delete)

    # ============== Export ==============

    def export(self) -> List[Dict[str, Any]]:
        """Export all history"""
        return [e.to_dict() for e in self._history.values()]

    def import_history(self, entries: List[Dict[str, Any]], merge: bool = True) -> int:
        """Import history entries"""
        imported = 0

        for data in entries:
            url = data.get("url")
            if not url:
                continue

            if merge:
                # Check if exists
                existing = self.get_entry_by_url(url)
                if existing:
                    # Update
                    existing.visit_count += data.get("visit_count", 1)
                    if data.get("title"):
                        existing.title = data["title"]
                    continue

            # Add new
            self.add_visit(url=url, title=data.get("title", ""))
            imported += 1

        return imported


# Singleton instance
_history_service: Optional[HistoryService] = None


def get_history_service() -> HistoryService:
    """Get the history service instance"""
    global _history_service
    if _history_service is None:
        _history_service = HistoryService()
    return _history_service
