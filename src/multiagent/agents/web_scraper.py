from urllib.parse import urljoin
import httpx
from bs4 import BeautifulSoup
from ..config import get_settings
from ..tools.web_security import validate_public_url


def fetch_webpage(url: str) -> dict:
    settings = get_settings()
    try:
        current = validate_public_url(url)
        with httpx.Client(timeout=settings.app_http_timeout, follow_redirects=False, headers={"User-Agent": "MultiAgentResearchAssistant/1.0"}) as client:
            for _ in range(4):
                response = client.get(current)
                if response.is_redirect:
                    location = response.headers.get("location")
                    if not location:
                        return {"ok": False, "error": "Redirect response did not include a location.", "url": current}
                    current = validate_public_url(urljoin(current, location))
                    continue
                response.raise_for_status()
                if "text/html" not in response.headers.get("content-type", "").lower():
                    return {"ok": False, "error": "The URL did not return an HTML page.", "url": current}
                if len(response.content) > settings.app_max_web_bytes:
                    return {"ok": False, "error": "The webpage exceeds the configured size limit.", "url": current}
                soup = BeautifulSoup(response.text, "html.parser")
                for node in soup(["script", "style", "noscript", "svg", "nav", "footer"]):
                    node.decompose()
                title = soup.title.get_text(" ", strip=True) if soup.title else "Untitled page"
                headings = [h.get_text(" ", strip=True) for h in soup.find_all(["h1", "h2", "h3"])][:30]
                text = "\n".join(line.strip() for line in soup.get_text("\n").splitlines() if line.strip())
                links = [{"text": a.get_text(" ", strip=True)[:120], "url": urljoin(current, a.get("href", ""))} for a in soup.find_all("a", href=True)[:30]]
                return {"ok": True, "url": current, "title": title, "headings": headings, "content": text[:settings.app_max_web_chars], "links": links}
            return {"ok": False, "error": "Too many redirects.", "url": current}
    except UnsafeURLError as exc:
        return {"ok": False, "error": str(exc), "url": url}
    except httpx.HTTPStatusError as exc:
        return {"ok": False, "error": f"The website returned HTTP {exc.response.status_code}.", "url": url}
    except (httpx.TimeoutException, httpx.RequestError) as exc:
        return {"ok": False, "error": f"Could not retrieve the webpage ({type(exc).__name__}).", "url": url}
