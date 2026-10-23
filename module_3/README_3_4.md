# Reasoning and Breaking Tasks Down

## 1. What Is It?

Reasoning and task decomposition are prompt-design techniques for solving problems that require multiple connected steps.

- **Reasoning-oriented prompting** gives the model a task that requires analysis, comparison, calculation, planning, or several linked decisions.
- **Task decomposition** breaks a large task into smaller subtasks that are easier to perform, check, and combine.
- **A workflow or chain** connects those subtasks so the output of one step becomes the input to another.

These techniques are useful when a task has dependencies or when a mistake early in the process can affect the final answer.

## 2. Why Does It Matter?

Not every request needs the same amount of processing. A simple rewrite may need only a clear instruction, while planning a project from several documents may require multiple steps.

Using the right approach can help you:

- Improve reliability on multi-step problems.
- Make complex work easier to test and debug.
- Identify where an error entered a workflow.
- Keep each stage focused on a specific responsibility.
- Balance answer quality against latency and token cost.

More reasoning is not automatically better. It can add time and cost, and it does not guarantee a correct answer. Choose the simplest approach that reliably solves the task.

## 3. How Does It Work?

### When to use reasoning-oriented prompts

Consider asking for a structured analysis or intermediate steps when the task involves:

- **Multi-step logic:** several conditions must be considered together.
- **Planning:** actions must be ordered and depend on earlier decisions.
- **Math:** calculations require multiple operations or checks.
- **Code analysis:** an error must be traced through several functions or states.
- **Document comparison:** evidence from different sections must be combined.
- **Trade-offs:** the answer depends on evaluating competing options against criteria.

For example, choosing a project plan from several requirements may involve extracting constraints, comparing alternatives, checking dependencies, and recommending a plan.

### When extra reasoning is unnecessary

For simple tasks, a direct instruction is usually enough.

| Task | Usually suitable approach | Why |
|---|---|---|
| Extract an email address | Direct extraction prompt | The task is narrow and specific |
| Classify feedback as positive or negative | Direct classification prompt | The output categories define the task |
| Rewrite a paragraph politely | Direct rewriting prompt | The transformation is straightforward |
| Solve a multi-stage scheduling problem | Structured analysis or decomposition | Decisions depend on several constraints |
| Debug a complex workflow | Stepwise investigation | Multiple causes and dependencies may be involved |

A task can still need validation even if it does not need extensive reasoning. For example, extracted dates or email addresses can be checked against the source.

### Break a complex task into steps

A complex task can be decomposed within one prompt or across multiple calls.

**Option A: Steps inside one prompt**

Give the model an ordered procedure, then ask for a final answer.

```text
Task:
Compare the two university policies.

Procedure:
1. Extract the eligibility requirements from each policy.
2. Identify requirements shared by both.
3. Identify requirements that differ.
4. Check that each comparison is supported by the source text.
5. Present the result in a table.

Constraints:
Do not infer requirements that are not stated in the policies.
```

This is simple to implement, but the intermediate work may not be independently checked by your application.

**Option B: A multi-step chain**

Make each step a separate stage in an application:

```text
Policy documents
      ↓
Step 1: Extract requirements
      ↓
Step 2: Compare requirements
      ↓
Step 3: Verify claims against sources
      ↓
Step 4: Format the final answer
```

This approach can make each stage easier to test. It may also increase latency, token use, and implementation complexity because multiple calls or processing stages may be required.

### Prompting reasoning models

Reasoning models are designed to handle complex problems without needing ritual phrases such as "think step by step." Instead, specify:

- **Goal:** what needs to be solved.
- **Context:** relevant background and source material.
- **Constraints:** rules, limits, and requirements.
- **Success criteria:** what a good answer must contain.
- **Output format:** how the result should be presented.

Ask for a concise explanation, key calculations, assumptions, or evidence when those are useful to verify the answer. You do not need to request a model's private internal reasoning. A clear summary of the method and supporting evidence is often more useful.

### A simple way to choose

1. Start with a direct prompt.
2. Test it on representative examples.
3. If errors occur because the task has several dependent steps, add an ordered procedure or split the work into stages.
4. Check intermediate outputs where errors would be costly.
5. Compare quality, token use, and response time before keeping the more complex design.

## 4. Simple Example

Suppose you have two university policy documents and want to know whether a student qualifies for a scholarship.

### Direct prompt

```text
Based on the documents, does the student qualify for the scholarship?
```

This may work for a simple case, but it does not explicitly require the model to check every eligibility condition.

