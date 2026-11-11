# Humming Hearts 公式サイト

公開されるのは `public/` の中身だけです。

- `public/index.html`・`public/css/style.css`・`public/js/main.js` … トップページ。**直接書きかえない**（下の道具が書き出す）
- `tools/build_top.py` … トップページを組み立てる道具。曲・ユニット・メンバー・お知らせ・リンクは、このファイルの「中身」の欄を書きかえて `python3 tools/build_top.py` を実行する
- `tools/build_pages.py` … ユニットとメンバーの個別ページ（`public/units/`・`public/members/`）を組み立てる道具。文章は `tools/pages_data.json`（旧サイトの文章そのまま）。`build_top.py` の中身を変えたときは、こちらも実行する（上の帯や並びが共通のため）。個別ページを出すユニットは `build_top.py` の `PAGES`、メンバーは `MSLUG` に書く
- `public/images/` … 画像。`chara`（立ち絵）・`face`（丸い顔）・`emblem`（ユニットの紋章）・`kv`（ユニットの絵）・`jacket`（ジャケット）。ファイル名はユニット番号で付け、制作用の記号（TRT など）は使わない
- `public/data/content.json` … 以前のトップページが使っていた中身。いまのトップページでは使っていない（ユニット・キャラクターのページを作るときに整理する）
- `public/rule-the-darkness.html` … ミニゲーム
- `wrangler.jsonc` … Cloudflare に置くための設定（`main` に入れると自動で公開）

## 確認と公開のしかた

- `main` に入ったものが本番として公開されます（`https://hh-official-site.meloriilab.workers.dev`。ドメインをつないだら humming-hearts.com）
- ほかのブランチは、Cloudflare が下見用のURLを作ります。URLはプルリクエストに Cloudflare が書き込むコメントに出ます
- 下見用の組み立てには `wrangler.jsonc` の `"previews": {}` が必要です。消さないでください

## `main` に入れたのに本番が変わらないとき

2026-11-10 に、`main` に取り込んだあとも本番が古い版のままになったことがあります。Cloudflare の組み立てが「順番待ち」のまま始まっていませんでした（失敗ではなく、始まっていない）。

- まず、端末に古い表示が残っているだけではないかを確かめる（下見用のアドレスと見比べる）
- GitHub の `main` の最新の記録に、Cloudflare の「Workers Builds: hh-official-site」の結果が付いているかを見る。付いていなければ、組み立てが始まっていない
- 直し方は2つ。Cloudflare の管理画面（Workers & Pages → hh-official-site → Deployments）で組み立てをやり直すか、`main` に次の変更を取り込む（取り込みのたびに組み立てが走る）
- 取り込んだあとは、本番のアドレスを実際に開いて、新しい版になっているかを確かめてから「反映した」と伝える
