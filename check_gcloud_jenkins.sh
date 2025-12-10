#!/bin/bash

# Script to check and install Google Cloud SDK on Jenkins server
# This script can be run inside the Jenkins container

echo "=== Checking Google Cloud SDK Installation ==="
echo ""

# Check if gcloud is in PATH
if command -v gcloud &> /dev/null; then
    echo "✓ gcloud found in PATH"
    gcloud --version
    exit 0
fi

echo "✗ gcloud not found in PATH"
echo ""
echo "Checking common installation locations..."

# Check common locations
LOCATIONS=(
    "/usr/bin/gcloud"
    "/usr/local/bin/gcloud"
    "/var/jenkins_home/google-cloud-sdk/bin/gcloud"
    "$HOME/google-cloud-sdk/bin/gcloud"
)

FOUND=false
for location in "${LOCATIONS[@]}"; do
    if [ -f "$location" ] && [ -x "$location" ]; then
        echo "✓ Found gcloud at: $location"
        echo "Version: $($location --version | head -1)"
        FOUND=true
        break
    fi
done

if [ "$FOUND" = false ]; then
    echo "✗ gcloud not found in any common location"
    echo ""
    echo "=== Installation Instructions ==="
    echo ""
    echo "Option 1: Rebuild Jenkins container with custom Dockerfile"
    echo "  Your custom_jenkins/Dockerfile already includes gcloud installation."
    echo "  Run: docker build -t custom-jenkins:latest -f custom_jenkins/Dockerfile ."
    echo ""
    echo "Option 2: Install manually in running Jenkins container"
    echo "  Run these commands inside the Jenkins container:"
    echo ""
    echo "  ARCH=\$(dpkg --print-architecture)"
    echo "  if [ \"\$ARCH\" = \"arm64\" ]; then"
    echo "    curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-linux-arm.tar.gz"
    echo "    tar -xzf google-cloud-cli-linux-arm.tar.gz -C /var/jenkins_home"
    echo "    rm google-cloud-cli-linux-arm.tar.gz"
    echo "  else"
    echo "    curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-linux-x86_64.tar.gz"
    echo "    tar -xzf google-cloud-cli-linux-x86_64.tar.gz -C /var/jenkins_home"
    echo "    rm google-cloud-cli-linux-x86_64.tar.gz"
    echo "  fi"
    echo "  /var/jenkins_home/google-cloud-sdk/install.sh --quiet --usage-reporting=false --path-update=false"
    echo ""
    exit 1
fi
