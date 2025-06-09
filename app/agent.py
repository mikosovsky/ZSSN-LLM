from langchain_azure_ai.chat_models import AzureAIChatCompletionsModel
from azure.core.credentials import AzureKeyCredential
from langchain_core.messages import HumanMessage, SystemMessage

PROVIDERS = {"OpenRouter":0, "Azure AI Foundry":1}
MODELS = { "OpenRouter": "deepseek/deepseek-r1-0528:free", "Azure AI Foundry": "DeepSeek-R1-0528" }

class Agent:
    def __init__(self, provider, endpoint_url, api_key, model):
        self.provider = provider
        self.endpoint_url = endpoint_url
        self.api_key = api_key
        self.model = model
        self.chat_model = self._initialize_chat_model()

    def _initialize_chat_model(self):
        if self.provider == "Azure AI Foundry":
            return AzureAIChatCompletionsModel(
                endpoint=self.endpoint_url,
                credential=AzureKeyCredential(self.api_key),
                model=self.model,
            )
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
        
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
