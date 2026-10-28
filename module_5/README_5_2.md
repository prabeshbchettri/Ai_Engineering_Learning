# The Agent Loop

## 1. What Is It?

The **agent loop** is the repeated process an AI agent uses to work toward a goal. The model decides what to do, the application performs an action or tool call, and the agent uses the result to decide what happens next.

A simplified loop is:

`Goal → Decide → Tool call → Observe result → Decide again → Finish or repeat`

The loop lets an agent adapt when a tool returns unexpected, incomplete, or useful new information.

## 2. Why Does It Matter?

Many real tasks cannot be completed reliably with a single model response. An agent may need to search, inspect the result, and then make another search or call a different tool.

The loop is the mechanism that connects these steps. Without a controlled loop, an application may stop too early, keep repeating actions, or consume too much time and money.

A well-designed loop should be:

- **Goal-directed:** Every action should help complete the user's task.
- **Result-aware:** The next decision should consider the latest tool result.
- **Bounded:** The loop must have limits so it cannot continue forever.
- **Observable:** Developers should be able to inspect tool calls, results, errors, and stopping reasons.

## 3. How Does It Work?

### The ReAct pattern: reason and act

**ReAct** means combining reasoning and acting. In this pattern, the model decides on an action, the application executes it, and the model uses the observation to choose the next step.

The basic sequence is:

1. **Goal:** Receive the user's request.
2. **Decide:** Choose the next useful action.
3. **Act:** Call a tool, such as a search function or calculator.
4. **Observe:** Read the tool's output.
5. **Continue or finish:** Choose another action or return the final answer.

The key idea is that an observation can change the next action. The loop is not simply repeating the same prompt; it is updating the decision using new information.

### Step by step or plan first?

There are two common approaches:

| Approach | How it works | Useful when |
|---|---|---|
| Step-by-step | The agent chooses one action, observes the result, and then chooses the next action | The right next step depends strongly on new results |
| Plan first | The agent creates a plan, then carries out the steps, checking results along the way | The task has several understandable stages that can be organized in advance |

A plan can improve organization, but it may need to change if a tool fails or new information appears. A plan-first agent should still check results and have stopping rules.

### Conditions for stopping

A loop should stop for a defined reason. Common stopping conditions include:

- **Success:** The model or application identifies that the task is complete.
- **Maximum steps:** The loop has reached its allowed number of iterations or tool calls.
- **Repeated action:** The agent keeps requesting the same action with the same inputs and is making no progress.
- **Tool or system error:** A failure makes it unsafe or impossible to continue.
- **Human input required:** The agent needs clarification or approval before taking another action.

A maximum step count is essential, but it is not sufficient on its own. A reliable implementation also needs a clear success condition, error handling, and ideally repeated-action detection.

## 4. Simple Example

Suppose an agent must find a university's application deadline and report it.

A possible sequence is:

1. Call a search tool for the university's admissions page.
2. Inspect the result and open the relevant page.
3. Extract the deadline from the page.
4. Return the deadline and its source.

If the first search returns an outdated page, the agent can use that observation to search for the current admissions page instead.

### A small Python example

The following example demonstrates the control flow using a mock tool. It does not call a real AI model or an external service. The `choose_action` function stands in for the decision an LLM would make.

```python
def mock_tool(action):
    results = {
        "search": "Found the university admissions page.",
        "open": "The page says the deadline is June 30.",
        "extract": "Deadline: June 30."
    }
    return results.get(action, "Unknown action")


def choose_action(observations):
    # Demonstration only: a real agent would use a model
    # to choose based on the goal and previous results.
    actions = ["search", "open", "extract"]

    if len(observations) < len(actions):
        return actions[len(observations)]

    return "finish"


def run_agent(max_steps=5):
    observations = []

    for step in range(max_steps):
        action = choose_action(observations)

        if action == "finish":
            print("Task complete.")
            return observations

        result = mock_tool(action)
        observations.append((action, result))
        print(f"Step {step + 1}: {action} -> {result}")

    print("Stopped: maximum step limit reached.")
    return observations


run_agent()
```

### What this example demonstrates

1. `choose_action` selects the next action using the information collected so far.
2. `mock_tool` represents a tool that performs an action and returns an observation.
3. The loop runs one action at a time and records each result.
4. The agent finishes when `choose_action` returns `"finish"`.
5. If it never finishes, `max_steps` still limits the number of actions.

The example uses a fixed decision function so the control flow is easy to understand. In a real agent, an LLM might choose among available tools, and the application would need to validate the requested tool and its arguments before executing it.

