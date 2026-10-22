# LangChain Basics and Conversations

**Unit:** 2.1  
**Day:** 7  
**Topic:** LangChain Basics and Conversations

---

## What is it?

LangChain is a framework that helps developers build applications powered by large language models (LLMs). It provides a consistent interface for interacting with chat models, creating reusable prompt templates, managing conversation messages, connecting tools, and combining multiple operations into a workflow. Instead of writing separate integration code for every model provider, you can often switch providers by changing the model configuration while keeping most of your application logic unchanged. However, provider-specific features, parameters, and response formats may still require adjustments.

A key concept is that **a chat model does not automatically remember previous calls**. Your application must provide the relevant conversation history whenever the next response depends on earlier messages. LangChain helps you manage this process, but it does not magically give the underlying model persistent memory.

## Why does it matter?

- **Consistent model integration:** LangChain simplifies interactions with providers such as OpenAI, Google, and Anthropic, reducing the need to rewrite application code for every provider.
- **Reusable prompts:** Prompt templates separate instructions from input data, making prompts easier to maintain, test, and reuse.
- **Conversation management:** Structured messages help applications maintain context across multiple turns in a chatbot conversation.
- **Application workflows:** LangChain allows developers to combine models, tools, retrievers, and other operations to build practical AI applications.
- **Cost and reliability monitoring:** Inspecting token usage, response metadata, and stop reasons helps developers understand API costs, detect truncated responses, and troubleshoot model behavior.

In industry, these capabilities are used in customer-support chatbots, document question-answering systems, AI assistants, retrieval-augmented generation (RAG) applications, and tool-using AI agents.

## How does it work?

### Step 1: Understand the intuition

Think of LangChain as an adapter between your application and an AI model.

Your application prepares a request, LangChain sends it to the configured chat model, and the model returns a response. If you want the model to continue a conversation, your application includes the relevant earlier messages in the next request.

A useful mental model is:

**Application input → Prompt template → Messages → Chat model → Response → Application logic**

The important distinction is that LangChain organizes the interaction, while the chat model generates the answer.

### Step 2: Understand the process in plain English

A typical conversational application follows these steps:

1. **Configure the model:** Select a provider, model name, and API credentials.
2. **Create a prompt template:** Define reusable instructions with placeholders for changing information.
3. **Prepare the messages:** Include system instructions, the current user message, and any relevant previous conversation messages.
4. **Call the model:** Invoke the chat model with the prepared messages.
5. **Inspect the response:** Read the assistant's message and, when available, metadata such as token usage and the reason generation stopped.
6. **Update the history:** Add the user's message and the assistant's reply to your application's conversation history.
7. **Repeat:** Send the updated history with the next request if the model needs to understand earlier turns.

### Step 3: Understand the message structure

A chat conversation is represented as an ordered list of messages. Each message has a role and content.

| Message type | Purpose | Example |
|---|---|---|
| System message | Establishes the assistant's behavior and constraints | You are a helpful AI tutor. |
| Human message | Contains the user's input | Explain machine learning. |
| AI message | Contains an assistant response | Machine learning enables systems to learn patterns from data. |
| Tool message | Contains the output returned by a tool | The calculator returned 42. |

The exact supported message types depend on the framework and provider integration. Tool messages are generally part of a tool-calling workflow rather than ordinary user-assistant conversation.

The order matters. If the application omits an earlier message, the model generally cannot use that message's contents unless the information is supplied elsewhere in the current request.

### Step 4: Understand prompt templates

A prompt template lets you define a reusable instruction containing placeholders.

For example, instead of manually building a new string every time, define:

- Template: `Explain {topic} in simple language for a {audience}.`
- Topic: `transformers`
- Audience: `beginner`

The resulting prompt becomes:

`Explain transformers in simple language for a beginner.`

This approach makes it easier to maintain consistent instructions, validate inputs, and reuse the same prompt for different tasks.

### Step 5: Understand the mathematics

