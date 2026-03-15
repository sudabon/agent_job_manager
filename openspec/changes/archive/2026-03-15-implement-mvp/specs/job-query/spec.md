## ADDED Requirements

### Requirement: ジョブ一覧取得

`GET /v1/jobs` でジョブ一覧を取得できる。認証済みユーザーが投入したジョブのみが返る。

#### Scenario: ジョブ一覧の取得
- **WHEN** 認証済みユーザーがジョブ一覧を取得する
- **THEN** そのAPIキーで投入されたジョブ一覧が作成日時降順で返る

#### Scenario: ステータスによる絞り込み
- **WHEN** `status=running` クエリパラメータを指定してジョブ一覧を取得する
- **THEN** status が running のジョブのみが返る

#### Scenario: ページング
- **WHEN** `page=2&per_page=10` を指定してジョブ一覧を取得する
- **THEN** 11件目〜20件目のジョブが返り、ページング情報が含まれる

#### Scenario: ジョブが存在しない場合
- **WHEN** ジョブが1件も存在しない状態で一覧を取得する
- **THEN** 空の一覧が返る（エラーにはならない）

### Requirement: ジョブ詳細取得

`GET /v1/jobs/{job_id}` でジョブの詳細状態を取得できる。

#### Scenario: ジョブ詳細の取得
- **WHEN** 存在するジョブの job_id を指定して詳細を取得する
- **THEN** job_id, job_type, status, timeout_sec, created_at, started_at, finished_at, exit_code, error_type, metadata が返る

#### Scenario: 存在しないジョブの詳細取得
- **WHEN** 存在しない job_id を指定して詳細を取得する
- **THEN** 404 Not Found エラーが返る

#### Scenario: 他ユーザーのジョブの詳細取得
- **WHEN** 別の APIキーで投入されたジョブの詳細を取得する
- **THEN** 404 Not Found エラーが返る

### Requirement: ジョブログ取得

`GET /v1/jobs/{job_id}/logs` でジョブの実行ログを取得できる。

#### Scenario: ジョブログの取得
- **WHEN** 完了済みジョブのログを取得する
- **THEN** stdout と stderr が返る

#### Scenario: 未完了ジョブのログ取得
- **WHEN** status が queued または running のジョブのログを取得する
- **THEN** 現時点で取得可能なログが返る（stdout/stderr は空文字の場合がある）

#### Scenario: 存在しないジョブのログ取得
- **WHEN** 存在しない job_id を指定してログを取得する
- **THEN** 404 Not Found エラーが返る
