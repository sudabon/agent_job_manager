## ADDED Requirements

### Requirement: APIキーによる認証

すべてのジョブ系 API エンドポイントは APIキー認証を必須とする。APIキーは `X-API-Key` ヘッダーで送信し、サーバ側で SHA-256 ハッシュと照合する。

#### Scenario: 有効なAPIキーでのリクエスト
- **WHEN** 有効な APIキーを `X-API-Key` ヘッダーに設定してジョブ系 API にリクエストする
- **THEN** リクエストは認証され、正常にレスポンスが返る

#### Scenario: APIキー未指定でのリクエスト
- **WHEN** `X-API-Key` ヘッダーなしでジョブ系 API にリクエストする
- **THEN** 401 Unauthorized エラーが返る

#### Scenario: 無効なAPIキーでのリクエスト
- **WHEN** 無効な APIキーを `X-API-Key` ヘッダーに設定してリクエストする
- **THEN** 401 Unauthorized エラーが返る

#### Scenario: 無効化されたAPIキーでのリクエスト
- **WHEN** `is_active` が false の APIキーでリクエストする
- **THEN** 401 Unauthorized エラーが返る

### Requirement: APIキーのハッシュ保存

APIキーは DB 上に SHA-256 でハッシュ化して保存する。平文のキーは保存しない。

#### Scenario: APIキーの保存
- **WHEN** 新しい APIキーを生成する
- **THEN** DB には SHA-256 ハッシュ値のみが保存され、平文は保存されない

### Requirement: APIキーの論理名管理

各 APIキーには論理名（name）を持たせ、識別可能にする。

#### Scenario: 論理名付きAPIキーの作成
- **WHEN** 論理名を指定して APIキーを作成する
- **THEN** 指定した論理名で APIキーが登録される

### Requirement: APIキーの CLI 管理

APIキーの作成は CLI コマンドで行う。

#### Scenario: CLI でAPIキーを作成
- **WHEN** CLI コマンドで APIキー作成を実行する
- **THEN** 新しい APIキーが生成され、平文のキーが一度だけ表示される