LangChain itself is not a machine-learning algorithm, so it does not have one universal training equation. Its core conversational behavior can nevertheless be described using message lists and conditional language generation.

**Conversation construction**

`conversation_t = [system_message, user_message_1, assistant_message_1, ..., user_message_t]`

This represents the ordered messages supplied to the model for a particular call. A real application may omit the system message, include additional message types, or send only a selected portion of the history.

**Next-token prediction**

`P(token_t | token_1, token_2, ..., token_(t-1))`

This represents the probability of generating the next token given the preceding tokens. A chat model generates a response by repeatedly predicting and selecting tokens until generation stops.

**Conditional response generation**

`P(response | conversation)`

This represents the probability distribution over possible responses given the supplied conversation. The model uses the provided context to generate a response; it does not automatically access every previous request made by the application.

**Prompt-template substitution**

`final_prompt = template with each placeholder replaced by its input value`

This is a conceptual representation of template formatting, not a machine-learning equation.

### Step 6: Understand what the response metadata tells you

Do not inspect only the generated text. A model response may also provide metadata such as:

- **Input tokens:** Tokens consumed by the supplied messages and prompt.
- **Output tokens:** Tokens generated in the response.
- **Total tokens:** The total reported token usage, commonly the sum of input and output tokens.
- **Finish reason:** Why generation stopped, such as reaching a stop condition or a token limit.
- **Model information:** The model identifier or other provider-specific response details.

Availability and exact field names vary by integration. Some providers return token usage directly, while others may omit it unless additional settings are enabled.

A response that ends because it reached a token limit may be incomplete. A normal stop reason does not, by itself, guarantee that the answer is correct or complete.

## Theory Deep Dive

### 1. Core foundations

LangChain conversational applications combine several concepts:

**A. Message-based interaction**

A conversation is a sequence of messages rather than one unstructured string. Message roles help the model distinguish instructions, user requests, assistant replies, and tool results.

**B. Stateless model calls**

For an ordinary chat-model API call, the model receives the request and generates a response without automatically retrieving the history of previous API calls. The application must resend relevant context or use an external system to retrieve it.

**C. Conditional language generation**

The model generates a response conditioned on the input context. At the token level, the probability of the next token depends on the preceding tokens.

**D. Separation of concerns**

A prompt template defines how inputs are formatted, the model performs generation, and application logic determines how messages and results are handled. Separating these responsibilities makes an application easier to test and maintain.

### 2. Key assumptions

- **Context must be supplied:** Information from an earlier call is unavailable unless it is included in the new request or retrieved through another mechanism.
- **The model follows probabilistic generation:** Identical inputs do not always produce identical responses, depending on sampling settings, provider behavior, and other factors.
- **Context windows are limited:** The total prompt and generated response must fit within the model's supported context and output limits.
- **Prompt templates require valid inputs:** Missing placeholders, incorrect variable names, and unexpected input types can cause errors or produce unintended prompts.
- **Provider behavior can differ:** A common interface does not guarantee identical capabilities, parameters, tokenization, tool-calling behavior, or response metadata across providers.
- **Conversation history must be managed deliberately:** Keeping every message forever can increase cost and eventually exceed the context window.

### 3. Important properties

**Property 1: Conversation continuity depends on context**

If the application sends the previous messages again, the model can use their contents to answer the next question. If those messages are omitted, the model generally cannot know what was discussed earlier.

**Property 2: Conversation history is not the same as persistent memory**

History is the information supplied in a request. Persistent memory is an application-level mechanism that stores or retrieves selected information across requests or sessions. A memory system may use a database, a summary, or a retrieval mechanism.

**Property 3: Prompt templates improve consistency**

A shared template reduces duplicated formatting logic. It does not guarantee correct answers, and untrusted user input must still be handled carefully.

**Property 4: Token usage affects cost and limits**

More conversation history usually means more input tokens. This can increase API costs and leave less room for the generated answer.

**Property 5: A successful call does not imply a successful task**

An API request may complete normally while producing an incorrect, irrelevant, or incomplete answer. Applications need suitable validation and evaluation.

