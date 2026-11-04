import ipaddress
import socket
from urllib.parse import urlparse

class UnsafeURLError(ValueError):
    pass

def validate_public_url(url: str) -> str:
    """Allow public HTTP(S) URLs only; reject private/loopback/link-local targets."""
    parsed = urlparse(url.strip())
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise UnsafeURLError("Enter a complete public http:// or https:// URL.")
    if parsed.username or parsed.password:
        raise UnsafeURLError("URLs containing embedded credentials are not allowed.")
    host = parsed.hostname.rstrip(".").lower()
    if host in {"localhost", "localhost.localdomain"} or host.endswith(".local"):
        raise UnsafeURLError("Local hostnames are not allowed.")
    try:
        addresses = {ipaddress.ip_address(host)}
    except ValueError:
        try:
            addresses = {ipaddress.ip_address(item[4][0]) for item in socket.getaddrinfo(host, None)}
        except socket.gaierror as exc:
            raise UnsafeURLError("The hostname could not be resolved.") from exc
    for address in addresses:
        if not address.is_global:
            raise UnsafeURLError("Private, loopback, link-local, and reserved network destinations are blocked.")
    return url.strip()
