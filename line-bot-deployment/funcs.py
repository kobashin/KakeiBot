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


def makeDynamoDBTableItem_from_image(image, event):
    """
    This function is used to make a table item put into DynamoDB from image.
    """
    item = {}

    # Set your Azure Document Intelligence endpoint and key from environment variables
    endpoint = os.environ["AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT"]
    key = os.environ["AZURE_DOCUMENT_INTELLIGENCE_KEY"]

    # Image -> json
    # Call Azure Document Intelligence API to analyze the receipt
    document_intelligence_client = DocumentIntelligenceClient(
        endpoint=endpoint, credential=AzureKeyCredential(key)
    )
    poller = document_intelligence_client.begin_analyze_document(
        "prebuilt-receipt", AnalyzeDocumentRequest(bytes_source=image.read())
    )
    receipts = poller.result()

    # json -> DynamoDB item
    # Convert response from Azure Document Intelligence API to DynamoDB item
    # get userID, timestamp and groupID from LINE event
    item['userID'] = event.source.user_id
    item['timestamp'] = event.timestamp
    item['groupID'] = event.source.group_id

    # For almost all cases, there is only one receipt in the response.
    for idx, receipt in enumerate(receipts.documents):
        # Receipt Type
        receipt_type = receipt.doc_type
        if receipt_type:
            item['receipt_type'] = receipt_type

        # Merchant Name
        merchant_name = receipt.fields.get("MerchantName")
        if merchant_name:
            item['merchant_name'] = merchant_name.value_string

        # Transaction Date
        transaction_date = receipt.fields.get("TransactionDate")
        if transaction_date:
            item['date'] = convert_transaction_date_to_string(transaction_date.value_date)

        # Category
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

        # Price
        price = receipt.fields.get("Total")
        if price:
            item['price'] = price.value_number
        else:
            item['price'] = 0

    return item


def convert_transaction_date_to_string(transaction_date):
    """
    This function converts transaction date to string.
    Format of returned value should be like '%Y-%m%d-%H%M'.

    For example:
        transaction_date : 2025-06-22
        return value : '2025-0622-0000'
    If time does not exist in transaction_date,
    it will be set to '0000' like '2025-0622-0000'.
    """
    if isinstance(transaction_date, datetime.date):
        return transaction_date.strftime('%Y-%m%d') + '-0000'


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
