from langchain_azure_ai.chat_models import AzureAIChatCompletionsModel
from azure.core.credentials import AzureKeyCredential
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.prompts import PromptTemplate
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.docstore.document import Document
from langchain.text_splitter import CharacterTextSplitter

PROVIDERS = {"OpenRouter":0, "Azure AI Foundry":1}
MODELS = { "OpenRouter": "deepseek/deepseek-r1-0528:free", "Azure AI Foundry": "DeepSeek-R1-0528" }

class Agent:
    def __init__(self, provider, endpoint_url, api_key, model):
        self.set_connection_config(provider, endpoint_url, api_key, model)
        self.prompt_template = self._init_prompt_template()
        self.db = VectorStore()

    def _initialize_chat_model(self):
        if self.provider == "Azure AI Foundry":
            return AzureAIChatCompletionsModel(
                endpoint=self.endpoint_url,
                credential=AzureKeyCredential(self.api_key),
                model=self.model
            )
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
        
    def set_connection_config(self, provider, endpoint_url, api_key, model):
        self.provider = provider
        self.endpoint_url = endpoint_url
        self.api_key = api_key
        self.model = model
        self.chat_model = self._initialize_chat_model()
        
    def _init_prompt_template(self):
        prompt_template = PromptTemplate(
            input_variables=["context", "question"],
            template="""
You are a financial advisor. Use the following context to answer the question.
Context:
{context}

Question:
{question}

Answer:
"""
        )
        return prompt_template
    
    def _prepare_prompt(self, context, question):
        return self.prompt_template.format(context=context, question=question)
    
    def _build_vectorstore(self):
        pass
        
    def test_connection(self):
        try:
            # Attempt to get a response from the model
            response = self.chat_model.invoke(
                [SystemMessage(content="Answer by one sentence."),
                 HumanMessage(content="Hello, world!")],
                config={
                    "generation_config": {
                        "max_tokens": 10
                    }
                }
            )
            return True, response.content
        except Exception as e:
            return False, str(e)

class VectorStore:
    def __init__(self):
        self.embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        dummy_doc = Document(page_content="This is a dummy document for initializing the vector store.")
        self.db = FAISS.from_documents([dummy_doc], self.embedding)
        self.db.index.reset()
        self.db.docstore._dict.clear()
        self.db.index_to_docstore_id.clear()

    def add_documents(self, documents):
        docs = []
        text_spliter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200, separator="\n")
        docs = text_spliter.split_documents(documents)
        self.db.add_documents(docs)

    def search(self, prompt, k=5):
        results = self.db.similarity_search(prompt, k=k)
        return results