### 4. Common variations and types

| Concept | Description | Typical use |
|---|---|---|
| Single-turn chat | Sends only the current request and instructions | One-off explanations or classification |
| Multi-turn chat | Sends relevant previous messages with each request | Chatbots and conversational assistants |
| Prompt templates | Reusable prompts with placeholders | Standardized instructions |
| Conversation summaries | Replaces older messages with a concise summary | Long-running conversations |
| Persistent memory | Stores selected information outside the model call | User preferences and cross-session context |
| Streaming responses | Delivers generated output incrementally | Interactive chat interfaces |
| Tool-calling workflows | Allows the model to request supported tools | Search, calculations, and application actions |
| Model switching | Changes the configured model or provider | Testing, portability, and provider selection |

### 5. Limitations and edge cases

- **Missing history:** A follow-up question such as "What about its disadvantages?" may be unclear if the earlier topic is omitted.
- **Context-window overflow:** Long conversations may exceed the model's limits. Truncation, summarization, or retrieval can help, but each approach may discard important details.
- **Provider incompatibility:** Switching providers may require changes to parameters, tool definitions, structured output settings, or metadata handling.
- **Sensitive information:** Conversation history may contain private data. Store only what is necessary and apply appropriate access controls and retention policies.
- **Prompt injection:** User messages and retrieved documents may contain instructions that conflict with application rules. Treat untrusted content as data and validate sensitive actions.
- **Misleading metadata:** Missing token counts do not mean zero usage. Finish reasons also differ across providers.
- **API failures:** Network errors, invalid credentials, rate limits, and provider outages require appropriate exception handling.
- **History duplication:** Adding the same user or assistant message more than once can distort the conversation and waste tokens.

### 6. API keys and security

Never hard-code a real API key in source code that will be pushed to GitHub. Store credentials in environment variables or an appropriate secrets manager.

For local development, a `.env` file can be used with a library such as `python-dotenv`, provided the file is excluded from version control. Commit a `.env.example` containing placeholder values instead.

Do not expose a private API key in frontend JavaScript or a browser application. Route requests through a backend that protects the key and applies authentication, rate limiting, and suitable usage controls.

Remember that environment variables reduce accidental exposure but do not automatically make a compromised machine or deployment secure.

## Code Implementation

### Installation

Install the packages required by the practical example and visualization:

```bash
pip install -U langchain-core langchain-openai python-dotenv numpy matplotlib
```

Set `OPENAI_API_KEY` in your environment. For local development, you can store it in a `.env` file and add `.env` to `.gitignore`.

### From Scratch (NumPy only)

This example simulates the core conversation-history mechanism without calling an LLM. It demonstrates that the application must explicitly provide previous messages.

```python
import numpy as np

# A small vocabulary makes it possible to demonstrate how an
# application can represent and inspect conversation history.
vocabulary = np.array([
    "hello",
    "machine",
    "learning",
    "is",
    "useful"
])

# These illustrative vectors are not trained language-model embeddings.
embeddings = np.array([
    [1.0, 0.0],
    [0.0, 1.0],
    [0.0, 0.8],
    [0.5, 0.5],
    [0.8, 0.2]
])

def encode_word(word):
    """Return the vector for a word in the demonstration vocabulary."""
    matches = np.where(vocabulary == word)[0]

    # Fail explicitly for unknown words instead of returning a misleading vector.
    if len(matches) == 0:
        raise ValueError(f"Unknown word: {word}")

    return embeddings[matches[0]]


def display_conversation(messages):
    """Print messages in their original conversational order."""
    for message in messages:
        print(f"{message['role']}: {message['content']}")


# The application stores messages so later requests can reuse their context.
history = [
    {"role": "system", "content": "You are a helpful AI tutor."},
    {"role": "user", "content": "I am learning machine learning."},
    {"role": "assistant", "content": "Great! Machine learning is useful."}
]

print("First conversation:")
display_conversation(history)

# Add a follow-up message to the existing conversation.
history.append({
    "role": "user",
    "content": "Explain it simply."
})

print("\nConversation after the second user turn:")
display_conversation(history)

# This request deliberately omits previous messages to simulate missing context.
third_call_without_history = [
    {"role": "user", "content": "What are its benefits?"}
]

print("\nThird call without history:")
display_conversation(third_call_without_history)

print("\nMessages with history:", len(history))
print("Messages without history:", len(third_call_without_history))

# The vector lookup is separate from conversation handling.
print("\nVector for 'learning':", encode_word("learning"))
```

