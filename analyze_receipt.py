"""
This code sample shows Prebuilt Receipt operations with the Azure AI Document Intelligence client library.
The async versions of the samples require Python 3.8 or later.

To learn more, please visit the documentation - Quickstart: Document Intelligence (formerly Form Recognizer) SDKs
https://learn.microsoft.com/azure/ai-services/document-intelligence/quickstarts/get-started-sdks-rest-api?pivots=programming-language-python
"""

import os
import sys

# Add the line-bot-deployment directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'line-bot-deployment'))
from funcs import (make_table_item_from_image, print_item,
                   debug_image_processing, check_environment)


# Sample document
# local_image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img", "receipt-beckscoffee.jpg")

# uotami
# local_image_path = "D:\\share\\receipts\\PXL_20250811_022722372.jpg"

# hamazushi
# local_image_path = "D:\\share\\receipts\\PXL_20250811_023722668.jpg"

# matsukiyo
# local_image_path = "D:\\share\\receipts\\PXL_20250811_023758660.jpg"

# nitori
# local_image_path = "D:\\share\\receipts\\PXL_20250811_023257992.jpg"

# yamaya
local_image_path = "D:\\share\\receipts\\PXL_20250811_023318354.jpg"

# Debug the image first
print("🔍 Starting debugging process...")
debug_image_processing(local_image_path)
check_environment()

# Try to process the image
print("📤 Attempting to process image...")
try:
    item = make_table_item_from_image(local_image_path)
    print("✅ Success!")
    print_item(item)
except Exception as e:
    print(f"❌ Error occurred: {e}")
    print(f"Error type: {type(e).__name__}")

    # Additional debugging for this specific error
    if "InvalidContentLength" in str(e):
        print("\n🔍 InvalidContentLength specific debugging:")
        try:
            with open(local_image_path, 'rb') as f:
                content = f.read()
                print(f"Actual bytes being sent: {len(content):,}")

                # Check if content is corrupted or has unexpected size
                import hashlib
                file_hash = hashlib.md5(content).hexdigest()
                print(f"File MD5 hash: {file_hash}")

                # Check first few bytes to verify it's a valid image
                magic_bytes = content[:10]
                print(f"File magic bytes: {magic_bytes.hex()}")

        except Exception as debug_err:
            print(f"Debug error: {debug_err}")

    import traceback
    traceback.print_exc()
