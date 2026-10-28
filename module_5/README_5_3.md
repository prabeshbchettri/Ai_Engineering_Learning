# Building Agents with LangGraph

## 1. What Is It?

**LangGraph** is a framework for building AI workflows and agents as a graph of connected steps. It is designed for applications where you need control over what happens next, including branching, repeated tool use, saved progress, and pauses for human approval.

An **AI agent** is an application in which a language model can decide what action to take, such as answering directly or calling a tool. Instead of placing the entire workflow inside one large loop, LangGraph lets you represent the workflow as:

- **State:** The information currently carried through the workflow.
- **Nodes:** Functions that perform work, such as calling a model, running a tool, or checking a condition.
- **Edges:** Connections that determine which node runs next.

A graph might look like this:

```text
User question
     |
     v
Classify question
     |
     +---- Simple question ----> Answer directly ----> End
     |
     +---- Needs information --> Call model / tool
                                      |
                                      v
                               Check the result
                                  |       |
                              Need more   Finished
                                  |       |
                                  +--loop  v
                                         End
```

## 2. Why Does It Matter?

A basic agent loop can work well for small experiments, but complex agents need more explicit control.

LangGraph helps you:

- **Control the workflow:** Make the possible steps and transitions explicit.
- **Use branches:** Send different kinds of requests down different paths.
- **Repeat actions:** Let an agent call tools more than once when needed.
- **Save progress:** Persist workflow state through a configured checkpointer.
- **Add human approval:** Pause before sensitive actions and resume after a person responds.
- **Debug behavior:** Inspect state and execution traces to understand what happened.

These capabilities are useful for research assistants, document-processing agents, booking workflows, customer-support systems, and other applications where reliability and visibility matter.

## 3. How Does It Work?

### 3.1 State

**State** is the data shared between graph steps. It can contain the user's question, conversation messages, retrieved documents, tool results, or a final answer.

For example:

```python
from typing_extensions import TypedDict

class AgentState(TypedDict):
    question: str
    answer: str
    needs_tool: bool
```

The exact fields depend on the application. A node reads the state and returns updates to it.

### 3.2 Nodes

A **node** is a function that performs one step. It receives the current state and returns the fields it wants to update.

```python
def answer_directly(state: AgentState):
    return {"answer": f"You asked: {state['question']}"}
```

This small example uses a simple Python function rather than an LLM. In a real agent, a node might call a language model or execute a tool.

### 3.3 Edges

An **edge** connects one node to another. A normal edge always routes to its configured destination.

For example:

```text
START -> classify_question -> answer_directly -> END
```

`START` and `END` are special graph markers that represent the beginning and end of a run.

### 3.4 Conditional edges

A **conditional edge** chooses the next node based on the current state or a decision made by a routing function.

```python
def route_question(state: AgentState):
    if state["needs_tool"]:
        return "use_tool"
    return "answer_directly"
```

The graph can route questions that need external information to a tool node while sending straightforward questions directly to an answer node.

### 3.5 Loops

Agents often need to repeat steps. For example, a model may request a tool, inspect the tool result, and then request another tool.

```text
Model decides
    |
    v
Run tool
    |
    v
Return tool result to model
    |
    +---- Another tool needed? ---- Yes ----> Model decides
    |
    No
    |
    v
Final answer
```

A loop needs a stopping condition. Without one, the workflow may run indefinitely or consume excessive time and resources. Set appropriate iteration limits and handle tool errors.

### 3.6 Checkpointing and human approval

LangGraph can save graph state using a **checkpointer**. When configured correctly, this supports persistence and resuming a workflow, often using a thread identifier to associate saved progress with a conversation or task.

Human-in-the-loop workflows can pause before a consequential action, such as sending an email or confirming a booking. A person reviews the proposed action, then the graph can resume. A pause alone does not guarantee safety: the application must define what requires approval and enforce the approval result.

## 4. Simple Example

This example builds a small graph with two paths:

- Simple questions go directly to an answer node.
- Questions marked as requiring a tool go to a placeholder tool node first.

The example demonstrates graph structure and routing. The “tool” is simulated; it does not call a real API or language model.

### Install the dependencies

```bash
pip install -U langgraph typing_extensions
```

### Code

```python
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END


class AgentState(TypedDict):
    question: str
    needs_tool: bool
    answer: str


def classify_question(state: AgentState):
    # For this demo, the caller supplies needs_tool.
    return {}


def answer_directly(state: AgentState):
    return {
        "answer": f"Direct answer to: {state['question']}"
    }


def use_tool(state: AgentState):
    # Placeholder for a real tool call.
    tool_result = "Example information returned by a tool."
    return {
        "answer": (
            f"Question: {state['question']} "
            f"Tool result: {tool_result}"
        )
    }


def route_question(state: AgentState):
    if state["needs_tool"]:
        return "use_tool"
    return "answer_directly"


builder = StateGraph(AgentState)

builder.add_node("classify_question", classify_question)
builder.add_node("answer_directly", answer_directly)
builder.add_node("use_tool", use_tool)

builder.add_edge(START, "classify_question")
builder.add_conditional_edges(
    "classify_question",
    route_question,
    {
        "answer_directly": "answer_directly",
        "use_tool": "use_tool",
    },
)
builder.add_edge("answer_directly", END)
builder.add_edge("use_tool", END)

graph = builder.compile()

simple_result = graph.invoke({
    "question": "What is an AI agent?",
    "needs_tool": False,
    "answer": "",
})
print(simple_result["answer"])

tool_result = graph.invoke({
    "question": "What is the latest exchange rate?",
    "needs_tool": True,
    "answer": "",
})
print(tool_result["answer"])
```

