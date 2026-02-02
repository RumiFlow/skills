from mcp.server.fastmcp import FastMCP
from playwright.sync_api import sync_playwright
import os
import time
from dotenv import load_dotenv

# Setup paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SHARED_ENV_PATH = os.path.join(SCRIPT_DIR, "..", "..", ".env")
ASSETS_DIR = os.path.join(SCRIPT_DIR, "..", "assets")
load_dotenv(SHARED_ENV_PATH)

# Ensure assets dir exists
os.makedirs(ASSETS_DIR, exist_ok=True)

# Configuration
WILMA_USER = os.getenv("WILMA_USER")
WILMA_PASS = os.getenv("WILMA_PASS")
WILMA_URL = os.getenv("WILMA_URL")

mcp = FastMCP("WilmaConnect")

def login_and_fetch(action_callback):
    """
    Spins up a headless browser, logs in, and runs the callback.
    """
    if not all([WILMA_USER, WILMA_PASS, WILMA_URL]):
        raise ValueError("Missing Wilma credentials in .env")

    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        try:
            # 1. Go to Wilma URL
            print(f"Navigating to {WILMA_URL}...")
            page.goto(WILMA_URL)
            
            # 2. Handle Login
            # Wait for username field. Selector might vary.
            # Common Wilma/Visma selectors:
            # - #login-username / #login-password
            # - input[name="Login"]
            
            try:
                # Try standard Wilma login form first
                page.wait_for_selector('input[type="text"], input[name="Login"]', timeout=5000)
                page.fill('input[type="text"], input[name="Login"]', WILMA_USER)
                page.fill('input[type="password"]', WILMA_PASS)
                page.click('input[type="submit"], button[type="submit"]')
            except Exception:
                print("Standard form not found immediately, checking for redirects or alternative login...")
                # Sometimes there's a 'Log in' link first
                if page.get_by_text("Kirjaudu").count() > 0:
                    page.get_by_text("Kirjaudu").click()
                
                # Wait again for inputs
                page.wait_for_selector('input[type="text"]', timeout=10000)
                page.fill('input[type="text"]', WILMA_USER)
                page.fill('input[type="password"]', WILMA_PASS)
                # Press Enter to submit
                page.press('input[type="password"]', 'Enter')

            # 3. Wait for Homepage
            print("Waiting for homepage...")
            page.wait_for_load_state("networkidle")
            
            # Check title
            title = page.title()
            if "Wilma" in title and "Login" not in title and "Kirjaudu" not in title:
                print(f"Login successful. Title: {title}")
            else:
                 # Try one last wait for a known element if title is ambiguous
                 try:
                     page.wait_for_selector('a[href*="logout"]', timeout=5000)
                 except:
                     raise Exception(f"Login verification failed. Title: {title}, URL: {page.url}")
            
            # Check for specific elements to confirm login
            # e.g., title contains "Wilma"
            
            # 4. Perform Action
            return action_callback(page)

        except Exception as e:
            # Take screenshot on failure
            timestamp = int(time.time())
            screenshot_path = os.path.join(ASSETS_DIR, f"error_{timestamp}.png")
            html_path = os.path.join(ASSETS_DIR, f"error_{timestamp}.html")
            
            page.screenshot(path=screenshot_path)
            with open(html_path, "w") as f:
                f.write(page.content())
                
            print(f"Error at URL: {page.url}")
            print(f"Page Title: {page.title()}")
            print(f"Error screenshot saved to {screenshot_path}")
            print(f"Page HTML saved to {html_path}")
            raise e
        finally:
            browser.close()

@mcp.tool()
def get_homepage_title():
    """Logs in and returns the page title to verify connection."""
    def action(page):
        return page.title()
    
    try:
        return login_and_fetch(action)
    except Exception as e:
        return f"Login failed: {str(e)}"

