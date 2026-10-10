# AI Travel Guide

An AI-powered travel guide that generates information about tourist destinations and converts it into audio in multiple languages.

## Features

- Search for tourist destinations
- Generate AI-powered destination descriptions
- Choose Summary or Detailed information
- Generate audio guides using Murf Falcon
- Multilingual support: English, Hindi, Telugu, and Tamil
- Choose male or female voices
- Read the generated text transcript
- Listen to generated audio in the web interface

## Technologies Used

- Python
- Flask
- HTML, CSS, and JavaScript
- Google Gemini API
- Murf Falcon API

## Project Structure

```text
AI-Travel-Guide/
├── Backend/
│   ├── app.py
│   └── test_gemini.py
├── Frontend/
│   ├── index.html
│   └── index.js
├── .env
├── .gitignore
└── requirements.txt
```

The `.env` file contains private API keys and should never be uploaded to GitHub.

## Setup Instructions

### 1. Install Python

Install a compatible Python version if it is not already installed.

### 2. Create and activate a virtual environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Configure API keys

Create a `.env` file in the project root and add your own API keys:

```text
GEMINI_API_KEY=your_gemini_api_key
MURF_API_KEY=your_murf_api_key
```

Replace the placeholder values with your own keys. Never publish your actual keys.

### 5. Start the backend

```powershell
python Backend/app.py
```

Keep the terminal running while using the application locally.

### 6. Open the frontend

Open `Frontend/index.html` in your browser. The frontend API URL must point to the running Flask backend.

## Notes

This repository contains the project source code. A live deployed link will be added separately after deployment.
