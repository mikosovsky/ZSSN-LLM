# ZSSN‑LLM – interactive investment advisor powered by LLM

ZSSN‑LLM is a web application written in Python that combines the capabilities of a large language model (LLM) with up‑to‑date stock‑market data and user‑provided documents.  The project uses [Streamlit](https://streamlit.io) to build a simple user interface, [LangChain](https://python.langchain.com) to drive agents and a FAISS vector database to search information in uploaded files.  Thanks to this you can chat with an agent who can quote your documents, fetch current quotes from Yahoo Finance, generate candlestick charts and answer questions about companies.

## Key features

* **Choice of LLM provider** – the app supports two LLM providers: Azure AI Foundry and OpenRouter.  On first launch the user selects a provider and enters the endpoint URL and API key; on this basis the agent object is created.  Available models for each provider are defined in the Streamlit interface.
* **Financial agent** – the agent uses a prompt template that encourages the model to think step by step and to use tools when it needs extra information.  It maintains chat memory so the context of the conversation is preserved across turns.
* **Vector store** – files uploaded by the user are split into chunks, embedded using the `sentence‑transformers/all‑MiniLM‑L6‑v2` model and stored in a FAISS database.  A pre‑built vector store is provided in the `resources/vectorstore` folder and is automatically loaded when the application starts.  Users can add new documents (PDF/TXT/CSV) from within the interface – their content will be included in the store.
* **Access to stock‑market data** – the MCP server exposes a set of tools to fetch data about companies using the `yfinance` library: current share price, basic company info, price history, dividends, splits, recommendations, financial calendar and latest news.  There is also a tool that generates a candlestick chart with `mplfinance` and saves it as an image.
* **Chat interface** – you talk with the agent in a Streamlit chat window.  Messages are shown as bubbles, you can attach multiple files in a single question, and the answer preview can include generated charts.

| MCP tool                    | Description (invoked by the agent)                                                |
| --------------------------- | --------------------------------------------------------------------------------- |
| `get_stock_price`           | Returns the current price of the given company                                    |
| `get_stock_info`            | Returns basic company info such as sector, market cap, opening price and day high |
| `get_stock_history`         | Returns the trading history for the given period as an array of dictionaries      |
| `get_stock_dividends`       | Returns information about dividends paid                                          |
| `get_stock_splits`          | Returns information about stock splits                                            |
| `get_stock_recommendations` | Returns the latest analyst recommendations                                        |
| `get_stock_calendar`        | Returns the company’s earnings calendar                                           |
| `get_stock_news`            | Returns a list of the latest news about the company                               |
| `plot_stock_price`          | Generates a candlestick chart and saves it in the `app/static` directory          |

## Directory structure

* **`app/`** – contains the application code: agent module (`agent.py`), MCP server (`server.py`), dependency list (`requirements.txt`) and the main Streamlit script (`streamlit_app.py`).
* **`resources/`** – auxiliary data.  The `nasdaq_data.csv`/`nasdaq_data.json` file lists companies from the NASDAQ, and `vectorstore/` contains a pre‑built FAISS index with NASDAQ stocks basic informations.
* **`.streamlit/`** – Streamlit configuration (static file serving enabled).

## Requirements

To run the application you need Python 3.10 or newer and `pip`.  Dependencies are described in `app/requirements.txt`.  You should also have your own API key and endpoint for the selected LLM provider (Azure AI Foundry or OpenRouter).

## Installation and running

1. **Clone the repository**

   ```bash
   git clone https://github.com/mikosovsky/ZSSN-LLM.git
   cd ZSSN-LLM
   ```

2. **Create and activate a virtual environment**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**

   All required libraries (LangChain, Streamlit, FAISS, yfinance etc.) are listed in `app/requirements.txt`.  Install them with:

   ```bash
   pip install --upgrade pip
   pip install -r app/requirements.txt
   ```

   If you encounter problems installing `faiss-cpu` or `pymupdf` on some systems, install missing system packages (e.g. `libgl1`, `libglib2.0` on Linux).

4. **Start the application**

   ```bash
   streamlit run app/streamlit_app.py
   ```

   After a few seconds a browser window will appear with the title *Investing in the Future: A Deep Dive into the Stock Market*.  From the sidebar you can open a dialog where you choose the provider, enter the endpoint URL and API key.  Once you save the configuration, the app will restart and be ready for use.

5. **Start a conversation**

   Type a question about companies or the market in the chat box.  You can attach several PDF, CSV or TXT files; their contents will be read and added to the vector store.  The agent will analyse the context and reply, using MCP tools when necessary.

## Adding your own tools

The MCP server (`app/server.py`) uses the `@mcp.tool()` decorator to expose functions to the agent.  To extend functionality, simply define a new function with a docstring describing the arguments and return value, then decorate it with `@mcp.tool()` – the new function will be loaded automatically the next time the agent starts.  This makes it easy to fetch data from other services, create PDF reports or integrate your own data sources.

## Vector store notes

The default FAISS store contains an index generated from the files in the `resources` folder.  If you want to build your own store from scratch, run the following in Python:

```python
from agent import VectorStore
store = VectorStore()
store.add_documents([Document(page_content="text", metadata={"source": "file.txt"})])
store.save("resources/vectorstore")
```

While the application is running, new documents added by users are saved in memory; you can persist them to disk using `store.save()` in helper scripts.

## License

The project is released under the MIT license.  You can find the full text in the [`LICENSE`](LICENSE) file.