## 5. Practical AI Engineering Application

In an LLM application, the loop often coordinates the model and tool-calling code:

`User request → Model selects tool → Application validates call → Tool runs → Result returns to model → Repeat or final answer`

The model typically does not execute the tool directly. The application receives the tool request, checks it, runs the corresponding function, and sends the result back to the model.

### Build the loop safely

When implementing your own agent loop:

1. **Define the tools.** Give each tool a clear purpose and input format.
2. **Validate tool calls.** Reject unknown tools or invalid arguments.
3. **Execute only permitted actions.** Apply authorization checks, especially for actions that modify data or affect other people.
4. **Return tool results.** Provide the model with useful results and clear error messages.
5. **Track progress.** Keep the conversation or state needed to make the next decision.
6. **Enforce limits.** Bound the number of iterations, elapsed time, and tool usage or cost where possible.
7. **Detect repetition.** Compare recent tool names and arguments, or track whether the agent is making progress.
8. **Handle errors.** Decide which failures can be retried and which should stop the task.
9. **Return a clear ending.** Report success, failure, or that the limit was reached rather than silently stopping.

### Detecting repeated actions

A simple repetition check can compare a tool name and its arguments with recent calls. If the agent repeatedly requests the same search with the same query and receives the same result, the application can stop or ask the model for a different approach.

However, identical calls are not always wrong. Some tasks legitimately require repeating an action. Treat repetition detection as a safety signal, not a universal proof of failure.

### What the loop does and does not do

- **It does:** Coordinate decisions, tool execution, observations, and stopping.
- **It does not:** Guarantee that the model's decisions are correct or that the task will succeed.
- **It does not:** Replace tool validation, permissions, error handling, or monitoring.

## 6. Key Takeaways

- An agent loop repeats decision, action, and observation until a stopping condition is reached.
- ReAct describes the pattern of reasoning about an action, acting, and using the observation to decide what comes next.
- Step-by-step agents decide after each result; plan-first agents organize several steps in advance but should still adapt when needed.
- A maximum step limit prevents unbounded loops, while success conditions and repetition checks improve control.
- The application executes and validates tool calls; the model's requested action should not be trusted automatically.
- A loop that always stops may still fail to complete the task, so report why it stopped.

## 7. Common Misconceptions

- **"A maximum step count guarantees success."** It guarantees a bound on iterations, not a correct answer.
- **"The model directly runs tools."** Usually, the application executes the requested tool after validating the call.
- **"Plan-first agents never change their plans."** A robust agent can revise its plan when observations or errors require it.
- **"Repeated actions always mean a bug."** Repetition can be legitimate, but repeated identical actions without progress should be investigated.
- **"ReAct means exposing every internal thought."** For implementation, the important part is the action-and-observation cycle. Applications can use concise decisions and tool traces without exposing private internal reasoning.

## 8. Quick Revision

**Q1. What are the main stages of an agent loop?**  
A: Decide, act, observe the result, and then repeat or finish.

**Q2. What does ReAct stand for?**  
A: Reasoning and acting in an alternating process, with observations informing the next action.

**Q3. Why is a maximum step limit needed?**  
A: To prevent an agent from continuing indefinitely and consuming unbounded resources.

**Q4. What is the difference between step-by-step and plan-first execution?**  
A: Step-by-step chooses the next action after each result; plan-first creates an initial plan before execution.

**Q5. Does reaching the step limit mean the task succeeded?**  
A: No. It means the loop stopped because it reached its limit; the application should report that clearly.

## Try It

### Task 1: Three tool calls in a row

Design a task that requires three tools, such as:

1. Search for a university course page.
2. Open the page found by the search.
3. Extract the course registration deadline.

Record each tool's output and use it to decide what happens next.

### Task 2: An impossible task

Give the agent a task it cannot complete with its available tools, such as asking it to retrieve a private database record when no database tool exists.

Check that:

- The agent does not invent a tool or claim it succeeded.
- It stops when the maximum number of steps is reached, or earlier when it identifies that the task cannot be completed.
- It reports a clear stopping reason.

### Completion checklist

- [ ] I can explain the decide-act-observe loop.
- [ ] I understand the difference between step-by-step and plan-first execution.
- [ ] My loop has a clear success condition.
- [ ] My loop has a maximum step limit.
- [ ] My loop handles repeated actions and tool errors.
- [ ] The application reports whether the task succeeded or stopped without success.

**Learning outcome:** Explain how an agent loop works and build one that always stops.
