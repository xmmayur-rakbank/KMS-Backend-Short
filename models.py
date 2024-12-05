from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI

embeddings = AzureOpenAIEmbeddings(
    deployment="text-data-002",  # Azure OpenAI deployment name
    model="text-embedding-ada-002",  # Model you want to use
    api_key="db8d369a30e840b39ccdfdce4808ec7f",  # Your Azure OpenAI API key
    azure_endpoint="https://rakbankgenaidevai.openai.azure.com/",  # Your Azure OpenAI resource URL
    openai_api_version="2023-05-15"  # API version you're using
)

llm = AzureChatOpenAI(
    openai_api_version="2023-05-15",  # API version,
    azure_endpoint="https://rakbankgenaidevai.openai.azure.com/",  # Your Azure OpenAI resource URL
    api_key="db8d369a30e840b39ccdfdce4808ec7f",  # Your Azure OpenAI API key
    deployment_name="gpt-4o",
)

