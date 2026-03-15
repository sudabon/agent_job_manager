## ADDED Requirements

### Requirement: Pythonジョブの登録

利用者は `POST /v1/jobs/python` で Python コードを送信してジョブを作成できる。

#### Scenario: 正常なジョブ登録
- **WHEN** 有効なコード、タイムアウト、メタデータを指定してジョブ登録する
- **THEN** ジョブが作成され、`job_id` と `status: "queued"` を含むレスポンスが返る

#### Scenario: メタデータ省略でのジョブ登録
- **WHEN** metadata を省略してジョブ登録する
- **THEN** ジョブが正常に作成される（metadata は null として保存される）

### Requirement: コードの必須バリデーション

`code` フィールドは必須とする。

#### Scenario: code が空文字
- **WHEN** `code` に空文字を指定してジョブ登録する
- **THEN** 422 バリデーションエラーが返る

#### Scenario: code が未指定
- **WHEN** `code` フィールドなしでジョブ登録する
- **THEN** 422 バリデーションエラーが返る

### Requirement: コードサイズ制限

`code` の最大サイズを 64KB に制限する。

#### Scenario: コードサイズ超過
- **WHEN** 64KB を超えるコードでジョブ登録する
- **THEN** 400 バリデーションエラーが返る（コードサイズ超過の旨）

### Requirement: タイムアウトのバリデーション

`timeout_sec` は最小 1 秒、最大 300 秒の範囲内でなければならない。デフォルト値は 30 秒とする。

#### Scenario: タイムアウト範囲内
- **WHEN** `timeout_sec` に 10 を指定してジョブ登録する
- **THEN** ジョブが正常に作成される

#### Scenario: タイムアウト下限未満
- **WHEN** `timeout_sec` に 0 を指定してジョブ登録する
- **THEN** 400 バリデーションエラーが返る

#### Scenario: タイムアウト上限超過
- **WHEN** `timeout_sec` に 600 を指定してジョブ登録する
- **THEN** 400 バリデーションエラーが返る

#### Scenario: タイムアウト省略
- **WHEN** `timeout_sec` を省略してジョブ登録する
- **THEN** デフォルト値 30 秒でジョブが作成される
