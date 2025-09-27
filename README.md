url:http://13.236.185.251/
# 概要

このプロジェクトは、Vue 3 + TypeScript のフロントエンドと Django + Django REST Framework のバックエンドを組み合わせた小説ランキングシステムです。ユーザーは年代別に小説を閲覧し、ショッピングカート機能を利用できます。ここで初めてVue 3のComposition APIと非同期通信を使用し、またPiniaを使った状態管理も初めて取り入れました。

# 主な使用技術

1. フロントエンド：Vue 3、TypeScript、Pinia、Vue Router、Vite
2. バックエンド：Python、Django、Django REST Framework
3. データベース：SQLite
4. その他：Git、Gunicorn（デプロイ）、AWS EC2（ホスティング）

# 機能一覧

- ログイン・登録機能 ：ユーザーアカウントの作成と認証を実現
- 年代別小説表示 ：YearSelectorコンポーネントを使って特定の年代の小説をフィルタリング
- ショッピングカート機能 ：小説をカートに追加・削除、カート内商品の管理
