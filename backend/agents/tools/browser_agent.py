"""
Browser automation agent using Playwright.
Can visit URLs, scrape content, take screenshots, fill forms, click buttons.
"""

from typing import Dict, Any, List
from backend.agents.base_agent import BaseAgent, AgentValidationError
from backend.agents.registry import AgentRegistry


@AgentRegistry.register
class BrowserAgent(BaseAgent):
    """
    Browser automation for web scraping and testing.
    Uses Playwright for headless browser control.
    """
    
    def validate_input(self, context: Dict[str, Any]) -> bool:
        super().validate_input(context)
        
        if "action" not in context:
            raise AgentValidationError(f"{self.name}: 'action' required")
        
        valid_actions = ["navigate", "screenshot", "scrape", "fill_form", "click", "extract"]
        if context["action"] not in valid_actions:
            raise AgentValidationError(f"{self.name}: Invalid action. Must be one of {valid_actions}")
        
        if context["action"] in ["navigate", "screenshot", "scrape"] and "url" not in context:
            raise AgentValidationError(f"{self.name}: 'url' required for {context['action']}")
        
        return True
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute browser automation.
        
        Actions:
        - navigate: Go to URL and return page content
        - screenshot: Take screenshot of URL
        - scrape: Extract specific data from page
        - fill_form: Fill and submit form
        - click: Click element
        - extract: Extract text, links, or images
        """
        action = context["action"]
        url = context.get("url")
        
        try:
            from playwright.async_api import async_playwright
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                if action == "navigate":
                    await page.goto(url)
                    content = await page.content()
                    title = await page.title()
                    
                    result = {
                        "url": url,
                        "title": title,
                        "html": content[:5000],  # First 5000 chars
                        "success": True
                    }
                
                elif action == "screenshot":
                    await page.goto(url)
                    screenshot_bytes = await page.screenshot(full_page=True)
                    
                    # Save to file
                    import base64
                    screenshot_b64 = base64.b64encode(screenshot_bytes).decode()
                    
                    result = {
                        "url": url,
                        "screenshot": screenshot_b64,
                        "success": True
                    }
                
                elif action == "scrape":
                    await page.goto(url)
                    selector = context.get("selector", "body")
                    
                    # Extract text content
                    elements = await page.query_selector_all(selector)
                    texts = []
                    for elem in elements:
                        text = await elem.inner_text()
                        texts.append(text)
                    
                    result = {
                        "url": url,
                        "selector": selector,
                        "elements_found": len(texts),
                        "content": texts,
                        "success": True
                    }
                
                elif action == "extract":
                    await page.goto(url)
                    extract_type = context.get("extract_type", "text")
                    
                    if extract_type == "links":
                        links = await page.query_selector_all("a")
                        hrefs = [await link.get_attribute("href") for link in links]
                        result = {"links": hrefs, "count": len(hrefs)}
                    
                    elif extract_type == "images":
                        images = await page.query_selector_all("img")
                        srcs = [await img.get_attribute("src") for img in images]
                        result = {"images": srcs, "count": len(srcs)}
                    
                    else:  # text
                        text = await page.inner_text("body")
                        result = {"text": text[:10000], "length": len(text)}
                    
                    result["success"] = True
                
                await browser.close()
                
                result["_tokens_used"] = 0  # No LLM calls
                result["_model_used"] = "playwright"
                
                return result
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "_tokens_used": 0,
                "_model_used": "playwright"
            }
