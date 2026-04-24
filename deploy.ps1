# VirtualChef - Google Cloud Run Deployment Script (PowerShell)
# Prerequisites: gcloud CLI installed and authenticated

$ErrorActionPreference = "Stop"

# Configuration
$PROJECT_ID = if ($env:GCP_PROJECT_ID) { $env:GCP_PROJECT_ID } else { gcloud config get-value project }
$REGION = if ($env:GCP_REGION) { $env:GCP_REGION } else { "us-central1" }
$SERVICE_NAME = "virtualchef"
$IMAGE_NAME = "gcr.io/$PROJECT_ID/$SERVICE_NAME"

Write-Host "🍳 VirtualChef Deployment to Google Cloud Run" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "Project: $PROJECT_ID"
Write-Host "Region: $REGION"
Write-Host "Service: $SERVICE_NAME"
Write-Host ""

# Step 1: Enable required APIs
Write-Host "📦 Enabling required APIs..." -ForegroundColor Yellow
gcloud services enable `
    cloudbuild.googleapis.com `
    run.googleapis.com `
    secretmanager.googleapis.com `
    containerregistry.googleapis.com `
    --project="$PROJECT_ID"

# Step 2: Secret Manager setup instructions
Write-Host ""
Write-Host "🔐 Setting up secrets..." -ForegroundColor Yellow
Write-Host "Create secrets with these commands (replace with your actual keys):" -ForegroundColor White
Write-Host ""
Write-Host '  echo "your-google-api-key" | gcloud secrets create GOOGLE_API_KEY --data-file=-' -ForegroundColor Gray
Write-Host '  echo "your-tavily-api-key" | gcloud secrets create TAVILY_API_KEY --data-file=-' -ForegroundColor Gray
Write-Host ""

# Check if secrets exist
$googleKeyExists = gcloud secrets describe GOOGLE_API_KEY --project="$PROJECT_ID" 2>$null
$tavilyKeyExists = gcloud secrets describe TAVILY_API_KEY --project="$PROJECT_ID" 2>$null

if (-not $googleKeyExists) {
    Write-Host "⚠️  Secret GOOGLE_API_KEY does not exist. Please create it before deploying." -ForegroundColor Red
}

if (-not $tavilyKeyExists) {
    Write-Host "⚠️  Secret TAVILY_API_KEY does not exist. Please create it before deploying." -ForegroundColor Red
}

# Prompt to continue
$continue = Read-Host "Continue with deployment? (y/n)"
if ($continue -ne "y") {
    Write-Host "Deployment cancelled." -ForegroundColor Yellow
    exit 0
}

# Step 3: Build and push Docker image
Write-Host ""
Write-Host "🔨 Building Docker image..." -ForegroundColor Yellow
gcloud builds submit --tag "${IMAGE_NAME}:latest" .

# Step 4: Deploy to Cloud Run
Write-Host ""
Write-Host "🚀 Deploying to Cloud Run..." -ForegroundColor Yellow
gcloud run deploy $SERVICE_NAME `
    --image "${IMAGE_NAME}:latest" `
    --platform managed `
    --region $REGION `
    --allow-unauthenticated `
    --memory 1Gi `
    --cpu 1 `
    --min-instances 0 `
    --max-instances 10 `
    --timeout 300 `
    --set-secrets "GOOGLE_API_KEY=GOOGLE_API_KEY:latest,TAVILY_API_KEY=TAVILY_API_KEY:latest" `
    --project="$PROJECT_ID"

# Step 5: Get the service URL
Write-Host ""
Write-Host "✅ Deployment complete!" -ForegroundColor Green
$SERVICE_URL = gcloud run services describe $SERVICE_NAME `
    --platform managed `
    --region $REGION `
    --format 'value(status.url)' `
    --project="$PROJECT_ID"

Write-Host ""
Write-Host "🌐 Your VirtualChef is live at:" -ForegroundColor Cyan
Write-Host "   $SERVICE_URL" -ForegroundColor White
Write-Host ""
Write-Host "📊 View logs at:" -ForegroundColor Cyan
Write-Host "   https://console.cloud.google.com/run/detail/$REGION/$SERVICE_NAME/logs?project=$PROJECT_ID" -ForegroundColor White
