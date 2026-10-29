# Building MCP Servers

## 1. What Is It?

An **MCP server** is a program that exposes a system's capabilities to compatible AI applications through the Model Context Protocol (MCP).

Instead of writing a separate custom integration for every AI app, you can package useful operations and information behind an MCP server. For example, a support-request server could let an agent create a request, check its status, and read support policies.

An MCP server can expose three main kinds of capabilities:

- **Tools:** Operations an application or model can invoke, such as creating or checking a support request.
- **Resources:** Information an application can read, such as support policies or reference documents.
- **Prompts:** Reusable prompt templates for common tasks, such as preparing a support request.

A server exposes only the capabilities it implements; it does not have to provide all three.

## 2. Why Does It Matter?

Without a shared interface, developers may need to build and maintain a different integration for each AI application that uses their system.

An MCP server helps by:

- **Reusing integrations:** Multiple MCP-compatible applications can connect to the same server.
- **Encapsulating system logic:** The server handles how requests are validated and how the underlying system is accessed.
- **Making capabilities discoverable:** Clients can inspect the tools and other capabilities the server provides.
- **Separating data from reasoning:** The AI model can decide when to use a capability without needing direct access to the underlying database or service.
- **Supporting controlled access:** The server can validate inputs and enforce permissions before carrying out operations.

This is useful for internal business systems, support platforms, project-management tools, document stores, and databases.

## 3. How Does It Work?

### A. Design tools, resources, and prompts

Consider a support-request system.

| MCP capability | What it exposes | Example |
|---|---|---|
| **Tool** | An action or operation | `create_support_request` |
| **Tool** | A query or lookup operation | `get_support_request` |
| **Resource** | Readable reference information | Support policies |
| **Prompt** | A reusable task template | Help a user prepare a clear support request |

Tools should perform a specific task. Resources should provide useful information. Prompts should help a user or application reuse a common interaction pattern.

### B. Give tools clear descriptions and typed inputs

An AI application needs to understand what each tool does and what arguments it requires. Use clear names, accurate descriptions, and structured input schemas.

For example:

- `create_support_request`: Create a support request with a title and description.
- `get_support_request`: Retrieve a request using its ID.

A tool should reject invalid inputs with an understandable error. Avoid vague names such as `process`, `do_task`, or `handle_data`, because the model may not know when to use them.

Keep tool results focused. Return the request ID, status, and other information needed for the next step rather than dumping a large database record.

### C. Local and remote servers

An MCP server can run in different environments:

- **Local server:** Runs on the same machine as the client, often launched as a subprocess using standard input/output (stdio).
- **Remote server:** Runs on another machine and is accessed over a network using a supported transport, such as Streamable HTTP.

Local does not automatically mean safe: a local server may have access to files or commands available to the current user. Remote servers require careful authentication and authorization, and all servers should be granted only the permissions they need.

For remote deployments, use the authentication mechanism supported by the server and client, protect credentials, and use encrypted connections such as HTTPS where applicable. Do not assume that every MCP server or transport uses the same authentication configuration.

### D. Test the server before connecting an agent

An MCP inspector is a development tool that lets you connect to an MCP server, inspect its advertised capabilities, and call tools directly.

A useful test sequence is:

1. Start the server using its documented command.
2. Connect an MCP inspector to the server.
3. Check that the expected tools, resources, and prompts appear.
4. Call each tool with valid inputs.
5. Try missing fields, invalid values, and unknown request IDs.
6. Confirm that errors are understandable and do not expose secrets.
7. Check that a tool does not perform an unintended action when given invalid input.

Testing the server independently makes it easier to separate server problems from agent or model problems.

### E. Connect several servers to one agent

An agent can use tools from multiple MCP servers. For example, one server might expose support requests, while another exposes internal documentation.

When connecting multiple servers:

- Use clear, distinct tool names and descriptions.
- Check for duplicate or confusing names.
- Make each server's purpose clear to the agent.
- Expose only the tools required for the task.
- Test how the agent chooses between tools with similar purposes.

Some integrations may namespace or otherwise adapt tool names. Do not assume every client resolves name collisions automatically; inspect the tools that the agent actually receives.

### F. Change a server safely

Changing a server can affect every application that depends on it. Renaming or removing a tool may break an agent's workflow, and changing an input schema may make previous calls invalid.

A safe change process is:

1. Record the server version and current tool schemas.
2. Make the change in a development environment.
3. Test tools directly with the inspector.
4. Test all affected agents and clients.
5. Document breaking changes.
6. Version the server or its interface and communicate changes to consumers.
7. Deploy carefully and keep a rollback plan for important systems.

Where compatibility matters, prefer adding a new tool or introducing a migration period over abruptly renaming or removing a widely used tool.

## 4. Simple Example

The following is a small illustrative Python MCP server for support requests. It uses the FastMCP API provided by the official Python MCP SDK. Package APIs and execution commands can change, so check the current SDK documentation before using it in a project.

Install the SDK in your project's environment:

```bash
python -m pip install "mcp[cli]"
```

Create a file named `support_server.py`:

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Support Requests")

# In-memory storage for a learning example only.
requests = {}
next_id = 1


@mcp.tool()
def create_support_request(title: str, description: str) -> dict:
    """Create a support request with a title and description."""
    global next_id

    clean_title = title.strip()
    clean_description = description.strip()

    if not clean_title:
        raise ValueError("Title must not be empty.")

    if not clean_description:
        raise ValueError("Description must not be empty.")

    request_id = str(next_id)
    next_id += 1

    record = {
        "request_id": request_id,
        "title": clean_title,
        "description": clean_description,
        "status": "open",
    }
    requests[request_id] = record
    return record


