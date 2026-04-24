#!/bin/bash
# VirtualChef - Google Cloud Run Deployment Script
# Prerequisites: gcloud CLI installed and authenticated

set -e

# Configuration
PROJECT_ID="${GCP_PROJECT_ID:-$(gcloud config get-value project)}"
REGION="${GCP_REGION:-us-central1}"
SERVICE_NAME="virtualchef"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "🍳 VirtualChef Deployment to Google Cloud Run"
echo "=============================================="
echo "Project: ${PROJECT_ID}"
echo "Region: ${REGION}"
echo "Service: ${SERVICE_NAME}"
echo ""

# Step 1: Enable required APIs
echo "📦 Enabling required APIs..."
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    secretmanager.googleapis.com \
    containerregistry.googleapis.com \
    --project="${PROJECT_ID}"

# Step 2: Create secrets in Secret Manager (if they don't exist)
echo ""
echo "🔐 Setting up secrets..."
echo "Note: You'll need to add secret values manually in the Cloud Console"
echo "or run these commands with your actual API keys:"
echo ""
echo "  echo -n 'your-google-api-key' | gcloud secrets create GOOGLE_API_KEY --data-file=-"
echo "  echo -n 'your-tavily-api-key' | gcloud secrets create TAVILY_API_KEY --data-file=-"
echo ""

# Check if secrets exist
if ! gcloud secrets describe GOOGLE_API_KEY --project="${PROJECT_ID}" &>/dev/null; then
    echo "⚠️  Secret GOOGLE_API_KEY does not exist. Please create it before deploying."
fi

if ! gcloud secrets describe TAVILY_API_KEY --project="${PROJECT_ID}" &>/dev/null; then
    echo "⚠️  Secret TAVILY_API_KEY does not exist. Please create it before deploying."
fi

# Step 3: Build and push Docker image
echo ""
echo "🔨 Building Docker image..."
gcloud builds submit --tag "${IMAGE_NAME}:latest" .

# Step 4: Deploy to Cloud Run
echo ""
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy "${SERVICE_NAME}" \
    --image "${IMAGE_NAME}:latest" \
    --platform managed \
    --region "${REGION}" \
    --allow-unauthenticated \
    --memory 1Gi \
    --cpu 1 \
    --min-instances 0 \
    --max-instances 10 \
    --timeout 300 \
    --set-secrets "GOOGLE_API_KEY=GOOGLE_API_KEY:latest,TAVILY_API_KEY=TAVILY_API_KEY:latest" \
    --project="${PROJECT_ID}"

# Step 5: Get the service URL
echo ""
echo "✅ Deployment complete!"
SERVICE_URL=$(gcloud run services describe "${SERVICE_NAME}" \
    --platform managed \
    --region "${REGION}" \
    --format 'value(status.url)' \
    --project="${PROJECT_ID}")

echo ""
echo "🌐 Your VirtualChef is live at:"
echo "   ${SERVICE_URL}"
echo ""
echo "📊 View logs at:"
echo "   https://console.cloud.google.com/run/detail/${REGION}/${SERVICE_NAME}/logs?project=${PROJECT_ID}"
