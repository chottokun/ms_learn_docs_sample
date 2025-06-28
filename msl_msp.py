import httpx
import json
import diskcache

MCP_ENDPOINT = "https://learn.microsoft.com/api/mcp"
cache = diskcache.Cache(".mcp_cache")

def cache_key(query, endpoint, timeout):
    return f"{query}|{endpoint}|{timeout}"

async def mcp_docs_search(query: str, endpoint: str = MCP_ENDPOINT, timeout: float = 15.0):
    key = cache_key(query, endpoint, timeout)
    if key in cache:
        return cache[key]
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
                if line.startswith('data: '):
                    line_stripped = line[len('data: '):].lstrip()
                else:
                    line_stripped = line.lstrip()
                if not line_stripped or not line_stripped.startswith('{'):
                    continue
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
                    continue
    final_results = []
    for item in results:
        if isinstance(item, list):
            final_results.extend(item)
        else:
            final_results.append(item)
    cache.set(key, final_results, expire=3600)
    return final_results

async def clear_mcp_cache():
    cache.clear()