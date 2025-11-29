🌿 VunaGuide Backend (API & Agents)

This is the backend service for VunaGuide, an AI-powered agricultural assistant for Kenyan farmers. It hosts the core Agentic logic, orchestrating Google's Gemini 2.5 Flash models to diagnose crop diseases and provide real-time farming advice.

🏗️ Architecture (Google ADK)

This service implements a Manager-Worker Agent Pattern using the Google Agent Development Kit (ADK) framework:

Manager Service (The Orchestrator):

Acts as the central router.

Decides whether to run the Visual Diagnosis Pipeline (if an image is present) or the Chat/Search Pipeline (if text only).

Enforces strict logic flow to prevent hallucinations.

Agronomist Agent (Worker):

A specialized LlmAgent equipped with vision capabilities.

Identifies plants, detects diseases (e.g., Maize Lethal Necrosis), and suggests remedies.

Sentinel Agent (Evaluator):

A dedicated safety auditor.

Reviews the Agronomist's output before it reaches the user to catch dangerous advice or banned chemical suggestions.

🛠️ Tech Stack

Framework: FastAPI (Python 3.12+)

AI Engine: Google Vertex AI (Gemini 2.5 Flash)

Agent Framework: Google ADK (Agent Development Kit)

Package Manager: Pipenv

🚀 Setup Guide

1. Prerequisites

Python 3.12 or higher installed.

A Google Cloud Project with Vertex AI API enabled.

Local authentication (gcloud CLI) or a Service Account key.

2. Installation

# Install dependencies

pipenv install

# Activate virtual environment

pipenv shell

3. Environment Configuration

Create a .env file in the root directory:

# Your Google Cloud Project ID

GOOGLE_CLOUD_PROJECT=your-project-id-here

# Region (us-central1 is recommended for Gemini 2.5)

LOCATION=us-central1

# Model ID

MODEL_ID=gemini-2.5-flash

4. Running the Server

uvicorn app.main:app --reload

The API will be available at: http://127.0.0.1:8000

🧪 Testing the API

You can test the agent logic directly via the Swagger UI:

Go to http://127.0.0.1:8000/docs

Use the POST /api/v1/analyze endpoint.

Image: Upload a crop photo to test the Agronomist + Sentinel pipeline.

Question: Type "Maize prices?" to test the Google Search grounding.

📜 License

MIT License.
