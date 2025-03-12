#!/bin/bash
# Production build script

echo "Building frontend..."
cd frontend && npm run build

if [ $? -ne 0 ]; then
  echo "Frontend build failed!"
  exit 1
fi

echo "Copying build to backend static directory..."
rm -rf backend/static/*
cp -r frontend/build/* backend/static/

echo "Build complete! The app is ready to be served from the backend." 