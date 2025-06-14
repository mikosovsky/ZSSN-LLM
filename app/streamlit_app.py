import streamlit as st
import pandas as pd
from time import sleep
import fitz
from langchain.docstore.document import Document
from agent import Agent
import asyncio
import nest_asyncio

# Function to increment the file button counter
# This is used to ensure unique keys for each file download button
file_button_counter = 0
documents = []
nest_asyncio.apply()  # Apply nest_asyncio to allow nested event loops
async def foo():
    asyncio.sleep(2)
    return "habla habla hyc"

def run_async_in_event_loop(coro):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        print("except done")
        print("===========LOOP IS RUNNING?================")
        print(loop.is_running())
        print(loop.is_closed())
        return loop.run_until_complete(coro)
    
    print("try done")
    future = asyncio.run_coroutine_threadsafe(coro, loop)
    return future.result()

def increment_counter():
    global file_button_counter
    return_value = file_button_counter
    file_button_counter += 1
    return return_value

def file_to_doc(file):
    if file.name.endswith('.pdf'):
        global documents
        file_bytes = file.read()
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        return Document(page_content=text, metadata={"source": file.name})

# Dialog to set provider, endpoint URL, and API key
providers = {"OpenRouter":0, "Azure AI Foundry":1}
models = { "OpenRouter": "deepseek/deepseek-r1-0528:free", "Azure AI Foundry": "DeepSeek-V3-0324" }
@st.dialog("Set config for LLM")
def set_api_key():
    st.markdown("Please select provider and model additionally please set your endpoint URL and API Key.")
    provider = st.selectbox("Select Provider", ["OpenRouter", "Azure AI Foundry"], index=providers.get(st.session_state.get("provider", "OpenRouter"), 0))
    endpoint_url = st.text_input("Endpoint URL", value=st.session_state.ENDPOINT_URL, placeholder="Enter endpoint URL")
    api_key = st.text_input("API Key", value=st.session_state.API_KEY, placeholder="Enter API key", type="password")
    if st.button("Submit"):
        if api_key and endpoint_url:
            st.session_state.API_KEY = api_key
            st.session_state.ENDPOINT_URL = endpoint_url
            st.session_state.model = models.get(provider)
            st.session_state.provider = provider
            st.success("Config set successfully!")
            st.session_state.agent = Agent(
                provider=st.session_state.provider,
                endpoint_url=st.session_state.ENDPOINT_URL,
                api_key=st.session_state.API_KEY,
                model=st.session_state.model
            )
            sleep(1)
            st.rerun()
        else:
            st.error("Please enter a valid config.")

st.title("Investing in the Future: A Deep Dive into the Stock Market")


# Sidebar configuration
with st.sidebar:
    st.button("Change LLM config", on_click=set_api_key)
    st.header("📊 Stock Market Analysis")
    st.write("Explore the latest trends and insights in the stock market.")
    st.write("Use the sidebar to navigate through different sections.")

# Initialize session state for messages if not already present
if "messages" not in st.session_state:
    st.session_state.messages = []

# Check if API key, endpoint url, model and provider are set, if not prompt user to set it
if "API_KEY" not in st.session_state or "ENDPOINT_URL" not in st.session_state or "model" not in st.session_state or "provider" not in st.session_state:
    st.session_state.API_KEY = ""
    st.session_state.ENDPOINT_URL = ""
    st.session_state.model = ""
    st.session_state.provider = ""
    set_api_key()

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["files"]:
            files_btns = [st.download_button(label=file["name"], data=file["data"], file_name=file["name"], icon="📄", key=f"file_btn_{increment_counter()}") for file in message["files"]]

# Chat input for user interaction
if prompt := st.chat_input("Start a conversation",
                           accept_file="multiple",
                           file_type=["pdf", "csv", "txt"]):
    # Store user input in session state
    with st.chat_message("user"):
        req_prompt = ""
        files_btns = []
        files_dict = []
        if prompt.text:
            req_prompt = prompt["text"]
            st.markdown(req_prompt)
        if prompt.files:
            files_btns = [st.download_button(label=file.name, data=file, file_name=file.name, icon="📄", key=f"file_btn_{increment_counter()}") for file in prompt.files]
            files_dict = [{"name": file.name, "data": file} for file in prompt.files]
            docs = [file_to_doc(file) for file in prompt.files]
            st.session_state.agent.add_documents(docs)
        st.session_state.messages.append({"role": "user", "content": req_prompt, "files": files_dict})

        
    # Simulate a response from a model (placeholder)
    with st.spinner("Thinking..."):
        with st.chat_message("assistant"):
            ans = run_async_in_event_loop(st.session_state.agent.ainvoke(req_prompt))
            # ans = run_async_in_event_loop(foo())
            if not ans:
                ans = "There was no answer from the model, please try again."
            st.session_state.messages.append({"role": "assistant", "content": ans, "files": []})
            st.markdown(ans)