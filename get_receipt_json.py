'''
For each image file in D:\share\receipts, do processes below.

1. Set the environment variables.
2. Debug the image processing.
3. Process the image and extract receipt information from Azure.
4. Save the extracted information to a JSON file.
'''
import os
import sys
import json
import time
sys.path.append(os.path.join(os.path.dirname(__file__), 'line-bot-deployment'))
from funcs import (debug_image_processing,
                   set_azure_client, begin_analyze_document)

# Get images from the directory
image_dir = "D:\\share\\receipts"
image_files = [f for f in os.listdir(image_dir) if f.endswith((".jpg", ".jpeg", ".png"))]

# 1. Set the environment variables.
client = set_azure_client()

# Start the image processing
for image_file in image_files:
    # Construct the full file path
    full_image_path = os.path.join(image_dir, image_file)

    # 2. Debug the image processing.
    debug_image_processing(full_image_path)

    # 3. Process the image and extract receipt information from Azure.
    result = begin_analyze_document(client, full_image_path)

    # 4. Save the extracted information to a JSON file.
    try:
        # Convert the document to a dictionary if it's not already
        if hasattr(result.documents[0], '__dict__'):
            document_data = result.documents[0].__dict__
        else:
            document_data = result.documents[0]

        with open(f"D:\\share\\receipts\\json\\{image_file}.json", "w", encoding='utf-8') as json_file:
            json.dump(document_data, json_file, ensure_ascii=False, indent=4, default=str)

        print(f"Successfully saved JSON for {image_file}")

    except TypeError as e:
        print(f"JSON serialization error for {image_file}: {e}")
        # Fallback: save as string representation
        with open(f"D:\\share\\receipts\\json\\{image_file}.txt", "w", encoding='utf-8') as txt_file:
            txt_file.write(str(result.documents[0]))
        print(f"Saved as text file instead: {image_file}.txt")

    # wait for a while before processing the next image
    time.sleep(20)
