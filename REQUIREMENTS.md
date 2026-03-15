# AIエージェント用ジョブ実行サーバ 要求仕様書（MVP）および開発マイルストーン

## 1. 文書概要

### 1.1 目的
本書は、学習目的およびオープンソース公開を前提とした **AIエージェント用ジョブ実行サーバ** の初期要求仕様を定義する。  
対象技術スタックは **Python / FastAPI / Clean Architecture** とし、まずは小さく作り切れる **MVP** を定義したうえで、次段階の **v0.2**、**v0.3** の拡張マイルストーンを示す。

### 1.2 背景
AIエージェントや自動化ワークフローでは、以下のような要件が頻繁に発生する。

- 生成した Python コードを安全に実行したい
- 実行結果を API 経由で取得したい
- 非同期ジョブとして状態管理したい
- 標準出力・標準エラーを記録したい
- 実行時間制限や隔離環境を設けたい

これらを満たす **セルフホスト可能な実行基盤** は、学習題材としても OSS としても価値が高い。

### 1.3 スコープ
本書では以下を対象とする。

- MVP の要求仕様
- v0.2 の拡張項目
- v0.3 の拡張項目
- 実装上の非機能要件
- 推奨アーキテクチャ構成

本書では以下は対象外とする。

- 本番運用レベルの完全なサンドボックス保証
- Kubernetes 前提の分散実行
- マルチリージョン構成
- 課金システム
- 高度な GUI プラットフォーム機能

---

## 2. プロダクト概要

### 2.1 コンセプト
AIエージェントや外部システムが API 経由でジョブを投入し、サーバが隔離環境でコードを実行して、状態・ログ・結果を管理する。

### 2.2 想定ユースケース
1. AIが生成した Python コードの安全な試行実行
2. CSV や JSON を処理するデータ変換ジョブ
3. レポート生成やファイル加工
4. 外部 AI エージェントの実行基盤
5. 将来的な GitHub / Slack / workflow 実行の基盤

### 2.3 想定ユーザー
- 個人開発者
- OSS 利用者
- AI エージェント開発者
- 社内自動化ツールを試作したいエンジニア

---

## 3. MVP 要求仕様

### 3.1 MVP のゴール
以下を満たす最小構成を MVP とする。

- APIキー認証付きでジョブを登録できる
- Python コードをジョブとして受け付けられる
- ジョブは非同期で処理される
- Docker による隔離環境で実行される
- タイムアウト制御がある
- 実行結果、標準出力、標準エラー、終了ステータスを保存・取得できる
- ジョブ状態を API で参照できる

### 3.2 対象ジョブ種別
MVP では **Python ジョブのみ** を対象とする。

#### 入力
- Python コード文字列
- 実行タイムアウト秒数
- 任意のメタデータ

#### 非対象
- shell 実行
- 複数ステップワークフロー
- 外部API呼び出し制御
- ジョブキャンセル
- ファイルアップロード
- リトライ

---

## 4. 機能要件（MVP）

### 4.1 認証
- API キー認証を提供する
- すべてのジョブ系 API は認証必須とする
- API キーは DB 上にハッシュ化して保存する
- API キーには論理名を持たせる

### 4.2 ジョブ登録
利用者は Python コードを送信してジョブを作成できる。

#### API
`POST /v1/jobs/python`

#### リクエスト例
```json
{
  "code": "print('hello')",
  "timeout_sec": 10,
  "metadata": {
    "source": "agent-a"
  }
}
```

#### バリデーション
- code は必須
- code の最大サイズを制限する
- timeout_sec は最小値・最大値を持つ
- metadata は任意

#### レスポンス例
```json
{
  "job_id": "job_xxx",
  "status": "queued"
}
```

### 4.3 ジョブ一覧取得
利用者は自分が投入したジョブ一覧を取得できる。

#### API
`GET /v1/jobs`

#### 要件
- ページング可能
- ステータスによる絞り込みが可能
- 作成日時順に取得できる

### 4.4 ジョブ詳細取得
利用者はジョブの詳細状態を取得できる。

#### API
`GET /v1/jobs/{job_id}`

#### 返却項目
- job_id
- job_type
- status
- timeout_sec
- created_at
- started_at
- finished_at
- exit_code
- error_type
- metadata

### 4.5 ジョブログ取得
利用者は実行ログを取得できる。

#### API
`GET /v1/jobs/{job_id}/logs`

#### 返却項目
- stdout
- stderr

### 4.6 非同期実行
- ジョブ登録時は即時実行完了を待たない
- ジョブは queue に投入される
- worker が queue から取り出して処理する

### 4.7 ジョブ状態管理
MVP では以下の状態を持つ。

- queued
- running
- succeeded
- failed
- timed_out

### 4.8 実行環境
- Docker コンテナで Python コードを実行する
- 実行ごとに一時ワークディレクトリを分離する
- コンテナ内でコードファイルを生成して実行する
- コンテナ実行後は後片付けを行う

### 4.9 タイムアウト制御
- 指定秒数を超えたジョブは停止する
- タイムアウト時は `timed_out` として記録する
- stderr または内部エラー情報にタイムアウト理由を残す

