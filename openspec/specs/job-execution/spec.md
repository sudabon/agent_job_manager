# job-execution Specification

## Purpose
TBD - created by archiving change implement-mvp. Update Purpose after archive.
## Requirements
### Requirement: Docker コンテナでの隔離実行

Python コードは Docker コンテナ内で実行する。実行ごとにコンテナを起動し、終了後に後片付けを行う。

#### Scenario: 正常なコード実行
- **WHEN** `print('hello')` を含むジョブが実行される
- **THEN** Docker コンテナ内でコードが実行され、stdout に `hello` が記録される

#### Scenario: 実行エラーのあるコード
- **WHEN** 構文エラーを含むコードが実行される
- **THEN** ジョブは `failed` 状態となり、stderr にエラー内容が記録される

#### Scenario: コンテナの後片付け
- **WHEN** ジョブ実行が完了する（成功・失敗問わず）
- **THEN** 使用したコンテナは削除される

### Requirement: 一時ワークディレクトリの分離

実行ごとに一時ワークディレクトリを作成し、コンテナ内でコードファイルを生成して実行する。

#### Scenario: ワークディレクトリの分離
- **WHEN** 複数のジョブが同時に実行される
- **THEN** 各ジョブは独立した一時ディレクトリで実行され、互いに干渉しない

### Requirement: タイムアウト制御

指定秒数を超えたジョブは強制停止する。

#### Scenario: タイムアウト発生
- **WHEN** `timeout_sec: 5` のジョブが 5 秒以上実行を続ける
- **THEN** コンテナは強制停止され、ジョブ状態は `timed_out` となる

#### Scenario: タイムアウト理由の記録
- **WHEN** タイムアウトが発生する
- **THEN** stderr または内部エラー情報にタイムアウトの理由が記録される

### Requirement: コンテナのセキュリティ制約

実行コンテナはネットワーク無効、メモリ制限付きで起動する。

#### Scenario: ネットワーク無効化
- **WHEN** ジョブが外部ネットワークにアクセスしようとする
- **THEN** ネットワークアクセスは失敗する

#### Scenario: メモリ制限
- **WHEN** ジョブが過大なメモリを消費しようとする
- **THEN** コンテナが OOM で停止し、ジョブは `failed` 状態となる

### Requirement: ログサイズ制限

stdout/stderr それぞれ最大 1MB に制限する。

#### Scenario: ログサイズ超過
- **WHEN** ジョブが 1MB を超える stdout を出力する
- **THEN** 1MB で切り捨てられ、切り捨てが発生した旨が記録される

