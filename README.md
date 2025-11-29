# 🌿 VunaGuide Backend (API & Agents)

<p align="center">
  <strong>Backend service for VunaGuide: An AI-powered agricultural assistant for Kenyan farmers.</strong>
</p>

<p align="center">
  <a href="https://github.com/reez-code/vunaguide-frontend">View Frontend Repository</a> · 
  <a href="https://github.com/reez-code/vunaguide-backend/issues/new?labels=bug">Report Bug</a> · 
  <a href="https://github.com/reez-code/vunaguide-backend/issues/new?labels=enhancement">Request Feature</a>
</p>

---

## 📑 Table of Contents

- [Overview](#-overview)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Setup Guide](#-setup-guide)
- [Testing the API](#-testing-the-api)
- [License](#-license)

---

## 📖 Overview

This backend hosts the core Agentic logic for VunaGuide, orchestrating Google's Gemini 2.5 Flash models. It is responsible for diagnosing crop diseases from images and providing real-time, grounded farming advice via chat.

---

## 🏗️ Architecture (Google ADK)

This service implements a **Manager-Worker Agent Pattern** using the Google Agent Development Kit (ADK) framework:

### 1. Manager Service (The Orchestrator)

- Acts as the central router.
- Decides whether to run the Visual Diagnosis Pipeline (if an image is present) or the Chat/Search Pipeline (if text only).
- Enforces strict logic flow to prevent hallucinations.

### 2. Agronomist Agent (Worker)

- A specialized `LlmAgent` equipped with vision capabilities.
- Identifies plants, detects diseases (e.g., Maize Lethal Necrosis), and suggests remedies.

### 3. Sentinel Agent (Evaluator)

- A dedicated safety auditor.
- Reviews the Agronomist's output before it reaches the user to catch dangerous advice or banned chemical suggestions.

---

## 🛠️ Tech Stack

| Category            | Technology       | Why we chose it                                            |
| ------------------- | ---------------- | ---------------------------------------------------------- |
| **Framework**       | FastAPI          | High-performance Python web framework for building APIs.   |
| **Language**        | Python 3.12+     | Leveraging the latest features for async/await and typing. |
| **AI Engine**       | Google Vertex AI | Powered by Gemini 2.5 Flash for multimodal reasoning.      |
| **Agent Framework** | Google ADK       | Structured agent orchestration, tools, and runners.        |
| **Package Manager** | Pipenv           | Deterministic dependency management.                       |

---

## 🚀 Setup Guide

Follow these steps to get the backend running locally.

### 1. Prerequisites

- **Python 3.12+** installed on your machine.
- A **Google Cloud Project** with Vertex AI API enabled.
- Local authentication (gcloud CLI) or a Service Account key.

### 2. Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/reez-code/vunaguide-backend.git
cd vunaguide-backend

# Install dependencies
pipenv install

# Activate virtual environment
pipenv shell
```

### 3. Environment Configuration

Create a `.env` file in the root directory to configure your Google Cloud connection:

```env
# Your Google Cloud Project ID
GOOGLE_CLOUD_PROJECT=your-project-id-here

# Region (us-central1 is recommended for Gemini 2.5)
LOCATION=us-central1

# Model ID
MODEL_ID=gemini-2.5-flash
```

### 4. Running the Server

Start the FastAPI server with hot-reload enabled:

```bash
uvicorn app.main:app --reload
```

The API will be available at: **http://127.0.0.1:8000**

---

## 🧪 Testing the API

You can test the agent logic directly via the Swagger UI:

1. Go to **http://127.0.0.1:8000/docs**
2. Use the **POST /api/v1/analyze** endpoint:
   - **Image**: Upload a crop photo to test the Agronomist + Sentinel pipeline.
   - **Question**: Type "Maize prices?" to test the Google Search grounding.

---

## 📜 License

This project is open-source and available under the **MIT License**.

---

<p align="center">
  <sub>Built with ❤️ for Kenyan Farmers using Google Vertex AI & Agentic Design Kit (ADK)</sub>
</p>
