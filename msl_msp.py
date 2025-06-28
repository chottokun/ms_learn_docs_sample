import httpx
import json

MCP_ENDPOINT = "https://learn.microsoft.com/api/mcp"

async def mcp_docs_search(query: str, endpoint: str = MCP_ENDPOINT, timeout: float = 15.0):
    """
    Microsoft Learn MCPエンドポイントにクエリを投げ、検索結果リストを返す。
    RAG等の他プロジェクトからも利用できるよう汎用化。
    """
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "microsoft_docs_search",
            "arguments": {"question": query}
        },
        "id": 1
    }
    results = []
    async with httpx.AsyncClient(timeout=timeout) as client:
        async with client.stream("POST", endpoint, json=payload) as response:
            async for line in response.aiter_lines():
                # 'data:' プレフィックスを削除
                if line.startswith('data: '):
                    line_stripped = line[len('data: '):].lstrip()
                else:
                    line_stripped = line.lstrip()
                if not line_stripped or not line_stripped.startswith('{'):
                    continue  # JSONで始まらない行は完全にスキップ
                try:
                    chunk = json.loads(line_stripped)
                    result = chunk.get("result")
                    if result:
                        content = result.get("content")
                        if content and isinstance(content, list) and isinstance(content[0], dict) and 'text' in content[0]:
                            for entry in content:
                                text = entry.get('text')
                                if text:
                                    items = json.loads(text)
                                    results.extend(items)
                        elif content and isinstance(content, list) and isinstance(content[0], str):
                            items = [json.loads(item) for item in content]
                            results.extend(items)
                        elif content and isinstance(content, str):
                            items = json.loads(content)
                            results.extend(items)
                        elif content and isinstance(content, list):
                            results.extend(content)
                        else:
                            results.append(result)
                except Exception:
                    continue  # JSONデコード失敗行はスキップ

    # 平坦化
    final_results = []
    for item in results:
        if isinstance(item, list):
            final_results.extend(item)
        else:
            final_results.append(item)
    return final_results