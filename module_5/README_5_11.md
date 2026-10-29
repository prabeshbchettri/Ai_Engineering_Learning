# Compaction, Offloading and Tool Context

## 1. What Is It?

Long-running AI agents collect conversation history, tool results, plans, and intermediate decisions. If all of this is repeatedly sent to the model, the context can become large, expensive, and difficult to manage.

**Compaction** means reducing older context into a shorter representation while preserving information needed to continue the task.

**Offloading** means keeping information outside the model's immediate context, such as in a file, scratchpad, database, or application state, and retrieving it when needed.

**Tool context management** means controlling which tool descriptions and tool results are included in a model request.

These techniques help an agent keep working without carrying every detail in every step.

## 2. Why Does It Matter?

In a long task, an agent might perform dozens of searches, inspect files, and make decisions. Sending all previous messages and full tool outputs at every step can:

- Consume the model's context window.
- Increase token usage, cost, and latency.
- Make important facts harder to find among irrelevant details.
- Cause useful information to be truncated or omitted.
- Waste space on tools that are not relevant to the current step.

The solution is not to discard history indiscriminately. The agent should preserve what matters, store exact facts safely, and retrieve details only when necessary.

## 3. How Does It Work?

### Step 1: Compact older history into a rolling summary

A **rolling summary** is a short summary that is updated as the task progresses. Instead of summarizing the entire history from scratch every time, update the existing summary with new decisions, findings, and progress.

A useful summary preserves:

- **Goal:** what the agent is trying to accomplish.
- **Constraints:** requirements, limits, and user preferences relevant to the task.
- **Decisions:** choices already made and why.
- **Progress:** work completed and important findings.
- **Unfinished work:** the next actions and unresolved questions.

Example:

```text
Goal: Find the return policy for a damaged item.
Constraint: Use the store's official policy.
Decision: Search the official help center first.
Progress: Found a policy allowing eligible damaged items to be returned within 30 days.
Unfinished work: Verify whether the policy applies to clearance items.
```

This is more useful than a vague summary such as "We searched for the return policy."

### Step 2: Keep precise data separate

Summaries are good for meaning and progress, but they can accidentally change or omit exact details.

Store precision-sensitive values separately, including:

- Order numbers and IDs.
- Dates and deadlines.
- Monetary amounts.
- File paths and URLs.
- Exact configuration values.
- Database keys or other identifiers.

For example, keep a readable summary alongside a structured record:

```python
task_summary = "Found the customer's order; verify its delivery status."

exact_details = {
    "order_id": "ORD-804271",
    "delivery_date": "2026-10-25",
    "refund_amount": 42.50,
}
```

The values are illustrative. In a real application, validate exact values and preserve their types and formats. Retrieve the original record when a detail must be verified rather than trusting a paraphrased summary.

### Step 3: Offload notes and progress outside the context

A **scratchpad** is a place to store working notes, a plan, intermediate results, or progress outside the model's current prompt. It could be a file, database record, or application-managed state.

The basic workflow is:

1. The agent reads the current task state.
2. It performs a step, such as searching or editing a file.
3. It writes important findings and progress to persistent storage.
4. Later, it retrieves the relevant notes before continuing.

This lets the agent resume work without including every earlier tool call in each request.

A simple local-file example:

```python
from pathlib import Path

notes_file = Path("agent_notes.txt")

# Save progress outside the model's immediate context.
notes_file.write_text(
    "Goal: Compare three candidate documents.\n"
    "Completed: Reviewed documents A and B.\n"
    "Next: Review document C and compare the findings.\n",
    encoding="utf-8",
)

# Read the saved progress when it is needed again.
saved_notes = notes_file.read_text(encoding="utf-8")
print(saved_notes)
```

This demonstrates basic storage only. It does not automatically connect to an LLM or manage an agent's context. A real application must decide when to write notes, what to store, and when to retrieve them.

