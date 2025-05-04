import boto3

dynamodb = boto3.client('dynamodb')
response = dynamodb.scan(TableName='KakeiBot-Table')
print(response)
