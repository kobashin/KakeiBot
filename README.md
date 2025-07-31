# KakeiBot

LINE Messagning APIとAWS Lambdaを組み合わせて家計簿アプリを作成しています。

---

## 概要
KakeiBotは、LINEメッセージ（テキスト・画像）を受け取り、家計簿データをDynamoDBに保存し、必要に応じて応答や集計を行うアプリケーションです。

<!-- Insert image -->

出費の記録<br>
<img src="./img/record_01.png" width="300" />
<br>毎週の出費の記録<br>
<img src="./img/weekly_notify_01.png" width="300" />

---

## シーケンス図（Mermaid）

```mermaid
sequenceDiagram
    participant User as ユーザー
    participant LINE as LINE Platform
    participant Lambda as AWS Lambda
    participant Azure as Azure Document Intelligence
    participant DynamoDB as DynamoDB

    Note over User,DynamoDB: テキストメッセージフロー
    User->>LINE: テキストメッセージ送信
    LINE->>Lambda: Webhook (event)
    Lambda->>Lambda: makeDynamoDBTableItem_from_text()
    Lambda->>DynamoDB: データ保存
    Lambda->>Lambda: makeResponseMessage()
    Lambda->>LINE: 応答メッセージ
    LINE->>User: 応答表示

    Note over User,DynamoDB: 画像メッセージフロー（レシート）
    User->>LINE: レシート画像送信
    LINE->>Lambda: Webhook (event)
    Lambda->>LINE: 画像データ取得リクエスト
    LINE->>Lambda: 画像データ
    Lambda->>Azure: 画像解析リクエスト
    Azure->>Lambda: 解析結果（テキスト、日付、金額等）
    Lambda->>Lambda: makeDynamoDBTableItem_from_image()
    Lambda->>DynamoDB: データ保存
    Lambda->>Lambda: makeResponseMessage()
    Lambda->>LINE: 応答メッセージ
    LINE->>User: 応答表示
```

---

## 主な処理の流れ

### 1. テキストメッセージ処理
- ユーザーがLINEでテキストを送信
- Lambda関数がテキストからカテゴリ、金額等を抽出
- DynamoDBに保存
- 応答を返信

### 2. 画像メッセージ処理
- ユーザーがレシート画像を送信
- Lambda関数が画像を取得
- Azureの画像解析APIで日本語テキスト、金額、日付等を抽出
- DynamoDBに保存
- 応答を返信

### 3. 週次レポート
- 別のLambda関数が週に一度自動実行（EventBridgeでスケジュール）
- DynamoDBから一週間分のデータを集計
- LINEグループにサマリーを送信

---

## ライセンス

このプロジェクトはMITライセンスのもとで公開されています。

## 参考文献
- [LINE Messaging APIの使い方](https://note.com/tomisan/n/ne5d7fbd55507)
- [LINE Developers](https://developers.line.biz/ja/)
- [ボットを作成する](https://developers.line.biz/ja/docs/messaging-api/building-bot/)
- [ユーザーIDの取得](https://developers.line.biz/ja/docs/messaging-api/getting-user-ids/#page-title)
- [LINEのWebhook入門](https://lineapiusecase.com/ja/api/webhook.html)
- [AWS×LINE Messaging APIで家計簿を作ってみた①](https://zenn.dev/tn_a/articles/649c57463de040)
