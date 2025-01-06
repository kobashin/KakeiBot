import re
import datetime
from zoneinfo import ZoneInfo


def makeDynamoDBTableItem(text, event):
    """
    This function is used to make a table item put into DynamoDB

    design DynamoDB table
        userID          automatically   get from LINE Messaging API
        timestamp       automatically   get from Python library
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
    # get userID and timestamp from LINE event
    item['userID'] = event.source.user_id
    item['timestamp'] = event.timestamp

    '''
        date
    '''
    # for each splitted item, check if it is date.
    # if it is, treat it as date.
    is_date = [bool(re.match(r'^[0-9]{4}-[0-9]{4}-[0-9]{4}$', item))
               for item in splitted]

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
    is_price = [bool(re.match(r'^[0-9]+$', item)) for item in splitted]

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
