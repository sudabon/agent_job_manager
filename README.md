# Agent Job Manager

AIエージェントが Python コードをサブミットし、Docker コンテナ内で安全に実行するジョブ管理サーバ。

## 特徴

- **コード実行の隔離**: Docker コンテナによるサンドボックス実行（ネットワーク無効・メモリ制限）
- **非同期ジョブキュー**: arq + Redis によるジョブのキューイングとワーカー実行
- **APIキー認証**: SHA-256 ハッシュによるキー管理。キーごとにジョブを分離
- **Clean Architecture**: domain / app / infra / interface の4層構成
- **ヘルスチェック**: liveness / readiness エンドポイント（DB・Redis の疎通確認）

## 技術スタック

| カテゴリ | 技術 |
|---------|------|
| 言語 | Python 3.13 |
| フレームワーク | FastAPI |
| DB | PostgreSQL 16 |
| キュー | arq (Redis 7) |
| ジョブ実行 | Docker (python:3.12-slim) |
| ORM | SQLAlchemy 2.0 (async) |
| マイグレーション | Alembic |
| パッケージ管理 | uv |

## セットアップ

### 前提条件

- Docker / Docker Compose
- Python 3.13+
- uv

### 起動

```bash
# 全サービス起動（PostgreSQL, Redis, API, Worker）
docker compose up

# マイグレーション適用
cd backend
uv run alembic upgrade head

# APIキー作成
uv run python -m src.infra.cli.create_api_key --name "my-agent"
```

### 開発

```bash
cd backend
uv sync
uv run uvicorn src.main:app --reload  # http://localhost:8000
uv run arq src.infra.queue.worker.WorkerSettings
```

## API

すべてのジョブ関連エンドポイントは `X-API-Key` ヘッダが必要。

### ジョブ投入

```
POST /v1/jobs/python
```

```json
{
  "code": "print('Hello')",
  "timeout_sec": 30,
  "metadata": {}
}
```

### ジョブ一覧

```
GET /v1/jobs?page=1&per_page=20&status=succeeded
```

### ジョブ詳細

```
GET /v1/jobs/{job_id}
```

### ジョブログ取得

```
GET /v1/jobs/{job_id}/logs
```

### ヘルスチェック

```
GET /health/live
GET /health/ready
```

## ジョブの状態遷移

```
queued → running → succeeded
                 → failed
                 → timed_out
```

## 環境変数

`AJM_` プレフィックスで設定する。主要な項目:

| 変数 | デフォルト | 説明 |
|------|-----------|------|
| `AJM_DATABASE_URL` | `postgresql+asyncpg://...` | DB接続文字列 |
| `AJM_REDIS_URL` | `redis://localhost:6379/0` | Redis接続文字列 |
| `AJM_DEFAULT_TIMEOUT_SEC` | `30` | デフォルトタイムアウト |
| `AJM_MAX_TIMEOUT_SEC` | `300` | 最大タイムアウト |
| `AJM_MAX_CODE_SIZE_BYTES` | `65536` | コードサイズ上限 |
| `AJM_MAX_LOG_BYTES` | `1048576` | ログサイズ上限 |
| `AJM_DOCKER_MEMORY_LIMIT` | `256m` | コンテナメモリ制限 |
| `AJM_DOCKER_BASE_IMAGE` | `python:3.12-slim` | 実行用Dockerイメージ |

## テスト

```bash
cd backend
uv run pytest                    # 全テスト
uv run pytest tests/unit/        # ユニットテスト
uv run pytest tests/integration/ # 統合テスト
uv run ruff check .              # リント
uv run mypy src/                 # 型チェック
```

## ディレクトリ構成

```
backend/src/
├── main.py              # FastAPI アプリケーション起動
├── domain/              # ドメイン層（エンティティ・状態遷移ルール）
├── app/                 # アプリケーション層（ユースケース・DTO・リポジトリIF）
├── infra/               # インフラ層（DB・Docker・Redis・設定）
└── interface/           # インターフェース層（コントローラ・ビューモデル）
```

詳細は [AGENTS.md](./AGENTS.md) を参照。
