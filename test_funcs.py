# import functions in line-bot-deployment.funcs
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'line-bot-deployment'))
from funcs import makeDynamoDBTableItem

test_text_array = ["交通費\n2000",
                   "食費\nお昼ご飯\n1000",
                   "食費\n1000\nお昼ご飯"]

for test_text in test_text_array:
    test_item = makeDynamoDBTableItem(test_text)
    print(test_text)
    print('---')
    print(test_item)
    print('---')
