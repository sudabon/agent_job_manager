## Context

`backend/src/` は Clean Architecture 4 層（domain / app / infra / interface）で構成されており、レイヤ規約はおおむね守られている。一方で MVP 段階の実装コードに以下の症状が累積していた。

- 例外 → HTTP 応答変換が `infra/web/middleware/error_handling.py` と `app/usecase/submit_python_job.py` の 2 箇所に分散しており、500 系応答ボディに `str(exc)` が露出する。
- ULID/UUID フォールバック関数が `app/usecase/submit_python_job.py` と `infra/cli/create_api_key.py` に同形で重複している。
- `SqlAlchemyJobRepository.update()` のフィールド毎代入と `_to_model()` の項目構築が二重定義になっており、`Job` エンティティのフィールド追加で更新漏れが起きやすい。`update()` 内の "model 不在時の add" 分岐は呼び出しシーケンス上デッドコード。
- `GetJobUseCase` / `GetJobLogsUseCase` に「取得 → 所有権比較 → `JobNotFound`」が完全同形で重複している。
- `infra/web/dependencies.get_job_controller` が 4 つの usecase と repo・queue・presender を 1 関数で手組みしており、Settings からの引数伝搬と相まって肥大化している。
- `interface/presender/` は `presenter` のスペル誤り。`src/worker.py`（8 行）と `src/infra/queue/worker.py` でモジュール名が衝突気味。

外部 API 契約は `openspec/specs/` 各 spec で固定されており、4xx 系の挙動を変えてはならない。一方で 5xx 応答ボディは現行 spec に明示の規定がなく、内部メッセージの露出を「ポリシー違反」と再定義することは可能。

## Goals / Non-Goals

**Goals:**
- 5xx 応答から内部例外文字列を排除し、情報漏洩リスクを除去する。
- 例外 → HTTP のマッピングを 1 箇所（middleware）に集約し、二重定義を解消する。
- ID 生成・所有権チェック・ORM マッピングの重複を共通化し、エンティティ拡張時の更新漏れリスクを下げる。
- 依存組み立て（DI）を usecase 単位の provider に分割し、テスト時の差し替え粒度を細かくする。
- ドメインエンティティ `Job` の責務を「投入データ」と「実行結果」に分離する（内部表現のみ）。
- 命名揺れ（`presender`、`worker.py` の二重）を解消する。

**Non-Goals:**
- 新機能の追加（ジョブ種別の追加、cancel/retry エンドポイント等）。
- 4xx 応答コード・ボディ形・既存ユースケース挙動の変更。
- データベーススキーマ変更（マイグレーション不要）。
- パフォーマンス最適化、依存パッケージのバージョン更新。
- フロントエンドの実装（未着手のまま）。

## Decisions

### D1: 例外 → HTTP の集約先は ErrorHandlingMiddleware

**決定**: 例外型と HTTP ステータスのマッピングは `ErrorHandlingMiddleware` のみで行う。`SubmitPythonJobUseCase` 内の `try/except InvalidTimeout` → `ValidationError` の翻訳は削除し、ドメイン例外を素のまま伝播させる。マッピングは `_EXCEPTION_TO_RESPONSE: dict[type[Exception], tuple[int, str]]` のテーブル形式で表現する。

**代替案**:
- usecase 側で常にアプリ例外（`ValidationError` 等）に翻訳する → 翻訳箇所が usecase 数だけ増える、ドメイン例外の意味が失われる。
- 例外ハンドラを FastAPI の `exception_handlers` に分散登録 → middleware と二系統になり、既存の middleware 構造と整合しない。

### D2: 5xx は固定文言、詳細はログのみ

**決定**: 未知例外の 5xx 応答ボディを `{"detail": "internal server error", "request_id": "<id>"}` の固定形に変更し、`str(exc)` は使わない。詳細スタックは `LOGGER.exception(..., extra={"request_id": ...})` でのみ残す。これは新規 capability `error-response-policy` で明文化する。

**代替案**:
- 環境変数で本番のみ抑制、開発では露出 → 設定漏れによる事故が怖い。常時固定でも開発時はログから取得可能なので不採用。

### D3: ID 生成は infra/identity/identifier.py に集約

**決定**: ULID/UUID フォールバックを `infra/identity/identifier.py:new_id() -> str` 1 関数に集約し、`SubmitPythonJobUseCase`・`infra/cli/create_api_key.py` の両方からこれを使用する。`bare except Exception` は `except ImportError` に絞る。

**代替案**:
- domain 層に置く → ULID 依存は外部ライブラリであり、ドメインの純粋性を侵す。
- 各箇所のローカル関数のまま統一スタイルだけ揃える → 重複が残るため不採用。

### D4: JobRepository.update は単一マッパーで上書き

**決定**: `_to_model()` と `update()` のフィールド毎代入の二重定義を、`apply_to_model(job: Job, model: JobModel) -> None` という 1 つのマッパー関数に統合する。`update()` は「`session.get` → `apply_to_model(job, model)` → commit」の単純経路にし、`if model is None: add` のデッドコードは削除する（先行する `add()` 呼び出しを前提とするため、なければ呼び出し側のバグ）。`_to_model()` は内部で空の `JobModel()` に対して `apply_to_model` を適用する形に書き直す。

