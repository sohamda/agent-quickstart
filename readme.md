My tryout repo with some examples of agents utilizing Azure AI Agent Service. 

To run this sample:
1. Follow the [setup instructions in the docs](https://learn.microsoft.com/en-us/azure/ai-services/agents/quickstart?pivots=programming-language-python-azure).
1. Clone this repo and install the requirements, e.g., using ```pip install -r requirements.txt```.
1. Rename ```.env.example``` to ```.env``` and add the connection string of your AI Foundry project.
1. Ensure that you can authenticate using [Azure Default Credential](https://learn.microsoft.com/en-us/python/api/azure-identity/azure.identity.defaultazurecredential?view=azure-python), e.g., by logging into your Azure CLI (```az login```).
1. For tracing examples you need to create a log analytics workspace and app insight resource and connect it to your project. Check [this](https://learn.microsoft.com/en-us/azure/ai-services/agents/concepts/tracing)