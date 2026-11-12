#!/usr/bin/env bash
set -e

export NVM_DIR="$HOME/.nvm"
if [ ! -s "$NVM_DIR/nvm.sh" ]; then
  curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
fi
\. "$NVM_DIR/nvm.sh"

nvm install --lts
echo "node: $(node --version)"
echo "npm: $(npm --version)"

npm install -g @anthropic-ai/claude-code

echo "CLAUDE_INSTALL_DONE"
claude --version
