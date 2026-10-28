# Planning and Reflection

## 1. What Is It?

**Planning and reflection** are techniques that help an AI agent handle tasks that involve multiple steps.

- **Planning:** The agent breaks a goal into smaller steps before acting.
- **Reflection:** The agent reviews its progress or result, identifies problems, and decides whether to improve it.
- **Plan revision:** The agent changes its approach when a step fails or new information changes what should happen next.

Instead of immediately trying to complete a complex request in one attempt, an agent can use a workflow like this:

```text
User's goal
    |
    v
Create a short plan
    |
    v
Complete a step
    |
    v
Check progress
    |
    +---- Plan still works? ---- Yes ----> Next step
    |                                  |
    No                                 v
    |                              Review result
    v                                  |
Revise the plan                        v
    |                                 End
    +----------> Continue         If needed, improve
```

Planning and reflection are strategies for controlling an agent's workflow. They do not guarantee that its decisions or final answers will be correct.

## 2. Why Does It Matter?

A simple question may need only one model response. A larger task—such as researching a policy, comparing options, and preparing a report—may require several tools and decisions.

Planning and reflection can help an agent:

- **Organize complex work:** Break a large goal into manageable steps.
- **Handle dependencies:** Complete prerequisites before steps that rely on them.
- **Recover from problems:** Change course when a tool fails or new evidence appears.
- **Catch mistakes:** Compare the result with the user's requirements before returning it.
- **Avoid premature completion:** Notice missing steps or unsupported claims.

However, planning and checking also have costs. They can require extra model calls, increase latency, consume more tokens, and sometimes introduce unnecessary complexity. Use them when the task's difficulty and consequences justify the extra work.

## 3. How Does It Work?

### 3.1 Plan before acting

The agent turns the user's goal into a short sequence of concrete steps.

For example, a request to compare two university policies might lead to this plan:

1. Search the documents for the first policy.
2. Search for the second policy.
3. Compare the relevant requirements.
4. Summarize the differences and cite the sources.

A useful plan is specific enough to guide action but flexible enough to change when needed. It should not include unnecessary steps just to look thorough.

### 3.2 Execute the plan one step at a time

The agent performs a step, often by calling a tool, then uses the result to decide what to do next.

```text
Plan -> Search first policy -> Save findings
     -> Search second policy -> Save findings
     -> Compare findings -> Draft response
```

The agent's state can store the current plan, completed steps, tool results, and outstanding work. In a graph-based workflow, nodes can perform actions and conditional edges can decide whether to continue, retry, or revise the plan.

### 3.3 Revise the plan when circumstances change

A plan should guide the agent, not trap it in a fixed sequence.

Suppose a document search returns no relevant results. The agent might:

- Rewrite the search query.
- Search another approved source.
- Ask the user for clarification.
- Mark the step as blocked and continue with the remaining feasible work.
- Explain that it cannot complete the task with the available evidence.

The best response depends on the cause of the problem. A temporary network failure might justify a limited retry; missing information may require clarification instead.

### 3.4 Reflect on the result

After completing a task, the agent can check its output against explicit requirements.

For example, a report reviewer might check:

- Does the response answer every part of the request?
- Are factual claims supported by retrieved evidence?
- Are the requested sections included?
- Are there contradictions or missing information?
- Does the result follow the required format?

A useful review has a clear standard. Asking a model to “check your work” without telling it what to check can produce vague feedback or false confidence.

### 3.5 Retry only when it is useful

If the review finds a fixable problem, the agent can revise the answer or repeat a relevant step.

```text
Draft result
    |
    v
Check against requirements
    |
    +---- Pass ----> Return result
    |
    +---- Fail ----> Identify specific issue
                         |
                         v
                    Revise or retry
                         |
                         v
                    Check again
```

Set a retry or revision limit. Otherwise, the agent may repeatedly rewrite an answer without meaningful improvement, wasting time and tokens. If the issue cannot be resolved, it should explain the limitation rather than pretend the task succeeded.

### 3.6 Balance quality against cost

Planning and reflection are not necessary for every request.

| Task | Planning and reflection |
|---|---|
| Define a common term | Usually unnecessary |
| Extract one date from a document | Usually unnecessary; a simple validation may be enough |
| Compare several policies using documents | A short plan can help |
| Research multiple sources and prepare a report | Planning and a final review may be useful |
| Perform a consequential external action | Validate the action and apply appropriate approval controls |

Use the simplest workflow that reliably meets the task's requirements. Extra reasoning steps do not automatically mean better results.

## 4. Simple Example

The following Python example demonstrates a basic review-and-revise loop. It uses ordinary Python functions rather than an LLM, so the behavior is deterministic and easy to understand.

The example checks whether a draft contains three required sections. If a section is missing, the program adds a placeholder. It illustrates the workflow pattern, not intelligent writing or semantic fact-checking.

```python
def draft_report():
    return """\
Summary: The two policies have different requirements.
Comparison: The first policy requires registration.
Sources: University policy documents.
"""


def review_report(report, required_sections):
    missing = [
        section
        for section in required_sections
        if f"{section}:" not in report
    ]
    return missing


def revise_report(report, missing_sections):
    for section in missing_sections:
        report += f"\n{section}: Further information needed."
    return report


required_sections = ["Summary", "Comparison", "Sources"]

report = draft_report()
print("Initial review:", review_report(report, required_sections))

missing = review_report(report, required_sections)

if missing:
    report = revise_report(report, missing)

print("\nRevised report:\n")
print(report)
print("Final review:", review_report(report, required_sections))
```

### How it works

