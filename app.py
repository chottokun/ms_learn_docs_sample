import streamlit as st
import asyncio
from msl_msp import mcp_docs_search  # モジュールからインポート

st.set_page_config(page_title="Microsoft Docs 検索 (MCP Streamable)", layout="wide")
st.title("Microsoft Learn ドキュメント検索（Streamable HTTP）")

query = st.text_input("🔍 検索キーワードを入力してください")

if st.button("検索"):
    if not query:
        st.warning("検索語句を入力してください。")
    else:
        with st.spinner("検索中（streamable HTTP）..."):
            results = asyncio.run(mcp_docs_search(query))
            st.write("[DEBUG] MCPレスポンス結果:", results)
            if not results:
                st.info("該当するドキュメントが見つかりませんでした。")
            else:
                found_displayable_results = False
                for item in results:
                    if isinstance(item, dict) and 'title' in item:
                        st.markdown(f"### [{item['title']}]({item.get('contentUrl', item.get('url', '#'))})")
                        st.write(item.get("content", ""))
                        st.divider()
                        found_displayable_results = True
                if not found_displayable_results:
                    st.info("該当するドキュメントが見つかりませんでした。")