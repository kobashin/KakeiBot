import re


def makeDynamoDBTableItem(text):
    """
    This function is used to make a table item put into DynamoDB

    design DynamoDB table
        userID          automatically   get from LINE Messaging API
        timestamp       automatically   get from Python library
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

    # for each splitted item, check if it is numeric.
    # if it is, treat it as price.
    is_price = [bool(re.match(r'^[0-9]+$', item)) for item in splitted]

    # if True in is_price, get the price
    if True in is_price:
        price = splitted[is_price.index(True)]
        item['price'] = price

    # get the category
    item['category'] = splitted[0]
    # get the sub-category if it exists
    if is_price.index(True) >= 2:
        item['sub-category'] = splitted[1]
    else:
        item['sub-category'] = '-'

    return item


def makeResponseMessage(item):
    """
    This function is used to make a response for LINE bot from table item
    """

    tmp_response = [f"{key}:{value}" for key, value in item.items()]
    tmp_response = '\n'.join(tmp_response)
    response = "Your log is successfully put into KakeiBot database!\n" \
        + tmp_response

    return response
