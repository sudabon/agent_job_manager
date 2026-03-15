## Why

AIエージェントや自動化ワークフローが生成した Python コードを安全に実行し、結果を API 経由で取得できる基盤が必要である。セルフホスト可能なジョブ実行サーバの MVP を構築し、非同期ジョブ処理・Docker 隔離実行・状態管理・ログ取得を実現する。

## What Changes

- APIキー認証付きの REST API を新規構築する
- Python コードをジョブとして受け付け、Docker コンテナ内で隔離実行する仕組みを導入する
- ジョブの非同期処理基盤（Queue + Worker）を構築する
- ジョブ状態管理（queued → running → succeeded/failed/timed_out）を実装する
- 実行結果（stdout/stderr/exit_code）の保存・取得 API を提供する
- タイムアウト制御を実装する
- ヘルスチェック API を提供する
- PostgreSQL によるデータ永続化を導入する

## Capabilities

### New Capabilities

- `api-key-auth`: APIキー認証。キーのハッシュ保存、論理名管理、全ジョブ系APIの認証必須化
- `job-submission`: Pythonジョブの登録。コード・タイムアウト・メタデータの受付とバリデーション
- `job-execution`: Docker コンテナによるジョブの隔離実行。タイムアウト制御、一時ワークディレクトリ分離
- `job-query`: ジョブ一覧取得（ページング・ステータス絞り込み）、ジョブ詳細取得、ジョブログ取得
- `job-state-management`: ジョブ状態遷移管理（queued/running/succeeded/failed/timed_out）とドメインルール
- `async-job-processing`: Queue による非同期ジョブ処理基盤。Worker プロセスによるジョブ取得・実行・結果保存
- `health-check`: Liveness / Readiness ヘルスチェック API

### Modified Capabilities

（既存specなし）

## Impact

- **コード**: backend/ 配下に Clean Architecture に基づく全層（domain/app/infra/interface）を新規構築
- **API**: `/v1/jobs/python`, `/v1/jobs`, `/v1/jobs/{job_id}`, `/v1/jobs/{job_id}/logs`, `/health/live`, `/health/ready` を新規追加
- **依存関係**: FastAPI, SQLAlchemy, Alembic, Redis（Queue）, Docker SDK を追加
- **インフラ**: PostgreSQL, Redis, Docker Engine が必要
- **テスト**: domain/app 層のユニットテスト、API 統合テスト、E2E テストを整備
