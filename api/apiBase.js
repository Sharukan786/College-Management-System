const trimTrailingSlash = (value) => String(value || '').replace(/\/+$/, '');

const configuredBaseRaw = trimTrailingSlash(
  import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_BASE
);

function normalizeHostBase(value) {
  if (!value) return '';
  return value.endsWith('/api') ? value.slice(0, -4) : value;
}

function resolveHostBase() {
  const configuredBase = normalizeHostBase(configuredBaseRaw);
  if (configuredBase) return configuredBase;

  // Render static rewrite for /api is unreliable in this deployment,
  // so use direct backend host in production by default.
  if (!import.meta.env.DEV && typeof window !== 'undefined') {
    if (window.location.hostname === 'cms1-weof.onrender.com') {
      return 'https://cms-x82g.onrender.com';
    }
  }

  return '';
}

const hostBase = resolveHostBase();

export const API_BASE = hostBase ? `${trimTrailingSlash(hostBase)}/api` : '/api';

export function buildApiUrl(path) {
  const normalizedPath = String(path || '').startsWith('/') ? path : `/${path}`;
  return `${API_BASE}${normalizedPath}`;
}
