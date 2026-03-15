## 1. プロジェクト基盤セットアップ

- [x] 1.1 backend/ に uv プロジェクトを初期化し、FastAPI, SQLAlchemy, Alembic, arq, docker, pydantic-settings, ulid 等の依存パッケージを追加する
- [x] 1.2 infra/config/ に pydantic-settings ベースの設定クラスを作成する（DB URL, Redis URL, Docker イメージ名, タイムアウト上下限等）
- [x] 1.3 infra/persistence/ に SQLAlchemy async セッション管理を実装する
- [x] 1.4 Alembic を初期化し、async 対応の設定を行う
- [x] 1.5 infra/logging/ に構造化ログ設定を実装する（request_id, job_id 対応）
- [x] 1.6 docker-compose.yml を作成する（PostgreSQL, Redis, API サーバ, Worker）

## 2. Domain層

- [x] 2.1 domain/entity/ に JobId, Job エンティティを作成する（dataclass）
- [x] 2.2 domain/entity/ に JobStatus 列挙型を作成する（queued, running, succeeded, failed, timed_out）
- [x] 2.3 domain/entity/ に ApiKeyId, ApiKey エンティティを作成する
- [x] 2.4 domain/entity/ に JobType 列挙型を作成する（python）
- [x] 2.5 domain/entity/ に ErrorType 列挙型を作成する（timeout, execution_error, oom 等）
- [x] 2.6 domain/service/ に JobDomainService を作成する（状態遷移バリデーション）
- [x] 2.7 domain 層のユニットテストを作成する（状態遷移ルール、タイムアウトバリデーション）

## 3. Application層

- [x] 3.1 app/repository/ に JobRepository 抽象クラスを定義する
- [x] 3.2 app/repository/ に ApiKeyRepository 抽象クラスを定義する
- [x] 3.3 app/port/ に JobRunnerPort 抽象クラスを定義する（Docker 実行の抽象化）
- [x] 3.4 app/port/ に JobQueuePort 抽象クラスを定義する（Queue 投入の抽象化）
- [x] 3.5 app/dto/ にジョブ登録の入出力 DTO を定義する
- [x] 3.6 app/dto/ にジョブ一覧・詳細・ログ取得の入出力 DTO を定義する
- [x] 3.7 app/common/ に共通エラークラスを定義する（JobNotFound, InvalidJobStateTransition, AuthenticationFailed 等）
- [x] 3.8 app/usecase/ に SubmitPythonJobUseCase を実装する
- [x] 3.9 app/usecase/ に GetJobUseCase を実装する
- [x] 3.10 app/usecase/ に ListJobsUseCase を実装する（ページング・ステータス絞り込み対応）
- [x] 3.11 app/usecase/ に GetJobLogsUseCase を実装する
- [x] 3.12 app/usecase/ に ExecuteJobUseCase を実装する（Worker から呼ばれる: 状態遷移 + Docker 実行 + 結果保存）
- [x] 3.13 app 層のユニットテストを作成する（各 usecase の正常系・異常系）

## 4. Infrastructure層 - データ永続化

- [x] 4.1 infra/persistence/ に SQLAlchemy の Job モデルを作成する
- [x] 4.2 infra/persistence/ に SQLAlchemy の ApiKey モデルを作成する
- [x] 4.3 Alembic マイグレーションを作成する（jobs, api_keys テーブル、インデックス）
- [x] 4.4 infra/persistence/ に JobRepository の具象実装を作成する
- [x] 4.5 infra/persistence/ に ApiKeyRepository の具象実装を作成する

## 5. Infrastructure層 - Docker Runner

- [x] 5.1 infra/runner/ に DockerRunner（JobRunnerPort 実装）を作成する
- [x] 5.2 DockerRunner にコンテナ起動・コード実行・結果取得ロジックを実装する
- [x] 5.3 DockerRunner にタイムアウト制御を実装する
- [x] 5.4 DockerRunner にネットワーク無効化・メモリ制限を実装する
- [x] 5.5 DockerRunner にログサイズ制限（stdout/stderr 各 1MB）を実装する
- [x] 5.6 DockerRunner にコンテナの後片付けロジックを実装する

## 6. Infrastructure層 - Queue & Worker

- [x] 6.1 infra/queue/ に arq ベースの JobQueue（JobQueuePort 実装）を作成する
- [x] 6.2 infra/queue/ に arq Worker の設定・起動コードを作成する
- [x] 6.3 Worker の job handler を実装する（ExecuteJobUseCase を呼び出す）

## 7. Infrastructure層 - 認証

- [x] 7.1 infra/auth/ に APIキーのハッシュ化・照合ユーティリティを作成する（SHA-256）
- [x] 7.2 infra/cli/ に APIキー作成の CLI コマンドを実装する

## 8. Interface層

- [x] 8.1 interface/controller/ に JobController を作成する（usecase 呼び出し + viewmodel 変換）
- [x] 8.2 interface/controller/ に HealthController を作成する
- [x] 8.3 interface/viewmodel/ にジョブ関連の ViewModel を定義する
- [x] 8.4 interface/viewmodel/ にヘルスチェックの ViewModel を定義する
- [x] 8.5 interface/presender/ に必要な型変換ロジックを実装する
- [x] 8.6 infra/web/ に FastAPI ルーター定義を作成する（/v1/jobs/python, /v1/jobs, /v1/jobs/{job_id}, /v1/jobs/{job_id}/logs）
- [x] 8.7 infra/web/ にヘルスチェックルーター定義を作成する（/health/live, /health/ready）
- [x] 8.8 infra/web/ に APIキー認証の Depends を実装する
- [x] 8.9 infra/web/ にエラーハンドリング Middleware を実装する（ドメインエラー → HTTP ステータス変換）
- [x] 8.10 infra/web/ に request_id Middleware を実装する

## 9. アプリケーション統合

- [x] 9.1 src/main.py に FastAPI アプリの組み立て（DI 設定、ルーター登録、Middleware 登録）を実装する
- [x] 9.2 Worker 起動用のエントリポイントを作成する

## 10. テスト

- [x] 10.1 domain 層のユニットテストを作成する（状態遷移、バリデーション）
- [x] 10.2 app 層のユニットテストを作成する（各 usecase のモックテスト）
- [x] 10.3 infra/persistence 層の統合テストを作成する（実 DB 使用）
- [x] 10.4 interface 層の統合テストを作成する（FastAPI TestClient 使用）
- [x] 10.5 pytest の conftest.py にフィクスチャを整備する
