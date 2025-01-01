# KakeiBot

LINE Messagning APIとAWS Lambdaを組み合わせて家計簿アプリを作成しています。

## 概要

- 家計簿管理を簡単に実施するためのアプリケーションです
- 一番ラクな管理方法を考えた結果、LINEという身近なアプリケーションを使うのが良いと考えました
- 所定のフォーマットに従ってLINEのBotに出費を記録すると、AWS上のデータベースに登録する仕組みです。

## ライセンス

このプロジェクトはMITライセンスのもとで公開されています。

## 参考文献
- [LINE Messaging APIの使い方](https://note.com/tomisan/n/ne5d7fbd55507)
- [LINE DEvelopers](https://developers.line.biz/ja/)
- [ボットを作成する](https://developers.line.biz/ja/docs/messaging-api/building-bot/)
- [ユーザーIDの取得](https://developers.line.biz/ja/docs/messaging-api/getting-user-ids/#page-title)
- [LINEのWebhook入門](https://lineapiusecase.com/ja/api/webhook.html)
- [AWS×LINE Messaging APIで家計簿を作ってみた①](https://zenn.dev/tn_a/articles/649c57463de040)
