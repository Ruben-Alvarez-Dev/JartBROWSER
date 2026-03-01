"""
Tab Search & Indexing Service

Provides search and filtering capabilities for tabs,
including metadata indexing and real-time search.
"""

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Set
from collections import defaultdict
import asyncio


@dataclass
class TabIndex:
    """Indexed tab data"""

    tab_id: int
    url: str
    title: str
    domain: str
    words: Set[str] = field(default_factory=set)
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_updated: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SearchResult:
    """Search result for a tab"""

    tab_index: TabIndex
    score: float
    match_type: str  # exact, partial, domain, title, url
    matched_terms: List[str] = field(default_factory=list)


class TabSearchService:
    """
    Service for searching and filtering tabs.

    Provides:
    - Full-text search across tabs
    - Domain filtering
    - Date filtering
    - Real-time indexing
    - Search ranking
    """

    def __init__(self):
        self._index: Dict[int, TabIndex] = {}
        self._domain_index: Dict[str, Set[int]] = defaultdict(set)
        self._word_index: Dict[str, Set[int]] = defaultdict(set)
        self._search_enabled: bool = True

    # ============== Indexing ==============

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            # Simple domain extraction
            if "://" in url:
                domain = url.split("://")[1].split("/")[0]
            else:
                domain = url.split("/")[0]
            return domain.lower()
        except Exception:
            return ""

    def _extract_words(self, text: str) -> Set[str]:
        """Extract searchable words from text"""
        # Convert to lowercase and split
        words = re.findall(r"\b\w+\b", text.lower())

        # Filter short words and common words
        stop_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "from",
            "is",
            "it",
            "this",
            "that",
            "be",
            "as",
            "are",
            "was",
            "were",
            "been",
            "have",
            "has",
        }

        return {w for w in words if len(w) > 2 and w not in stop_words}

    async def index_tab(
        self, tab_id: int, url: str, title: str, metadata: Optional[Dict[str, Any]] = None
    ) -> TabIndex:
        """Index a tab"""
        # Remove old index entries
        if tab_id in self._index:
            old_index = self._index[tab_id]
            self._domain_index[old_index.domain].discard(tab_id)
            for word in old_index.words:
                self._word_index[word].discard(tab_id)

        # Extract domain and words
        domain = self._extract_domain(url)
        words = self._extract_words(f"{title} {url}")

        # Create index
        index = TabIndex(
            tab_id=tab_id, url=url, title=title, domain=domain, words=words, metadata=metadata or {}
        )

        self._index[tab_id] = index

        # Update inverted indexes
        self._domain_index[domain].add(tab_id)
        for word in words:
            self._word_index[word].add(tab_id)

        return index

    async def remove_tab(self, tab_id: int) -> bool:
        """Remove tab from index"""
        if tab_id not in self._index:
            return False

        index = self._index[tab_id]

        # Remove from indexes
        self._domain_index[index.domain].discard(tab_id)
        for word in index.words:
            self._word_index[word].discard(tab_id)

        del self._index[tab_id]
        return True

    async def update_tab(
        self,
        tab_id: int,
        url: Optional[str] = None,
        title: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[TabIndex]:
        """Update indexed tab"""
        if tab_id not in self._index:
            return None

        index = self._index[tab_id]

        # Re-index if URL or title changed
        new_url = url or index.url
        new_title = title or index.title

        if url or title:
            await self.index_tab(tab_id, new_url, new_title, metadata)

        # Update metadata
        if metadata:
            index.metadata.update(metadata)
            index.last_updated = datetime.utcnow()

        return self._index.get(tab_id)

    # ============== Search ==============

    async def search(
        self, query: str, limit: int = 20, domain: Optional[str] = None
    ) -> List[SearchResult]:
        """Search tabs"""
        if not self._search_enabled:
            return []

        query_words = self._extract_words(query)

        if not query_words:
            return []

        results: Dict[int, SearchResult] = {}

        # Search by domain
        if domain:
            matching_tabs = self._domain_index.get(domain.lower(), set())
        else:
            # Search by words
            matching_tabs: Set[int] = set()
            for word in query_words:
                if word in self._word_index:
                    matching_tabs.update(self._word_index[word])

        # Score results
        for tab_id in matching_tabs:
            index = self._index.get(tab_id)
            if not index:
                continue

            score = 0.0
            match_type = "partial"
            matched_terms = []

            query_lower = query.lower()
            url_lower = index.url.lower()
            title_lower = index.title.lower()

            # Exact match (highest score)
            if query_lower == url_lower or query_lower == title_lower:
                score = 100.0
                match_type = "exact"
                matched_terms = [query]

            # URL match
            elif query_lower in url_lower:
                score = 50.0
                match_type = "url"
                matched_terms = [query]

            # Title match
            elif query_lower in title_lower:
                score = 40.0
                match_type = "title"
                matched_terms = [query]

            # Word match
            else:
                for word in query_words:
                    if word in index.words:
                        score += 10.0
                        matched_terms.append(word)

                if score > 0:
                    match_type = "content"

            if score > 0:
                results[tab_id] = SearchResult(
                    tab_index=index, score=score, match_type=match_type, matched_terms=matched_terms
                )

        # Sort by score
        sorted_results = sorted(results.values(), key=lambda r: r.score, reverse=True)

        return sorted_results[:limit]

    # ============== Filtering ==============

    async def filter_by_domain(self, domain: str, limit: int = 50) -> List[TabIndex]:
        """Filter tabs by domain"""
        tab_ids = self._domain_index.get(domain.lower(), set())

        results = []
        for tab_id in tab_ids:
            if tab_id in self._index:
                results.append(self._index[tab_id])

        return results[:limit]

    async def filter_by_date(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 50,
    ) -> List[TabIndex]:
        """Filter tabs by date"""
        results = []

        for index in self._index.values():
            if start_date and index.created_at < start_date:
                continue
            if end_date and index.created_at > end_date:
                continue
            results.append(index)

        results.sort(key=lambda x: x.created_at, reverse=True)
        return results[:limit]

    async def filter_by_tags(
        self, tags: List[str], match_all: bool = False, limit: int = 50
    ) -> List[TabIndex]:
        """Filter tabs by tags"""
        results = []

        for index in self._index.values():
            if match_all:
                if all(t in index.tags for t in tags):
                    results.append(index)
            else:
                if any(t in index.tags for t in tags):
                    results.append(index)

        return results[:limit]

    # ============== Tags ==============

    async def add_tag(self, tab_id: int, tag: str) -> Optional[TabIndex]:
        """Add a tag to a tab"""
        index = self._index.get(tab_id)
        if not index:
            return None

        if tag not in index.tags:
            index.tags.append(tag)
            index.last_updated = datetime.utcnow()

        return index

    async def remove_tag(self, tab_id: int, tag: str) -> Optional[TabIndex]:
        """Remove a tag from a tab"""
        index = self._index.get(tab_id)
        if not index:
            return None

        if tag in index.tags:
            index.tags.remove(tag)
            index.last_updated = datetime.utcnow()

        return index

    def get_all_tags(self) -> List[str]:
        """Get all unique tags"""
        tags = set()
        for index in self._index.values():
            tags.update(index.tags)
        return sorted(list(tags))

    # ============== Statistics ==============

    def get_stats(self) -> Dict[str, Any]:
        """Get search index statistics"""
        domains = len(self._domain_index)
        unique_words = len(self._word_index)

        # Top domains
        domain_counts = [(d, len(t)) for d, t in self._domain_index.items()]
        domain_counts.sort(key=lambda x: x[1], reverse=True)

        return {
            "total_indexed_tabs": len(self._index),
            "unique_domains": domains,
            "unique_words": unique_words,
            "top_domains": domain_counts[:10],
            "search_enabled": self._search_enabled,
        }

    def get_all_tabs(self) -> List[TabIndex]:
        """Get all indexed tabs"""
        return list(self._index.values())


# Singleton
_tab_search_service: Optional[TabSearchService] = None


def get_tab_search_service() -> TabSearchService:
    """Get the tab search service instance"""
    global _tab_search_service
    if _tab_search_service is None:
        _tab_search_service = TabSearchService()
    return _tab_search_service
