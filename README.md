# KakeiBot

LINE Messagning APIとAWS Lambdaを組み合わせて家計簿アプリを作成しています。

## 概要

- 家計簿管理を簡単に実施するためのアプリケーションです
- 一番ラクな管理方法を考えた結果、LINEという身近なアプリケーションを使うのが良いと考えました
- 所定のフォーマットに従ってLINEのBotに出費を記録すると、AWS上のデータベースに登録する仕組みです。

## インストール方法

以下の手順でプロジェクトをローカル環境にインストールしてください。

```bash
リポジトリをクローン
git clone https://github.com/kobashin/KakeiBot.git

以下、編集中。

ディレクトリに移動
cd repository

依存関係をインストール
pip install -r requirements.txt```

## 使い方

実行方法の例

```python main.py --option value```

## サンプル

サンプルコード

```print("Hello, World!")```

## ライセンス

このプロジェクトはMITライセンスのもとで公開されています。

## 貢献

貢献方法は以下の通りです。

1.フォークする。
2.新しいブランチを作成する。(git checkout -b feature/YourFeature)
3.コードをコミットする。(git commit -m 'Add some feature')
4.プッシュする。(git push origin feature/YourFeature)
5.プルリクエストを作成する。

## クレジット
(使用したライブラリや貢献者の名前を記す。)

## 参考文献
https://note.com/tomisan/n/ne5d7fbd55507
https://developers.line.biz/ja/
https://manager.line.biz/
https://developers.line.biz/ja/docs/messaging-api/getting-started/
https://developers.line.biz/ja/docs/messaging-api/building-bot/
https://developers.line.biz/ja/docs/messaging-api/getting-user-ids/#page-title
https://github.com/line/line-bot-sdk-python
https://lineapiusecase.com/ja/api/webhook.html
https://developers.line.biz/ja/docs/messaging-api/building-bot/
https://zenn.dev/tn_a/articles/649c57463de040

https://qiita.com/matsuyu2511/items/020e5694ea468230dd6e
https://zenn.dev/enumura/articles/71d88d98bc7052

DuC

