## ADDED Requirements

### Requirement: ジョブ状態の定義

ジョブは以下の状態を持つ: queued, running, succeeded, failed, timed_out

#### Scenario: 初期状態
- **WHEN** ジョブが登録される
- **THEN** ジョブの状態は `queued` となる

### Requirement: 状態遷移ルール

ジョブの状態遷移は以下のルールに従う。
- `queued` → `running` のみ遷移可能
- `running` → `succeeded`, `failed`, `timed_out` のいずれかに遷移可能
- 終了状態（succeeded, failed, timed_out）からは他の状態に遷移できない

#### Scenario: queued から running への遷移
- **WHEN** Worker がジョブを取得して実行を開始する
- **THEN** ジョブ状態が `queued` から `running` に遷移する

#### Scenario: running から succeeded への遷移
- **WHEN** ジョブが正常に完了する（exit_code = 0）
- **THEN** ジョブ状態が `running` から `succeeded` に遷移する

#### Scenario: running から failed への遷移
- **WHEN** ジョブが異常終了する（exit_code ≠ 0）
- **THEN** ジョブ状態が `running` から `failed` に遷移する

#### Scenario: running から timed_out への遷移
- **WHEN** ジョブがタイムアウトする
- **THEN** ジョブ状態が `running` から `timed_out` に遷移する

#### Scenario: 不正な状態遷移の拒否
- **WHEN** 終了状態（succeeded/failed/timed_out）のジョブを running に遷移しようとする
- **THEN** InvalidJobStateTransition エラーが発生する

#### Scenario: queued から直接終了状態への遷移の拒否
- **WHEN** `queued` のジョブを直接 `succeeded` に遷移しようとする
- **THEN** InvalidJobStateTransition エラーが発生する

### Requirement: 実行結果の保存

ジョブ実行の結果として以下を保存する: 状態、stdout、stderr、exit_code、started_at、finished_at、error_type

#### Scenario: 成功時の結果保存
- **WHEN** ジョブが正常に完了する
- **THEN** status=succeeded、stdout、stderr、exit_code=0、started_at、finished_at が保存される

#### Scenario: 失敗時の結果保存
- **WHEN** ジョブが異常終了する
- **THEN** status=failed、stdout、stderr、exit_code（非0）、error_type、started_at、finished_at が保存される

#### Scenario: タイムアウト時の結果保存
- **WHEN** ジョブがタイムアウトする
- **THEN** status=timed_out、error_type=timeout、started_at、finished_at が保存される
