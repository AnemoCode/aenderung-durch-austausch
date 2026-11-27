#!/usr/bin/env bash
# Builds static/css/tailwind.css with the Tailwind standalone CLI, so no Node or
# npm is needed. The binary is downloaded once, checked against the official
# checksum and cached in .bin/ (or $TAILWIND_BIN_DIR).
#
# Usage:
#   scripts/tailwind.sh            build once (minified)
#   scripts/tailwind.sh --watch    rebuild whenever a template changes
#   scripts/tailwind.sh --install  only download the binary
set -euo pipefail

VERSION=3.4.17
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BIN_DIR="${TAILWIND_BIN_DIR:-$ROOT/.bin}"

# Checksums from the release's sha256sums.txt on GitHub.
case "$(uname -s)-$(uname -m)" in
  Linux-x86_64)
    PLATFORM=linux-x64
    SHA256=7d24f7fa191d2193b78cd5f5a42a6093e14409521908529f42d80b11fde1f1d4 ;;
  Linux-aarch64 | Linux-arm64)
    PLATFORM=linux-arm64
    SHA256=69b1378b8133192d7d2feb12a116fa12d035594f58db3eff215879e4ad8cf39b ;;
  Darwin-arm64)
    PLATFORM=macos-arm64
    SHA256=a1d0c7985759accca0bf12e51ac1dcbf0f6cf2fffb62e6e0f62d091c477a10a3 ;;
  Darwin-x86_64)
    PLATFORM=macos-x64
    SHA256=6cbdad74be776c087ffa5e9a057512c54898f9fe8828d3362212dfe32fc933a3 ;;
  *)
    echo "tailwind.sh: unsupported platform $(uname -s)-$(uname -m)" >&2
    exit 1 ;;
esac

BIN="$BIN_DIR/tailwindcss-$VERSION-$PLATFORM"

sha256_of() {
  if command -v sha256sum >/dev/null; then
    sha256sum "$1" | cut -d' ' -f1
  else
    shasum -a 256 "$1" | cut -d' ' -f1
  fi
}

if [ ! -x "$BIN" ]; then
  mkdir -p "$BIN_DIR"
  echo "Downloading Tailwind CSS $VERSION ($PLATFORM)..."
  curl -fsSL --retry 3 --connect-timeout 20 -o "$BIN.part" \
    "https://github.com/tailwindlabs/tailwindcss/releases/download/v$VERSION/tailwindcss-$PLATFORM"
  if [ "$(sha256_of "$BIN.part")" != "$SHA256" ]; then
    rm -f "$BIN.part"
    echo "tailwind.sh: checksum mismatch for the downloaded binary" >&2
    exit 1
  fi
  chmod +x "$BIN.part"
  mv "$BIN.part" "$BIN"
fi

if [ "${1:-}" = "--install" ]; then
  exit 0
fi

cd "$ROOT"
exec "$BIN" -c tailwind.config.js -i tailwind/input.css -o static/css/tailwind.css --minify "$@"
