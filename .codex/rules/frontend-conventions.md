---
globs: ["frontend/**"]
---
# フロントエンド コーディング規約

- `any` 型の使用は禁止。`unknown` を使い、型ガードで絞り込む。
- コンポーネントは関数コンポーネントのみ使用する。
- コンポーネント名は PascalCase、関数・変数は camelCase。
- UIコンポーネントは Shadcn/ui をベースに使用する。独自スタイルは TailwindCSS で適用する。
- サーバー状態の取得・キャッシュは TanStack Query を使用する。`useEffect` + `fetch` で代用しない。
- API クライアントは `frontend/src/lib/` に集約する。
- マジックナンバー・文字列リテラルは定数として定義する。
- フロントエンドのコマンドは `frontend/` ディレクトリ内で実行する。
