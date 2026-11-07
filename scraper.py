from bs4 import BeautifulSoup
import requests


# Standard headers to fetch a website
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}


NOISE_TAGS = ["script", "style", "img", "input", "nav", "footer", "header",
              "aside", "noscript", "svg", "iframe", "form"]

# If a plain fetch yields less text than this, assume the page is built by
# JavaScript (or blocks simple clients) and retry with a real browser.
MIN_TEXT_CHARS = 200


def _fetch_html_requests(url, timeout=10):
    response = requests.get(url, headers=headers, timeout=timeout)
    response.raise_for_status()
    return response.content


def _fetch_html_browser(url, timeout=20):
    """
    Render the page in headless Chromium so JavaScript-driven content is present.
    Requires:  uv pip install playwright  &&  playwright install chromium
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as e:
        raise RuntimeError(
            "This page needs a browser to render. Install it with:\n"
            "  uv pip install playwright && playwright install chromium"
        ) from e

    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            page = browser.new_page(user_agent=headers["User-Agent"])
            page.goto(url, wait_until="domcontentloaded", timeout=timeout * 1000)
            try:
                # Give client-side rendering a chance to finish
                page.wait_for_load_state("networkidle", timeout=timeout * 1000)
            except Exception:
                pass  # chatty pages never go idle; use whatever has rendered
            return page.content()
        finally:
            browser.close()


def _extract(html):
    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.get_text(strip=True) if soup.title else "No title found"
    root = soup.find("main") or soup.find("article") or soup.body
    if not root:
        return title, ""
    for irrelevant in root(NOISE_TAGS):
        irrelevant.decompose()
    return title, root.get_text(separator="\n", strip=True)


def fetch_website_contents(url, max_chars=2_000, use_browser="auto"):
    """
    Return the title and contents of the website at the given url,
    truncated to max_chars.

    use_browser:
      "auto"  - try a plain request first; fall back to a headless browser if the
                request fails or returns almost no text (JS-rendered / bot-blocked)
      True    - always use the headless browser
      False   - never use the browser
    """
    title, text = "No title found", ""
    if use_browser is not True:
        try:
            title, text = _extract(_fetch_html_requests(url))
        except requests.RequestException:
            if use_browser is False:
                raise
    if use_browser is True or (use_browser == "auto" and len(text) < MIN_TEXT_CHARS):
        title, text = _extract(_fetch_html_browser(url))
    return (title + "\n\n" + text)[:max_chars]


def fetch_website_links(url):
    """
    Return the links on the webiste at the given url
    I realize this is inefficient as we're parsing twice! This is to keep the code in the lab simple.
    Feel free to use a class and optimize it!
    """
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")
    links = [link.get("href") for link in soup.find_all("a")]
    return [link for link in links if link]
