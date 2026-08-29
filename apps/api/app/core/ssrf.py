import ipaddress
import socket
from urllib.parse import urljoin, urlparse

import httpx

MAX_RESPONSE_SIZE = 5 * 1024 * 1024  # 5 MB
MAX_REDIRECTS = 3
FETCH_TIMEOUT = 10.0
ALLOWED_PORTS = {80, 443}
FORBIDDEN_HOSTNAMES = {
    "localhost",
    "127.0.0.1",
    "::1",
    "0.0.0.0",
    "metadata.google.internal",
    "instance-data",
    "metadata",
}

# Blocked IP networks for defense-in-depth
BLOCKED_NETWORKS = [
    ipaddress.ip_network("0.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("100.64.0.0/10"),  # Carrier-grade NAT
    ipaddress.ip_network("127.0.0.0/8"),    # Loopback
    ipaddress.ip_network("169.254.0.0/16"),  # Link-local / Cloud metadata
    ipaddress.ip_network("172.16.0.0/12"),  # Private RFC1918
    ipaddress.ip_network("192.0.0.0/24"),   # IETF Protocol Assignments
    ipaddress.ip_network("192.0.2.0/24"),   # TEST-NET-1
    ipaddress.ip_network("192.168.0.0/16"), # Private RFC1918
    ipaddress.ip_network("198.18.0.0/15"),  # Benchmarking
    ipaddress.ip_network("198.51.100.0/24"),# TEST-NET-2
    ipaddress.ip_network("203.0.113.0/24"), # TEST-NET-3
    ipaddress.ip_network("224.0.0.0/4"),    # Multicast
    ipaddress.ip_network("240.0.0.0/4"),    # Reserved
    ipaddress.ip_network("255.255.255.255/32"),
    # IPv6 blocked ranges
    ipaddress.ip_network("::/128"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("::ffff:0:0/96"),  # IPv4-mapped
    ipaddress.ip_network("100::/64"),       # Discard prefix
    ipaddress.ip_network("2001:db8::/32"),  # Documentation
    ipaddress.ip_network("fc00::/7"),       # Unique Local Address (private)
    ipaddress.ip_network("fe80::/10"),      # Link-local unicast
    ipaddress.ip_network("ff00::/8"),       # Multicast
]


class SSRFValidationError(ValueError):
    """Raised when a URL or IP fails SSRF security validation."""
    pass


def is_ip_allowed(ip_str: str) -> bool:
    """
    Verify that an IP address is a public, non-reserved, non-private routable address.
    Blocks loopback, RFC1918, link-local, cloud metadata (169.254.169.254), CGNAT, and IPv6 equivalents.
    """
    try:
        ip = ipaddress.ip_address(ip_str)

        # Handle IPv4-mapped IPv6 addresses (e.g. ::ffff:127.0.0.1)
        if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped:
            ip = ip.ipv4_mapped

        if (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_multicast
            or ip.is_reserved
            or ip.is_unspecified
        ):
            return False

        for blocked_net in BLOCKED_NETWORKS:
            # Match IPv4 to IPv4 and IPv6 to IPv6
            if ip.version == blocked_net.version and ip in blocked_net:
                return False

        return True
    except ValueError:
        return False


def validate_url_for_ssrf(url: str) -> list[str]:
    """
    Validate that a URL scheme is http/https, port is 80/443, and its host does not resolve
    to private, loopback, link-local, or cloud metadata IP addresses.
    Returns list of verified IP addresses for the hostname.
    """
    if not url or len(url) > 2048:
        raise SSRFValidationError("Invalid URL length (must be 1-2048 characters)")

    parsed = urlparse(url)
    scheme = parsed.scheme.lower()
    if scheme not in ("http", "https"):
        raise SSRFValidationError(f"Invalid URL protocol: '{parsed.scheme}'. Only http and https are permitted.")

    # Validate destination port
    port = parsed.port
    if port is not None and port not in ALLOWED_PORTS:
        raise SSRFValidationError(f"Invalid URL port: {port}. Only standard HTTP/HTTPS ports (80, 443) are allowed.")

    hostname = parsed.hostname
    if not hostname:
        raise SSRFValidationError("URL must include a valid hostname")

    # Reject standard loopback and metadata hostnames immediately
    if hostname.lower() in FORBIDDEN_HOSTNAMES or hostname.lower().endswith(".internal") or hostname.lower().endswith(".local"):
        raise SSRFValidationError(f"Access to restricted hostname '{hostname}' is forbidden.")

    # Resolve all DNS records for hostname
    try:
        addr_info = socket.getaddrinfo(hostname, port or (443 if scheme == "https" else 80), proto=socket.IPPROTO_TCP)
        if not addr_info:
            raise SSRFValidationError("Could not resolve host IP address")

        resolved_ips: list[str] = []
        for entry in addr_info:
            sockaddr = entry[4]
            ip_str = sockaddr[0]
            if not is_ip_allowed(ip_str):
                raise SSRFValidationError(f"Access to restricted or internal network address ({ip_str}) is prohibited.")
            if ip_str not in resolved_ips:
                resolved_ips.append(ip_str)

        return resolved_ips
    except socket.gaierror as e:
        raise SSRFValidationError(f"Failed to resolve host '{hostname}': {e}")


async def safe_fetch_url(url: str) -> str:
    """
    Safely fetch a URL with SSRF checks, redirect loop protection,
    port restriction, per-hop IP re-validation, and response streaming size bounds.
    """
    current_url = url
    for _ in range(MAX_REDIRECTS + 1):
        # Validate URL and resolve DNS, verifying all resolved IPs are public
        validate_url_for_ssrf(current_url)

        async with httpx.AsyncClient(
            timeout=httpx.Timeout(FETCH_TIMEOUT, connect=5.0),
            follow_redirects=False,
            headers={"User-Agent": "CareerOS-Bot/1.0 (Job Ingestion; Security Verified)"},
        ) as client:
            async with client.stream("GET", current_url) as resp:
                # Check for redirect and validate next hop target
                if resp.status_code in (301, 302, 303, 307, 308):
                    location = resp.headers.get("Location")
                    if not location:
                        raise SSRFValidationError("Redirect response missing Location header")
                    current_url = urljoin(current_url, location)
                    continue

                resp.raise_for_status()

                # Enforce body size limit from Content-Length header if present
                content_length = resp.headers.get("Content-Length")
                if content_length:
                    try:
                        if int(content_length) > MAX_RESPONSE_SIZE:
                            raise SSRFValidationError(f"Remote content exceeds maximum permitted size ({MAX_RESPONSE_SIZE} bytes)")
                    except ValueError:
                        pass

                # Stream and buffer response chunks with hard byte counter
                chunks = []
                total_bytes = 0
                async for chunk in resp.aiter_bytes():
                    total_bytes += len(chunk)
                    if total_bytes > MAX_RESPONSE_SIZE:
                        raise SSRFValidationError(f"Response body exceeds maximum allowed size ({MAX_RESPONSE_SIZE} bytes)")
                    chunks.append(chunk)

                body_bytes = b"".join(chunks)
                encoding = resp.encoding or "utf-8"
                try:
                    return body_bytes.decode(encoding)
                except Exception:
                    return body_bytes.decode("utf-8", errors="replace")

    raise SSRFValidationError(f"Too many redirects (limit: {MAX_REDIRECTS})")
