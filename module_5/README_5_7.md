# MCP Fundamentals

## 1. What Is It?

The **Model Context Protocol (MCP)** is an open protocol for connecting AI applications to external tools, data sources, and reusable prompts through a common interface.

Without a shared protocol, developers often build a separate integration for every AI application and every external system. MCP provides a standard way for an AI application to communicate with an MCP server, reducing the need to rebuild each integration from scratch.

An MCP server might expose access to a folder of documents, a code repository, a database, or another service.

## 2. Why Does It Matter?

AI agents are more useful when they can access information and perform actions outside the language model. However, every external system can have its own API, authentication method, and data format.

MCP helps by:

- **Reducing integration work:** An application with MCP support can connect to compatible MCP servers.
- **Reusing integrations:** A server can expose capabilities to multiple compatible clients.
- **Separating responsibilities:** The AI application can focus on the agent workflow while a server handles access to a particular system.
- **Making capabilities discoverable:** Clients can learn which tools, resources, and prompts a server offers.
- **Supporting different backends:** Servers can connect agents to files, databases, developer tools, and other services.

MCP does not automatically make every system accessible or safe. A server must implement the relevant capabilities, and the application still needs appropriate permissions and security controls.

## 3. How Does It Work?

### A. Host, client, and server

MCP uses three main roles:

- **Host:** The AI application the person uses. It manages the interaction with the model and coordinates access to MCP capabilities. An agent application built with LangChain and LangGraph can act as a host.
- **Client:** The component inside the host that communicates with an MCP server using the protocol.
- **Server:** A program that exposes capabilities from a system, such as a document folder, database, or repository.

The host may connect to multiple MCP servers, often using a separate client connection for each server.

A simplified view:

```text
User
 |
 v
AI application / Host
 |-- Language model
 |-- MCP client
       |
       | MCP protocol
       v
   MCP server
       |
       v
   Files, database, or external service
```

The model does not usually communicate with an MCP server directly. The host and its client manage the protocol interaction, while the application decides how available capabilities are presented to the model and how results are used.

### B. What can an MCP server offer?

MCP defines several kinds of capabilities. Three important ones are tools, resources, and prompts.

| Capability | Purpose | Example |
|---|---|---|
| **Tools** | Actions the client can make available for the model or application to invoke. | Search a repository, create an issue, or query a database. |
| **Resources** | Data that an application can read or provide as context. | A document, a file, or a record. |
| **Prompts** | Reusable prompt templates or workflows that a client can present to a user. | A template for reviewing code or summarizing a document. |

Their availability and behavior depend on the server and client implementation. Not every server provides all three capabilities.

A useful distinction: a tool generally represents an operation, a resource represents information, and a prompt provides reusable instructions or a template.

### C. Tool calling versus MCP

These concepts are related but solve different problems.

**Tool calling** is a model interaction pattern. The model requests that an available function or tool be run, usually with structured arguments. The application executes it and returns the result to the model.

**MCP** is a protocol for exposing and exchanging tools, resources, and prompts between applications and servers.

For example:

1. An MCP server exposes a `search_documents` tool.
2. The AI application connects to the server and discovers its available tools.
3. The application makes the relevant tool available to the agent.
4. The model decides to call `search_documents` with a query.
5. The application routes the call through the MCP client to the server.
6. The server runs the operation and returns a result.
7. The agent uses the result to answer the user.

The model's tool call is not itself MCP. MCP supplies a standardized way for the application to discover and communicate with the external capability.

### D. Connecting to existing MCP servers

You do not always need to create an MCP server yourself. Existing servers may provide access to file systems, source-code repositories, databases, and other services.

A typical setup involves:

1. Choose a server that supports the system you need.
2. Read its documentation and check its permissions, configuration, and trustworthiness.
3. Configure how the server runs or how the client connects to it.
4. Connect the host using an MCP client.
5. Discover the server's tools, resources, or prompts.
6. Expose only the capabilities the agent needs.
7. Test normal behavior, errors, and permission boundaries.

MCP servers may use different connection transports, such as standard input/output (stdio) for a locally launched process or HTTP-based transport for a remote server. Follow the specific server and client documentation rather than assuming every server uses the same setup.

## 4. Simple Example

Suppose you have a folder of course notes and want an agent to find and summarize a file.

### Example workflow

