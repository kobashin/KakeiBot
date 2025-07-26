"""
    References
        https://learn.microsoft.com/ja-jp/azure/ai-services/computer-vision/quickstarts-sdk/image-analysis-client-library?tabs=linux%2Cvisual-studio&pivots=programming-language-python
        
"""
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials

from array import array
import os
from PIL import Image
import sys
import time

'''
Authenticate
Authenticates your credentials and creates a client.
'''
subscription_key = os.environ["AZURE_COMPUTER_VISION_KEY"]
endpoint = os.environ["AZURE_COMPUTER_VISION_ENDPOINT"]

computervision_client = ComputerVisionClient(
                            endpoint,
                            CognitiveServicesCredentials(subscription_key)
                        )
'''
END - Authenticate
'''

'''
Quickstart variables
These variables are shared by several examples
'''
# Images used for the examples: Describe an image, Categorize an image, Tag an image,
# Detect faces, Detect adult or racy content, Detect the color scheme,
# Detect domain-specific content, Detect image types, Detect objects
images_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
# remote_image_url = "https://raw.githubusercontent.com/Azure-Samples/cognitive-services-sample-data-files/master/ComputerVision/Images/landmark.jpg"
'''
END - Quickstart variables
'''

'''
Tag an Image - local
This example returns a tag (key word) for each thing in a local image.
'''
print("===== Tag an image - local =====")
# Open local image file
local_image_path = os.path.join(images_folder, "receipt-seveneleven.jpg")
local_image = open(local_image_path, "rb")

# Call API with local image
tags_result_local = computervision_client.tag_image_in_stream(local_image)
# tags_result_remote = computervision_client.tag_image(remote_image_url)

# Print results with confidence score
print("Tags in the local image: ")
if (len(tags_result_local.tags) == 0):
    print("No tags detected.")
else:
    for tag in tags_result_local.tags:
        print("'{}' with confidence {:.2f}%".format(
                                                tag.name,
                                                tag.confidence * 100
                                            ))

print()

# Close the image file
local_image.close()
'''
END - Tag an Image - local
'''
print("End of Computer Vision quickstart.")