### Step 4: Trim tool results before sending them back

Tools can return much more information than the model needs. A web search may return many pages; a database query may return thousands of rows; a code tool may return a long log.

Instead of sending the entire result into the next model request:

- Keep the fields or passages relevant to the current decision.
- Summarize long outputs.
- Remove duplicates and irrelevant records.
- Preserve source references or identifiers for follow-up.
- Store the full result externally when it may need later inspection.

For example:

```text
Full tool result:
- 40 search results
- Repeated descriptions
- Unrelated pages
- Relevant official policy passage
- Source URL

Compact result sent to the model:
- Key finding: eligible damaged items can be returned within 30 days
- Source: official policy page
- Uncertainty: clearance-item eligibility not yet checked
- Reference: saved search result set 12
```

Do not remove caveats, contradictory evidence, or source details needed to make a reliable decision. Keep the full output available when verification may be necessary.

### Step 5: Include only relevant tool descriptions

A tool description explains what a tool does, what inputs it accepts, and how to use it. Tool descriptions take up context too.

If an agent can access search, email, file editing, database queries, and code execution, it may not need every tool for every step.

A context-aware system can make the tools relevant to the current step available, such as:

- Search tools for finding information.
- File tools for reading or editing documents.
- Database tools for querying stored records.
- Code tools for executing or testing code.

Only expose or include tools that the current task needs and that the agent is authorized to use. Do not remove a tool that is essential for a required action.

### Step 6: Use prompt caching where supported

Some model APIs support **prompt caching**, which can reduce repeated processing costs or latency when an identical or matching prefix is reused. Availability, cache rules, minimum sizes, pricing, and expiration behavior depend on the provider and model.

A common strategy is to put stable content first:

1. Fixed system instructions.
2. Stable tool descriptions.
3. Less stable task details.
4. Recent history and tool results.

This ordering may improve cache reuse when the provider's caching rules support it. It does not guarantee a cache hit. Measure actual cache reads, cache writes, token usage, latency, and cost using the provider's usage information.

Caching does not mean the model has unlimited memory, and it does not replace context reduction.

### Step 7: Give independent subtasks their own context

A complex task can be divided into smaller, self-contained subtasks. A separate agent can receive only the instructions and information required for its assigned job, then return a concise result to the main agent.

For example:

- Main agent: compare three policy documents.
- Research agent: extract the return conditions from document A.
- Research agent: extract the return conditions from document B.
- Main agent: compare the findings and identify unresolved questions.

This can prevent unrelated working details from crowding the main agent's context. It also adds coordination overhead and does not guarantee better results. Each subtask needs clear instructions, sufficient evidence, and a defined output format.

## 4. Simple Example

Suppose an agent must compare 20 product documents and prepare a recommendation. It searches each document, collects results, and revisits earlier findings.

**Approach A: Keep everything**

Every model request includes the full conversation, all search outputs, and every previous decision. Context grows quickly, and repeated information consumes tokens.

**Approach B: Summarize history**

The agent keeps a rolling summary of the goal, constraints, findings, and remaining work. This reduces repeated conversation history, but large tool outputs may still consume space.

**Approach C: Summarize and offload**

The agent keeps a rolling summary, trims tool outputs to relevant findings, saves detailed results and exact IDs externally, and retrieves them only when needed. It includes only the tools required for the current step and uses prompt caching if supported.

Approach C may reduce context size and cost while retaining access to important details. However, it must be evaluated: an overly aggressive summary or filter can remove evidence the agent needs.

## 5. Practical AI Engineering Application

A practical long-running agent can manage its context with this cycle:

1. **Load state:** read the current goal, constraints, summary, exact records, and unfinished work.
2. **Select tools:** include only the tools required for the next action.
3. **Act:** call the selected tool.
4. **Filter results:** extract relevant information and preserve source references.
5. **Update state:** append important findings to external notes and update the rolling summary.
6. **Compact when needed:** summarize older messages while preserving essential decisions and unfinished work.
7. **Continue or stop:** decide whether another action is needed.
8. **Measure:** track token usage, latency, cost, and task success.

