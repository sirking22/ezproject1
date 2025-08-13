#!/bin/sh
set -e

# Runtime configuration injection for SPA
# Variables expected: VITE_DEMO ("1" or "0"), VITE_API_URL (string)

: "${VITE_DEMO:=1}"
: "${VITE_API_URL:=}"

cat > /usr/share/nginx/html/config.js <<EOF
// Generated at container start. Do not edit.
window.__APP_CONFIG__ = {
  VITE_DEMO: "${VITE_DEMO}",
  VITE_API_URL: "${VITE_API_URL}"
};
EOF

echo "[entrypoint] Wrote /usr/share/nginx/html/config.js (VITE_DEMO=$VITE_DEMO)"


