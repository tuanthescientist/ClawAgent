#!/bin/bash

# ClawAgent GitHub Push Script
# This script pushes the local repository to GitHub

echo "🚀 Pushing ClawAgent to GitHub..."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if git remote is configured
if ! git remote get-url origin &> /dev/null; then
    echo -e "${YELLOW}Setting up GitHub remote...${NC}"
    git remote add origin https://github.com/tuanthescientist/ClawAgent.git
fi

echo -e "${YELLOW}Current branch:${NC}"
git branch

echo ""
echo -e "${YELLOW}Pushing to GitHub (main branch)...${NC}"

# Attempt push
if git push -u origin master --force; then
    echo -e "${GREEN}✓ Successfully pushed to GitHub!${NC}"
    echo -e "${GREEN}Repository: https://github.com/tuanthescientist/ClawAgent${NC}"
else
    echo -e "${RED}✗ Push failed. Check your authentication:${NC}"
    echo "  1. Ensure you have a GitHub Personal Access Token"
    echo "  2. Set it as your git credential"
    echo "  3. Or use: git remote set-url origin git@github.com:tuanthescientist/ClawAgent.git"
    exit 1
fi

echo ""
echo -e "${GREEN}Done! 🎉${NC}"
