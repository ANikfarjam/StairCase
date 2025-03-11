### <span style="color: green">LangChain</span>

LangChain is a framework for developing applications powered by large language models (LLMs).

LangChain simplifies every stage of the LLM application lifecycle:

* **Development:** Build your applications using LangChain's open-source components and third-party integrations. Use LangGraph to build stateful agents with first-class streaming and human-in-the-loop support.
* **Productionization:** Use LangSmith to inspect, monitor and evaluate your applications, so that you can continuously optimize and deploy with confidence.
* **Deployment:** Turn your LangGraph applications into production-ready APIs and Assistants with LangGraph Platform.

![langchain](./langchain_stack_112024_dark.svg)

### Components:

* langchain-core: Base abstractions and LangChain Expression Language.
* langchain-community: Third party integrations.
Partner packages (e.g. langchain-openai, langchain-anthropic, etc.): Some integrations have been further split into their own lightweight packages that only depend on langchain-core.
* langchain: Chains, agents, and retrieval strategies that make up an application's cognitive architecture.
* langgraph: Build robust and stateful multi-actor applications with LLMs by modeling steps as edges and nodes in a graph.
* langserve: Deploy LangChain chains as REST APIs.
The broader ecosystem includes:

* LangSmith: A developer platform that lets you debug, test, evaluate, and monitor LLM applications and seamlessly integrates with LangChain.
### <span style="color: green">instalation</span>

```bash
# Pip
pip install langchain
# Conda
conda install langchain -c conda-forge
```

**Note:** This will install the bare minimum requirements of LangChain. A lot of the value of LangChain comes when integrating it with various model providers, datastores, etc. By default, the dependencies needed to do that are NOT installed. You will need to install the dependencies for specific integrations separately


### <span style="color: green">Konko/Mistral-7B</span>

**Mistral-7B** is open source LLM model that we are going to use for this project

**Konko AI** provides a fully managed API to help application developers

Select the right open source or proprietary LLMs for their application
Build applications faster with integrations to leading application frameworks and fully managed APIs
Fine tune smaller open-source LLMs to achieve industry-leading performance at a fraction of the cost
Deploy production-scale APIs that meet security, privacy, throughput, and latency SLAs without infrastructure set-up or administration using Konko AI's SOC 2 compliant, multi-cloud infrastructure

<span style="color: green">Installation and Setup</span>
1- Sign in to our web app to create an API key to access models via our endpoints for chat completions and completions.
2- Enable a Python3.8+ environment
3- Install the SDK

```python
pip install konko
```

4- Set API Keys as environment variab (KONKO_API_KEY,OPENAI_API_KEY)
```env
export KONKO_API_KEY={your_KONKO_API_KEY_here}
export OPENAI_API_KEY={your_OPENAI_API_KEY_here} #Optional
```

### <span style = "color:green">Example Usage</span>

Completion with mistralai/Mistral-7B-v0.1:
```python
from langchain_community.llms import Konko
llm = Konko(max_tokens=800, model='mistralai/Mistral-7B-v0.1')
prompt = "Generate a Product Description for Apple Iphone 15"
response = llm.invoke(prompt)
```