### How it works

1. `AgentState` defines the data passed between nodes.
2. `StateGraph(AgentState)` creates a graph builder that uses this state schema.
3. `add_node()` registers the functions that perform work.
4. `add_edge(START, "classify_question")` sets the first node.
5. `add_conditional_edges()` uses `route_question()` to choose a path.
6. Each path reaches `END`, completing the run.
7. `graph.invoke()` runs the graph with the supplied initial state and returns the final state.

In this demonstration, `needs_tool` is supplied by the caller to keep the example simple. In a real application, a classifier, rules, or an LLM-based decision would determine whether a tool is needed. The placeholder `use_tool` function should be replaced with a real tool integration.

## 5. Practical AI Engineering Application

### Rebuilding a tool-using agent

If you already have an agent loop, map its responsibilities to graph nodes:

| Existing loop responsibility | Possible graph component |
|---|---|
| Keep track of messages and results | State |
| Ask the model what to do | Model node |
| Execute a requested tool | Tool node |
| Decide whether to continue | Conditional edge |
| Return the final response | Final-answer node |
| Save progress between steps | Checkpointer |

A typical tool-using flow is:

```text
START -> Model -> Decide
                  |
          +-------+-------+
          |               |
       Tool needed      No tool needed
          |               |
       Run tool       Final answer
          |               |
          +-> Model        v
                          END
```

The model can return to the tool-selection step after receiving a tool result. The workflow ends when the model produces a final response instead of requesting another tool.

### Ready-made agent or custom graph?

- **Ready-made agent:** Start with LangGraph's prebuilt tool-using agent when you need a conventional model-and-tools loop quickly.
- **Custom graph:** Build your own graph when you need custom routing, extra validation, different workflows for different requests, explicit approval steps, or specialized state management.

A prebuilt agent is a useful starting point, not a substitute for understanding the workflow. Confirm the APIs against the LangGraph version installed in your project, because library interfaces can change.

### Inspecting state to debug

The state returned by `graph.invoke()` is a useful first debugging aid:

```python
result = graph.invoke({
    "question": "Explain retrieval-augmented generation.",
    "needs_tool": False,
    "answer": "",
})

print(result)
```

Inspect the fields to check what information reached the end of the graph and whether the expected answer was produced. For more detailed debugging, use LangGraph's supported streaming or tracing facilities to inspect intermediate node updates and execution paths.

**Important distinction:** State inspection shows the data captured by the graph. It does not automatically explain every internal model decision or prove that the answer is correct. Validate outputs and inspect execution traces when you need to understand the route taken.

## 6. Key Takeaways

- LangGraph represents an agent workflow as connected nodes and edges.
- State carries the information that nodes read and update.
- Conditional edges enable branching; graph edges can also create loops.
- Loops need clear stopping conditions and suitable error handling.
- Checkpointers can preserve progress, while human approval can pause consequential workflows.
- Start with a prebuilt tool-using agent for common patterns; use a custom graph when you need more control.
- Inspect final state and intermediate execution details to debug the workflow.

## 7. Common Misconceptions

- **“LangGraph is the language model.”** No. It coordinates workflow steps; the model is a separate component.
- **“Every node must call an LLM.”** No. Nodes can run Python logic, call tools, validate data, or make routing decisions.
- **“A conditional edge is the same as a loop.”** A conditional edge chooses a destination. A loop happens when the graph routes back to an earlier step.
- **“Saving state means the agent is automatically reliable.”** Persistence helps resume work, but it does not guarantee correct answers, safe actions, or successful recovery.
- **“A tool-using agent should always call a tool.”** No. Simple questions may be answered directly when the system can do so reliably.

## 8. Quick Revision

**Q1. What are the three main building blocks of a LangGraph workflow?**  
**A:** State stores information, nodes perform work, and edges determine the next step.

**Q2. What is a conditional edge used for?**  
**A:** It routes execution to different nodes based on a condition or routing decision.

**Q3. How can an agent repeat tool use?**  
**A:** Route from the tool-result step back to the model or decision step until the agent is ready to finish.

**Q4. Why use a checkpointer?**  
**A:** To persist workflow state so a run can support recovery or resumption when configured appropriately.

**Q5. When should you choose a custom graph instead of a prebuilt agent?**  
**A:** When the application needs specific branching, validation, approval, or state-management behavior that a ready-made pattern does not provide directly.

## Try It

1. Rebuild your previous tool-using agent loop as a LangGraph graph.
2. Define state for the conversation messages, tool results, and final answer.
3. Add a conditional branch that sends simple questions straight to an answer node without calling a tool.
4. Route tool results back to the model when another tool call is needed.
5. Inspect the final state and, if possible, intermediate node updates to understand which path ran.
6. Add a stopping condition or iteration limit so repeated tool use cannot continue forever.

**Outcome:** Build a controllable LangGraph agent and debug its behavior by inspecting its state.
