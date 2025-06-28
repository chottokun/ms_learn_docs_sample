# 目的
Microsoft Learn Docs MCP serverを利用した検索のサンプルです。

## 概要
- Microsoft Learn Docs MCP serverに対してキーワード検索を行い、公式ドキュメントから関連情報を取得します。
- MCPクエリ・レスポンス処理はモジュール（`msl_msp.py`）として分離し、RAGや他プロジェクトからも再利用できる設計です。
- Streamlitで簡易な検索UIを提供します。
- **同一クエリへのサーバー負荷を抑えるため、クエリ結果はファイルキャッシュ（diskcache）されます（デフォルト1時間/TTL変更可、手動クリア可、キャッシュは`.mcp_cache`ディレクトリに保存）**。

## 構成ファイル
- `app.py` : Streamlitによる検索UI本体。MCP検索処理はモジュールから呼び出します。
- `msl_msp.py` : MCPサーバーへのクエリ投入・レスポンス解析を行うモジュール。

## Microsoft Learn Docs MCP server
- エンドポイント: `https://learn.microsoft.com/api/mcp`
- 検索は基本的に英語で問い合わせのようです。
- 認証や利用制限がある場合があります。

## モジュール（msl_msp.py）の使い方

```python
from msl_msp import mcp_docs_search
import asyncio

# 検索クエリを指定
query = "Azure Functions Python"

# 非同期で呼び出し
results = asyncio.run(mcp_docs_search(query))

# 結果はリストで返る（各要素はdict: title, content, url など）
for item in results:
    print(item['title'], item.get('url', item.get('contentUrl', '')), item['content'])
```

### モジュールの主な仕様
- `async def mcp_docs_search(query: str, endpoint: str = ..., timeout: float = ...) -> list`
    - Microsoft Learn MCPサーバーにクエリを投げ、検索結果（辞書のリスト）を返します。
    - ストリーム応答の `data: ...` プレフィックスや二重JSONデコードにも対応。
    - RAGや他のバックエンドからもimportして再利用可能。
- **キャッシュ機能付き（diskcacheによるファイルキャッシュ）**
    - 同じクエリはファイルキャッシュ（`.mcp_cache`ディレクトリ、diskcache利用）から即時返却され、サーバー負荷を抑制します。
    - デフォルトのキャッシュ有効期限（TTL）は1時間（`expire=3600`）。`msl_msp.py`の`cache.set`で変更可能。
    - 明示的なキャッシュクリアも可能：

```python
from msl_msp import clear_mcp_cache
asyncio.run(clear_mcp_cache())  # キャッシュ全消去
```

#### キャッシュ仕様詳細
- キャッシュは`diskcache`パッケージで実装され、`.mcp_cache`ディレクトリに保存されます。
- TTL（有効期限）はデフォルト1時間（3600秒）ですが、`msl_msp.py`の`cache.set`引数で調整可能です。
- キャッシュはクエリ・エンドポイント・タイムアウトごとに分離されます。
- 手動でキャッシュ全消去も可能です。
- 複数プロセス/アプリ間でもキャッシュが共有されます。

## 必要なパッケージ
- `diskcache`（ファイルキャッシュ用）
- `httpx`（非同期HTTPクライアント）
- `streamlit`（UI用）

```bash
pip install diskcache httpx streamlit
```

## Streamlitアプリ（app.py）の使い方

```bash
streamlit run app.py
```

- 検索キーワードを入力し「検索」ボタンを押すと、MCPサーバーから関連ドキュメントが表示されます。
- 「キャッシュクリア」ボタンでキャッシュを手動消去できます。
- 検索処理は `msl_msp.py` の `mcp_docs_search` を呼び出しています。

## 注意事項
- Microsoft公式MCPサーバーは認証や利用制限がある場合があります。
- 大量アクセスにならないようにご利用ください。
- 検索結果が空の場合、クエリやサーバー仕様を見直してください。
- **キャッシュディレクトリ（.mcp_cache）が作成されます。不要な場合は手動で削除してください。**

## 参考
- [Microsoft Learn Docs MCP server 公式ドキュメント](https://learn.microsoft.com/ja-jp/azure/developer/azure-mcp-server/tools/ai-search)
- [MCPプロトコル解説記事](https://zenn.dev/cloud_ace/articles/model-context-protocol)