@mcp.tool()
def list_messages(limit: int = 10):
    """Lists recent messages from the inbox."""
    def action(page):
        # Navigate to messages
        # Usually /messages/index
        page.click('a[href*="messages"]', timeout=5000)
        page.wait_for_selector('.table-condensed', timeout=10000) # Message table
        
        # Scrape rows
        messages = []
        rows = page.query_selector_all('tr.message-row, tr.new-message-row') # Hypothetical classes
        
        # If classes unknown, just iterate table rows
        if not rows:
            rows = page.query_selector_all('tbody tr')

        for i, row in enumerate(rows):
            if i >= limit: break
            text = row.inner_text().replace('\n', ' | ')
            messages.append(text)
            
        return "\n".join(messages)

    try:
        return login_and_fetch(action)
    except Exception as e:
        return f"Error listing messages: {str(e)}"

@mcp.tool()
def get_news_for_all_children(limit_per_child: int = 5):
    """
    Iterates through all linked children/roles, goes to their 'Tiedotteet' (News) page,
    and summarizes the latest news items.
    """
    def action(page):
        # 1. Discover Children/Roles
        # Look for links that start with /! and are likely in the navbar dropdown
        # We assume we are on the homepage.
        
        # We wait for the dropdown to be present (it might be hidden behind a button)
        # Usually checking for a[href^="/!"] is enough.
        role_links = page.query_selector_all('a[href^="/!"]')
        
        children = []
        seen_ids = set()
        
        for link in role_links:
            href = link.get_attribute('href')
            name = link.inner_text().strip()
            
            # Filter out duplicates or irrelevant links
            # The ID is the part after /!
            role_id = href.split('!')[1].split('/')[0] # handle /!123 and /!123/
            
            if role_id not in seen_ids and name:
                seen_ids.add(role_id)
                children.append({"name": name, "href": href, "id": role_id})
        
        results = []
        
        if not children:
            # Maybe we are already on a child's page and have no other roles?
            # Or the selector failed.
            # Let's try to just get news for current view.
            results.append("No role switcher found, fetching news for current view...")
            children = [{"name": "Current", "href": None}]

        print(f"Found children: {[c['name'] for c in children]}")

        for child in children:
            child_name = child['name'].split()[0] # First name only
            
            # Navigate to child's context if needed
            if child['href']:
                print(f"Switching to {child['name']} ({child['href']})...")
                page.goto(WILMA_URL.rstrip('/') + child['href'])
                page.wait_for_load_state("networkidle")
            
            # Navigate to News (Tiedotteet)
            # Try finding the link first, usually href="/news" or similar
            try:
                # Common selectors for 'Tiedotteet'
                page.click('a[href*="news"], a:text("Tiedotteet")', timeout=5000)
                page.wait_for_load_state("networkidle")
            except:
                results.append(f"[{child_name}] Could not find 'Tiedotteet' link.")
                continue

            # Scrape News Items
            # Container: .news-item or .panel
            # We look for something containing dates and text.
            
            news_items = page.query_selector_all('.news-item, .panel-news') # Hypothetical classes
            
            # Fallback: look for common panel structures if specific classes fail
            if not news_items:
                news_items = page.query_selector_all('.panel')

            child_news = []
            for item in news_items[:limit_per_child]:
                try:
                    title_el = item.query_selector('h2, h3, .panel-heading')
                    date_el = item.query_selector('.timestamp, .date, small')
                    content_el = item.query_selector('.content, .panel-body')
                    
                    title = title_el.inner_text().strip() if title_el else "No Title"
                    date = date_el.inner_text().strip() if date_el else ""
                    content = content_el.inner_text().strip()[:200].replace('\n', ' ') + "..." if content_el else ""
                    
                    # Filter out non-news panels (like 'Upcoming exams' or 'Old announcements')
                    if not title or "kokeet" in title.lower() or "vanhat tiedotteet" in title.lower(): 
                        continue

                    child_news.append(f"[{child_name}] {date}: {title} - {content}")
                except:
                    continue
            
            if child_news:
                results.extend(child_news)
            else:
                results.append(f"[{child_name}] No recent news found.")
                
        return "\n".join(results)

    try:
        return login_and_fetch(action)
    except Exception as e:
        return f"Error fetching news: {str(e)}"

if __name__ == "__main__":
    mcp.run()