Keep these categories distinct:

| Technique | Main purpose |
|---|---|
| Compaction | Reduce older context while preserving what is needed to continue. |
| Rolling summary | Maintain an updated, concise record of task progress. |
| Offloading | Store detailed notes or results outside the immediate context. |
| Tool-result trimming | Send only useful parts of tool output to the model. |
| Tool selection | Avoid including irrelevant tool descriptions. |
| Prompt caching | Reuse eligible repeated prompt content to reduce processing overhead. |
| Separate subtask context | Isolate the working details of an independent subtask. |

### Try it: compare three strategies

Run the same task of 20 or more steps using three strategies:

1. Keep the full history and full tool results.
2. Keep a rolling summary instead of the full history.
3. Keep a rolling summary, trim tool results, and save detailed notes externally.

For each run, record:

- Whether the task was completed correctly.
- Total input and output tokens, if available.
- Estimated or actual cost.
- Completion time.
- Important details missed or incorrectly summarized.
- How often saved notes or full tool results had to be retrieved.

Use the same task, success criteria, and model settings where practical. Compare the results rather than assuming that the most compact approach is automatically the best.

### What these techniques do and do not do

**They do:**
- Reduce repeated context and help long tasks remain focused.
- Preserve progress between model calls.
- Keep exact records available for verification.
- Reduce unnecessary tool descriptions and oversized tool outputs.
- Potentially reduce cost or latency through more efficient context use and supported caching.

**They do not:**
- Guarantee that a summary preserves every important detail.
- Make external notes automatically available to the model; the application must retrieve them.
- Guarantee prompt-cache hits or cost savings.
- Make multi-agent systems automatically more accurate.
- Replace testing, access controls, or verification of important facts.

## 6. Key Takeaways

- Use rolling summaries to preserve the goal, constraints, decisions, progress, and unfinished work.
- Keep exact values such as IDs, dates, amounts, and paths in structured records.
- Offload detailed notes and full tool outputs, then retrieve them when necessary.
- Trim tool results before they re-enter the model's context, but preserve evidence and source references.
- Include only the tool descriptions relevant to the current step.
- Arrange stable prompt content for caching only when supported, and measure actual results.
- Compare task success, token usage, cost, and latency when evaluating context strategies.

## 7. Common Misconceptions

**Misconception: A summary can replace every original detail.**

A summary is a compact working representation, not a guaranteed exact copy. Keep original records for details that may need verification.

**Misconception: Offloaded information is automatically remembered by the model.**

No. The application must store the information and retrieve the relevant parts into a future model request.

**Misconception: Shorter context always produces better results.**

Over-trimming can remove important evidence or constraints. Optimize for relevant information and task success, not just minimum token count.

**Misconception: Prompt caching removes the need to manage context.**

Caching can reduce repeated processing for eligible content, but the prompt still has to fit the applicable context limits, and cache behavior depends on the provider.

**Misconception: Separate agents always improve performance.**

Subtasks can benefit from isolated contexts, but coordination overhead, inconsistent outputs, and missed dependencies can offset those benefits.

## 8. Quick Revision

**1. What is compaction?**

Reducing older context into a shorter form while preserving the information needed to continue the task.

**2. What should a rolling summary preserve?**

The goal, constraints, decisions, progress, important findings, and unfinished work.

**3. Why store exact details separately?**

Summaries may alter or omit precise values such as IDs, dates, monetary amounts, and file paths.

**4. How should large tool results be handled?**

Filter or summarize the relevant information, preserve references, and store the full result externally if it may be needed later.

**5. How do you know whether a context strategy works?**

Run comparable tasks and measure success, token usage, cost, latency, and information lost or misrepresented.
