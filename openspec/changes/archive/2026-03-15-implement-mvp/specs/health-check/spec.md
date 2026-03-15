## ADDED Requirements

### Requirement: Liveness チェック

`GET /health/live` でプロセスの生存確認ができる。認証不要。

#### Scenario: プロセス生存時
- **WHEN** API サーバが稼働中に `/health/live` にリクエストする
- **THEN** 200 OK が返る

### Requirement: Readiness チェック

`GET /health/ready` で DB および Redis（Queue）への接続状態を確認できる。認証不要。

#### Scenario: 全依存サービス正常時
- **WHEN** DB と Redis の両方に接続可能な状態で `/health/ready` にリクエストする
- **THEN** 200 OK が返り、各サービスの接続状態が含まれる

#### Scenario: DB 接続不可時
- **WHEN** DB に接続できない状態で `/health/ready` にリクエストする
- **THEN** 503 Service Unavailable が返り、DB 接続エラーの情報が含まれる

#### Scenario: Redis 接続不可時
- **WHEN** Redis に接続できない状態で `/health/ready` にリクエストする
- **THEN** 503 Service Unavailable が返り、Redis 接続エラーの情報が含まれる
