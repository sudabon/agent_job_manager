## Context

本プロジェクトは新規構築であり、既存コードベースは backend/frontend の雛形のみ存在する。
REQUIREMENTS.md に定義された MVP 仕様に基づき、AIエージェント用ジョブ実行サーバの初期実装を行う。
技術スタックは Python 3.13 / FastAPI / SQLAlchemy / PostgreSQL / Redis / Docker であり、Clean Architecture（domain / app / infra / interface の4層）に従う。

## Goals / Non-Goals

**Goals:**

- REQUIREMENTS.md セクション3〜12に定義された MVP 機能をすべて実装する
- Clean Architecture の依存方向を厳守し、テスト容易性を確保する
- APIキー認証によるセキュアなジョブ登録・参照を実現する
- Docker コンテナによる隔離実行とタイムアウト制御を実装する
- 非同期ジョブ処理基盤（Redis Queue + Worker）を構築する

**Non-Goals:**

- v0.2 機能（artifact保存、ジョブキャンセル、再実行、Web UI）
- v0.3 機能（実行ポリシー、リトライ制御、レート制限、Webhook、監査ログ）
- 本番運用レベルのサンドボックス保証
- Kubernetes 前提の分散実行
- フロントエンド実装（MVP スコープ外）

## Decisions

### 1. Queue 実装: Redis + arq

**決定**: Redis をメッセージブローカーとし、arq（async Redis queue）を Worker フレームワークとして採用する。

**理由**: arq は FastAPI と同じ asyncio ベースで親和性が高く、軽量かつシンプル。Celery は機能過多で MVP には不要。Redis は Readiness チェックの対象にもなるため、Queue と共用できる。

**代替案**: Celery + Redis（機能過多）、PostgreSQL LISTEN/NOTIFY（スケーラビリティに課題）、インメモリキュー（永続性なし）

### 2. Docker 実行: Docker SDK for Python

**決定**: `docker` パッケージ（Docker SDK for Python）を使用し、コンテナのライフサイクルを管理する。

**理由**: subprocess で `docker run` を呼ぶより型安全で、タイムアウト制御やログ取得が容易。公式 SDK であり保守性が高い。

**代替案**: subprocess + docker CLI（エラーハンドリングが煩雑）

### 3. APIキー認証方式

**決定**: APIキーは `X-API-Key` ヘッダーで送信する。サーバ側では SHA-256 ハッシュを DB に保存し、リクエスト時に照合する。

**理由**: シンプルかつ一般的な方式。MVP では OAuth2 や JWT は不要。

**代替案**: Bearer トークン（JWT が必要になり複雑）、Basic 認証（パスワード管理が必要）

### 4. ジョブID生成: ULID

**決定**: ジョブIDおよびAPIキーIDには ULID を使用する。プレフィックス付き（`job_`、`ak_`）で可読性を確保する。

**理由**: 時系列ソート可能、UUID v4 より衝突率が低く、URL セーフ。

**代替案**: UUID v4（時系列ソート不可）、連番（分散環境で衝突）

### 5. DB マイグレーション: Alembic

**決定**: AGENTS.md に記載の通り Alembic を使用する。

### 6. Worker プロセス構成

**決定**: API サーバとは別プロセスで Worker を起動する。Worker は arq の WorkerSettings に従い Redis からジョブを取得し、Docker コンテナで実行する。

**理由**: API サーバの応答性を維持し、ジョブ実行の負荷を分離する。

### 7. Python 実行用 Docker イメージ

**決定**: 公式 `python:3.12-slim` イメージを使用する。ネットワークは無効化し、メモリ制限を設ける。

**理由**: 軽量で起動が速い。セキュリティのため最小限のイメージを使用する。

### 8. ログサイズ制限

**決定**: stdout/stderr それぞれ最大 1MB に制限する。超過分は切り捨てる。

**理由**: 悪意あるコードや無限ループによる DB 肥大化を防ぐ。

## Risks / Trade-offs

- **[Docker Engine 依存]** → 開発・実行環境に Docker が必須。テスト時はモック DockerRunner で代替可能にする。
- **[単一 Worker のスケーラビリティ]** → MVP では単一 Worker で十分。v0.2 以降で Worker 数のスケールアウトを検討する。
- **[コンテナ起動のオーバーヘッド]** → ジョブごとにコンテナを起動するため数秒のレイテンシが発生する。MVP では許容する。
- **[Redis の SPOF]** → MVP では単一 Redis インスタンス。v0.3 以降で冗長化を検討する。
- **[stdout/stderr の切り捨て]** → 1MB 制限により大量出力が失われる可能性がある。制限超過時はログにその旨を記録する。
