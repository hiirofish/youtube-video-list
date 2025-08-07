# YouTube Channel Video Exporter

このツールは、指定したYouTubeチャンネルの全動画に関する詳細な情報を取得し、CSVファイルとしてエクスポートするPythonスクリプトです。

## 主な機能

-   **動画情報の取得**: タイトル、公開日、説明文、サムネイルURLなど。
-   **統計データの取得**: 再生回数、高評価数、コメント数。
-   **所属再生リストの特定**: 各動画がどの再生リストに含まれているかを表示。
-   **CSVエクスポート**: 取得した全データをソートし、`youtube_master_list.csv` として保存。

## 実行環境

-   Python 3.7 以上
-   必要なライブラリは `requirements.txt` を参照してください。

## セットアップ方法

#### 1. リポジトリのクローン
```bash
git clone [https://github.com/hiirofish/youtube-video-list.git](https://github.com/hiirofish/youtube-video-list.git)
cd youtube-video-list
```

#### 2. Google Cloud でのAPI設定
このスクリプトは YouTube Data API v3 を使用します。事前に以下の準備が必要です。

1.  [Google Cloud Console](https://console.cloud.google.com/) でプロジェクトを作成または選択します。
2.  プロジェクトで **YouTube Data API v3** を有効にします。
3.  「APIとサービス」>「認証情報」に移動し、「認証情報を作成」>「OAuth クライアント ID」を選択します。
4.  アプリケーションの種類で「**デスクトップアプリ**」を選択し、作成します。
5.  作成後、JSONファイルをダウンロードし、ファイル名を `client.json` に変更して、このリポジトリのルートディレクトリに配置してください。

#### 3. 依存ライブラリのインストール
```bash
pip install -r requirements.txt
```

#### 4. チャンネルIDの設定
リポジトリのルートディレクトリに `channel_id.txt` という名前で新しいファイルを作成します。
そのファイルの中に、情報を取得したいYouTubeチャンネルのIDを **一行だけ** 記述して保存してください。

**例 (`channel_id.txt` の中身):**
```
UCaQuget_3CnCCTYJEo8tttA
```

---
##### **チャンネルIDの確認方法**

**方法1：チャンネルのURLから確認する（最も簡単な方法）**
1.  ブラウザで目的のYouTubeチャンネルのトップページにアクセスします。
2.  アドレスバーのURLを確認します。
3.  URLが `https://www.youtube.com/channel/UCxxxxxxxxxxxxxxxxxxxxxx` のような形式の場合、`/channel/` の後にある `UC` から始まる文字列がチャンネルIDです。

**方法2：ご自身のチャンネルIDを確認する場合**
1.  [YouTube Studio](https://studio.youtube.com/) にログインします。
2.  左側のメニューから「カスタマイズ」を選択します。
3.  「基本情報」タブをクリックします。
4.  「チャンネルID」の項目に表示されているIDをコピーします。

**方法3：カスタムURLが設定されているチャンネルの場合**
チャンネルURLが `https://www.youtube.com/@Username` のようになっている場合、以下の手順で確認できます。
1.  チャンネルのトップページで、ページの何もないところを右クリックし、「ページのソースを表示」（またはそれに類する項目）を選択します。
2.  表示されたソースコード内で、`Ctrl + F` (Macの場合は `Cmd + F`) を押して検索ウィンドウを開き、`"channelId"` と入力して検索します。
3.  見つかった `"channelId":"UCxxxxxxxxxxxxxxxxxxxxxx"` の、`UC`から始まる部分が本当のチャンネルIDです。

---

## 実行方法

セットアップが完了したら、ターミナルで以下のコマンドを実行します。

```bash
python youtube_video_list.py
```

-   **初回実行時**: ブラウザが自動的に開き、Googleアカウントでの認証と権限の許可を求められます。許可すると、`token.json` というファイルが生成され、以降の認証が自動化されます。
-   **処理の完了**: スクリプトの実行が完了すると、プロジェクトのルートに `youtube_master_list.csv` という名前でCSVファイルが作成されます。

## 注意事項

-   **APIクォータ**: YouTube Data APIには1日あたりの使用量上限（クォータ）があります。動画数が非常に多いチャンネルで実行すると、上限に達してエラーが発生する可能性があります。その場合は、翌日に再度試してください。
-   **秘密情報の管理**: `client.json` と `token.json` は、ご自身の認証情報を含む非常に重要なファイルです。**絶対にGitHubなどで公開しないでください。** このリポジトリの `.gitignore` には、これらのファイルが誤ってアップロードされるのを防ぐ設定が含まれています。

## ライセンス

This project is licensed under the MIT License.
````