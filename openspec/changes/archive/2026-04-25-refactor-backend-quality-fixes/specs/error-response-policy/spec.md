## ADDED Requirements

### Requirement: 既知ドメイン／アプリケーション例外への HTTP マッピング

API は既知のドメイン例外およびアプリケーション例外を、固定された HTTP ステータスコードへ変換して応答 SHALL する。マッピングはアプリケーション全体で 1 箇所（middleware）に集約 MUST され、ユースケース層で重複定義 MUST NOT する。

#### Scenario: 認証失敗
- **WHEN** リクエスト処理中に `AuthenticationFailed` が発生する
- **THEN** ステータス 401 と `{"detail": "<例外メッセージ>"}` を返す

#### Scenario: 対象ジョブが存在しない
- **WHEN** リクエスト処理中に `JobNotFound` が発生する
- **THEN** ステータス 404 と `{"detail": "<例外メッセージ>"}` を返す

#### Scenario: バリデーションエラー（アプリ層）
- **WHEN** リクエスト処理中に `ValidationError` が発生する
- **THEN** ステータス 400 と `{"detail": "<例外メッセージ>"}` を返す

#### Scenario: ドメイン不変条件違反
- **WHEN** リクエスト処理中に `InvalidEntity` が発生する
- **THEN** ステータス 400 と `{"detail": "<例外メッセージ>"}` を返す

#### Scenario: タイムアウト範囲外
- **WHEN** リクエスト処理中に `InvalidTimeout` が発生する
- **THEN** ステータス 400 と `{"detail": "<例外メッセージ>"}` を返す

#### Scenario: 不正な状態遷移
- **WHEN** リクエスト処理中に `InvalidJobStateTransition` が発生する
- **THEN** ステータス 400 と `{"detail": "<例外メッセージ>"}` を返す

#### Scenario: マッピングの一意性
- **WHEN** ある例外型に対し HTTP ステータスを決定する
- **THEN** 例外 → ステータスのマッピングは middleware 内の単一テーブルにより決定され、ユースケース層では例外型の翻訳を行わない

### Requirement: 5xx 応答における内部例外詳細の非露出

未知の例外（マッピングテーブルに含まれない `Exception` 派生）が発生した場合、API は内部実装の詳細をクライアントに漏洩 MUST NOT する。応答ボディは固定の文言のみを返 SHALL し、相関のための `request_id` のみを公開 SHALL する。例外メッセージ・スタックトレース・内部ファイルパスは応答ボディに一切含め MUST NOT ない。詳細スタックは構造化ログにのみ記録 SHALL する。

#### Scenario: 未知例外発生時のレスポンスボディ
- **WHEN** リクエスト処理中にマッピングテーブルに含まれない例外が発生する
- **THEN** ステータス 500 と `{"detail": "internal server error", "request_id": "<request id>"}` を返す

#### Scenario: 例外メッセージ・スタックの非露出
- **WHEN** 未知例外による 500 応答が返される
- **THEN** レスポンスボディには例外クラス名・例外メッセージ・スタックトレース・内部ファイルパスが一切含まれない

#### Scenario: 詳細はログにのみ記録
- **WHEN** 未知例外が発生する
- **THEN** スタックトレースを含む完全な例外情報が `logger.exception` で構造化ログ（JSON）に出力され、当該ログには `request_id` が付与される

### Requirement: エラー応答における request_id の付与

未知例外による 5xx 応答には、当該リクエストに割り当てられた `request_id` を応答ボディと応答ヘッダの両方に必ず付与 MUST する。これによりクライアントから報告された `request_id` でサーバ側ログを一意に検索 SHALL できる。

#### Scenario: 5xx ボディに request_id が含まれる
- **WHEN** 未知例外による 500 応答が返される
- **THEN** レスポンスボディの `request_id` フィールドに、`X-Request-Id` ヘッダと同一の値が設定される

#### Scenario: ヘッダにも request_id が反映される
- **WHEN** 5xx 応答が返される
- **THEN** 応答ヘッダ `X-Request-Id`（または設定済みヘッダ名）にも同一の `request_id` が設定される
