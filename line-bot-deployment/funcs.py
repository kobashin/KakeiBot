import re
import datetime
from zoneinfo import ZoneInfo
import os
# Add these imports for Azure Document Intelligence
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest


def makeDynamoDBTableItem_from_text(text, event):
    """
    This function is used to make a table item put into DynamoDB from text.

    design DynamoDB table
        userID          automatically   get from LINE Messaging API
        timestamp       automatically   get from Python library
        groupID         automatically   get from LINE Messaging API
        date            optional        get from message
        category        mandatory       get from message
        sub-category    optional        get from message
        price           mandatory       get from message
        memo            optional        get from message

        priceの前に書かれている文字列はカテゴリーとして扱う
        ただし、カテゴリーが複数行にまたがる場合は以下のパターンに従う
            1行目: category
            2行目: sub-category
            3行目: sbu-categoryよりをさらに細分化したカテゴリー

        priceは必ず整数でなければならない

        priceの後に書かれている文字列はメモとして扱う
    """
    # tmp return value
    item = {}
    # split message
    splitted = text.split('\n')

    '''
        userID and timestamp
    '''
    # get userID, timestamp and groupID from LINE event
    item['userID'] = event.source.user_id
    item['timestamp'] = event.timestamp
    item['groupID'] = event.source.group_id

    '''
        date
    '''
    # for each splitted item, check if it is date.
    # if it is, treat it as date.
    is_date = [bool(re.match(r'^[0-9]{4}-[0-9]{4}-[0-9]{4}$', item)) for item
               in splitted]

    # if True in is_date, get the date
    if True in is_date:
        item['date'] = splitted[is_date.index(True)]
        splitted = splitted[1:]
    else:
        # if there is no date, use today's date like 'YYYY-MMDD-hhmm'
        # time-zone is 'Asia/Tokyo'
        # example: 2021-0123-1234
        # example: 2021-0123-2345
        item['date'] = datetime.datetime.now(
            ZoneInfo("Asia/Tokyo")
        ).strftime('%Y-%m%d-%H%M')

    '''
        price, category, sub-category, memo
    '''
    # for each splitted item, check if it is numeric.
    # if it is, treat it as price.
    is_price = [bool(re.match(r'^([0-9],*)+[0-9]$', item)) for item
                in splitted]

    # if True in is_price, get the price
    if True in is_price:
        # get the category
        item['category'] = splitted[0]

        # get the sub-category if it exists
        if is_price.index(True) >= 2:
            item['sub-category'] = splitted[1]
        else:
            item['sub-category'] = '-'

        price = splitted[is_price.index(True)]
        item['price'] = price

        # get the memo if it exists
        if len(splitted) > is_price.index(True) + 1:
            item['memo'] = splitted[is_price.index(True) + 1]
        else:
            item['memo'] = '-'

    else:
        item['category'] = '-'
        item['sub-category'] = '-'
        item['price'] = '0'
        item['memo'] = text

    return item


