"""
DOM Scanner & Page Analysis Service

Provides DOM scanning, element identification,
page structure analysis, and compact element representation.
"""

import uuid
import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Set
from enum import Enum


class ElementType(Enum):
    """Types of interactive elements"""
    LINK = "link"
    BUTTON = "button"
    INPUT = "input"
    SELECT = "select"
    TEXTAREA = "textarea"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    IMAGE = "image"
    FORM = "form"
    CONTAINER = "container"  # div, section, etc.
    TEXT = "text"
    OTHER = "other"


@dataclass
class ElementInfo:
    """Information about a DOM element"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    tag: str = ""
    element_type: ElementType = ElementType.OTHER
    selector: str = ""
    xpath: str = ""
    text: str = ""
    value: Optional[str] = None
    placeholder: Optional[str] = None
    href: Optional[str] = None
    src: Optional[str] = None
    alt: Optional[str] = None
    name: Optional[str] = None
    id_attr: Optional[str] = None
    classes: List[str] = field(default_factory=list)
    attributes: Dict[str, str] = field(default_factory=dict)
    visible: bool = True
    enabled: bool = True
    required: bool = False
    readonly: bool = False
    checked: bool = False
    selected: bool = False
    bounding_box: Optional[Dict[str, int]] = None  # x, y, width, height
    
    # Accessibility
    aria_label: Optional[str] = None
    aria_description: Optional[str] = None
    role: Optional[str] = None
    tab_index: Optional[int] = None
    
    # For compact representation
    hash: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "tag": self.tag,
            "element_type": self.element_type.value,
            "selector": self.selector,
            "xpath": self.xpath,
            "text": self.text[:200] if self.text else "",  # Truncate long text
            "value": self.value,
            "placeholder": self.placeholder,
            "href": self.href,
            "src": self.src,
            "alt": self.alt,
            "name": self.name,
            "id_attr": self.id_attr,
            "classes": self.classes,
            "attributes": self.attributes,
            "visible": self.visible,
            "enabled": self.enabled,
            "required": self.required,
            "readonly": self.readonly,
            "checked": self.checked,
            "selected": self.selected,
            "bounding_box": self.bounding_box,
            "aria_label": self.aria_label,
            "role": self.role,
            "hash": self.hash
        }
    
    def to_compact_dict(self) -> Dict[str, Any]:
        """Compact representation for LLM context"""
        result = {
            "t": self.tag,
            "e": self.element_type.value,
            "s": self.selector
        }
        
        if self.text:
            result["txt"] = self.text[:100]
        if self.value:
            result["val"] = self.value[:50]
        if self.placeholder:
            result["ph"] = self.placeholder
        if self.href:
            result["href"] = self.href[:100]
        if self.name:
            result["nm"] = self.name
        if self.aria_label:
            result["aria"] = self.aria_label
        if self.role:
            result["role"] = self.role
        
        return result
    
    def compute_hash(self) -> str:
        """Compute unique hash for deduplication"""
        content = f"{self.tag}:{self.selector}:{self.text[:50]}"
        return hashlib.md5(content.encode()).hexdigest()[:8]


@dataclass
class PageStructure:
    """Page structure information"""
    url: str
    title: str
    elements: List[ElementInfo] = field(default_factory=list)
    interactive_count: int = 0
    forms_count: int = 0
    links_count: int = 0
    inputs_count: int = 0
    images_count: int = 0
    semantic_sections: List[Dict[str, Any]] = field(default_factory=list)
   扫描_time_ms: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)


class DOMScannerService:
    """
    Service for scanning and analyzing page DOM.
    
    Provides:
    - Element identification
    - Page structure analysis
    - Compact element representation
    - Semantic section detection
    """
    
    # Interactive element selectors
    INTERACTIVE_SELECTORS = {
        ElementType.LINK: ['a[href]'],
        ElementType.BUTTON: ['button', 'input[type="button"]', 'input[type="submit"]', '[role="button"]'],
        ElementType.INPUT: ['input[type="text"]', 'input[type="email"]', 'input[type="password"]', 'input[type="search"]', 'input[type="tel"]', 'input[type="url"]', 'input:not([type])'],
        ElementType.SELECT: ['select'],
        ElementType.TEXTAREA: ['textarea'],
        ElementType.CHECKBOX: ['input[type="checkbox"]'],
        ElementType.RADIO: ['input[type="radio"]'],
        ElementType.IMAGE: ['img'],
    }
    
    # Semantic section selectors
    SEMANTIC_SELECTORS = {
        "header": ["header", "[role=\"banner\"]"],
        "nav": ["nav", "[role=\"navigation\"]"],
        "main": ["main", "[role=\"main\"]"],
        "aside": ["aside", "[role=\"complementary\"]"],
        "footer": ["footer", "[role=\"contentinfo\"]"],
        "article": ["article", "[role=\"article\"]"],
        "section": ["section", "[role=\"region\"]"],
        "form": ["form", "[role=\"form\"]"],
        "search": ["[role=\"search\"]"],
        "content": ["main", "[role=\"main\"]", ".content", ".main", "#content"],
    }
    
    def __init__(self):
        self._scan_cache: Dict[str, PageStructure] = {}
        self._max_elements_per_page: int = 500
        self._enable_deduplication: bool = True
    
    # ============== Element Detection ==============
    
    def _detect_element_type(self, tag: str, attributes: Dict[str, str]) -> ElementType:
        """Detect element type from tag and attributes"""
        tag_lower = tag.lower()
        
        # Check tag name
        if tag_lower == "a":
            return ElementType.LINK
        elif tag_lower == "button":
            return ElementType.BUTTON
        elif tag_lower == "input":
            input_type = attributes.get("type", "text").lower()
            if input_type in ["checkbox", "radio", "button", "submit", "reset", "file"]:
                return ElementType.INPUT  # Simplified
            return ElementType.INPUT
        elif tag_lower == "select":
            return ElementType.SELECT
        elif tag_lower == "textarea":
            return ElementType.TEXTAREA
        elif tag_lower == "img":
            return ElementType.IMAGE
        elif tag_lower in ["div", "span", "section", "article", "header", "footer"]:
            # Check for role attribute
            role = attributes.get("role", "").lower()
            if role == "button":
                return ElementType.BUTTON
            elif role == "link":
                return ElementType.LINK
            elif role == "textbox":
                return ElementType.INPUT
            elif role in ["search", "searchbox", "combobox"]:
                return ElementType.INPUT
            return ElementType.CONTAINER
        
        return ElementType.OTHER
    
    def _build_selector(self, tag: str, attributes: Dict[str, str], index: int) -> str:
        """Build CSS selector for element"""
        selector = tag.lower()
        
        # Add ID if present
        if "id" in attributes:
            return f"#{attributes['id']}"
        
        # Add classes
        if "class" in attributes:
            classes = attributes["class"].split()[:2]  # Limit to 2 classes
            if classes:
                selector += "." + ".".join(classes)
        
        # Add type for inputs
        if tag.lower() == "input" and "type" in attributes:
            selector += f"[type=\"{attributes['type']}\"]"
        
        return selector
    
    def _build_xpath(self, tag: str, attributes: Dict[str, str], path: List[str]) -> str:
        """Build XPath for element"""
        xpath = "/" + "/".join(path)
        
        if "id" in attributes:
            xpath += f"[@id='{attributes['id']}']"
        elif "class" in attributes:
            classes = attributes["class"].split()
            if classes:
                xpath += f"[@class='{classes[0]}']"
        
        return xpath
    
    def _extract_accessibility(self, element_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract accessibility information"""
        return {
            "aria_label": element_data.get("aria-label"),
            "aria_description": element_data.get("aria-describedby"),
            "role": element_data.get("role"),
            "tab_index": element_data.get("tabindex")
        }
    
    # ============== Scanning ==============
    
    async def scan_page(
        self,
        url: str,
        html: str,
        dom_snapshot: Optional[Dict[str, Any]] = None
    ) -> PageStructure:
        """Scan a page and extract elements"""
        import time
        start_time = time.time()
        
        structure = PageStructure(
            url=url,
            title=dom_snapshot.get("title", "") if dom_snapshot else ""
        )
        
        # In production, would parse HTML/DOM properly
        # For now, create sample elements from snapshot
        if dom_snapshot and "elements" in dom_snapshot:
            seen_hashes: Set[str] = set()
            
            for elem_data in dom_snapshot["elements"][:self._max_elements_per_page]:
                element = self._create_element_from_data(elem_data)
                
                if element:
                    # Deduplication
                    if self._enable_deduplication:
                        element.hash = element.compute_hash()
                        if element.hash in seen_hashes:
                            continue
                        seen_hashes.add(element.hash)
                    
                    structure.elements.append(element)
                    
                    # Count by type
                    if element.element_type == ElementType.LINK:
                        structure.links_count += 1
                    elif element.element_type == ElementType.INPUT:
                        structure.inputs_count += 1
                    elif element.element_type == ElementType.BUTTON:
                        structure.interactive_count += 1
                    elif element.element_type == ElementType.IMAGE:
                        structure.images_count += 1
        
        # Extract semantic sections
        structure.semantic_sections = await self._detect_semantic_sections(dom_snapshot)
        
        structure.scan_time_ms = int((time.time() - start_time) * 1000)
        return structure
    
    def _create_element_from_data(self, data: Dict[str, Any]) -> Optional[ElementInfo]:
        """Create ElementInfo from raw data"""
        tag = data.get("tag", "").lower()
        if not tag:
            return None
        
        attributes = data.get("attributes", {})
        
        element = ElementInfo(
            tag=tag,
            element_type=self._detect_element_type(tag, attributes),
            selector=data.get("selector", ""),
            xpath=data.get("xpath", ""),
            text=data.get("text", ""),
            value=data.get("value"),
            placeholder=attributes.get("placeholder"),
            href=attributes.get("href"),
            src=attributes.get("src"),
            alt=attributes.get("alt"),
            name=attributes.get("name"),
            id_attr=attributes.get("id"),
            classes=attributes.get("class", "").split() if attributes.get("class") else [],
            attributes=attributes,
            visible=data.get("visible", True),
            enabled=data.get("enabled", True),
            required=attributes.get("required") is not None,
            readonly=attributes.get("readonly") is not None,
            checked=data.get("checked", False),
            selected=data.get("selected", False)
        )
        
        # Accessibility
        a11y = self._extract_accessibility(attributes)
        element.aria_label = a11y["aria_label"]
        element.aria_description = a11y["aria_description"]
        element.role = a11y["role"]
        element.tab_index = a11y["tab_index"]
        
        return element
    
    async def _detect_semantic_sections(
        self,
        dom_snapshot: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Detect semantic sections of the page"""
        sections = []
        
        if not dom_snapshot:
            return sections
        
        # In production, would parse DOM for semantic elements
        # For now, return basic structure
        
        return sections
    
    # ============== Compact Representation ==============
    
    def get_compact_elements(
        self,
        elements: List[ElementInfo],
        max_elements: int = 50
    ) -> List[Dict[str, Any]]:
        """Get compact element representation for LLM context"""
        # Sort by importance (interactive first)
        priority = {
            ElementType.BUTTON: 1,
            ElementType.INPUT: 2,
            ElementType.LINK: 3,
            ElementType.SELECT: 4,
            ElementType.CHECKBOX: 5,
            ElementType.RADIO: 6,
            ElementType.TEXTAREA: 7,
            ElementType.IMAGE: 8,
            ElementType.CONTAINER: 9,
            ElementType.OTHER: 10
        }
        
        sorted_elements = sorted(
            elements,
            key=lambda e: (
                priority.get(e.element_type, 99),
                -len(e.text)  # Prefer elements with text
            )
        )
        
        return [e.to_compact_dict() for e in sorted_elements[:max_elements]]
    
    # ============== Search ==============
    
    async def find_element(
        self,
        elements: List[ElementInfo],
        selector: str
    ) -> Optional[ElementInfo]:
        """Find element by selector"""
        for element in elements:
            if element.selector == selector:
                return element
        return None
    
    async def find_elements_by_text(
        self,
        elements: List[ElementInfo],
        text: str,
        exact: bool = False
    ) -> List[ElementInfo]:
        """Find elements by text content"""
        results = []
        text_lower = text.lower()
        
        for element in elements:
            if exact:
                if element.text.lower() == text_lower:
                    results.append(element)
            else:
                if text_lower in element.text.lower():
                    results.append(element)
        
        return results
    
    async def find_elements_by_type(
        self,
        elements: List[ElementInfo],
        element_type: ElementType
    ) -> List[ElementInfo]:
        """Find elements by type"""
        return [e for e in elements if e.element_type == element_type]
    
    # ============== Validation ==============
    
    def validate_selector(self, selector: str) -> bool:
        """Validate CSS selector"""
        if not selector:
            return False
        
        # Basic validation
        try:
            # Would validate properly in production
            return True
        except Exception:
            return False
    
    # ============== Cache ==============
    
    def get_cached_structure(self, url: str) -> Optional[PageStructure]:
        """Get cached page structure"""
        return self._scan_cache.get(url)
    
    def cache_structure(self, structure: PageStructure) -> None:
        """Cache page structure"""
        self._scan_cache[structure.url] = structure
    
    def clear_cache(self, url: Optional[str] = None) -> None:
        """Clear cache"""
        if url:
            self._scan_cache.pop(url, None)
        else:
            self._scan_cache.clear()


# Singleton
_dom_scanner_service: Optional[DOMScannerService] = None


def get_dom_scanner_service() -> DOMScannerService:
    """Get the DOM scanner service instance"""
    global _dom_scanner_service
    if _dom_scanner_service is None:
        _dom_scanner_service = DOMScannerService()
    return _dom_scanner_service
