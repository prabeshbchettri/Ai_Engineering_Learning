# What Is an Agent?

## 1. What Is It?

An **AI agent** is a system that uses a model to decide what action to take next, can use tools to perform actions, observes the results, and repeats this process until it reaches a goal or a stopping condition.

Unlike a fixed workflow, an agent can choose its next step based on what it learns while working.

A simplified agent loop is:

`Goal → Decide → Act → Observe result → Decide again → Stop when done`

An agent is commonly built from these parts:

- **Model:** Interprets the task and helps decide what to do next.
- **Instructions:** Explain the goal, constraints, and expected behavior.
- **Tools:** Let the agent take actions, such as searching documents, calling an API, or running a calculation.
- **Memory or state:** Holds relevant information from earlier steps.
- **Loop:** Repeats decision-making and actions while the task continues.
- **Stopping rules:** Define when to finish, when to ask for help, or when to stop because a limit has been reached.

## 2. Why Does It Matter?

AI applications often need to do more than produce one answer. They may need to gather information, inspect results, choose another action, and then produce an outcome.

Agents are useful when:

- A task has several steps, but the exact steps cannot be known in advance.
- The next action depends on the result of the previous action.
- The system needs to choose among available tools.
- The task may require adjusting its approach when new information appears.

For example, a research assistant might search for a topic, notice that a source does not answer the question, try another search, compare the findings, and then summarize the evidence.

Agents also introduce more complexity. They can make unexpected choices, use tools unnecessarily, take longer, and incur higher model or tool costs. Use an agent only when its flexibility provides real value.

## 3. How Does It Work?

### The agent loop

1. **Receive a goal.** The user describes the result they want.
2. **Decide what to do.** The model chooses a suitable next step based on the goal, instructions, available tools, and current context.
3. **Act.** The system performs the chosen action. This might mean calling a search tool, reading a file, or requesting information from an API.
4. **Observe the result.** The system receives the tool's output and adds it to the context or state used for the next decision.
5. **Repeat or finish.** The model decides whether another action is needed or whether the goal has been achieved.
6. **Apply stopping rules.** The system stops when the task is complete, a step or time limit is reached, an error requires stopping, or human input is needed.

The loop matters because the result of one action can change what the agent should do next.

### Who decides the next step?

| Approach | Who controls the workflow? | Example |
|---|---|---|
| Single model call | Your code chooses to make one call; the model returns a response | Answer a straightforward question |
| Chain or fixed workflow | Your code defines the sequence of steps | Retrieve documents, build a prompt, generate an answer |
| Agent | The model chooses the next action from the available options, within the system's rules | Search, inspect results, and decide whether to search again |

An agent still runs inside software written by developers. Developers define its tools, permissions, instructions, limits, and stopping conditions. The model chooses among permitted next actions; it does not have unlimited control over the computer or application.

### When should you use an agent or a chain?

Use a **chain** when you can define the steps in advance. Fixed workflows are often easier to test, more predictable, faster, and less expensive.

Use an **agent** when the next step depends on information that has not yet been discovered and the system needs to choose dynamically.

A useful rule of thumb:

`Known sequence of steps → Chain`

`Next step depends on what happens → Consider an agent`

Do not choose an agent just because the application uses an LLM. Many useful AI applications are simple model calls or fixed workflows.

## 4. Simple Example

Imagine a user asks:

**"Find three reliable sources about solar energy, compare their main points, and summarize the findings."**

### A fixed chain

The application always performs these steps:

1. Search for sources.
2. Read the first three results.
3. Summarize them.

This is straightforward, but it may fail if the results are irrelevant or one source cannot be accessed. The sequence is fixed unless the developer explicitly programs alternative paths.

### An agent

The agent might:

1. Search for solar energy sources.
2. Inspect the results.
3. Notice that one result is not reliable or relevant.
4. Search again with a more specific query.
5. Compare the useful sources.
6. Produce a summary when enough evidence has been gathered.

The agent can adapt its next action based on the results. This flexibility is useful when the quality and availability of information are uncertain.

The example is conceptual: an actual research agent would need appropriate search tools, source-quality rules, permissions, and limits.

## 5. Practical AI Engineering Application

Consider a document-based university assistant.

A **simple RAG chain** might follow a fixed workflow:

`User question → Retrieve relevant document chunks → Build prompt → Generate answer`

This is suitable when every question can use the same retrieval-and-answer process.

An **agent-based assistant** might have access to several tools:

- Search university documents.
- Check a course timetable through an API.
- Calculate a deadline or date difference.
- Ask the user for missing information.

It could choose which tool to use based on the request, inspect the result, and decide whether another action is needed.

### Practical design checklist

Before building an agent, ask:

1. Can I describe the required steps in advance?
2. Does the next step genuinely depend on intermediate results?
3. Does the model need to choose between different tools or actions?
4. Would a fixed chain be sufficiently reliable?
5. What actions are allowed, and which require human approval?
6. What limits prevent endless loops, excessive costs, or unsafe actions?
7. How will I detect errors and decide when the task is complete?

Start with the simplest design that solves the problem. Add agent behavior only when dynamic decision-making is necessary.

## 6. Key Takeaways

- An agent pursues a goal by choosing actions, observing results, and repeating as needed.
- In a fixed chain, the application code defines the workflow; in an agent, the model chooses the next permitted action.
- Core components include a model, instructions, tools, memory or state, a loop, and stopping rules.
- Agents are useful for open-ended tasks where the next step depends on intermediate results.
- Chains are usually preferable when the steps are known because they are simpler and easier to control.
- Every agent needs clear limits and a reliable way to stop.

## 7. Common Misconceptions

- **"Every LLM application is an agent."** No. A single model call or a fixed RAG workflow is not necessarily an agent.
- **"An agent can do anything on its own."** No. It can only use the tools and permissions provided by its application.
- **"Agents are always better than chains."** No. Agents add flexibility but also add complexity, latency, cost, and potential failure points.
- **"Memory is always permanent."** No. Memory may be temporary state within one task, stored information across tasks, or another explicitly designed mechanism. Its behavior depends on the implementation.
- **"The agent should loop forever until it succeeds."** No. It needs stopping conditions and limits for steps, time, and resource use.

## 8. Quick Revision

**Q1. What is the agent loop?**  
A: Decide what to do, act, observe the result, and repeat or stop.

**Q2. Who chooses the next step in a fixed chain?**  
A: The application code defines the sequence.

**Q3. When is an agent useful?**  
A: When the next action depends on intermediate results and cannot be fully planned in advance.

**Q4. When is a chain usually preferable?**  
A: When the workflow is known and can be written down as fixed steps.

**Q5. Name the main parts of an agent.**  
A: Model, instructions, tools, memory or state, loop, and stopping rules.

## Try It

List five tasks a user might want your application to perform. For each task, decide whether a simple chain is enough or an agent is justified.

| User task | Chain or agent? | Why? |
|---|---|---|
| Answer a question using a supplied paragraph | Chain | The steps are predictable |
| Retrieve document chunks and answer a question | Chain | The workflow can be fixed |
| Research a topic and change searches based on the results | Agent may help | The next search depends on what was found |
| Calculate a total from a provided list of numbers | Chain or ordinary code | The steps are known |
| Troubleshoot an unfamiliar issue by testing possible causes | Agent may help | Each result can determine the next test |

These are starting points, not universal rules. Choose based on the actual task, available tools, reliability requirements, and cost.

**Learning outcome:** Be able to decide whether a problem genuinely needs an agent and identify the components required to build one.
