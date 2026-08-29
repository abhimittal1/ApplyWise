const SAFE_PROTOCOLS = new Set(['http:', 'https:', 'mailto:']);

/**
 * Sanitizes URLs to prevent XSS attacks via javascript:, data:, or other dangerous URI schemes.
 * Allows safe protocols (http, https, mailto) and safe relative paths (/path, #hash).
 * Returns undefined if the URL is invalid or uses an unsafe protocol.
 */
export function sanitizeUrl(url: string | null | undefined): string | undefined {
  if (!url) return undefined;

  const trimmed = url.trim();
  if (!trimmed) return undefined;

  // Safe relative paths
  if (trimmed.startsWith('/') || trimmed.startsWith('#')) {
    // Prevent protocol-relative URLs like '//malicious.com'
    if (trimmed.startsWith('//')) {
      return undefined;
    }
    return trimmed;
  }

  try {
    const parsed = new URL(trimmed, window.location.origin);
    if (SAFE_PROTOCOLS.has(parsed.protocol)) {
      return trimmed;
    }
  } catch {
    return undefined;
  }

  return undefined;
}
