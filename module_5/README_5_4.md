# Tools for Agents

## 1. What Is It?

In an AI agent, a **tool** is a function or service the language model can choose to use to get information or perform an operation. The model decides when a tool is appropriate, while the application executes the tool and returns its result to the model.

Examples include:

- Searching a collection of university documents with a RAG pipeline.
- Looking up an order or checking a calendar.
- Calculating a value with Python.
- Creating a support request.
- Sending an email after the required approval.

A tool usually has a **name**, a **description**, and defined **inputs**. It also returns a result that the agent can use.

```text
User request
     |
     v
Language model chooses a tool
     |
     v
Application executes the tool
     |
     v
Tool result returns to the model
     |
     v
Agent answers or chooses another action
```

## 2. Why Does It Matter?

A language model alone cannot automatically access your private documents, query your database, or perform actions in your application. Tools provide a controlled way to connect the model to those capabilities.

Well-designed tools help you:

- **Ground answers in your data:** Give an agent access to a RAG search system or database.
- **Extend what the agent can do:** Connect it to APIs, business systems, and useful Python functions.
- **Choose the right operation:** Let the model select among multiple tools based on their descriptions.
- **Control context size:** Return concise, relevant results rather than large data dumps.
- **Handle failures:** Give the agent a useful signal when an operation does not succeed.
- **Protect important actions:** Apply permissions and approval rules to tools that change external systems.

Tool design is part of AI Engineering because vague tool descriptions, oversized results, or unsafe permissions can make an otherwise capable agent unreliable.

## 3. How Does It Work?

### 3.1 Define each tool clearly

A tool should have:

- **Name:** A short, descriptive identifier, such as `search_university_docs`.
- **Description:** What it does and when the agent should use it.
- **Inputs:** The arguments it requires, including their expected types and meanings.
- **Output:** A useful result the model can interpret.
- **Failure behavior:** A clear way to communicate errors or unsuccessful operations.

For example:

```text
Name: search_university_docs

Description:
Search approved university documents for information about
courses, exam rules, and academic policies.

Input:
query (string) — the question or topic to search for.

Output:
A small list of relevant passages and their source names.
```

Descriptions should explain when a tool is appropriate. If an agent has several tools, distinguish them clearly—for example, searching university policy documents is different from searching the public web.

### 3.2 Turn a RAG pipeline into a tool

**Retrieval-augmented generation (RAG)** searches a document collection for relevant passages and provides those passages as context for an answer. A RAG pipeline can be exposed as a tool so an agent can decide when it needs information from your documents.

```text
Agent
  |
  | chooses search_university_docs
  v
RAG tool
  |
  +--> Convert question into a search query
  |
  +--> Retrieve relevant document chunks
  |
  +--> Return concise passages with sources
  |
  v
Agent reads the result and responds
```

The tool does not need to return a fully written answer. Often, returning relevant passages and source identifiers lets the agent use the evidence in its next step. Alternatively, if your RAG system already produces grounded answers, you can expose that answer as the tool result.

### 3.3 Let the model choose between tools

An agent may have multiple tools available, such as:

- `search_university_docs` — retrieve information from private university documents.
- `search_web` — look for current public information, if web access is available.
- `create_support_request` — create a support ticket in a connected system.

The model uses the request, tool names, descriptions, and input schemas to decide which tool to request. The application must validate the request and execute the selected function.

Tool selection is not guaranteed to be correct. Clear descriptions, constrained inputs, testing, and application-side validation help reduce mistakes.

### 3.4 Keep tool results small and useful

Tool results are usually added to the model's context. Large outputs can consume context space, increase cost or latency, and distract the model with irrelevant information.

Good practices include:

- Return the most relevant few results rather than every match.
- Limit the length of each document passage.
- Include source identifiers or links when they are useful.
- Remove unnecessary metadata and repeated content.
- Return structured fields instead of a large, unfiltered API response.

For example, instead of returning an entire 100-page handbook, a search tool might return three short passages with document names and page numbers. The right limit depends on the task and the model's context capacity.

### 3.5 Handle tool failures

Tools can fail because of network errors, invalid inputs, unavailable services, permission problems, or missing results.

A useful tool error should tell the agent what happened without exposing secrets or internal sensitive details.

Examples:

```text
Search completed, but no relevant passages were found.
```

