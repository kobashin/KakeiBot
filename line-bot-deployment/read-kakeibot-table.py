# reference: https://blog.serverworks.co.jp/first-api-construction
import json
import boto3
from botocore.exceptions import ClientError

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('KakeiBot-Table')

# HTML template for the graph page
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KakeiBot - データ分析ダッシュボード</title>
    <!-- グラフ表示 - Chart.jsを使用してカテゴリ別データを棒グラフで表示 -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"></script>
    <style>
        /* レスポンシブ設計 - モバイル対応のUIデザイン */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
            padding: 30px;
        }
        h1 {
            color: #333;
            margin-bottom: 10px;
            text-align: center;
        }
        .info {
            color: #666;
            text-align: center;
            margin-bottom: 30px;
            font-size: 14px;
        }
        .chart-container {
            position: relative;
            height: 400px;
            margin-bottom: 40px;
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }
        .stat-card h3 {
            font-size: 14px;
            opacity: 0.9;
            margin-bottom: 10px;
        }
        .stat-card .value {
            font-size: 32px;
            font-weight: bold;
        }
        .error {
            background: #fee;
            color: #c33;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
            display: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>KakeiBot - データ分析ダッシュボード</h1>
        <div class="info">DynamoDB テーブルのデータを可視化しています</div>
        
        <div class="error" id="error"></div>
        
        <div class="stats">
            <div class="stat-card">
                <h3>総アイテム数</h3>
                <div class="value" id="total-items">0</div>
            </div>
            <div class="stat-card">
                <h3>カテゴリ数</h3>
                <div class="value" id="category-count">0</div>
            </div>
        </div>
        
        <div class="chart-container">
            <canvas id="categoryChart"></canvas>
        </div>
    </div>

    <script>
        // Fetch data from API endpoint
        async function fetchData() {
            try {
                // 現在のURLのパスを /api/data に置き換える
                const baseUrl = window.location.origin + window.location.pathname.replace(/\\/users$/, '/users/api/data');
                const response = await fetch(baseUrl);
                const data = await response.json();
                
                if (response.ok) {
                    displayData(data);
                } else {
                    showError(data.error || 'データの取得に失敗しました');
                }
            } catch (error) {
                showError('通信エラー: ' + error.message);
            }
        }
        
        // Display data on the page
        function displayData(data) {
            // Update total items
            document.getElementById('total-items').textContent = data.items.length;
            
            // Count items by category
            const categoryCount = {};
            data.items.forEach(item => {
                const category = item.category || '未分類';
                categoryCount[category] = (categoryCount[category] || 0) + 1;
            });
            
            document.getElementById('category-count').textContent = Object.keys(categoryCount).length;
            
            // Create chart
            createChart(categoryCount);
        }
        
        // Create bar chart
        function createChart(categoryCount) {
            const ctx = document.getElementById('categoryChart').getContext('2d');
            
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: Object.keys(categoryCount),
                    datasets: [{
                        label: 'カテゴリ別アイテム数',
                        data: Object.values(categoryCount),
                        backgroundColor: [
                            'rgba(102, 126, 234, 0.8)',
                            'rgba(118, 75, 162, 0.8)',
                            'rgba(237, 100, 166, 0.8)',
                            'rgba(255, 154, 158, 0.8)',
                            'rgba(250, 208, 196, 0.8)'
                        ],
                        borderColor: [
                            'rgba(102, 126, 234, 1)',
                            'rgba(118, 75, 162, 1)',
                            'rgba(237, 100, 166, 1)',
                            'rgba(255, 154, 158, 1)',
                            'rgba(250, 208, 196, 1)'
                        ],
                        borderWidth: 1,
                        borderRadius: 5
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: true,
                            position: 'top'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                stepSize: 1
                            }
                        }
                    }
                }
            });
        }
        
        // Show error message
        function showError(message) {
            const errorDiv = document.getElementById('error');
            errorDiv.textContent = message;
            errorDiv.style.display = 'block';
        }
        
        // Load data when page loads
        window.addEventListener('load', fetchData);
    </script>
</body>
</html>
"""


def get_table_data():
    """Get all items from DynamoDB table"""
    response = table.scan()
    items = response.get('Items', [])
    return items


def lambda_handler(event, context):
    # デバッグ用ログ出力
    print(f"Received event: {json.dumps(event)}")
    
    try:
        path = event.get('path', '/')
        print(f"Path value: {path}")
        
        # HTMLページの表示 - ルートパス（/）または /users にアクセスするとダッシュボードが表示
        if path == '/' or path == '' or path == '/users':
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'text/html; charset=utf-8',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': HTML_TEMPLATE
            }
        
        # JSONデータAPI - /api/dataエンドポイントでJSONを返す
        elif path == '/api/data' or path == '/users/api/data':
            items = get_table_data()
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json; charset=utf-8',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET,OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'
                },
                'body': json.dumps({'items': items}, ensure_ascii=False, default=str)
            }
        
        # パスが見つからない場合
        else:
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Path not found'})
            }

    except ClientError as e:
        # DynamoDBクライアント関連のエラーハンドリング
        print(f"DynamoDB Client Error: {e.response['Error']['Message']}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': e.response['Error']['Message']})
        }

    except Exception as e:
        # その他の一般的なエラーハンドリング
        print(f"General Error: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)})
        }