#!/bin/sh

# Docker entrypoint script for Next.js frontend
# This script replaces environment variables at runtime

set -e

echo "Starting Gabi Agent Frontend..."

# Replace environment variables in the built application
if [ -d ".next" ]; then
    echo "Replacing environment variables in .next directory..."
    
    # Replace NEXT_PUBLIC_* variables in the built files
    find .next \( -type d -name .git -prune \) -o -type f -print0 | xargs -0 sed -i "s|NEXT_PUBLIC_API_URL_PLACEHOLDER|${NEXT_PUBLIC_API_URL:-http://localhost:8000}|g"
    find .next \( -type d -name .git -prune \) -o -type f -print0 | xargs -0 sed -i "s|NEXT_PUBLIC_APP_NAME_PLACEHOLDER|${NEXT_PUBLIC_APP_NAME:-Gabi Agent}|g"
    
    echo "Environment variables replaced successfully."
else
    echo "Warning: .next directory not found. Skipping environment variable replacement."
fi

# Start the application
echo "Starting Next.js application on port ${PORT:-3000}..."
exec node server.js 