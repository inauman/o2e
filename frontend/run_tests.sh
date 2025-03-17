#!/bin/bash
# Script to run frontend tests

# Set environment variables for Jest
export CI=true

# Run tests with detailed output and without watch mode
echo "Running frontend tests..."
npm test -- --watchAll=false --verbose

# Check exit code
if [ $? -eq 0 ]; then
  echo "✅ All frontend tests passed!"
else
  echo "❌ Some frontend tests failed. See above for details."
fi 