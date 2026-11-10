# Humming Hearts 公式サイト

公開されるのは `public/` の中身だけです。

- `public/index.html`・`public/css/style.css`・`public/js/main.js` … トップページ。**直接書きかえない**（下の道具が書き出す）
- `tools/build_top.py` … トップページを組み立てる道具。曲・ユニット・メンバー・お知らせ・リンクは、このファイルの「中身」の欄を書きかえて `python3 tools/build_top.py` を実行する
- `public/images/` … 画像。`chara`（立ち絵）・`face`（丸い顔）・`emblem`（ユニットの紋章）・`kv`（ユニットの絵）・`jacket`（ジャケット）。ファイル名はユニット番号で付け、制作用の記号（TRT など）は使わない
- `public/data/content.json` … 以前のトップページが使っていた中身。いまのトップページでは使っていない（ユニット・キャラクターのページを作るときに整理する）
- `public/rule-the-darkness.html` … ミニゲーム
- `wrangler.jsonc` … Cloudflare に置くための設定（`main` に入れると自動で公開）

## 確認と公開のしかた

- `main` に入ったものが本番として公開されます（`https://hh-official-site.meloriilab.workers.dev`。ドメインをつないだら humming-hearts.com）
- ほかのブランチは、Cloudflare が下見用のURLを作ります。URLはプルリクエストに Cloudflare が書き込むコメントに出ます
- 下見用の組み立てには `wrangler.jsonc` の `"previews": {}` が必要です。消さないでください
