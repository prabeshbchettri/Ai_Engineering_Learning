# Context Engineering Basics

## 1. What Is It?

**Context engineering** is the practice of deliberately choosing, organizing, and updating the information an AI model receives when it generates a response or decides what to do next.

An agent's context can include:

- **Instructions:** rules and goals the model should follow.
- **Conversation history:** earlier messages in the task.
- **Retrieved passages:** relevant text found in documents or a knowledge base.
- **Memories:** useful facts retained from earlier steps or interactions.
- **Tool descriptions:** explanations of available tools and how to call them.
- **Tool results:** outputs returned by tools, such as search results or code execution.
- **Current user input:** the latest request or information.

Context is limited by the model's **context window**, which is the amount of input and generated content the model can handle in a single request. The exact limit depends on the model.

Think of context as a limited workbench: the agent needs the right tools and notes on the bench, not every item it has ever encountered.

## 2. Why Does It Matter?

AI agents often perform tasks over many steps. At each step, they may send instructions, history, retrieved information, and tool results back to the model.

Poor context management can cause:

- **Goal drift:** the agent loses sight of the original objective.
- **Missed details:** relevant information is buried in a large amount of text.
- **Noise:** irrelevant content distracts from the current task.
- **Higher cost and latency:** larger requests can use more tokens and take longer to process.
- **Truncated information:** when a request exceeds a system's limits, some content may need to be removed or shortened.

More context is not automatically better. The aim is to provide enough relevant information for the current decision.

## 3. How Does It Work?

### Step 1: Identify the parts of the context

Break the model input into categories, such as instructions, history, retrieved passages, memories, tool descriptions, tool results, and the current user message. This makes it easier to see what is consuming space.

### Step 2: Treat context as a budget

A **token** is a small unit of text processed by a language model. Tokens are not exactly the same as words; punctuation, word parts, and other text can also use tokens.

The total input must fit within the model's available context window, while leaving room for the model's response when required.

A practical planning equation is:

`Total context = Instructions + History + Retrieved passages + Memories + Tool descriptions + Tool results + Current input`

This is a planning model, not a universal token-counting formula. Actual token counts depend on the content and model.

Give each category a rough limit. For example, keep instructions short, retrieve only relevant passages, summarize old history, and limit repetitive tool output. The limits should be adjusted to the task rather than treated as fixed rules.

### Step 3: Decide what belongs in context

For each category, decide whether information should be:

- **Always included:** essential rules and the current goal.
- **Retrieved when needed:** documents or facts relevant to a specific question.
- **Summarized:** older conversation history or lengthy tool results.
- **Excluded:** duplicated, irrelevant, stale, or unnecessary information.

Do not remove information simply because it is old. Keep it if it remains important to the current goal.

### Step 4: Separate and label information

Use clear labels so different types of content are easier for the model to distinguish.

For example:

```text
SYSTEM INSTRUCTIONS
Follow the user's goal. Use evidence from the retrieved passages.

CURRENT GOAL
Find the return policy for a damaged item.

RETRIEVED EVIDENCE
The policy allows damaged items to be returned within 30 days.

RECENT TOOL RESULT
The store's policy page was found successfully.

USER REQUEST
Can I return an item that arrived damaged?
```

Clear labels help organize context, but they do not guarantee that the model will follow every instruction or interpret every passage correctly. Retrieved content should be treated as evidence, not automatically as trusted instructions.

### Step 5: Inspect context over time

For long-running tasks, inspect the actual model input at different steps. Compare what has been added, repeated, summarized, or removed.

Look for:

- Repeated tool results that no longer help.
- Old conversation details unrelated to the current subtask.
- Retrieved passages that do not support the answer.
- Important instructions or evidence that have disappeared.
- Context that grows rapidly at each step.

Measure the token count of each category where possible. Character counts or word counts can be rough indicators, but token counts are more useful when the model's limits are measured in tokens.

## 4. Simple Example

Imagine an AI agent that must answer: "Can I return a damaged item?"

After several steps, its context contains the original request, multiple search results, a long conversation history, and repeated copies of the same store policy.

A poor approach is to keep adding every result to the next model request.

A better approach is to organize the context like this:

| Context part | What to include |
|---|---|
| Instructions | Answer using relevant evidence; state uncertainty if evidence is missing. |
| Current goal | Determine the return policy for a damaged item. |
| Retrieved evidence | The relevant policy passage and its source. |
| History summary | The searches already completed and any useful conclusion. |
| Tool results | Only new results needed for the next decision. |
| Excluded content | Duplicate search results and unrelated conversation details. |

