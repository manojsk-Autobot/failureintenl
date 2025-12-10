#!/usr/bin/env python3
"""Test Gemini API and list available models."""
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("ERROR: GEMINI_API_KEY not found in environment")
    exit(1)

# Configure Gemini
genai.configure(api_key=api_key)

# List available models
print("Available Gemini models:")
print("-" * 60)
for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"Model: {model.name}")
        print(f"  Display Name: {model.display_name}")
        print(f"  Supported methods: {model.supported_generation_methods}")
        print()

# Test with a simple prompt
print("\nTesting with gemini-pro model:")
print("-" * 60)
try:
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content("Say 'Hello, the Gemini API is working!'")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error with gemini-pro: {e}")

print("\nTesting with models/gemini-pro model:")
print("-" * 60)
try:
    model = genai.GenerativeModel('models/gemini-pro')
    response = model.generate_content("Say 'Hello, the Gemini API is working!'")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error with models/gemini-pro: {e}")
