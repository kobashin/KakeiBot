import sys
sys.path.append('line-bot-deployment')
from funcs import make_table_item_from_text

event = {
    'source_user_id': 'U55f2c6b5b...',
    'timestamp': '1762587967374',
    'source_group_id': 'C57d06bd3d5843415dce05ff7cb6c2b50',
}

message_text = '2025-1108\n食費\n自炊\n1756\nロマンチック村'


class Source:
    def __init__(self, event):
        self.user_id = event['source_user_id']
        self.group_id = event['source_group_id']


class Event:
    def __init__(self, event, source):
        self.source = source
        self.timestamp = event['timestamp']


source_object = Source(event=event)
event_object = Event(event=event, source=source_object)


def test_object():
    assert event_object.source.user_id == 'U55f2c6b5b...'
    assert event_object.timestamp == '1762587967374'
    assert event_object.source.group_id == 'C57d06bd3d5843415dce05ff7cb6c2b50'


def test_making_table_item():
    item = make_table_item_from_text(message_text, event_object)
    assert item['userID'] == 'U55f2c6b5b...'
    assert item['timestamp'] == '1762587967374'
    assert item['groupID'] == 'C57d06bd3d5843415dce05ff7cb6c2b50'
    assert item['date'] == '2025-1108-1200'
    assert item['category'] == '食費'
    assert item['sub-category'] == '自炊'
    assert item['price'] == '1756'
    assert item['memo'] == 'ロマンチック村'
