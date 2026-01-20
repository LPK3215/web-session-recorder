"""Browser controller for launching and managing Playwright browsers."""

from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from typing import Optional, Dict, Any
import logging

from app.core.config import config

logger = logging.getLogger(__name__)


class BrowserController:
    """Controller for managing Playwright browser instances."""
    
    def __init__(self):
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self._window_width: Optional[int] = None
        self._window_height: Optional[int] = None
    
    async def launch_browser(
        self,
        browser_type: str = "chrome",
        headless: bool = False,
        use_local: bool = True,
        window_width: Optional[int] = None,
        window_height: Optional[int] = None
    ) -> Browser:
        """
        Launch a browser instance.
        
        Args:
            browser_type: Type of browser (chrome, edge, firefox, chromium)
            headless: Whether to run in headless mode
            use_local: Whether to use locally installed browser
            window_width: Browser window width (optional)
            window_height: Browser window height (optional)
        
        Returns:
            Browser instance
        """
        if not self.playwright:
            self.playwright = await async_playwright().start()
        
        # Get launch options from config
        launch_args = config.get('browser', 'browser.launch.args', [])
        timeout = config.get('browser', 'browser.launch.timeout', 30000)
        slow_mo = config.get('browser', 'browser.launch.slow_mo', 0)
        
        # Remove --start-maximized if window size is specified
        if window_width and window_height:
            launch_args = [arg for arg in launch_args if arg != '--start-maximized']
            # Add window size argument
            launch_args.append(f'--window-size={window_width},{window_height}')
        
        launch_options = {
            'headless': headless,
            'args': launch_args,
            'timeout': timeout,
            'slow_mo': slow_mo
        }
        
        # Launch browser based on type
        try:
            if browser_type == "chrome" and use_local:
                self.browser = await self.playwright.chromium.launch(
                    channel="chrome",
                    **launch_options
                )
                logger.info("Launched local Chrome browser")
            elif browser_type == "edge" and use_local:
                self.browser = await self.playwright.chromium.launch(
                    channel="msedge",
                    **launch_options
                )
                logger.info("Launched local Edge browser")
            elif browser_type == "firefox":
                self.browser = await self.playwright.firefox.launch(**launch_options)
                logger.info("Launched Firefox browser")
            else:
                # Default to Chromium
                self.browser = await self.playwright.chromium.launch(**launch_options)
                logger.info("Launched Chromium browser")
            
            return self.browser
            
        except Exception as e:
            logger.error(f"Error launching browser: {e}")
            raise
    
    async def create_context(
        self,
        incognito: bool = True,
        user_data_dir: Optional[str] = None,
        window_width: Optional[int] = None,
        window_height: Optional[int] = None
    ) -> BrowserContext:
        """
        Create a browser context.
        
        Args:
            incognito: Whether to use incognito mode
            user_data_dir: Path to user data directory (for persistent context)
            window_width: Browser window width (optional)
            window_height: Browser window height (optional)
        
        Returns:
            BrowserContext instance
        """
        if not self.browser:
            raise RuntimeError("Browser not launched. Call launch_browser() first.")
        
        # Get context options from config
        default_viewport = config.get('browser', 'browser.context.viewport', {'width': 1920, 'height': 1080})
        
        # Use custom window size if provided, otherwise use config default
        viewport = {
            'width': window_width if window_width else default_viewport.get('width', 1920),
            'height': window_height if window_height else default_viewport.get('height', 1080)
        }
        
        locale = config.get('browser', 'browser.context.locale', 'zh-CN')
        timezone_id = config.get('browser', 'browser.context.timezone_id', 'Asia/Shanghai')
        accept_downloads = config.get('browser', 'browser.context.accept_downloads', True)
        ignore_https_errors = config.get('browser', 'browser.context.ignore_https_errors', True)
        
        context_options = {
            'viewport': viewport,
            'locale': locale,
            'timezone_id': timezone_id,
            'accept_downloads': accept_downloads,
            'ignore_https_errors': ignore_https_errors
        }
        
        try:
            self.context = await self.browser.new_context(**context_options)
            logger.info(f"Created browser context (incognito={incognito}, viewport={viewport['width']}x{viewport['height']})")
            
            # Store window size for later use
            self._window_width = viewport['width']
            self._window_height = viewport['height']
            
            return self.context
            
        except Exception as e:
            logger.error(f"Error creating context: {e}")
            raise
    
    async def navigate(self, url: Optional[str] = None) -> Page:
        """
        Navigate to a URL or create a blank page.
        
        Args:
            url: URL to navigate to (None for blank page)
        
        Returns:
            Page instance
        """
        if not self.context:
            raise RuntimeError("Context not created. Call create_context() first.")
        
        try:
            self.page = await self.context.new_page()
            
            # Set window size if specified
            if hasattr(self, '_window_width') and hasattr(self, '_window_height'):
                try:
                    # Set viewport size (this is the content area)
                    await self.page.set_viewport_size({
                        'width': self._window_width,
                        'height': self._window_height
                    })
                    logger.info(f"Set viewport size to {self._window_width}x{self._window_height}")
                except Exception as e:
                    logger.warning(f"Could not set viewport size: {e}")
            
            if url:
                await self.page.goto(url, wait_until='domcontentloaded', timeout=30000)
                logger.info(f"Navigated to: {url}")
            else:
                await self.page.goto('about:blank')
                logger.info("Created blank page")
            
            return self.page
            
        except Exception as e:
            logger.error(f"Error navigating: {e}")
            raise
    
    async def inject_capturer(self, page: Page, script_content: str) -> None:
        """
        Inject JavaScript capturer script into a page.
        
        Args:
            page: Page to inject script into
            script_content: JavaScript code to inject
        """
        try:
            await page.add_init_script(script_content)
            logger.debug("Injected capturer script into page")
        except Exception as e:
            logger.error(f"Error injecting script: {e}")
            raise
    
    async def close_browser(self) -> None:
        """Close the browser and cleanup resources."""
        try:
            if self.page:
                await self.page.close()
                self.page = None
            
            if self.context:
                await self.context.close()
                self.context = None
            
            if self.browser:
                await self.browser.close()
                self.browser = None
            
            if self.playwright:
                await self.playwright.stop()
                self.playwright = None
            
            logger.info("Browser closed successfully")
            
        except Exception as e:
            logger.error(f"Error closing browser: {e}")
            raise
    
    def is_running(self) -> bool:
        """Check if browser is currently running."""
        return self.browser is not None and self.browser.is_connected()