This implementation illustrates message handling, not actual LLM inference. It does not train a model, generate language, or provide real semantic embeddings.

### Using Libraries (LangChain + OpenAI)

This example creates a three-turn conversation using a prompt template. It sends the history on every turn, inspects response metadata, and compares the final request with one that omits the history.

```python
import os
from dotenv import load_dotenv

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI

# Load local development credentials without embedding them in source code.
load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError(
        "Set OPENAI_API_KEY in your environment or local .env file."
    )

# Low temperature reduces sampling variability but does not guarantee
# identical answers across every model or provider configuration.
model = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0
)

# The template separates fixed instructions from changing user inputs.
prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a concise AI tutor. Explain concepts simply. "
        "Use earlier messages when they are provided."
    ),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{question}")
])

# Compose the prompt and model into one reusable chain.
chain = prompt | model

history = []

questions = [
    "I am learning machine learning. Remember that I am a beginner.",
    "Explain it in two simple sentences.",
    "What are its benefits for someone like me?"
]

for turn, question in enumerate(questions, start=1):
    print(f"\n--- Turn {turn} ---")
    print("User:", question)

    # Each call receives the messages collected before the current turn.
    response = chain.invoke({
        "history": history,
        "question": question
    })

    print("Assistant:", response.content)

    # Usage metadata may be absent for some integrations or configurations.
    usage = response.usage_metadata
    if usage:
        print("Input tokens:", usage.get("input_tokens"))
        print("Output tokens:", usage.get("output_tokens"))
        print("Total tokens:", usage.get("total_tokens"))
    else:
        print("Token usage was not returned.")

    # Finish reasons are provider-specific and may be absent.
    finish_reason = response.response_metadata.get("finish_reason")
    print("Finish reason:", finish_reason or "Not provided")

    # Store both sides of the completed turn so later requests can
    # interpret references to earlier information.
    history.append(HumanMessage(content=question))
    history.append(AIMessage(content=response.content))


# Compare the final question when earlier context is omitted.
print("\n--- Third turn without history ---")

response_without_history = chain.invoke({
    "history": [],
    "question": questions[2]
})

print("Assistant:", response_without_history.content)
print("Without history, the model may not know what 'its' refers to.")
```

**Implementation notes:**

- The model identifier must be available to your account and supported by the installed integration. Change it if necessary.
- `MessagesPlaceholder` inserts the supplied message list into the prompt.
- The history is stored in Python memory and disappears when the process ends unless it is persisted elsewhere.
- Token usage and finish-reason fields can vary by provider.
- Switching providers usually requires installing and configuring the corresponding LangChain integration package.

### Switching providers

For example, install the Google Gemini integration:

```bash
pip install -U langchain-google-genai
```

Then configure the model with a Google API key stored in an environment variable:

```python
import os
from langchain_google_genai import ChatGoogleGenerativeAI

# Fail early if credentials are missing instead of making a failing API call.
if not os.getenv("GOOGLE_API_KEY"):
    raise RuntimeError("Set GOOGLE_API_KEY before creating the model.")

model = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
```

The prompt and history logic can often remain unchanged with a compatible chat model. Always verify the current model identifier and provider-specific configuration.

## Visual Intuition

A useful diagram would show three requests flowing through the same prompt template and model. The first request introduces a topic, the second request includes the first exchange, and the third request either includes the history or sends only the latest question.

The diagram should emphasize that **the application carries the conversation forward by sending previous messages again**.