```text
User: Find and summarize my notes about RAG
              |
              v
Agent decides to search for relevant files
              |
              v
MCP client sends a tool request
              |
              v
File-system MCP server searches permitted folder
              |
              v
Server returns matching file information or content
              |
              v
Agent summarizes the relevant information
```

### What happens at each step?

1. The user asks a question in the AI application.
2. The agent has access to a file-search tool exposed by an MCP server.
3. The model requests that tool with an appropriate search argument.
4. The host routes the request through the MCP client.
5. The server accesses only the configured folder and returns results.
6. The model uses the returned content to write a summary.

The server provides the file-system capability; the model interprets the user's request and uses the returned information to formulate an answer.

**Safety note:** A file-system server may be able to read, write, or delete files depending on its implementation and configuration. Point it at a limited folder, grant only the necessary permissions, and do not connect an untrusted server to sensitive files.

## 5. Practical AI Engineering Application

A common pattern is to use **LangChain's MCP integration** to connect to an MCP server, adapt its tools for the agent, and use those tools inside a **LangGraph** workflow.

The overall architecture looks like this:

```text
User request
    |
    v
LangGraph agent
    |
    v
Language model chooses a tool
    |
    v
LangChain tool adapter
    |
    v
MCP client
    |
    v
MCP server
    |
    v
External system
    |
    v
Tool result returns to the agent
```

### Suggested implementation steps

1. Choose an MCP server for the system you want to access, such as a file-system server.
2. Install the MCP integration package and dependencies recommended by the current LangChain documentation.
3. Configure the server's launch command or connection details and permitted resources.
4. Use the LangChain MCP integration to discover and load the server's tools.
5. Provide the loaded tools to your LangGraph agent or tool-calling node.
6. Ask the agent to perform a small read-only task, such as locating and summarizing a document.
7. Test missing files, invalid arguments, server failures, and permission boundaries.

Exact imports and APIs can vary by package version and integration. Consult the current LangChain MCP documentation and the chosen server's instructions before copying code into a project.

### What MCP does and does not do

**MCP does:**

- Standardize communication between compatible applications and servers.
- Provide a common way to discover and use tools, resources, and prompts.
- Help reuse integrations across supported AI applications.

**MCP does not:**

- Replace the language model or the agent's reasoning loop.
- Guarantee that a model will choose the right tool.
- Automatically grant access to every file or external service.
- Replace authentication, authorization, input validation, or security reviews.
- Guarantee that a server's output is trustworthy.

Treat tool descriptions and returned content as external input. Retrieved documents can contain misleading text or prompt-injection attempts, so the agent should not treat document content as higher-priority instructions.

## 6. Key Takeaways

- **MCP (Model Context Protocol)** standardizes how AI applications connect to external capabilities.
- The **host** is the AI application, the **client** communicates with servers, and the **server** exposes capabilities from a system.
- MCP servers can offer **tools, resources, and prompts**.
- **Tool calling** describes how a model requests an operation; **MCP** standardizes how the application discovers and communicates with external capabilities.
- Existing MCP servers can connect agents to systems such as file folders, code repositories, and databases.
- LangChain's MCP support can make server tools available to a LangGraph agent.
- Use least-privilege permissions and trusted servers, especially when tools can modify data.

## 7. Common Misconceptions

- **“MCP is a language model.”** No. It is a protocol for connecting applications with external capabilities.
- **“MCP and tool calling mean the same thing.”** No. Tool calling is a model interaction pattern; MCP is a protocol for exchanging capabilities between applications and servers.
- **“Every MCP server provides tools, resources, and prompts.”** No. A server exposes the capabilities it implements.
- **“Connecting an MCP server makes it safe.”** No. You must review the server, restrict permissions, and validate how the agent uses its outputs.
- **“The model connects directly to every server.”** Typically, the host and its MCP client manage server communication and coordinate tool use.

## 8. Quick Revision

**Q1. What problem does MCP solve?**  
It provides a standard way for AI applications to connect to external tools and data sources.

**Q2. What are the host, client, and server?**  
The host is the AI application, the client communicates with an MCP server, and the server exposes capabilities from an external system.

**Q3. What are the three important MCP capability types?**  
Tools, resources, and prompts.

**Q4. How is tool calling different from MCP?**  
Tool calling is how a model requests an operation; MCP is a protocol for discovering and communicating with external capabilities.

**Q5. How can an MCP server help a LangGraph agent?**  
LangChain's MCP integration can load compatible server tools so the agent can use them as part of its workflow.
