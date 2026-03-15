# async-job-processing Specification

## Purpose
TBD - created by archiving change implement-mvp. Update Purpose after archive.
## Requirements
### Requirement: ジョブの非同期受付

ジョブ登録時は即時実行完了を待たず、queue に投入して即座にレスポンスを返す。

#### Scenario: ジョブ登録の即時応答
- **WHEN** ジョブを登録する
- **THEN** ジョブは queue に投入され、status=queued のレスポンスが即座に返る（実行完了を待たない）

### Requirement: Worker によるジョブ処理

Worker プロセスが queue からジョブを取得し、Docker コンテナで実行する。

#### Scenario: Worker がジョブを取得して実行
- **WHEN** queue にジョブが投入される
- **THEN** Worker がジョブを取得し、状態を running に更新してから Docker コンテナで実行する

#### Scenario: Worker が実行結果を保存
- **WHEN** ジョブの実行が完了する
- **THEN** Worker が stdout, stderr, exit_code, finished_at を DB に保存し、状態を終了状態に更新する

### Requirement: Queue の信頼性

ジョブは queue に投入された順序で処理される。Worker が停止しても queue に残ったジョブは失われない。

#### Scenario: 順序通りの処理
- **WHEN** ジョブ A、B、C の順に queue に投入される
- **THEN** Worker は A、B、C の順にジョブを取得して処理する

#### Scenario: Worker 再起動時のジョブ保持
- **WHEN** Worker プロセスが再起動する
- **THEN** queue に残っているジョブは失われず、再起動後に処理される

