# Humming Hearts 公式サイト

公開されるのは `public/` の中身だけです。

- `public/index.html` … トップページ
- `public/data/content.json` … 曲・ユニット・メンバー・さえずりなどの中身。文章や曲を差し替えるときは、このファイルだけを書きかえます
- `public/images/` … 立ち絵などの画像
- `public/css/`・`public/js/` … 見た目と動き
- `public/rule-the-darkness.html` … ミニゲーム
- `wrangler.jsonc` … Cloudflare に置くための設定（`main` に入れると自動で公開）

## 確認と公開のしかた

- `main` に入ったものが本番として公開されます（`https://hh-official-site.meloriilab.workers.dev`。ドメインをつないだら humming-hearts.com）
- ほかのブランチは、Cloudflare が下見用のURLを作ります。URLはプルリクエストに Cloudflare が書き込むコメントに出ます
- 下見用の組み立てには `wrangler.jsonc` の `"previews": {}` が必要です。消さないでください
