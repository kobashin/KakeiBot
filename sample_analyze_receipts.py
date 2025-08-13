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
from funcs import make_table_item_from_image, print_item


def debug_image_processing(image_path):
    """Debug function to check image processing"""
    from PIL import Image

    print("=== Image Debug Info ===")
    print(f"File path: {image_path}")
    print(f"File exists: {os.path.exists(image_path)}")

    if os.path.exists(image_path):
        file_size = os.path.getsize(image_path)
        print(f"File size: {file_size / (1024*1024):.2f} MB ({file_size:,} bytes)")

        try:
            with Image.open(image_path) as img:
                print(f"Image dimensions: {img.size[0]} x {img.size[1]} pixels")
                print(f"Image format: {img.format}")
                print(f"Image mode: {img.mode}")
        except Exception as e:
            print(f"PIL Error: {e}")

        try:
            with open(image_path, 'rb') as f:
                content = f.read()
                print(f"Raw file content size: {len(content):,} bytes")
                print(f"Content matches file size: {len(content) == file_size}")
        except Exception as e:
            print(f"File read error: {e}")
    else:
        print("❌ File does not exist!")

    print("=" * 40)


def check_environment():
    """Check Azure environment variables"""
    print(f"=== Environment Check ===")
    endpoint = os.environ.get("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
    key = os.environ.get("AZURE_DOCUMENT_INTELLIGENCE_KEY")
    print(f"Endpoint set: {bool(endpoint)}")
    print(f"Key set: {bool(key)}")
    if endpoint:
        print(f"Endpoint: {endpoint}")
    print("=" * 40)


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
