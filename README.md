# 全国スイーツ探索マップ | GitHub Actions 版

ChatGPT の定期タスクが承認待ちで停止する問題を避けるため、地図の正本を GitHub 上に置き、GitHub Actions と GitHub Pages で管理する構成です。初期データは ChatGPT ライブラリの 2026-11-09 版（37 店舗）。47 都道府県の地図表示は既存 HTML を保持しています。

## 初回のセットアップ（無料の GitHub 公開リポジトリが必要）

1. GitHub の `https://github.com/new` で、新しい **Public** リポジトリ `sweets-map` を作成します。非公開の `story-game` リポジトリを転用しません。
2. このフォルダの内容を、GitHub リポジトリのルートへアップロードします。`.github/workflows/` フォルダも含めてください。ブラウザからのフォルダアップロードが難しければ、PC から `git add . && git commit -m 'Initial sweets map' && git push` を使ってください。
3. GitHub の `Settings > Pages` で `Source: GitHub Actions` を選択します。
4. `Actions > Research sweets, validate and publish map` から **Run workflow** を 1 回実行します。成功すると `Settings > Pages` に公開 URL が表示されます。`https://<USERNAME>.github.io/sweets-map/` が標準的な URL 形式ですが、実際の URL は GitHub が表示したものを確認してください。
5. 1 時間ごと（UTC 17 分）に検索・チェック・公開処理が自動実行されます。GitHub Actions のスケジュールは遅延・スキップの可能性があり、正確な時刻の実行は保証されません。7 日ごとの稼働記録を自動コミットし、無活動による停止のリスクを減らします。

## 自動化の範囲と検証の厳格さ

- `scripts/discover.py`: 全国の県をローテーションし、直近 30 日のニュース RSS を検索して記事の**未検証候補**を `data/discovered_articles.json` に追加します。見つけただけでは店舗に追加しません。
- `data/verified_candidates.json`: 人が店名、県、市、**番地までの住所**、特徴的な商品、出典 URL をまとめて確認した候補の受付口です。この JSON に店舗候補を入れると、次回実行時に出典 HTML から店名・完全な住所・商品を再検査します。確認できない場合は追加しません。
- `scripts/accept_verified.py`: 上記の再検査が通った候補のみ、重複や都道府県の整合性を確認して `data/shops.json` の `shops` に追記します。一度に 5 店舗という上限はありません。
- `scripts/build.py`: 元の `site/index.html` の `BASE_SHOPS` データブロックと日付・件数表示のみを更新します。県別ナビゲーションや地図操作コードには触れません。
- `scripts/validate.py`: 47 都道府県・10 地方区分、データの整合性、地図側の主要コードが保たれているか検証します。GitHub Actions でも JS の構文を検査します。
- ユーザー提供の未検証 YouTube リスト 5 件は `data/youtube_playlists_to_retry.json` に残しています。動画ページから実店舗の住所・商品・出典が確認できるまでは登録しません。

**重要:** この構成の RSS 検索は候補を集めるだけです。ニュース見出しだけから実店舗・番地・商品を正確に決めることはできないため、候補の追加には証拠付きの確認が必要です。根拠のない「自動 100 店登録」をする仕組みではありません。`verified_candidates.json` の審査済み候補については、自動再検査・反映ができます。

## データ保存先

- GitHub の `data/shops.json` と `site/index.html` が新しい正本になります。
- ChatGPT ライブラリの `/全国スイーツマップ/...` とは**自動同期しません**。ライブラリへの書き戻しは ChatGPT 側の操作・承認に依存するため、この構成の目的である「毎回承認なし」を満たせません。過去のライブラリは残しておきます。
- HTML のリンクは GitHub Pages の固定 URL を使い、毎回ファイルをダウンロードする必要はありません。

## 費用、保守、安全性

- GitHub Free の公開リポジトリで GitHub Pages を使用できます。GitHub Actions の使用条件・制限はプランと GitHub の方針に従います。
- GitHub は、公開リポジトリで 60 日間活動がない場合にスケジュールを自動無効化する場合があります。週次の稼働記録（`data/automation_status.json`）をコミットして無活動による停止のリスクを下げますが、GitHub Actions が絶対に停止しない保証ではありません。1 ヵ月程度に一度、動作・実行履歴を点検する必要があります。
- `data/shops.json` は基本的に人手で検証済みの出典を保持するため、既存店が閉店していると疑われても勝手に消しません。必要に応じて調査します。
- 自動で店舗情報を創作したり、動画リストの内容を推測して追加したりはしません。

### 手動ローカル確認

```bash
python scripts/build.py
python scripts/validate.py
```
