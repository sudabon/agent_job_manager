---
globs: ["backend/**"]
---
# バックエンド コーディング規約

## 全般

- 型ヒントは必ず付与する。`Any` の使用は最小限に。
- docstringはpublicなクラス・関数に付与する（Google style）。
- 変数名・関数名は snake_case、クラス名は PascalCase。
- マジックナンバーは定数として定義する。
- async/await を一貫して使用する。sync関数と混在させない。

## Domain層

- entity は `dataclass` または Pydantic の `BaseModel` で定義する。
- entity にバリデーションロジックを持たせてよい（ドメイン不変条件）。
- ドメインサービスはステートレスにする。

## Application層

- usecase クラスは1つのパブリックメソッド（`execute` 等）を持つ。
- リポジトリは抽象基底クラス（`ABC`）として `app/repository/` で定義する。
- 外部サービスの機能インターフェースは `app/port/` で定義する（通知・外部API等）。
- DTO は Pydantic `BaseModel` で定義し、入出力を明確にする。
- 共通の結果クラスやエラークラスは `app/common/` に配置する。

## Infrastructure層

- SQLAlchemy モデルは `infra/persistence/` に配置する（domain の entity とは分離）。
- infra → domain entity の変換メソッドを用意する。
- 外部APIクライアント等もこの層に配置する。
- app の port インターフェースの具象実装をこの層に配置する。
- 設定値は `infra/configuration/` に集約し、`pydantic-settings` 等で環境変数から取得する。
- ロギングの設定・フォーマットは `infra/logging/` に配置する。

## Interface層

- router は薄く保ち、ロジックは controller に委譲する。
- controller は usecase を呼び出し、結果を viewmodel に変換して返す。
- FastAPI の `Depends` を使って usecase やリポジトリをDI注入する。
- リクエストバリデーションは Pydantic スキーマ（dto）で行う。