The agent can now focus on the policy instead of repeatedly processing irrelevant material.

The key idea is not to delete history blindly. It is to preserve the useful conclusions and evidence while reducing unnecessary detail.

## 5. Practical AI Engineering Application

Context engineering matters in chatbots, Retrieval-Augmented Generation (RAG) systems, and tool-using agents.

A practical workflow is:

1. **Build the context:** combine the instructions, current request, relevant history, retrieved passages, and necessary tool information.
2. **Count and inspect:** log the context categories and estimate or measure their token usage.
3. **Control growth:** summarize older messages, limit tool output, remove duplicates, and retrieve only relevant passages.
4. **Preserve important information:** retain the current goal, required instructions, and evidence needed for the decision.
5. **Evaluate the result:** check whether the agent answers correctly, follows the goal, and uses the right evidence.

### Example: logging context size in Python

This conceptual example records the character count of each context section. It does **not** calculate model tokens or send anything to an AI model.

```python
context_parts = {
    "instructions": "Answer using the provided evidence.",
    "history": "The user has already searched the store policy page.",
    "retrieved_passages": "Damaged items may be returned within 30 days.",
    "tool_results": "Policy page found successfully.",
    "user_input": "Can I return a damaged item?",
}

for name, text in context_parts.items():
    print(f"{name}: {len(text)} characters")

total_characters = sum(len(text) for text in context_parts.values())
print(f"Total: {total_characters} characters")
```

**How it works:**

- `context_parts` represents the sections assembled for a model request.
- `len(text)` counts characters in each section, not tokens.
- The loop prints the size of each section so you can identify which parts are growing.
- The total provides a simple overview of the assembled text.

For real model requests, inspect the final messages actually sent to the model and use the relevant model or tokenizer tools to count tokens. Character counts are useful for a first inspection but cannot confirm that a request fits a token limit.

### Try it: compare steps 1, 10, and 20

For a long-running agent task, log the context at step 1, step 10, and step 20.

At each step, record:

- The size of each context category.
- Which information is still useful.
- Which information is repeated or stale.
- Whether the current goal and essential instructions are still present.

Then decide what should remain, be retrieved on demand, be summarized, or be removed. This helps reveal whether an agent's mistakes come from poor context management rather than from the model's reasoning alone.

### What context engineering does and does not do

**It does:**
- Organize information provided to the model.
- Reduce unnecessary context and manage token usage.
- Help preserve the goal and relevant evidence across multiple steps.
- Make agent behavior easier to inspect and debug.

**It does not:**
- Increase the model's context-window limit.
- Guarantee correct answers or perfect attention.
- Replace good retrieval, clear instructions, or evaluation.
- Make untrusted retrieved text safe simply by labeling it.

## 6. Key Takeaways

- Context is a limited resource shared by instructions, history, retrieved passages, memories, tool descriptions, tool results, and user input.
- More context is not always better; relevance matters.
- Long agent runs can accumulate noise, repeat information, and lose important details.
- Inspect the actual model input at multiple steps instead of guessing what it contains.
- Set rough budgets and decide what to include, retrieve, summarize, or exclude.
- Clearly label instructions, evidence, memories, tool results, and user input.
- Measure tokens when possible; character counts are only a rough proxy.

## 7. Common Misconceptions

**Misconception: Adding more context always improves an answer.**

Not necessarily. Irrelevant or repetitive context can increase cost and make useful information harder to find.

**Misconception: The context window is the same as the amount of history an application can store.**

No. An application may store a long history, but each model request can include only the content selected for that request within the model's limits.

**Misconception: Summarizing history means losing everything important.**

A careful summary can preserve the goal, decisions, constraints, and evidence while leaving out unnecessary details. Important facts should be checked before being discarded.

**Misconception: Labels guarantee that the model will treat content correctly.**

Labels improve organization, but they are not a security boundary. Untrusted document text and tool output still require appropriate handling.

## 8. Quick Revision

**1. What is context engineering?**

Deliberately selecting, organizing, and updating the information sent to a model.

**2. Why can a long-running agent become less reliable?**

Its context may grow with irrelevant history, repeated results, and noise, while important details become harder to find.

**3. What are four ways to manage context?**

Always include essential information, retrieve information when needed, summarize older content, and exclude irrelevant or duplicated content.

**4. What should you inspect when debugging an agent?**

The actual model input at different steps, including its categories, token usage, relevance, and missing information.

**5. Are character counts the same as token counts?**

No. Character counts are a rough size indicator; model token counts are more appropriate for checking context-window usage.
