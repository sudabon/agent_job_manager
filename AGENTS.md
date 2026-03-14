# AGENTS.md

このファイルはClaude Codeがリポジトリを操作する際のガイドラインである。
詳細なルールは `.claude/rules/` に分割して配置している。

## プロジェクト概要

モノレポ構成のWebアプリケーション。

- **バックエンド** (`backend/`): Python 3.13 / FastAPI。Clean Architectureに基づく4層構成。
- **フロントエンド** (`frontend/`): React / TypeScript / Vite / TailwindCSS。

## ディレクトリ構成

```
├── backend/                   # バックエンド
│   ├── src/
│   │   ├── main.py            # サーバプロセス管理
│   |   ├── app/              # Application層
│   |   │   ├── common/       # 共通で利用する結果クラスやエラークラスなど
│   |   │   ├── dto/          # Data Transfer Object（層間のデータ受け渡し）
│   |   │   ├── repository/   # データ永続化のためインタフェース定義（抽象クラス）
│   |   │   ├── port/         # 外部サービス機能のインターフェース定義（抽象クラス）
│   |   │   └── usecase/      # ビジネスロジックの実行フロー
│   |   ├── domain/           # Domain層
│   |   │   ├── entity/       # エンティティ（ドメインモデル）
│   |   │   └── service/      # ドメインサービス（エンティティ横断ロジック）
│   |   ├── infra/            # Infrastructure層
│   |   │   ├── cli/          # CLIコマンド
│   |   │   ├── config/       # 設定（環境変数・アプリ設定）
│   |   │   ├── notification/ # 通知（メール・Slack等）
│   |   │   ├── logging/      # ロギング
│   |   │   ├── persistence/  # データ永続化（RDBMS・NoSQL・Memory）
│   |   │   └── web/          # Web関連（FastAPIルーター定義・Middleware）
│   |   └── interface/        # Interface層
│   |       ├── controller/   # 入力リクエスト処理
│   |       ├── presender/    # 出力変換（domain固有の型をviewmodel固有の型へ変換）
│   |       └── viewmodel/    # レスポンス整形用ViewModel
|   └── tests                 # 単体テスト
│       ├── arch/             # クリーンアーキテクチャのテスト
│       ├── app/              # Application層の単体テスト
│       ├── domain/           # Domain層の単体テスト
│       ├── infra/            # Infrastructure層の単体テスト
│       └── interface/        # Interface層の単体テスト
├── frontend/                 # フロントエンド
│   ├── src/
│   │   ├── components/       # UIコンポーネント（Shadcn/ui ベース）
│   │   ├── pages/            # ページコンポーネント
│   │   ├── hooks/            # カスタムフック
│   │   ├── lib/              # ユーティリティ・API クライアント
│   │   ├── types/            # 型定義
│   │   └── routes/           # React Router ルート定義
│   ├── e2e/                  # Playwright E2Eテスト
│   ├── package.json
│   └── vite.config.ts
```

## 技術スタック

### バックエンド

- **言語**: Python 3.13
- **フレームワーク**: FastAPI
- **パッケージ管理**: uv
- **ORM**: SQLAlchemy（asyncio対応）
- **DB**: PostgreSQL
- **マイグレーション**: Alembic
- **テスト**: pytest
- **リンター**: Ruff
- **型チェック**: mypy
- **DI**: FastAPIの `Depends` を利用（API認証等）

### フロントエンド

- **言語**: TypeScript
- **フレームワーク**: React
- **ビルドツール**: Vite
- **パッケージ管理**: pnpm
- **UIライブラリ**: Shadcn/ui + TailwindCSS
- **データ取得**: TanStack Query
- **ルーティング**: React Router
- **テスト**: Vitest（ユニット）/ Playwright（E2E）
- **リンター**: ESLint

## コマンド

### バックエンド

```bash
# 開発環境
uv sync                        # 依存パッケージのインストール
uv run uvicorn src.main:app --reload   # 開発サーバー起動

# テスト
uv run pytest                  # テスト全体実行
uv run pytest tests/unit/      # ユニットテストのみ
uv run pytest tests/integration/  # 統合テストのみ
uv run pytest -x               # 最初の失敗で停止
uv run pytest -k "test_name"   # 特定テストの実行

# リント・型チェック
uv run ruff check .            # リントチェック
uv run ruff check . --fix      # 自動修正
uv run ruff format .           # フォーマット
uv run mypy src/               # 型チェック

# マイグレーション
uv run alembic upgrade head    # 最新までマイグレーション適用
uv run alembic revision --autogenerate -m "説明"  # マイグレーション作成
uv run alembic downgrade -1    # 1つ前にロールバック
```

### フロントエンド

```bash
cd frontend
pnpm install                   # 依存パッケージのインストール
pnpm dev                       # 開発サーバー起動
pnpm test                      # Vitest ユニットテスト実行
pnpm test:e2e                  # Playwright E2Eテスト実行
pnpm lint                      # ESLint チェック
pnpm build                     # プロダクションビルド
```

## 注意事項

- DBのURL等はすべて環境変数から取得する（`pydantic-settings` 推奨）。
- バックエンド・フロントエンド間の型定義の乖離に注意する。APIスキーマを信頼の源泉とする。
