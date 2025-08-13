import re
import datetime
from zoneinfo import ZoneInfo
import os
# Add these imports for Azure Document Intelligence
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest


def make_table_item_from_text(text, event):
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
        userID, timestamp and groupID
    '''
    # If event isn't empty, get userID, timestamp and groupID from LINE event
    if event:
        item['userID'] = event.source.user_id
        item['timestamp'] = event.timestamp
        item['groupID'] = event.source.group_id
    # In case of being called directly from terminal, not via LINE event
    else:
        item['userID'] = '-'
        item['timestamp'] = '-'
        item['groupID'] = '-'

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


def make_table_item_from_image(image_data, event=None):
    """
    This function is used to make a table item put into DynamoDB from image.
    """
    item = {}

    '''
        userID, timestamp and groupID
    '''
    # If event isn't empty, get userID, timestamp and groupID from LINE event
    if event:
        item['userID'] = event.source.user_id
        item['timestamp'] = event.timestamp
        item['groupID'] = event.source.group_id
    # In case of being called directly from terminal, not via LINE event
    else:
        item['userID'] = '-'
        item['timestamp'] = '-'
        item['groupID'] = '-'

    try:
        # Set timeout for Azure client
        endpoint = os.environ["AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT"]
        key = os.environ["AZURE_DOCUMENT_INTELLIGENCE_KEY"]

        client = DocumentIntelligenceClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(key)
        )

        # If image_data is an object of BytesIO
        if hasattr(image_data, 'getvalue'):
            poller = client.begin_analyze_document(
                "prebuilt-receipt",
                AnalyzeDocumentRequest(bytes_source=image_data.getvalue())
            )

        # If image_data is the path to image file
        '''
            azure.core.exceptions.HttpResponseError: (InvalidRequest) Invalid request.
            Code: InvalidRequest
            Message: Invalid request.
            Inner error: {
                "code": "InvalidContentLength",
                "message": "The input image is too large.
                    Refer to documentation for the maximum file size."
            }

            Max document size is 4MB for Free(F0) tier.
            https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/service-limits?view=doc-intel-4.0.0
        '''
        if isinstance(image_data, str):
            # check if it exists
            if os.path.exists(image_data):
                # get file size
                tmp_file_size = os.path.getsize(image_data)
                file_size_mb = tmp_file_size / (1024*1024)

                # if file size is equal or more than 4MB, resize and send to AnalyzeDocumentRequest
                if file_size_mb >= 4:
                    # Resize image to reduce file size
                    from PIL import Image
                    import io

                    print(f"Image size ({file_size_mb:.2f}MB) exceeds 4MB limit. Resizing...")

                    with Image.open(image_data) as img:
                        # Convert to RGB if necessary
                        if img.mode in ('RGBA', 'P'):
                            img = img.convert('RGB')

                        # Calculate new dimensions (reduce to ~75% of original)
                        new_width = int(img.width * 0.75)
                        new_height = int(img.height * 0.75)

                        # Resize image
                        resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

                        # Save to bytes with compression
                        img_buffer = io.BytesIO()
                        resized_img.save(img_buffer, format='JPEG', quality=85, optimize=True)
                        resized_bytes = img_buffer.getvalue()

                        print(f"Resized to {len(resized_bytes) / (1024*1024):.2f}MB")

                        poller = client.begin_analyze_document(
                            "prebuilt-receipt",
                            AnalyzeDocumentRequest(bytes_source=resized_bytes)
                        )

                # if file size is within the limit, send it to AnalyzeDocumentRequest directory
                else:
                    poller = client.begin_analyze_document(
                        "prebuilt-receipt",
                        AnalyzeDocumentRequest(
                            bytes_source=open(image_data, 'rb').read())
                    )

            else:
                # If image_data is not a valid file path
                raise ValueError("Invalid image file path")

        # Wait with timeout
        result = poller.result(timeout=45)  # 45 seconds max

        # Process result and return item
        # For almost all cases, there is only one receipt in the response.
        for idx, receipt in enumerate(result.documents):
            # merchant name
            merchant_name = receipt.fields.get("MerchantName")
            if merchant_name:
                item['merchant_name'] = merchant_name.value_string

            # date
            item = get_date(item, receipt)

            # category, sub-category and memo
            item = get_category(item, receipt)

            # price
            item = get_price(item, receipt)

            # evidence
            item['evidence'] = receipt

    except Exception as e:
        item['date'] = datetime.datetime.now(
                ZoneInfo("Asia/Tokyo")
            ).strftime('%Y-%m%d-%H%M')

        item['category'] = 'Error'
        item['price'] = 0
        item['memo'] = f'Image analysis failed: {str(e)}'

    return item


def convert_transaction_datetime_to_string(transaction_date, transaction_time):
    """
    "TransactionDate": {
        "type": "date",
        "valueDate": "2025-07-29",
        "content": "2025/07/29(",

        ...

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

        ...

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
    # Check if both date and time are not None
    if transaction_date is None or transaction_time is None:
        # Fall back to current time if either is None
        import datetime
        from zoneinfo import ZoneInfo
        return datetime.datetime.now(ZoneInfo("Asia/Tokyo")).strftime('%Y-%m%d-%H%M')

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
    tmp_receipt_type = receipt.fields.get("ReceiptType")
    receipt_type = tmp_receipt_type.value_string

    if receipt_type:
        item['receipt_type'] = receipt_type

        # If receipt type is "Meal", set category to "食費"
        if receipt_type == "Meal":
            item['category'] = "食費"

            """
            If merchant name has some types of strings, set sub-category
            For example:
                "ヨークベニマル" -> "自炊"
                "かましい" -> "自炊"
                "かましん" -> "自炊"
                "OTANI" -> "自炊"
            """
            if 'ヨークベニマル' in item['merchant_name']:
                item['sub-category'] = "自炊"
                item['memo'] = "ヨークベニマル"
            elif 'かましい' in item['merchant_name'] or 'かましん' in item['merchant_name']:
                item['sub-category'] = "自炊"
                item['memo'] = "かましん"
            elif 'OTANI' in item['merchant_name']:
                item['sub-category'] = "自炊"
                item['memo'] = "オータニ"
            elif 'たいらや' in item['merchant_name'] or 'だいらや' in item['merchant_name']:
                item['sub-category'] = "自炊"
                item['memo'] = "たいらや"
            else:
                item['sub-category'] = "外食"

        elif receipt_type in ["Healthcare", "Supplies"]:
            item['category'] = "日用品"
            item['sub-category'] = "-"

            if 'カワチ' in item['merchant_name']:
                item['memo'] = "カワチ"

            elif 'マツモトキヨシ' in item['merchant_name']:
                item['memo'] = "マツモトキヨシ"

            else:
                item['memo'] = "-"

        else:
            item['category'] = "-"
            item['sub-category'] = "-"

        return item


def get_price(item, receipt):
    """
        "Total": {
            "type": "currency",
            "valueCurrency": {
                "currencySymbol": "¥",
                "amount": 420,
                "currencyCode": "JPY"
            },
            "content": "¥420",
        }
    """
    price = receipt.fields.get("Total")
    if price and price.value_currency.amount is not None:
        # price must be integer
        item['price'] = int(price.value_currency.amount)
    else:
        item['price'] = 0

    return item


def get_date(item, receipt):
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

    return item


def print_item(item):
    """
    This function is used to print item
    """
    print("item:")
    for key, value in item.items():
        print(f"{key}: {value}")
    print("\n")