```text
The support service is temporarily unavailable. No ticket was created.
```

```text
The query is missing. Provide a non-empty search question.
```

Depending on the error, the agent may:

1. Retry a temporary failure, preferably with a retry limit.
2. Correct invalid inputs.
3. Use another suitable tool.
4. Ask the user for missing information.
5. Explain that it could not complete the task.

Do not treat every failure as retryable. Repeating a permanent permission error will not help, and retrying an action without checking whether it already succeeded can create duplicate records.

### 3.6 Separate read tools from action tools

Tools differ in their effect on external systems.

| Tool type | What it does | Examples | Main concern |
|---|---|---|---|
| Read-only | Retrieves information without intentionally changing the system | Search RAG documents, check ticket status, look up a policy | Data access and privacy |
| Action or write | Creates, updates, deletes, or sends something | Create a ticket, update a booking, send an email | Unintended or duplicate actions |

Read-only tools can still expose sensitive information, so they also need appropriate access controls. Action tools need additional care because they can change the world outside the model.

For action tools:

- Validate arguments on the application side.
- Check the user's permissions.
- Require confirmation or human approval for consequential actions when appropriate.
- Avoid exposing unnecessary destructive operations.
- Make the outcome clear: distinguish success, failure, and uncertain status.
- Use idempotency or duplicate checks where supported, especially before retrying an action.

**Important:** A model's decision to call a tool is not authorization. Your application must enforce permissions and safety rules independently.

## 4. Simple Example

This Python example demonstrates two tools: one searches a tiny, in-memory university knowledge base, and another creates a simulated support request. It uses LangChain's tool decorator to expose functions with descriptions and input schemas.

The support-request function only creates a local dictionary for demonstration. It does not contact a real support service.

### Install the dependency

```bash
pip install -U langchain-core
```

### Code

```python
from langchain_core.tools import tool


UNIVERSITY_DOCS = [
    {
        "source": "Exam Policy",
        "text": "Students must check the official exam notice "
                "for the published examination schedule.",
    },
    {
        "source": "Library Policy",
        "text": "Students can consult the library rules for "
                "borrowing periods and renewal conditions.",
    },
]


@tool
def search_university_docs(query: str) -> str:
    """Search university documents for academic policies and rules.
    Use this when a question needs information from university documents."""
    if not query.strip():
        return "Search failed: provide a non-empty query."

    terms = query.lower().split()
    matches = [
        doc for doc in UNIVERSITY_DOCS
        if any(term in doc["text"].lower() for term in terms)
    ]

    if not matches:
        return "No relevant passages were found."

    # Keep the output small and include source names.
    return "\n".join(
        f"Source: {doc['source']}\nPassage: {doc['text']}"
        for doc in matches[:3]
    )


@tool
def create_support_request(summary: str) -> str:
    """Create a support request for a problem that needs staff follow-up.
    Use this only when the user asks to report or submit a problem."""
    if not summary.strip():
        return "Request failed: provide a non-empty summary."

    # Simulate creating a ticket; no external system is contacted.
    ticket = {
        "ticket_id": "DEMO-001",
        "summary": summary.strip(),
        "status": "created",
    }

    return (
        f"Support request {ticket['ticket_id']} created. "
        f"Status: {ticket['status']}. "
        f"Summary: {ticket['summary']}"
    )


tools = [search_university_docs, create_support_request]

for agent_tool in tools:
    print(agent_tool.name)
    print(agent_tool.description)
    print()
```

### How it works

1. The `@tool` decorator turns each Python function into a tool that LangChain can describe to a model.
2. The function name and docstring help explain what the tool does and when to use it.
3. The function parameters define the inputs. Here, both tools accept a string.
4. The search tool returns a small set of matching passages with source names.
5. The support tool validates its input and returns a simulated ticket result.
6. The `tools` list groups the available tools so they can be supplied to a compatible model or agent.

This example defines the tools but does not run an LLM or complete an agent loop. To build a full agent, bind the tools to a compatible chat model and implement the model/tool cycle using your chosen agent framework. The agent requests a tool call; your framework executes the function and returns its result to the model.

The keyword search above is intentionally simple. A real RAG tool should call your existing retrieval pipeline rather than rely on substring matching.

## 5. Practical AI Engineering Application

