#!/usr/bin/env bash
export NVM_DIR="$HOME/.nvm"
\. "$NVM_DIR/nvm.sh"
echo "PATH=$PATH"
which claude
claude --version
