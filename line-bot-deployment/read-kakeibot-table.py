# reference: https://blog.serverworks.co.jp/first-api-construction
import json
import boto3
from botocore.exceptions import ClientError
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('KakeiBot-Table')


def get_last_week_date_range():
    """先週の日付範囲を計算（6日前00:00〜本日23:59 JST）"""
    now = datetime.now(ZoneInfo('Asia/Tokyo'))
    start_time = now - timedelta(days=6)
    start_time = start_time.replace(hour=0, minute=0, second=0, microsecond=0)
    end_time = now.replace(hour=23, minute=59, second=0, microsecond=0)

    start_str = start_time.strftime('%Y-%m%d-%H%M')
    end_str = end_time.strftime('%Y-%m%d-%H%M')
    start_short = start_time.strftime('%m/%d')
    end_short = end_time.strftime('%m/%d')

    return start_str, end_str, start_short, end_short


def get_weekly_summary():
    """先週の食費と拠出金額を取得"""
    start_str, end_str, start_short, end_short = get_last_week_date_range()

    # 食費クエリ
    food_response = table.scan(
        FilterExpression='category = :food AND #dt BETWEEN :start AND :end',
        ExpressionAttributeNames={'#dt': 'date'},
        ExpressionAttributeValues={
            ':food': '食費',
            ':start': start_str,
            ':end': end_str
        }
    )

    food_summary = {'自炊': 0, '外食': 0, 'その他': 0}
    for item in food_response.get('Items', []):
        sub_cat = item.get('sub-category', 'その他')
        price = int(item.get('price', 0))
        if sub_cat in food_summary:
            food_summary[sub_cat] += price
        else:
            food_summary['その他'] += price

    # 拠出クエリ
    withdrawal_response = table.scan(
        FilterExpression='category = :withdrawal AND #dt BETWEEN :start AND :end',
        ExpressionAttributeNames={'#dt': 'date'},
        ExpressionAttributeValues={
            ':withdrawal': '拠出',
            ':start': start_str,
            ':end': end_str
        }
    )

    withdrawal_summary = {}
    for item in withdrawal_response.get('Items', []):
        person = item.get('sub-category', 'その他')
        price = int(item.get('price', 0))
        withdrawal_summary[person] = withdrawal_summary.get(person, 0) + price

    return {
        'period': {'start': start_short, 'end': end_short},
        'food': food_summary,
        'food_total': sum(food_summary.values()),
        'withdrawal': withdrawal_summary,
        'withdrawal_total': sum(withdrawal_summary.values())
    }


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
        .weekly-section {
            margin-top: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
        }
        .weekly-section h2 {
            color: #333;
            font-size: 18px;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }
        .weekly-detail {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
        }
        .detail-card {
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }
        .detail-card h3 {
            color: #667eea;
            font-size: 16px;
            margin-bottom: 15px;
        }
        .detail-item {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #eee;
        }
        .detail-item:last-child {
            border-bottom: none;
        }
        .detail-item .label {
            color: #666;
        }
        .detail-item .value {
            font-weight: bold;
            color: #333;
        }
        .detail-total {
            margin-top: 10px;
            padding-top: 10px;
            border-top: 2px solid #667eea;
            font-size: 18px;
            font-weight: bold;
            text-align: right;
            color: #667eea;
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

        <div class="weekly-section">
            <h2>先週の詳細 (<span id="period-range">-</span>)</h2>
            <div class="weekly-detail">
                <div class="detail-card">
                    <h3>食費</h3>
                    <div id="food-details">
                        <div class="detail-item">
                            <span class="label">自炊</span>
                            <span class="value" id="food-jisui">¥0</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">外食</span>
                            <span class="value" id="food-gaishoku">¥0</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">その他</span>
                            <span class="value" id="food-other">¥0</span>
                        </div>
                    </div>
                    <div class="detail-total" id="food-total">合計: ¥0</div>
                </div>
                <div class="detail-card">
                    <h3>拠出金額</h3>
                    <div id="withdrawal-details"></div>
                    <div class="detail-total" id="withdrawal-total">合計: ¥0</div>
                </div>
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

        // Fetch weekly summary from API endpoint
        async function fetchWeeklySummary() {
            try {
                const baseUrl = window.location.origin + window.location.pathname.replace(/\\/users$/, '/users/api/weekly-summary');
                const response = await fetch(baseUrl);
                const data = await response.json();

                if (response.ok) {
                    displayWeeklySummary(data);
                } else {
                    console.error('Failed to fetch weekly summary:', data.error);
                }
            } catch (error) {
                console.error('Weekly summary error:', error.message);
            }
        }

        // Display weekly summary data
        function displayWeeklySummary(data) {
            // Update period range
            document.getElementById('period-range').textContent =
                `${data.period.start} ~ ${data.period.end}`;

            // Update food expenses
            document.getElementById('food-jisui').textContent =
                `¥${data.food['自炊'].toLocaleString()}`;
            document.getElementById('food-gaishoku').textContent =
                `¥${data.food['外食'].toLocaleString()}`;
            document.getElementById('food-other').textContent =
                `¥${data.food['その他'].toLocaleString()}`;
            document.getElementById('food-total').textContent =
                `合計: ¥${data.food_total.toLocaleString()}`;

            // Update withdrawal amounts
            const container = document.getElementById('withdrawal-details');
            container.innerHTML = '';

            for (const [person, amount] of Object.entries(data.withdrawal)) {
                const div = document.createElement('div');
                div.className = 'detail-item';
                div.innerHTML = `
                    <span class="label">${person}</span>
                    <span class="value">¥${amount.toLocaleString()}</span>
                `;
                container.appendChild(div);
            }

            document.getElementById('withdrawal-total').textContent =
                `合計: ¥${data.withdrawal_total.toLocaleString()}`;
        }

        // Load data when page loads
        window.addEventListener('load', () => {
            fetchData();
            fetchWeeklySummary();
        });
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

        # 週次サマリーAPI - /api/weekly-summaryエンドポイント
        elif path == '/api/weekly-summary' or path == '/users/api/weekly-summary':
            summary = get_weekly_summary()
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json; charset=utf-8',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET,OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'
                },
                'body': json.dumps(summary, ensure_ascii=False, default=str)
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
