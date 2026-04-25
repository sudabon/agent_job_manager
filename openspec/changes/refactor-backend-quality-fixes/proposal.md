## Why

バックエンド `backend/src/` のコードレビューで、(1) 500 応答に内部例外メッセージがそのまま漏れるセキュリティ問題、(2) 例外マッピング・所有権チェック・ID 生成・ORM フィールド代入の重複と更新漏れリスク、という保守性とセキュリティの両面に関わる問題を確認した。MVP の振る舞いを変えずに早期に解消することで、以後の機能追加（FE 接続、ジョブ種別の追加等）で同じ落とし穴を踏まないようにする。

## What Changes

- **BREAKING**（外向き）: `5xx` 応答のレスポンスボディから内部例外メッセージを除去し、固定の `{"detail": "internal server error", "request_id": "..."}` を返す（4xx は従来どおり日本語/英語のドメインメッセージを保持）
- 例外 → HTTP の変換責務を `ErrorHandlingMiddleware` に集約し、`SubmitPythonJobUseCase` 内の `InvalidTimeout` → `ValidationError` 翻訳を削除（middleware が直接 400 にマップ）
- ULID／UUID フォールバック関数 `_default_ulid_factory` と `_new_identifier` の重複を `infra/identity/identifier.py` の `new_id()` に統合し、import 失敗の握りつぶしを `ImportError` に絞る
- `SqlAlchemyJobRepository.update()` のフィールド毎代入と `_to_model()` の二重定義を「単一マッパー＋ `session.merge`」に統一し、デッドコード（add フォールバック）を削除
- `GetJobUseCase` / `GetJobLogsUseCase` に重複する「取得＋所有権チェック＋ `JobNotFound`」を共通ヘルパ（`find_owned_job`）に抽出
- `infra/web/dependencies.get_job_controller` の手動 DI を usecase 単位の provider に分割
- `Job` エンティティの実行結果系 6 フィールドを Value Object `JobExecution` に分離（内部のみ。外部 API 形は不変）
- `presender/` ディレクトリ名（typo）→ `presenter/` にリネーム
- `src/worker.py`（薄い arq 起動エントリ）を削除、起動コマンドを `arq src.infra.queue.worker.WorkerSettings` に統一

## Capabilities

### New Capabilities

- `error-response-policy`: API 全体に共通する HTTP エラー応答の仕様。例外型→ステータスコードのマッピングと、5xx 時に内部例外文字列を露出させない情報漏洩防止ポリシーを規定する。

### Modified Capabilities

なし（H2〜H5 はいずれも内部実装の整理であり、ユーザ向けの振る舞い・契約は変わらない。`async-job-processing` `job-submission` `job-query` 等の既存仕様は据え置き）。

## Impact

- **影響コード（変更）**: `backend/src/infra/web/middleware/error_handling.py`, `backend/src/app/usecase/submit_python_job.py`, `backend/src/app/usecase/get_job.py`, `backend/src/app/usecase/get_job_logs.py`, `backend/src/infra/persistence/job_repository.py`, `backend/src/infra/web/dependencies.py`, `backend/src/domain/entity/job.py`, `backend/src/domain/service/job_domain_service.py`, `backend/src/infra/cli/create_api_key.py`
- **影響コード（新規）**: `backend/src/infra/identity/identifier.py`, `backend/src/infra/persistence/mappers/job_mapper.py`（任意）
- **影響コード（リネーム/削除）**: `backend/src/interface/presender/` → `presenter/`、`backend/src/worker.py` 削除
- **API への影響**: 5xx ボディ形式が変わる（`detail` が固定文字列になる）。4xx 系および 2xx 系の挙動は不変
- **ドキュメント**: `AGENTS.md` のディレクトリ構成図中 `presender` 表記を `presenter` に修正
- **依存パッケージ**: 追加なし
- **マイグレーション**: なし
- **テスト**: 既存のアーキテクチャテスト・統合テストはディレクトリ名変更に追従が必要。500 応答ボディの assertion がある場合は更新