### Improved prompt

```text
Goal:
Determine whether the student meets the scholarship requirements.

Context:
Use the university policy and the student's supplied academic information.

Procedure:
1. Extract every eligibility condition from the policy.
2. Match each condition against the student's information.
3. Mark each condition as met, not met, or unknown.
4. Make a conclusion only from the checked conditions.

Constraints:
- Do not invent missing student information.
- Treat unknown information as unknown, not as proof of eligibility.
- Cite or quote the relevant policy details for each condition.

Output:
Create a table with Condition, Evidence, Status, and then give a short conclusion.
```

### Why this is more reliable

The improved prompt turns a broad judgment into smaller checks. It also distinguishes between a condition that is not met and one for which information is missing. This makes the conclusion easier to inspect.

The prompt still cannot guarantee correctness. For high-stakes decisions, verify the policy interpretation and calculations independently.

## 5. Practical AI Engineering Application

Task decomposition is useful in document question-answering, code assistants, research workflows, and AI agents.

### Example: Document question-answering

A user asks: "Compare the attendance requirements in these three course outlines and tell me which course has the strictest rule."

A robust workflow might be:

1. **Retrieve:** find the relevant attendance sections in the documents.
2. **Extract:** identify each course's attendance rule and any stated exceptions.
3. **Normalize:** represent the rules in a consistent format.
4. **Compare:** compare the rules using an explicitly defined criterion.
5. **Verify:** check the comparison against the original passages.
6. **Respond:** give the conclusion with supporting source references.

This is a practical form of task decomposition. It separates finding information from interpreting and presenting it.

### Single prompt versus a chain

| Approach | Advantages | Trade-offs |
|---|---|---|
| One well-structured prompt | Simple, often faster, fewer orchestration steps | Harder to inspect or independently validate intermediate stages |
| Multiple prompts or chain stages | Easier to test stages and retry failures | More orchestration, possible extra latency and token cost |
| Tool-assisted workflow | Can retrieve or calculate using external systems | Requires tool permissions, error handling, and validation |

Choose based on the task's complexity and reliability requirements, not simply because a multi-step design seems more advanced.

### Evaluate the result

When comparing a direct prompt with a reasoning-oriented or decomposed prompt, test both on the same representative questions. Track:

- **Accuracy:** Was the answer correct?
- **Evidence support:** Are claims supported by the documents?
- **Token use:** How much input and output text was processed?
- **Latency:** How long did the answer take?
- **Consistency:** Does the prompt behave reliably across different examples?

For a fair comparison, use the same model, source documents, and questions. Repeat tests when response times vary, and avoid concluding that one approach is better from a single example.

## 6. Key Takeaways

- Use structured reasoning or decomposition for multi-step logic, planning, math, debugging, and evidence-based comparisons.
- Use direct prompts for straightforward extraction, classification, and rewriting tasks.
- Break complex work into stages when each stage has a clear purpose or needs independent validation.
- Reasoning models generally do not need the phrase "think step by step"; provide the goal, context, constraints, and success criteria.
- More steps can improve inspectability but may increase latency, token use, and complexity.
- Test prompt designs using accuracy, evidence support, token use, and response time.

## 7. Common Misconceptions

### "Asking for reasoning guarantees a correct answer."

No. A model can still misunderstand the task, use incorrect assumptions, or make calculation errors. Validate important outputs.

### "Every prompt should ask the model to think step by step."

No. For simple transformations, a direct instruction is often sufficient. Extra processing may not improve the result.

### "A longer prompt is always better."

No. Include relevant context and precise constraints, not unnecessary instructions. A concise, well-targeted prompt can outperform a long, unfocused one.

### "Splitting a task into more steps always improves quality."

No. Each stage introduces possible errors and overhead. Decompose only when the stages make the work more reliable, easier to inspect, or easier to maintain.

## 8. Quick Revision

**Q1. When should you use reasoning-oriented prompting?**

When the task involves multiple dependent steps, planning, calculations, debugging, or combining evidence.

**Q2. When is a direct prompt usually enough?**

For straightforward tasks such as extracting a field, classifying a short text, or rewriting a paragraph.

**Q3. What is task decomposition?**

Breaking a complex task into smaller subtasks that can be completed and checked separately.

**Q4. Do reasoning models need the phrase "think step by step"?**

Usually not. State the goal, relevant context, constraints, success criteria, and desired output.

**Q5. How can you compare two prompt designs?**

Test them on the same questions and compare correctness, evidence support, token use, latency, and consistency.
