import boto3

dynamodb = boto3.client('dynamodb')
response = dynamodb.scan(
    TableName='KakeiBot-Table',
    FilterExpression=(
        '(category = :deposit OR category = :withdrawal) '
        'AND (#dt BETWEEN :start AND :end)'
    ),
    ExpressionAttributeNames={
        # 'date' is a reserved word, so use ExpressionAttributeNames
        '#dt': 'date'
    },
    ExpressionAttributeValues={
        ':deposit': {'S': '入金'},
        ':withdrawal': {'S': '拠出'},
        ':start': {'S': '2025-0428-0000'},
        ':end': {'S': '2025-0504-2359'}
    }
)

# sum up prices for each sub-category
"""
    Each item is like that.
        {
            'sub-category': {'S': '真一郎'},
            'date': {'S': '2025-0501-1842'},
            'userID': {'S': 'U55f2c6b5b...'},
            'timestamp': {'N': '1746092545035'},
            'category': {'S': '入金'},
            'memo': {'S': '-'},
            'price': {'S': '10000'}
        }
"""

summary = {}
# iterate over items
for item in response['Items']:
    sub_category = item['sub-category']['S']
    price = int(item['price']['S'])
    # if sub-category is not in summary, add it
    if sub_category not in summary:
        summary[sub_category] = 0
    # add price to sub-category
    summary[sub_category] += price

# print summary
for sub_category, price in summary.items():
    print(f'{sub_category}: {price}円')
