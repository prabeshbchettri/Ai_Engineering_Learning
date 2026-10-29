# Harness Engineering

## 1. What Is It?

**Harness engineering** is the work of designing and improving everything around an AI model that allows it to operate as a useful, reliable agent.

A harness can include:
- The agent loop that decides what happens next.
- System instructions and task-specific guidance.
- Tools the agent can call and the information those tools return.
- Context building, context trimming, and memory.
- Permissions and human approval steps.
- Error handling, validation, and checks on the agent's work.

The model generates responses or chooses actions, while the harness organizes how those capabilities are used in an application.

## 2. Why Does It Matter?

A capable model can still perform poorly if it receives unclear instructions, has unsuitable tools, loses important context, or cannot verify its results.

Harness engineering matters because it helps you:
- **Improve reliability:** Check outputs instead of trusting every response.
- **Control actions:** Limit tool access and require approval for sensitive operations.
- **Reduce confusion:** Give the agent clear tool descriptions and relevant context.
- **Handle failures:** Return useful error messages so the agent can recover.
- **Measure improvements:** Compare changes against the same set of tasks.

When an agent fails, the problem may be its harness rather than the model itself. A larger model is not automatically the right fix.

## 3. How Does It Work?

### 3.1 Understand the agent loop

A typical tool-using agent follows a cycle:

1. Receive the user's request.
2. Read the instructions and relevant context.
3. Decide whether to answer directly or use a tool.
4. Call the selected tool, if needed.
5. Inspect the tool result and decide what to do next.
6. Check the result, then answer or continue working.

A simplified flow is:

`User request → Instructions and context → Model decision → Tool or answer → Validation → Final response`

The harness controls much of this process, including which tools are available, what results are shown, and when the agent must stop or ask for approval.

### 3.2 Design the tool set

A tool is a function or service the agent can use to perform an action, such as searching documents, reading a file, or running tests.

When designing tools:
- **General tools** can handle several kinds of tasks but may be harder for the agent to use correctly.
- **Narrow tools** do one clearly defined job and can be easier to understand, but too many tools may overwhelm the agent.
- Give each tool a clear name, description, input format, and result format.
- Return the information the agent needs without unnecessary output.
- Review tool usage and remove or redesign tools that are rarely used or often misused.

The right balance depends on the task and the model. Do not assume that either the fewest or the greatest number of tools is always best.

### 3.3 Let the agent check its own work

Do not rely only on the model's confidence. Add checks that can detect mistakes.

Examples include:
- Run unit tests after generating code.
- Validate structured output against a schema.
- Check a factual answer against retrieved source passages.
- Re-open a source to confirm a quoted detail.
- Check whether a requested file or result was actually created.

When a check fails, return a concise, actionable error message. The agent can use that feedback to try again, within defined limits.

`Generate result → Run check → Pass: return result / Fail: provide error feedback and retry`

Checks reduce certain errors, but they do not guarantee that every result is correct. The checks themselves must also be appropriate and reliable.

### 3.4 Use instructions on demand

Keep the agent's core instructions focused on behavior that applies to most tasks. Load detailed guidance only when a particular task requires it.

For example:
- **Core instructions:** Be accurate, respect permissions, use tools appropriately, and verify important results.
- **Request-handling guidance:** When the user asks to process a support request, load the relevant steps, required fields, and response format.

This approach can keep the active context more relevant and avoid sending every instruction for every task. The harness must still identify the task correctly and load the guidance before it is needed.

### 3.5 Fit the harness to the model

Different models may interpret instructions, select tools, and handle long contexts differently. A harness that works well with one model may perform worse with another.

Whenever you change the model:
1. Run the same evaluation tasks.
2. Check tool selection, output quality, and failure cases.
3. Adjust tool descriptions or instructions only when evidence supports a change.
4. Re-run the evaluation to confirm the effect.

### 3.6 Change one thing at a time

Treat a harness modification like a code change.

1. Establish a baseline using a fixed set of test tasks.
2. Change one part of the harness.
3. Run the same tasks under comparable conditions.
4. Measure the result and inspect failures.
5. Keep the change only if it improves the relevant outcomes without unacceptable trade-offs.

Changing several things at once makes it difficult to identify which change caused an improvement or regression.

### 3.7 Learn from existing harnesses

Study established coding agents and other agent systems to see how they organize:
- The agent loop and stopping conditions.
- Tool definitions and tool-result handling.
- Core instructions and task-specific guidance.
- Context and memory management.
- Tests, validation, permissions, and recovery.

