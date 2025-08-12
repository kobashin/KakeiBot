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
from funcs import makeDynamoDBTableItem_from_image, print_item

# Sample document
# local_image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img", "receipt-beckscoffee.jpg")

# uotami
# local_image_path = "D:\\share\\receipts\\PXL_20250811_022722372.jpg"

# hamazushi
local_image_path = "D:\\share\\receipts\\PXL_20250811_022827337_MP.jpg"


item = makeDynamoDBTableItem_from_image(local_image_path)
print_item(item)