### 4.10 実行結果保存
最低限以下を保存する。

- ジョブ状態
- 標準出力
- 標準エラー
- 終了コード
- 実行開始時刻
- 実行終了時刻
- エラー種別

### 4.11 ヘルスチェック
#### API
- `GET /health/live`
- `GET /health/ready`

#### 要件
- live はプロセス生存確認
- ready は DB および queue 接続確認

---

## 5. 非機能要件（MVP）

### 5.1 アーキテクチャ
Clean Architecture を採用し、以下の層に分離する。

- domain
- usecase
- interface
- infrastructure

### 5.2 保守性
- ユースケースは FastAPI から独立させる
- Docker 実行機構は interface ではなく infrastructure に閉じ込める
- DB 実装は repository interface 越しに扱う

### 5.3 テスト容易性
- ドメイン層は純粋 Python でテスト可能とする
- ユースケースはモック Repository / Runner でテスト可能とする
- API 層は integration test を持つ

### 5.4 セキュリティ
MVP では以下を最低限実施する。

- APIキーのハッシュ保存
- Docker による隔離実行
- 実行時間制限
- コードサイズ制限
- ログサイズ制限

### 5.5 観測性
- アプリケーションログを構造化ログで出力する
- request_id / job_id をログに含める
- エラー時にスタックトレースを記録する

---

## 6. システム構成（MVP）

### 6.1 コンポーネント
- FastAPI API サーバ
- Worker プロセス
- PostgreSQL
- Queue（Redis または同等）
- Docker Engine

### 6.2 構成イメージ
1. クライアントが API にジョブ登録
2. API サーバが DB 保存し queue に投入
3. Worker がジョブ取得
4. Docker コンテナでコード実行
5. 結果を DB 保存
6. クライアントが API で結果参照

---

## 7. 推奨ディレクトリ構成

```text
app/
  domain/
    job/
      entities.py
      enums.py
      repositories.py
      services.py
  usecases/
    submit_python_job.py
    start_job.py
    complete_job.py
    fail_job.py
    get_job.py
    list_jobs.py
    get_job_logs.py
  interfaces/
    api/
      routes/
        health.py
        jobs.py
      schemas/
        jobs.py
      dependencies/
        auth.py
  infrastructure/
    db/
      models.py
      repositories.py
      session.py
    queue/
      publisher.py
      consumer.py
    runner/
      docker_runner.py
    auth/
      api_key.py
    settings/
      config.py
  workers/
    job_worker.py
tests/
  unit/
  integration/
  e2e/
```

---

## 8. ドメイン設計（MVP）

### 8.1 Job エンティティ
主要属性の例:

- id
- job_type
- status
- code
- timeout_sec
- metadata
- created_at
- started_at
- finished_at
- exit_code
- error_type

### 8.2 JobStatus
列挙型として管理する。

- queued
- running
- succeeded
- failed
- timed_out

### 8.3 ドメインルール
- 実行前状態は queued のみ
- running から succeeded / failed / timed_out に遷移可能
- 終了状態から再度 running には遷移しない
- timeout_sec は定義された範囲内でなければならない

---

## 9. DB設計（MVP）

### 9.1 jobs テーブル
- id
- job_type
- status
- code
- timeout_sec
- metadata_json
- exit_code
- error_type
- stdout_text
- stderr_text
- created_at
- started_at
- finished_at
- submitted_by_api_key_id

### 9.2 api_keys テーブル
- id
- name
- hashed_key
- is_active
- created_at

### 9.3 インデックス
- jobs(status, created_at)
- jobs(submitted_by_api_key_id, created_at)
- api_keys(name)

---

## 10. API仕様（MVP）

### 10.1 POST /v1/jobs/python
Python ジョブ作成

### 10.2 GET /v1/jobs
ジョブ一覧取得

### 10.3 GET /v1/jobs/{job_id}
ジョブ詳細取得

### 10.4 GET /v1/jobs/{job_id}/logs
ジョブログ取得

### 10.5 GET /health/live
Liveness 確認

### 10.6 GET /health/ready
Readiness 確認

---

## 11. エラー仕様（MVP）

### 11.1 主なエラーコード
- 400: バリデーションエラー
- 401: 認証エラー
- 403: 権限エラー
- 404: ジョブ未発見
- 409: 状態競合
- 422: 不正入力
- 500: 内部エラー

### 11.2 ドメイン上の代表的エラー
- JobNotFound
- InvalidJobStateTransition
- InvalidTimeout
- AuthenticationFailed
- JobExecutionFailed
- JobTimedOut

---

## 12. テスト要件（MVP）

### 12.1 単体テスト
対象:
- Job 状態遷移
- timeout バリデーション
- ユースケース単位の正常系・異常系

### 12.2 結合テスト
対象:
- API + DB
- API + Queue
- Worker + Docker Runner

### 12.3 E2Eテスト
対象:
- Python ジョブ投入から結果取得までの一連動作

---

## 13. 開発マイルストーン

