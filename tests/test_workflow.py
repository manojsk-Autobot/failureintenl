"""Test the complete workflow."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import asyncio
from main import analyze_and_send

if __name__ == "__main__":
    # Test with default email
    print("Testing MSSQL Agent workflow...")
    result = asyncio.run(analyze_and_send("manojkumar.selvakumar@sky.uk"))
    print(f"\nTest {'PASSED' if result else 'FAILED'}")