def makeDynamoDBTableItem_from_image(image_data, event):
    """
    This function is used to make a table item put into DynamoDB from image.
    """
    item = {}

    try:
        # Set timeout for Azure client
        endpoint = os.environ["AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT"]
        key = os.environ["AZURE_DOCUMENT_INTELLIGENCE_KEY"]

        client = DocumentIntelligenceClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(key)
        )

        # Add timeout handling
        poller = client.begin_analyze_document(
            "prebuilt-receipt",
            AnalyzeDocumentRequest(bytes_source=image_data.getvalue())
        )

        # Wait with timeout
        result = poller.result(timeout=45)  # 45 seconds max

        # Process result and return item
        # For almost all cases, there is only one receipt in the response.
        for idx, receipt in enumerate(result.documents):

            # Merchant Name
            merchant_name = receipt.fields.get("MerchantName")
            if merchant_name:
                item['merchant_name'] = merchant_name.value_string

            # Datetime
            # Transaction Date
            transaction_date = receipt.fields.get("TransactionDate")
            # Transaction Time
            transaction_time = receipt.fields.get("TransactionTime")

            # If both date and time exist, combine them.
            if transaction_date and transaction_time:
                # Combine date and time
                item['date'] = convert_transaction_datetime_to_string(
                    transaction_date.value_date,
                    transaction_time.value_time
                )
            else:
                # If no transaction date found, use current date in Tokyo timezone
                item['date'] = datetime.datetime.now(
                    ZoneInfo("Asia/Tokyo")
                ).strftime('%Y-%m%d-%H%M')

            # Category
            item = get_category(item, receipt)

            # Price
            """
            "Total": {
                "type": "currency",
                "valueCurrency": {
                    "currencySymbol": "¥",
                    "amount": 420,
                    "currencyCode": "JPY"
                },
                "content": "¥420",
                "boundingRegions": [
                    {
                        "pageNumber": 1,
                        "polygon": [
                            1357,
                            1098,
                            1567,
                            1099,
                            1567,
                            1145,
                            1357,
                            1147
                        ]
                    }
                ],
                "confidence": 0.984,
                "spans": [
                    {
                        "offset": 221,
                        "length": 4
                    }
                ]
            }
            """
            price = receipt.fields.get("Total")
            if price and price.value_currency.amount is not None:
                # price must be integer
                item['price'] = int(price.value_currency.amount)
            else:
                item['price'] = 0

    except Exception as e:
        item = {
            'userID': event.source.user_id,
            'timestamp': event.timestamp,
            'groupID': event.source.group_id,
            'date': datetime.datetime.now(
                ZoneInfo("Asia/Tokyo")
            ).strftime('%Y-%m%d-%H%M'),
            'category': 'Error',
            'price': 0,
            'memo': f'Image analysis failed: {str(e)}'
        }

    return item


def convert_transaction_datetime_to_string(transaction_date, transaction_time):
    """
    "TransactionDate": {
        "type": "date",
        "valueDate": "2025-07-29",
        "content": "2025/07/29(",
        "boundingRegions": [
            {
                "pageNumber": 1,
                "polygon": [
                    428,
                    611,
                    740,
                    619,
                    739,
                    665,
                    426,
                    656
                ]
            }
        ],
        "confidence": 0.989,
        "spans": [
            {
                "offset": 101,
                "length": 11
            }
        ]
    },
    "TransactionTime": {
        "type": "time",
        "valueTime": "07:58:00",
        "content": "07:58",
        "boundingRegions": [
            {
                "pageNumber": 1,
                "polygon": [
                    843,
                    620,
                    967,
                    620,
                    967,
                    667,
                    842,
                    666
                ]
            }
        ],
        "confidence": 0.99,
        "spans": [
            {
                "offset": 115,
                "length": 5
            }
        ]
    }
    """
    # Convert date and time to string in the format 'YYYY-MMDD-HHMM'
    date_str = transaction_date.strftime('%Y-%m%d')
    time_str = transaction_time.strftime('%H%M')
    return f"{date_str}-{time_str}"


def makeResponseMessage(item):
    """
    This function is used to make a response for LINE bot from table item
    """

    # if userID exists in item, shorten it
    if 'userID' in item:
        item['userID'] = item['userID'][:10] + '...'

    tmp_response = [f"{key}:{value}" for key, value in item.items()]
    tmp_response = '\n'.join(tmp_response)
    response = "KakeiBot is updated!\n" \
        + tmp_response

    return response


def get_category(item, receipt):
    # Receipt Type
    receipt_type = receipt.doc_type

    if receipt_type:
        item['receipt_type'] = receipt_type

        # If receipt type is "receipt.retailMeal", set category to "食費"
        if receipt_type == "receipt.retailMeal":
            item['category'] = "食費"

            """
            If merchant name has some types of strings, set sub-category
            For example:
                "ヨークベニマル" -> "自炊"
                "かましい" -> "自炊"
                "かましん" -> "自炊"
            """
            if 'ヨークベニマル' in item['merchant_name']:
                item['sub-category'] = "自炊"
            elif 'かましい' in item['merchant_name'] or 'かましん' in item['merchant_name']:
                item['sub-category'] = "自炊"
            else:
                item['sub-category'] = "外食"

        else:
            item['category'] = "-"
            item['sub-category'] = "-"
        
        return item
