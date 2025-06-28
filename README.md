# 目的
Microsoft Learn Docs MCP serverを利用したQAシステム（Retrieval-Augmented Generation, RAG）を構築するサンプルです。

## 概要
- Microsoft Learn Docs MCP serverに対してキーワード検索を行い、公式ドキュメントから関連情報を取得します。
- MCPクエリ・レスポンス処理はモジュール（`msl_msp.py`）として分離し、RAGや他プロジェクトからも再利用できる設計です。
- Streamlitで簡易な検索UIを提供します。

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

## Streamlitアプリ（app.py）の使い方

```bash
streamlit run app.py
```

- 検索キーワードを入力し「検索」ボタンを押すと、MCPサーバーから関連ドキュメントが表示されます。
- 検索処理は `msl_msp.py` の `mcp_docs_search` を呼び出しています。

## 注意事項
- Microsoft公式MCPサーバーは認証や利用制限がある場合があります。
- 大量アクセスにならないようにご利用ください。
- 検索結果が空の場合、クエリやサーバー仕様を見直してください。

## 参考
- [Microsoft Learn Docs MCP server 公式ドキュメント](https://learn.microsoft.com/ja-jp/azure/developer/azure-mcp-server/tools/ai-search)
- [MCPプロトコル解説記事](https://zenn.dev/cloud_ace/articles/model-context-protocol)


