## 1. 共通ユーティリティの導入（H3: ID 生成の集約）

- [x] 1.1 `backend/src/infra/identity/__init__.py` を作成する
- [x] 1.2 `backend/src/infra/identity/identifier.py` に `new_id() -> str` を実装する（ULID 優先・`ImportError` 時のみ UUID にフォールバック）
- [x] 1.3 `app/usecase/submit_python_job.py` の `_default_ulid_factory` を削除し、`ulid_factory` のデフォルトを `new_id` に差し替える
- [x] 1.4 `infra/cli/create_api_key.py` の `_new_identifier` を削除し、`new_id` を使うよう書き換える
- [x] 1.5 `tests/unit/` に `new_id` の単体テストを追加（ULID あり／なしの両ケース、戻り値が文字列で空でないこと）
- [x] 1.6 `uv run pytest` 全通過と `uv run ruff check .` を確認

## 2. 所有権チェックの共通化（H5）

- [x] 2.1 `backend/src/app/usecase/_job_access.py` に `find_owned_job(repo: JobRepository, job_id: JobId, owner: ApiKeyId) -> Job` を実装する（`JobNotFound` を投げる）
- [x] 2.2 `app/usecase/get_job.py` を `find_owned_job` 利用に書き換える
- [x] 2.3 `app/usecase/get_job_logs.py` を `find_owned_job` 利用に書き換える
- [x] 2.4 `tests/unit/app/test_job_usecases.py` の既存ケースを更新し、ヘルパ単体のテストも追加する
- [x] 2.5 `uv run pytest tests/unit/app/` 通過を確認

## 3. JobRepository の単一マッパー化（H4）

- [x] 3.1 `backend/src/infra/persistence/mappers/__init__.py` を作成する
- [x] 3.2 `backend/src/infra/persistence/mappers/job_mapper.py` に `to_model(job: Job) -> JobModel`、`apply_to_model(job: Job, model: JobModel) -> None`、`to_domain(model: JobModel) -> Job` を移設する
- [x] 3.3 `infra/persistence/job_repository.py` の `_to_model` / `_to_domain` を削除し、`mappers.job_mapper` を呼ぶように書き換える
- [x] 3.4 `update()` を「`session.get` → `apply_to_model(job, model)` → `commit`」の単一経路に整理し、デッドな add フォールバック分岐を削除する
- [x] 3.5 `tests/integration/infra/test_sqlalchemy_repositories.py` に「先に `add` していない `update` 呼び出し時の挙動」をテストとして固定する（事前 `add` を前提とする現仕様の明文化）
- [x] 3.6 `uv run pytest tests/integration/infra/` 通過を確認

## 4. Job エンティティの責務分離（H7: JobExecution Value Object）

- [x] 4.1 `backend/src/domain/entity/job.py` に frozen dataclass `JobExecution(started_at, finished_at, exit_code, stdout, stderr, error_type)` を追加する
- [x] 4.2 `Job` から該当 6 フィールドを除き、`execution: JobExecution | None = None` に置き換える（既存の `created_at`, `status` 等は据え置き）
- [x] 4.3 `JobDomainService.mark_running` / `mark_finished` を `JobExecution` を生成して `replace(job, execution=...)` するよう書き換える
- [x] 4.4 `app/dto/job.py` の `JobDetailOutput.from_job` を `job.execution` 経由のアクセスに更新する（DTO の外部フィールド構造は維持）
- [x] 4.5 `infra/persistence/mappers/job_mapper.py` で `JobModel` の各フィールド ↔ `Job.execution` の双方向マッピングを実装する
- [x] 4.6 `tests/unit/domain/test_job_domain_service.py` の `mark_running` / `mark_finished` テストが新構造で同値判定できるよう更新する
- [x] 4.7 `tests/unit/app/test_job_usecases.py` を新構造に追従させる
- [x] 4.8 `uv run pytest` 全通過を確認

## 5. DI の usecase 単位分割（H6）