### Give your agent access to your own RAG system

Suppose you have built a RAG assistant for university documents. Instead of duplicating the retrieval logic, wrap the existing search function as a tool:

```python
@tool
def search_university_docs(query: str) -> str:
    """Search the university knowledge base and return relevant
    passages with source information."""
    results = existing_rag_search(query, top_k=3)

    if not results:
        return "No relevant passages were found."

    return format_concise_sources(results)
```

Here, `existing_rag_search()` and `format_concise_sources()` are placeholders for functions in your project; replace them with your actual implementation. Keep the tool's output limited to relevant passages and source metadata.

### Example workflow: search only

User request:

> What does the university policy say about exam schedules?

Possible flow:

```text
User asks about exam schedules
        |
        v
Agent selects the RAG search tool
        |
        v
RAG retrieves policy passages
        |
        v
Agent answers using the returned evidence
```

No action tool is needed because the user only asked for information.

### Example workflow: search, then act

User request:

> Find the support instructions for a missing student ID card, then create a support request for me.

Possible flow:

```text
User request
     |
     v
Search RAG documents for the instructions
     |
     v
Agent reviews the search result
     |
     v
Prepare a support request
     |
     v
Validate details and apply any required approval
     |
     v
Create the support request
     |
     v
Return the confirmed result to the user
```

This workflow combines a read operation with an action. The agent should use the retrieved information to prepare the request, but the application should still validate required fields and permissions before creating it. If a ticket-creation result is uncertain, check the service for an existing ticket before retrying.

### A practical tool-design checklist

Before adding a tool to an agent, ask:

- Is its name clear and distinct from other tools?
- Does the description state when to use it?
- Are its inputs explicit and validated?
- Does it return only useful information?
- Are errors clear and safe to expose to the model?
- Is it read-only or does it change an external system?
- Are permissions, confirmation, and duplicate-action handling in place where needed?
- Have normal, invalid-input, empty-result, and service-failure cases been tested?

## 6. Key Takeaways

- Tools connect an agent to functions, private data, APIs, and external actions.
- Tool names, descriptions, and input schemas help the model choose the right operation.
- A RAG pipeline can be wrapped as a search tool so the agent can retrieve information from your own documents.
- Keep results concise, relevant, and traceable to their sources.
- Handle failures with useful messages, appropriate retry limits, and graceful fallback behavior.
- Separate read-only tools from tools that create or change things.
- Tool calls requested by a model must still be validated and authorized by the application.

## 7. Common Misconceptions

- **“Adding a tool means the model executes it directly.”** The model generally requests a tool call; the application or agent framework executes the function and returns the result.
- **“More tools always make an agent better.”** Too many overlapping or poorly described tools can make tool selection harder.
- **“The agent can safely decide whether an action is allowed.”** Authorization and permission checks must be enforced outside the model.
- **“A successful tool call guarantees a correct final answer.”** The agent can misunderstand or misuse the result, so important outputs still need validation.
- **“A tool error should always trigger a retry.”** Retry only when appropriate; permanent errors and uncertain action outcomes need different handling.

## 8. Quick Revision

**Q1. What is a tool in an AI agent?**  
**A:** A callable function or service that lets the agent retrieve information or perform an operation.

**Q2. Why wrap a RAG pipeline as a tool?**  
**A:** It lets the agent choose when to search your document collection and use the retrieved evidence.

**Q3. What makes a tool easy for an agent to select?**  
**A:** A distinct name, a clear description, and well-defined inputs and outputs.

**Q4. Why should tool outputs be concise?**  
**A:** To reduce irrelevant context, conserve tokens, and make useful evidence easier for the model to process.

**Q5. How should read tools and action tools differ?**  
**A:** Read tools retrieve information; action tools change external systems and need suitable validation, permissions, and sometimes human approval.

## Try It

1. Wrap your Module 4 RAG search function as a tool named `search_university_docs`.
2. Return a small number of relevant passages and include source information.
3. Add a second tool such as `create_support_request`.
4. Test a question that needs only document search.
5. Test a task that requires searching the documents and then creating a request.
6. Test empty inputs, no search results, and a simulated service failure.
7. Verify that the application validates and authorizes action requests before executing them.

**Outcome:** Give an agent a well-designed set of tools, including your own RAG system.
