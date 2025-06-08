import streamlit as st
import pandas as pd

st.title("Investing in the Future: A Deep Dive into the Stock Market")


# Sidebar configuration
with st.sidebar:
    st.header("📊 Stock Market Analysis")
    st.write("Explore the latest trends and insights in the stock market.")
    st.write("Use the sidebar to navigate through different sections.")

if "messages" not in st.session_state:
    st.session_state.setdefault("messages", [])

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


if prompt := st.chat_input("Start a conversation",
                           accept_file=True,
                           file_type=["pdf", "csv", "txt"]):
    with st.chat_message("user"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.write(prompt)

    # Simulate a response from a model (placeholder)
    
    with st.chat_message("assistant"):
        ans = "This is a placeholder response. Replace with actual model response."
        st.session_state.messages.append({"role": "assistant", "content": ans})
        st.markdown(ans)
        
