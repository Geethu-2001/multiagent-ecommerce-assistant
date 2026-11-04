from functools import lru_cache
from langchain_ollama import ChatOllama
from .config import get_settings

@lru_cache(maxsize=1)
def get_llm() -> ChatOllama:
    settings = get_settings()
    if settings.llm_provider.lower() != "ollama":
        raise RuntimeError("This repository currently implements Ollama as its configured provider.")
    return ChatOllama(
        model=settings.ollama_model,
        base_url=settings.ollama_base_url,
        temperature=0,
        num_predict=900,
    )

def check_ollama() -> tuple[bool, str]:
    """Check local Ollama and configured model without downloading anything."""
    import httpx
    settings = get_settings()
    try:
        response = httpx.get(f"{settings.ollama_base_url.rstrip('/')}/api/tags", timeout=3.0)
        response.raise_for_status()
        names = {m.get("name", "") for m in response.json().get("models", [])}
        if settings.ollama_model not in names:
            # Some Ollama responses include a digest tag; compare the model's base name too.
            base = settings.ollama_model.split(":", 1)[0]
            if not any(name.split(":", 1)[0] == base for name in names):
                return False, f"Model '{settings.ollama_model}' is not present. Run: ollama pull {settings.ollama_model}"
        return True, f"Ollama is reachable; configured model: {settings.ollama_model}"
    except Exception as exc:
        return False, f"Cannot reach Ollama at {settings.ollama_base_url}. Start Ollama and check the URL. ({type(exc).__name__})"