Use these systems as design references, not as proof that their approach will work for your application. Test ideas against your own tasks and constraints.

## 4. Simple Example

Imagine an AI coding agent that edits a Python project. It can inspect files, modify code, and run tests.

A weak harness might tell the agent to “fix the bug” and let it return its changes without checking them.

A stronger harness could work like this:

1. **Inspect:** The agent reads the relevant code and tests.
2. **Plan:** It identifies the likely cause of the bug.
3. **Edit:** It uses a file-editing tool with a clear description and limited scope.
4. **Verify:** It runs the relevant tests.
5. **Recover:** If a test fails, the harness returns the test error to the agent so it can attempt a fix.
6. **Report:** It summarizes the changes and accurately reports which checks passed.

The important difference is not necessarily the model. The stronger harness gives the model a clearer process, appropriate tools, and a way to check its work.

## 5. Practical AI Engineering Application

Suppose you are building a document-question-answering agent that retrieves passages and answers questions.

Useful harness features include:
- A retrieval tool with a clear description of what it searches.
- Instructions to answer from the retrieved sources when the task requires evidence.
- A source-checking step that verifies whether the answer's claims are supported by the retrieved passages.
- A structured output validator if the application expects fields such as `answer` and `sources`.
- Error handling for empty retrieval results or failed tools.
- Permissions that prevent the agent from performing actions it is not authorized to take.

Keep these distinctions in mind:

- **The model** generates text and makes decisions based on its learned capabilities and current context.
- **The harness** manages the instructions, tools, workflow, context, permissions, and verification process around the model.
- **Evaluation** measures how well the complete system performs on defined tasks.

A harness can improve reliability, but it cannot guarantee correctness. For example, a source-checking step can fail if the retrieved passages are incomplete or the checker is unreliable.

### Practical experiment: improve one harness

Use the same 10 representative tasks to compare a baseline with three separate changes.

| Experiment | Single change | What to measure |
|---|---|---|
| A | Rewrite tool descriptions to be clearer | Correct tool selection and task success |
| B | Add a step that checks answers against retrieved sources | Source support, factual errors, and task success |
| C | Load detailed instructions only for request-handling tasks | Task success, instruction relevance, and token usage if available |

For each experiment:

1. Run all 10 tasks with the original harness and record the results.
2. Apply only one change.
3. Run the same 10 tasks again using comparable settings.
4. Record successful tasks, errors, tool mistakes, and any relevant cost or latency.
5. Compare against the baseline and keep the change only if the evidence supports it.

Calculate task success rate as:

`Task success rate = Number of successful tasks / Total tasks × 100`

For example, if 8 of 10 tasks succeed:

`Task success rate = 8 / 10 × 100 = 80%`

Ten tasks are useful for a small learning experiment, but the sample is too small to establish that a change will generalize to all real-world requests. Inspect individual failures and expand the test set as the project grows.

## 6. Key Takeaways

- A harness is the system around a model that makes it function as an agent.
- Tool design, instructions, context, permissions, error handling, and verification all affect performance.
- The same model can behave differently under different harnesses.
- Give agents reliable ways to check results and actionable feedback when checks fail.
- Load detailed instructions only when relevant, while keeping essential rules available.
- Re-test the harness when changing the model or its components.
- Change one thing at a time and keep changes only when measurements support them.

## 7. Common Misconceptions

### A better model will fix every agent failure

Not necessarily. The agent may need clearer tool descriptions, better context, stronger validation, or improved error handling.

### If the model says the answer is correct, it must be correct

A model's confidence is not proof. Use appropriate tests, source checks, or schema validation.

### More tools always make an agent more capable

Extra tools can create confusion and make selection harder. Choose tools based on the tasks the agent must perform.

### A harness that works with one model will work equally well with every model

Models differ in how they follow instructions and use tools. Evaluate the full system after switching models.

## 8. Quick Revision

**Q1. What is a harness?**  
The instructions, tools, workflow, context management, permissions, error handling, and checks surrounding a model.

**Q2. Why should an agent verify its work?**  
Verification can catch errors that fluent model output alone may not reveal.

**Q3. Why change one harness component at a time?**  
It makes it easier to identify which change caused an improvement or regression.

**Q4. What should you do after switching models?**  
Run the same evaluation tasks and check whether the harness still performs well.

**Q5. How can you tell whether a harness change helped?**  
Compare measurable results against a baseline using the same tasks and comparable conditions.
