# HH-official-site の作業の決まり

- 公開されるのは `public/` だけ。`public/` のページは手で直さず、`tools/build_top.py`・`tools/build_pages.py` を直して書き出す（README 参照）。
- **Kさんに見せる前・`main` に入れる前に、必ずチェック役を通す**（2026-11-17 Kさんの指示：「私はデバッガーではない」）。
  1. サブエージェント `site-checker`（`.claude/agents/site-checker.md`）に、変更の中身とKさんの指示を渡して確かめてもらう。
     サブエージェントが使えない環境では、`node tools/check/check_site.js` を走らせ、`tools/check/RULES.md` を見ながら自分で画面を確かめる。
  2. 不合格なら直して、もう一度通す。合格したものだけをKさんに見せる。
  3. Kさんへの報告に「チェック役：合格」と、何を確かめたかを1行添える。
- Kさんの新しい決まりごとは `tools/check/RULES.md` に足す。