1. `draft_report()` produces an initial draft.
2. `review_report()` checks whether all required section labels appear.
3. If anything is missing, `revise_report()` adds a placeholder for each missing section.
4. The final review checks whether the required labels are now present.

This example only checks formatting. It does **not** verify whether the claims are true, whether the sources support them, or whether the comparison is correct. A real AI application needs more meaningful checks for the task—for example, checking citations against retrieved passages or validating structured output against a schema.

## 5. Practical AI Engineering Application

### Add planning to a LangGraph agent

In a graph-based agent, planning and reflection can be represented as separate nodes:

```text
START
  |
  v
Create plan
  |
  v
Select next step
  |
  v
Execute step / call tool
  |
  v
Evaluate progress
  |
  +---- More work needed ----> Select next step
  |
  +---- Plan needs revision -> Revise plan
  |                                |
  |                                v
  |                         Select next step
  |
  +---- Work complete -------> Review final result
                                  |
                             +----+----+
                             |         |
                           Pass      Needs fix
                             |         |
                             v         v
                            END     Revise result
                                       |
                                       v
                                   Review again
```

Possible state fields include:

- `goal` — the user's requested outcome.
- `plan` — the current list of steps.
- `completed_steps` — work that has been completed.
- `tool_results` — relevant evidence returned by tools.
- `review_feedback` — specific issues found during review.
- `final_answer` — the response prepared for the user.

These are example field names, not a required LangGraph schema. Your implementation should store only the information needed by the workflow.

### Example: a RAG research assistant

Suppose a user asks:

> Compare the exam rules in two university documents and summarize the differences with sources.

A suitable workflow could be:

1. Plan the two searches and the comparison.
2. Use the RAG search tool to retrieve relevant passages from each document.
3. Check whether both documents supplied enough evidence.
4. If evidence is missing, revise the query or report the limitation.
5. Draft a comparison that distinguishes supported facts from uncertainty.
6. Review the answer to make sure the important claims have sources and both documents were considered.
7. Return the result.

The plan helps organize the searches; the RAG tool retrieves evidence; reflection checks the result against the task's requirements. Each component has a different role.

### Design a useful reviewer

A reviewer should use criteria tied to the user's request. For a source-grounded answer, it might check:

- Coverage: Did the answer address every requested part?
- Evidence: Can important factual claims be traced to the retrieved passages?
- Consistency: Does the answer contradict the available evidence?
- Format: Does it follow the requested output structure?

For high-stakes or factual applications, do not rely only on the same model's self-assessment. Add deterministic checks where possible, such as schema validation, required-field checks, citation verification, tests, or confirmation from an authoritative service.

### Compare planned and unplanned runs

To evaluate whether planning helps, run the same representative tasks with two workflows:

- **Baseline:** The agent starts acting immediately, without a separate planning step.
- **Planned:** The agent creates a plan before using tools.

Keep the model, tools, task inputs, and evaluation criteria as similar as possible. Compare:

| Measure | What it tells you |
|---|---|
| Task success | Did the workflow meet the user's requirements? |
| Steps or tool calls | How much work did the agent perform? |
| Latency | How long did the task take? |
| Token use or cost | What resources did it consume? |
| Error or retry count | How often did it need recovery? |

Use several representative tasks rather than drawing conclusions from one example. If model behavior is variable, repeat runs where practical. Planning is worthwhile when the improvement in success or reliability justifies its extra cost and time.

## 6. Key Takeaways

- Planning breaks a complex goal into smaller, ordered steps.
- A good agent can revise its plan when tools fail or new information appears.
- Reflection checks a result against explicit requirements and identifies fixable problems.
- Retries need limits; repeated self-review does not guarantee correctness.
- Use evidence checks and deterministic validation where possible instead of relying only on the model's opinion.
- Planning and reflection can improve complex workflows but add latency and cost.
- Compare planned and unplanned runs to determine whether planning is actually helping.

## 7. Common Misconceptions

- **“Every agent needs a planning step.”** Simple requests may be handled more efficiently without one.
- **“A plan must never change.”** Plans should adapt when new evidence or failures change what is feasible.
- **“An agent can prove its answer is correct by reviewing it.”** Self-review can catch issues, but the reviewer can also miss errors. External evidence and tests are important.
- **“More retries always improve the result.”** Retries can waste resources or repeat the same mistake unless the agent has specific feedback and a stopping limit.
- **“Planning is free.”** Extra model calls and checks add time, token use, and potentially monetary cost.

## 8. Quick Revision

**Q1. What is planning in an AI agent?**  
**A:** Breaking a user's goal into smaller steps before or during execution.

**Q2. When should an agent revise its plan?**  
**A:** When a step fails, new information changes the situation, or the current approach is no longer suitable.

**Q3. What is reflection?**  
**A:** Reviewing progress or the final result against explicit criteria and deciding whether a correction is needed.

**Q4. Why should retries be limited?**  
**A:** To prevent endless loops, unnecessary costs, and repeated attempts that do not improve the result.

**Q5. How can you test whether planning helps?**  
**A:** Compare planned and unplanned runs using the same tasks and measure success, steps, latency, token use, and failures.

## Try It

1. Choose a multi-part task, such as answering a question from two documents and comparing the results.
2. Run your agent without a separate planning step.
3. Run the same task with a short plan before tool use.
4. Add a review step that checks the result against explicit requirements.
5. Record task success, number of steps or tool calls, latency, and token use or cost.
6. Repeat with several tasks and decide where planning and reflection provide enough benefit to justify the overhead.

**Outcome:** Add planning and self-checking where they help, and leave them out where they do not.
