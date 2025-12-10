#!/usr/bin/env python3
"""Simple test for Gemini API with working model."""
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

print(f"Using API key: {api_key[:20]}...")

# Configure Gemini
genai.configure(api_key=api_key)

# Test with gemini-flash-latest (this should work)
print("\nTesting with gemini-flash-latest:")
print("-" * 60)
try:
    model = genai.GenerativeModel('gemini-flash-latest')
    response = model.generate_content("Say 'Hello! The Gemini API is working perfectly!'")
    print(f"✅ SUCCESS!")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"❌ FAILED: {e}")

# Test with the model from .env
model_name = os.getenv("GEMINI_MODEL", "gemini-flash-latest")
print(f"\nTesting with {model_name} (from .env):")
print("-" * 60)
try:
    model = genai.GenerativeModel(model_name)
    response = model.generate_content("Analyze this SQL error: The MERGE statement attempted to UPDATE or DELETE the same row more than once.")
    print(f"✅ SUCCESS!")
    print(f"Response: {response.text[:200]}...")
except Exception as e:
    print(f"❌ FAILED: {e}")