@mcp.tool()
def get_support_request(request_id: str) -> dict:
    """Get a support request by its ID."""
    record = requests.get(request_id)

    if record is None:
        raise ValueError(f"No support request found with ID {request_id}.")

    return record


@mcp.resource("support://policies")
def support_policies() -> str:
    """Read the basic support request policy."""
    return (
        "Support policy: include a clear title and a useful description. "
        "New requests start with status 'open'. Do not include passwords "
        "or other secrets in a support request."
    )


@mcp.prompt()
def prepare_support_request(issue: str) -> str:
    """Prepare a clear support request from a user's issue."""
    return (
        "Help the user prepare a concise support request. "
        "Do not invent facts or include secrets. "
        f"User's issue: {issue}"
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")
```

### Understand the example

- `FastMCP("Support Requests")` creates the server.
- `@mcp.tool()` exposes a Python function as a tool.
- Type hints such as `title: str` describe expected input types and help define the tool's input schema.
- The docstrings explain each tool's purpose to MCP clients.
- `@mcp.resource(...)` exposes the policy text as a resource.
- `@mcp.prompt()` exposes a reusable prompt template.
- `mcp.run(transport="stdio")` starts the server using standard input/output, a common way for a local client to launch an MCP server.

This example provides two tools and one resource, plus an optional prompt. Its storage is in memory, so requests disappear when the server process stops. It is for learning, not production. A real service should use durable storage, suitable access controls, and robust validation. Also, an MCP resource's presence does not guarantee every client automatically loads it into the model's context; the client decides how to use resources.

### Test it with an MCP inspector

Use the current MCP Inspector instructions for your installed SDK and environment. A common development workflow is to launch the inspector and configure it to run the local server using the equivalent of:

```bash
npx @modelcontextprotocol/inspector python support_server.py
```

The exact command and interface can vary by Inspector version. In the Inspector, verify that `create_support_request` and `get_support_request` are listed, inspect `support://policies`, and try valid and invalid tool inputs.

Because the example stores data in memory, create and retrieve requests within the same running server process. Restarting the server clears the sample data.

## 5. Practical AI Engineering Application

To use your server with an agent:

1. Run the server locally or deploy it to a trusted remote environment.
2. Configure an MCP client or a LangChain MCP integration to connect to it.
3. Discover the tools and make the appropriate ones available to your LangGraph agent.
4. Ask the agent to create a support request, then ask it to check the request using the returned ID.
5. Connect a second MCP-compatible application and verify that it can discover and use the server's capabilities.
6. Test errors, permissions, and changes to tool schemas before relying on the integration.

The exact LangChain imports and configuration depend on the current integration package and transport. Follow the official LangChain MCP integration documentation for version-specific setup.

### Production design checklist

- **Clear interface:** Use specific tool names, typed inputs, concise descriptions, and predictable outputs.
- **Validation:** Validate inputs on the server; do not rely only on the model to supply correct arguments.
- **Error handling:** Return useful errors without exposing internal paths, credentials, or sensitive records.
- **Authentication and authorization:** Identify callers and restrict what they may read or change, especially on remote servers.
- **Least privilege:** Give the server access only to the data and actions it needs.
- **Durability:** Store important records in a database or service rather than process memory.
- **Retry safety:** Use stable request IDs or idempotency mechanisms for operations that may be retried.
- **Compatibility:** Version the interface and test every client that depends on changed tools.
- **Observability:** Log relevant operations securely without unnecessarily recording sensitive data.

MCP standardizes how capabilities are exposed and accessed. It does not automatically provide durable storage, authorization policy, safe business logic, or correct agent behavior; these must be designed into the system.

## 6. Key Takeaways

- An MCP server packages a system's capabilities for use by compatible AI applications.
- **Tools** expose actions, **resources** expose readable information, and **prompts** provide reusable templates.
- Clear names, descriptions, typed inputs, focused results, and useful errors improve tool selection and reliability.
- Local servers often use stdio; remote servers use a supported network transport and need appropriate authentication and authorization.
- An MCP inspector helps test server capabilities independently of an agent.
- Multiple servers can work with one agent, but tool names and descriptions must remain clear and unambiguous.
- Version interface changes and test connected agents before deploying breaking changes.

## 7. Common Misconceptions

- **“An MCP server must be remote.”** No. It can run locally or remotely.
- **“An MCP server automatically makes its data safe.”** No. Access control, validation, and permission limits are still necessary.
- **“A tool's type hints replace validation.”** No. The server must still validate inputs and handle errors.
- **“All clients automatically load every resource and prompt.”** No. Client behavior differs; discoverability does not mean automatic use.
- **“Renaming a tool is always harmless.”** No. Connected agents may depend on its name, description, and input schema.
- **“An in-memory example is production-ready.”** No. It loses its data on restart and is not designed for concurrent or durable operation.

## 8. Quick Revision

**Q1. What is the difference between an MCP tool and a resource?**  
A tool performs an operation; a resource exposes information that a client can read.

**Q2. Why should tool names and descriptions be clear?**  
They help clients and models understand each tool's purpose and choose it appropriately.

**Q3. How can you test an MCP server independently?**  
Use an MCP inspector to discover capabilities and call tools directly with valid and invalid inputs.

**Q4. What should you consider when connecting several MCP servers?**  
Avoid confusing or conflicting tool names, restrict capabilities, and test the tools the agent actually sees.

**Q5. Why should server changes be versioned and tested?**  
Renaming tools or changing schemas can break connected agents and applications.