The following Python code generates a visualization of the difference in context supplied to the model.

```python
import matplotlib.pyplot as plt

# These values represent the number of messages supplied to each request.
turns = [
    "Turn 1",
    "Turn 2",
    "Turn 3 with history",
    "Turn 3 without history"
]
message_counts = [2, 4, 6, 1]

plt.figure(figsize=(10, 5))

# Comparing bar heights makes the difference in supplied context visible.
bars = plt.bar(turns, message_counts)

plt.title("Conversation Context Supplied to Each Model Call")
plt.xlabel("Model call")
plt.ylabel("Number of messages supplied")
plt.xticks(rotation=15, ha="right")

# Numeric labels make values easier to read accurately.
plt.bar_label(bars, padding=3)

plt.tight_layout()
plt.show()
```

More messages do not automatically mean better answers. Irrelevant history can increase cost and distract the model.

## Common Mistakes and Misconceptions

1. **Assuming LangChain gives the model permanent memory.**  
   LangChain helps manage messages and workflows. Your application must resend conversation history or retrieve stored information when needed.

2. **Sending only the latest question in a multi-turn conversation.**  
   Include relevant earlier messages when the new question depends on them. Otherwise, references such as "it," "that," or "as mentioned earlier" may be ambiguous.

3. **Treating every model provider as identical.**  
   LangChain provides a common interface, but models can differ in supported parameters, tool calling, context limits, tokenization, and response metadata.

4. **Committing API keys to GitHub.**  
   Use environment variables or a secrets manager. Keep `.env` out of version control and revoke exposed credentials immediately.

5. **Reading only `response.content`.**  
   Inspect available usage metadata and finish reasons as well. A response can be truncated, expensive, or incomplete even when it contains readable text.

## Interview Questions

**1. What is LangChain, and why is it useful?**

LangChain is a framework for building LLM applications. It provides reusable components for model integration, prompt templates, message handling, tools, and workflows.

**2. Why must conversation history be passed to a chat model?**

A typical model API call does not automatically retrieve previous calls. The application must supply earlier messages or retrieve relevant information through a separate memory system.

**3. What is the difference between a prompt template and a normal string?**

A normal string contains fixed text. A prompt template contains reusable placeholders that can be filled with different inputs at runtime.

**4. How would you implement a chatbot that remembers previous turns?**

Store each user's messages and the assistant's replies in a history structure. Include relevant history in subsequent requests, and use persistent storage if the conversation must survive application restarts.

**5. How would you investigate a chatbot response that appears incomplete?**

Inspect the finish reason, token usage, context-window constraints, provider errors, and configured output-token limit. If generation stopped at a token limit, adjust the limit or redesign the prompt and output strategy.

## Summary Table

| Aspect | Details |
|---|---|
| Type | LLM application framework and orchestration library |
| Input | Messages, prompt-template variables, model configuration, and optional conversation history |
| Output | Model-generated responses and, when available, usage and response metadata |
| Key equation | `P(response \| conversation)`; the response is conditioned on the supplied context |
| When to use | Chatbots, reusable prompts, multi-step LLM workflows, tool integrations, and RAG applications |
| When NOT to use | When a direct provider SDK is sufficient, when no orchestration is needed, or when a task requires a deterministic algorithm rather than language generation |

## What to Learn Next

1. **Prompt Engineering and Structured Outputs** — Learn how to write reliable instructions, constrain response formats, and validate model-generated data.
2. **Conversation Memory and Message History** — Learn to persist, summarize, and retrieve conversation context while controlling token usage.
3. **LangChain Chains, Tools, and LCEL** — Learn how to compose prompts, models, output parsers, and tools into reusable application workflows.

---

**Practical exercise:** Run the three-turn conversation, inspect token usage and the finish reason, and then remove the history from the third call. Compare the answers and explain why they may differ.

**Learning outcome:** You can call a chat model through LangChain, create reusable prompt templates, manage multi-turn conversations, protect API keys, inspect response metadata, and explain why a model appears to remember only the context supplied to it.