# v0.2 マイルストーン

## 13.1 目的
MVP を「動く」段階から「使いやすい」段階へ拡張する。

## 13.2 追加機能
### A. artifact 保存
ジョブ実行で生成されたファイルを成果物として保存・参照できる。

#### 要件
- コンテナ内の所定ディレクトリを回収対象とする
- 複数ファイルを保存できる
- artifact 一覧取得 API を持つ

#### 追加API
- `GET /v1/jobs/{job_id}/artifacts`
- `GET /v1/jobs/{job_id}/artifacts/{artifact_id}`

### B. ジョブ再実行
過去ジョブと同一入力で再実行できる。

#### 追加API
- `POST /v1/jobs/{job_id}/retry`

#### 要件
- 元ジョブの code / timeout / metadata を引き継ぐ
- 新しい job_id を払い出す
- 元ジョブとの関連を保持する

### C. ジョブキャンセル
実行前または実行中ジョブを中止できる。

#### 追加API
- `POST /v1/jobs/{job_id}/cancel`

#### 要件
- queued はキャンセル可能
- running は可能な限り停止を試みる
- 状態として cancelled を追加する

### D. 簡易 Web UI
管理用途の最低限 UI を提供する。

#### 画面例
- ジョブ一覧
- ジョブ詳細
- ログ表示
- artifact 一覧

### E. 実行履歴の見やすさ向上
- duration_ms の保存
- ステータス別件数取得
- フィルタリング強化

## 13.3 v0.2 での状態一覧
- queued
- running
- succeeded
- failed
- timed_out
- cancelled

## 13.4 v0.2 完了条件
- artifact が保存・取得できる
- キャンセル API が動作する
- retry API が動作する
- UI から主要操作が可能である

---

# v0.3 マイルストーン

## 14.1 目的
ジョブ実行基盤としての運用性と制御性を強化する。

## 14.2 追加機能
### A. 実行ポリシー
API キーごと、またはジョブ種別ごとに実行制約を定義できる。

#### ポリシー例
- 最大タイムアウト 30 秒
- ネットワーク禁止
- メモリ上限
- 許可 Docker イメージ固定
- artifact 最大サイズ制限

#### 追加要件
- policy テーブルを導入する
- API キーと policy を紐付ける
- ジョブ作成時に policy 検証を行う

### B. リトライ制御
一時的失敗時に自動再試行できる。

#### 要件
- 最大リトライ回数
- バックオフ
- リトライ対象エラー種別の定義
- attempt 管理テーブル導入

### C. レート制限
API キー単位でリクエスト数や同時実行数を制御する。

#### 制御例
- 1分あたりの作成数
- 同時 running 上限
- queue 積載上限

### D. Webhook 通知
ジョブ完了時・失敗時に外部へ通知できる。

#### 通知イベント
- job.succeeded
- job.failed
- job.timed_out
- job.cancelled

### E. 監査ログ
重要操作の追跡を可能にする。

#### 対象
- API キー利用
- ジョブ作成
- キャンセル
- リトライ
- ポリシー違反

## 14.3 v0.3 完了条件
- policy により投入制御できる
- retry が自動で機能する
- webhook 通知が送信される
- 監査ログに主要操作が残る

---

## 15. 将来的な拡張候補

- shell ジョブ対応
- ワークフロー / DAG 実行
- スケジュール実行
- GitHub 連携
- Slack 連携
- マルチテナント
- 管理者ロール
- OpenTelemetry 対応
- MinIO / S3 への artifact 保存
- rootless container / gVisor 対応

---

## 16. 実装優先順位の提案

### Phase 1
- FastAPI 雛形
- Job ドメインモデル
- API キー認証
- PostgreSQL
- Queue
- Worker
- Docker Runner

### Phase 2
- ジョブ状態管理の安定化
- ログ保存
- 一覧・詳細 API
- テスト整備

### Phase 3
- artifact
- retry
- cancel
- UI

### Phase 4
- policy
- rate limit
- webhook
- audit log

---

## 17. OSSとしての打ち出し方

### 想定メッセージ
> AI agents need a safe place to run Python jobs.  
> This project is a self-hostable execution server built with FastAPI and Clean Architecture.

### 差別化ポイント
- Python / FastAPI で読みやすい
- Clean Architecture の学習題材として使える
- OSS として拡張しやすい
- AI エージェント時代に需要がある
- 実務的なジョブ基盤の入門実装になる

---

## 18. まとめ

本プロジェクトの MVP は、**Python ジョブを API 経由で安全寄りに実行し、状態・ログ・結果を取得できる最小構成** に絞る。  
その上で、v0.2 では **artifact / retry / cancel / UI** を、v0.3 では **policy / retry 制御 / rate limit / webhook / audit log** を追加し、段階的に実運用に近づけていく。

学習対象としては以下を横断的に学べる点が非常に強い。

- FastAPI
- Clean Architecture
- 非同期ジョブ処理
- Docker 実行
- API 設計
- 状態遷移設計
- 認証認可
- テスト設計
- OSS としての機能分割