- [x] 5.1 `backend/src/app/usecase/submit_python_job.py` に `JobSubmissionLimits` dataclass を追加し、コンストラクタ引数を `(repo, queue, service, limits, *, ulid_factory, now_provider)` に短縮する
- [x] 5.2 `infra/web/dependencies.py` に `get_job_presenter`、`get_submit_use_case`、`get_get_job_use_case`、`get_list_jobs_use_case`、`get_get_job_logs_use_case` の各 provider を実装する
- [x] 5.3 `get_job_repository` を `get_job_controller` 内でも経由させて、リポジトリ生成経路を一本化する
- [x] 5.4 `get_job_controller` を上記 provider を `Depends` で受け取るだけの形に縮める
- [x] 5.5 `tests/integration/interface/test_job_api.py` の DI 上書き（fixture）を新 provider 名に追従させる
- [x] 5.6 `uv run pytest` 全通過を確認

## 6. 命名揺れの解消（H8: presender → presenter / src/worker.py 削除）

- [x] 6.1 `backend/src/interface/presender/` を `backend/src/interface/presenter/` にリネームする
- [x] 6.2 リネームに伴う `import` 文を全置換する（`src/interface/controller/`, `src/infra/web/dependencies.py`, テスト一式）
- [x] 6.3 `tests/arch/test_source_structure.py` のディレクトリ名規約を `presenter` に更新する
- [x] 6.4 `AGENTS.md` のディレクトリ構成図中 `presender` 表記を `presenter` に修正する
- [x] 6.5 `backend/src/worker.py` を削除する
- [x] 6.6 README / docker-compose / pyproject 等の Worker 起動コマンドを `arq src.infra.queue.worker.WorkerSettings` に統一する
- [x] 6.7 `uv run pytest` 全通過を確認

## 7. error-response-policy の実装（H1 + H2）

- [x] 7.1 `app/usecase/submit_python_job.py` の `try / except InvalidTimeout → ValidationError` 翻訳を削除し、ドメイン例外を素のまま伝播させる
- [x] 7.2 `infra/web/middleware/error_handling.py` に `_EXCEPTION_TO_STATUS: dict[type[Exception], int]` を定義し、`AuthenticationFailed=401`, `JobNotFound=404`, `ValidationError=400`, `InvalidEntity=400`, `InvalidTimeout=400`, `InvalidJobStateTransition=400` をマップする
- [x] 7.3 マッピングテーブルに無い `Exception` を 500 にフォールバックさせ、レスポンスボディを `{"detail": "internal server error", "request_id": <id>}` 固定に変更する（`str(exc)` を排除）
- [x] 7.4 `request_id` を `request.state.request_id` から取得し、未設定時は `"-"` などの安全な既定値に置き換える
- [x] 7.5 5xx 時に `LOGGER.exception("unhandled exception", extra={"request_id": ...})` で構造化ログ出力する（仕様書の Scenario「詳細はログにのみ記録」を満たす）
- [x] 7.6 `tests/integration/interface/` に「未知例外発生時に 500 ボディが固定文言になる」「ボディに例外メッセージが含まれない」「`X-Request-Id` ヘッダがボディと一致する」を検証する統合テストを追加する
- [x] 7.7 `tests/integration/interface/test_job_api.py` の既存 4xx 系テストが新ミドルウェア構成で引き続き通過することを確認する
- [x] 7.8 `uv run pytest` 全通過、`uv run ruff check .`、`uv run mypy src/` を確認

## 8. 仕上げ

- [x] 8.1 `tests/arch/test_dependency_rule.py` のレイヤ依存テストが新規モジュール（`infra/identity/`、`infra/persistence/mappers/`、`app/usecase/_job_access.py`）でも通過することを確認する
- [x] 8.2 `openspec validate refactor-backend-quality-fixes --strict` を実行し、change の整合性を最終確認する
- [x] 8.3 各タスクのコミットを `feat:` `refactor:` `fix:` の慣習に従って分割（H7 リファクタは `refactor:`、H1 セキュリティ修正は `fix:` で記録）