**代替案**:
- `session.merge()` を使う → 部分更新時の挙動と SQLAlchemy のキャッシュ整合に注意が必要で、現状の挙動と一致しない可能性がある。代わりに「明示 get → apply」の方が読みやすく安全。

### D5: 所有権チェックは app 層ヘルパに切り出す

**決定**: `app/usecase/_job_access.py`（または既存の `domain/service/job_domain_service.py`）に `find_owned_job(repo, job_id, owner) -> Job` を定義し、`GetJobUseCase` と `GetJobLogsUseCase` から共有する。`find_owned_job` は repo に依存するため domain ではなく app 層に置く。

**代替案**:
- `JobRepository.get_owned(job_id, owner) -> Job | None` を生やす → 「Not Found」と「他人のもの」を呼び出し側で区別したくなる将来のために `JobNotFound` を投げる関数を上位に置く方が拡張しやすい。

### D6: get_job_controller を usecase 単位 provider に分割

**決定**: `get_submit_use_case`, `get_get_job_use_case`, `get_list_jobs_use_case`, `get_get_job_logs_use_case` を個別 provider として用意し、`get_job_controller` はこれらと `get_job_presenter` を `Depends` で受けるだけにする。Settings → `JobSubmissionLimits` の変換も `get_submit_use_case` 内に閉じ込める。

**代替案**:
- DI コンテナ（dependency-injector 等）を導入 → 規模に対し過剰、既存の FastAPI `Depends` で十分。

### D7: Job エンティティに JobExecution Value Object を導入

**決定**: `started_at`, `finished_at`, `exit_code`, `stdout`, `stderr`, `error_type` を `JobExecution`（frozen dataclass）にまとめ、`Job.execution: JobExecution | None` として保持する。`JobDomainService.mark_running` / `mark_finished` も `JobExecution` を作って `replace(job, execution=...)` する形に変える。永続化層では `JobModel` のフィールド構造は変えず、マッパーで `Job.execution` の各属性に展開する。

**代替案**:
- 現状の 13 フィールドのまま据え置き → エンティティ責務の肥大化が続くため、軽量な Value Object 抽出を採用。
- DB 側もテーブル分割 → スキーマ変更を伴うため Non-Goal に抵触。今回は内部表現のみ。

### D8: presender → presenter リネームと src/worker.py 削除

**決定**: `interface/presender/` を `interface/presenter/` にリネーム。`src/worker.py` は削除し、起動コマンドを `arq src.infra.queue.worker.WorkerSettings` に統一する。`AGENTS.md` のディレクトリ構成図中の `presender` 表記も合わせて修正。

**代替案**:
- 互換のため `presender` を再エクスポートする shim を残す → 内部のみで利用される名前のため不要。

## Risks / Trade-offs

- **5xx ボディ形変更**: `str(exc)` を消すと、運用初期に意図せず本物の DB エラー等を画面で確認していた箇所がある場合に不便になる → ログを `request_id` で串刺しできるよう `JsonFormatter` に request_id 連携が既にあることを利用し、運用ドキュメントで「5xx は request_id でログ検索」を案内する。
- **`presender → presenter` リネーム**: 既存の git 履歴・PR レビューで一時的に diff が大きくなる → 1 コミットでリネームのみ、別コミットで内部修正、と分離してレビュー可能にする。アーキテクチャテスト（`tests/arch/`）も同時更新する。
- **`JobExecution` の導入**: usecase / mapper / テストの広範な書き換えが必要 → 単一 PR 内で完結させ、`tests/unit/domain/test_job_domain_service.py` で振る舞いの不変性を担保する。
- **`update()` のデッドコード削除**: 現在は防御的に書かれているため、削除によって「`add` 前に `update` を呼ぶバグ」が顕在化する可能性 → 実態としては `ExecuteJobUseCase` で `mark_running` の前に必ず `get` で実在確認しており、影響は無い見込みだが、unit テストを追加して保証する。
- **例外マッピング集約**: `InvalidTimeout` の翻訳削除により、ログ上の発生源モジュール名が usecase ではなく domain になる → ログ検索の grep キーワードを更新する。

## Migration Plan

1. **proposal / design / specs / tasks 完了後にブランチを切る**
2. 振る舞い不変の内部リファクタを先に投入（H3 ID 共通化 → H5 所有権ヘルパ → H4 mapper 統合 → H7 JobExecution → H6 DI 分割 → H8 リネーム）
3. 振る舞い変化を伴う `error-response-policy` の実装（H1 + H2）を最後に投入
4. 各ステップ後 `uv run pytest` 全通過を必須にする
5. ロールバック: 振る舞い変化を含む H1+H2 のコミットだけ revert すれば 5xx ボディ形を旧来に戻せる構成にしておく

## Open Questions

- `JobExecution` Value Object 化はスコープが大きいため、別 change として切り出す選択肢もある。今回は単一 change で進めるが、実装 PR で分割提案が出れば再検討する。
- `find_owned_job` の置き場所（app/usecase 配下のヘルパか、`domain/service/job_domain_service.py` 内の関数か）は実装時に確定する。後者を選ぶ場合、リポジトリ依存が domain 層に持ち込まれないよう repo を引数で受ける形に限定する。
