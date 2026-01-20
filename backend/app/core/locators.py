"""Locator generation system for DOM elements."""

from typing import List, Dict, Any, Optional
import logging

from app.core.config import config

logger = logging.getLogger(__name__)


class LocatorGenerator:
    """Generate multiple locator strategies for DOM elements."""
    
    def __init__(self):
        self.strategies_config = config.get('locators', 'locators.strategies', [])
        self.max_locators = config.get('locators', 'locators.max_locators_per_event', 5)
        self.validate_uniqueness = config.get('locators', 'locators.validate_uniqueness', True)
    
    def generate_locators(self, element_info: Dict[str, Any], iframe_context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Generate multiple locator strategies for an element.
        
        Args:
            element_info: Dictionary containing element information:
                - tag: HTML tag name
                - id: Element ID
                - class: Class names
                - role: ARIA role
                - aria_label: ARIA label
                - name: Name attribute
                - placeholder: Placeholder text
                - text: Text content
                - data_testid: data-testid attribute
                - label_text: Associated label text
                - attributes: Other attributes
            iframe_context: Optional iframe context information:
                - is_iframe: Boolean indicating if element is in iframe
                - frame_url: URL of the iframe
                - frame_id: ID of the iframe element
                - frame_name: Name of the iframe
        
        Returns:
            List of locator dictionaries with strategy, selector, and stability
        """
        locators = []
        is_in_iframe = iframe_context and iframe_context.get('is_iframe', False)
        
        # Try each strategy in priority order
        for strategy_config in self.strategies_config:
            if not strategy_config.get('enabled', True):
                continue
            
            strategy_name = strategy_config.get('name')
            locator = None
            
            if strategy_name == 'role':
                locator = self.generate_role_locator(element_info)
            elif strategy_name == 'label':
                locator = self.generate_label_locator(element_info)
            elif strategy_name == 'data_testid':
                locator = self.generate_testid_locator(element_info)
            elif strategy_name == 'placeholder':
                locator = self.generate_placeholder_locator(element_info)
            elif strategy_name == 'text':
                locator = self.generate_text_locator(element_info)
            elif strategy_name == 'css':
                locator = self.generate_css_locator(element_info)
            elif strategy_name == 'xpath':
                locator = self.generate_xpath_locator(element_info)
            
            if locator:
                locator['priority'] = strategy_config.get('priority', 99)
                locator['stability'] = strategy_config.get('stability', 'unknown')
                
                # Add iframe context to locator if element is in iframe
                if is_in_iframe:
                    locator = self._add_iframe_context(locator, iframe_context)
                
                locators.append(locator)
                
                # Stop if we have enough locators
                if len(locators) >= self.max_locators:
                    break
        
        # Sort by priority
        locators.sort(key=lambda x: x['priority'])
        
        return locators
    
    def generate_role_locator(self, element_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate role-based locator (Playwright getByRole)."""
        role = element_info.get('role') or self._infer_role(element_info.get('tag'))
        aria_label = element_info.get('aria_label')
        
        if not role:
            return None
        
        if aria_label:
            selector = f"role={role}[name='{aria_label}']"
        else:
            selector = f"role={role}"
        
        return {
            'strategy': 'role',
            'selector': selector,
            'playwright': f"page.get_by_role('{role}'" + (f", name='{aria_label}')" if aria_label else ")")
        }
    
    def generate_label_locator(self, element_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate label-based locator (Playwright getByLabel)."""
        label_text = element_info.get('label_text')
        
        if not label_text:
            return None
        
        return {
            'strategy': 'label',
            'selector': f"label={label_text}",
            'playwright': f"page.get_by_label('{label_text}')"
        }
    
    def generate_testid_locator(self, element_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate data-testid locator (Playwright getByTestId)."""
        test_id = element_info.get('data_testid')
        
        if not test_id:
            # Check for other data-* attributes
            attributes = element_info.get('attributes', {})
            for key, value in attributes.items():
                if key.startswith('data-test'):
                    test_id = value
                    break
        
        if not test_id:
            return None
        
        return {
            'strategy': 'data_testid',
            'selector': f"data-testid={test_id}",
            'playwright': f"page.get_by_test_id('{test_id}')"
        }
    
    def generate_placeholder_locator(self, element_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate placeholder-based locator (Playwright getByPlaceholder)."""
        placeholder = element_info.get('placeholder')
        
        if not placeholder:
            return None
        
        return {
            'strategy': 'placeholder',
            'selector': f"placeholder={placeholder}",
            'playwright': f"page.get_by_placeholder('{placeholder}')"
        }
    
    def generate_text_locator(self, element_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate text-based locator (Playwright getByText)."""
        text = element_info.get('text') or ''
        text = text.strip() if text else ''
        
        if not text or len(text) > 100:  # Skip very long text
            return None
        
        return {
            'strategy': 'text',
            'selector': f"text={text}",
            'playwright': f"page.get_by_text('{text}')"
        }
    
    def generate_css_locator(self, element_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate CSS selector (fallback)."""
        tag = element_info.get('tag', 'div')
        element_id = element_info.get('id')
        classes = element_info.get('class', '')
        
        # Build CSS selector
        selector = tag
        
        if element_id:
            selector += f"#{element_id}"
        elif classes:
            class_list = classes.split()
            if class_list:
                selector += '.' + '.'.join(class_list[:3])  # Use first 3 classes
        
        return {
            'strategy': 'css',
            'selector': selector,
            'playwright': f"page.locator('{selector}')"
        }
    
    def generate_xpath_locator(self, element_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate XPath selector (fallback)."""
        tag = element_info.get('tag', 'div')
        element_id = element_info.get('id')
        text = element_info.get('text') or ''
        text = text.strip() if text else ''
        
        # Build XPath
        if element_id:
            xpath = f"//{tag}[@id='{element_id}']"
        elif text and len(text) < 50:
            xpath = f"//{tag}[contains(text(), '{text[:30]}')]"
        else:
            xpath = f"//{tag}"
        
        return {
            'strategy': 'xpath',
            'selector': xpath,
            'playwright': f"page.locator('xpath={xpath}')"
        }
    
    def _infer_role(self, tag: Optional[str]) -> Optional[str]:
        """Infer ARIA role from HTML tag."""
        if not tag:
            return None
        
        role_map = {
            'button': 'button',
            'a': 'link',
            'input': 'textbox',
            'textarea': 'textbox',
            'select': 'combobox',
            'img': 'img',
            'h1': 'heading',
            'h2': 'heading',
            'h3': 'heading',
            'h4': 'heading',
            'h5': 'heading',
            'h6': 'heading',
            'nav': 'navigation',
            'main': 'main',
            'aside': 'complementary',
            'footer': 'contentinfo',
            'header': 'banner',
        }
        
        return role_map.get(tag.lower())
    
    def _add_iframe_context(self, locator: Dict[str, Any], iframe_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add iframe context to a locator.
        
        For elements inside iframes, we need to first locate the iframe,
        then locate the element within that iframe's frame.
        
        Args:
            locator: The base locator dictionary
            iframe_context: Iframe context information
        
        Returns:
            Updated locator with iframe context
        """
        frame_id = iframe_context.get('frame_id')
        frame_name = iframe_context.get('frame_name')
        frame_url = iframe_context.get('frame_url')
        
        # Build iframe selector
        iframe_selector = None
        if frame_id:
            iframe_selector = f"iframe#{frame_id}"
        elif frame_name:
            iframe_selector = f"iframe[name='{frame_name}']"
        elif frame_url:
            # Use src attribute if available
            iframe_selector = f"iframe[src*='{frame_url.split('/')[-1]}']"
        else:
            # Generic iframe selector (less reliable)
            iframe_selector = "iframe"
        
        # Update the locator with iframe context
        locator['iframe_selector'] = iframe_selector
        locator['in_iframe'] = True
        
        # Update Playwright code to include frame locator
        original_playwright = locator.get('playwright', '')
        if original_playwright:
            # Replace 'page.' with frame locator chain
            if frame_id:
                locator['playwright'] = f"page.frame_locator('iframe#{frame_id}').{original_playwright.replace('page.', '')}"
            elif frame_name:
                locator['playwright'] = f"page.frame_locator('iframe[name=\"{frame_name}\"]').{original_playwright.replace('page.', '')}"
            else:
                locator['playwright'] = f"page.frame_locator('{iframe_selector}').{original_playwright.replace('page.', '')}"
        
        return locator
