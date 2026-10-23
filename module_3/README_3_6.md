# Automatic Prompt Improvement

## 1. What Is It?

Automatic prompt improvement is the process of using a model or an optimization tool to create and evaluate better prompts instead of relying only on manual editing.

You provide the current prompt, examples of failures, and criteria for a good answer. A model can suggest alternatives, and an evaluation process can score those alternatives on a test set.

The goal is not to make the prompt longer. It is to find a prompt that performs better on the task's success criteria while remaining understandable, maintainable, and efficient.

## 2. Why Does It Matter?

Manually improving prompts can be slow, especially when an application has many test cases or several output requirements. Automatic improvement can help explore different instructions and examples more systematically.

It can help you:

- Generate several candidate prompts quickly.
- Use real failure cases to guide improvements.
- Compare prompt versions using the same evaluation criteria.
- Select useful few-shot examples based on measured results.
- Reduce reliance on personal intuition when tuning prompts.

However, automatic optimization is only as good as its evaluation process. If the test cases or scoring rules are weak, an optimizer may improve the score without improving real-world performance.

## 3. How Does It Work?

### Step 1: Prepare the current prompt and examples

Collect four things:

1. **Current prompt:** the instructions currently used by your application.
2. **Failure cases:** questions or inputs that produce incorrect or incomplete answers.
3. **Expected behavior:** what a good answer should contain or avoid.
4. **Evaluation method:** how you will decide whether an answer passes.

For example, a university document assistant might answer a question correctly but fail to name the supporting PDF. That failure suggests the prompt or output requirements should explicitly address source attribution.

### Step 2: Ask a model to propose alternatives

Give the model the current prompt, a small set of failure cases, and the criteria for success. Ask for several distinct versions and a short explanation of the changes.

Example instruction:

```text
You are helping improve a prompt for a university document-question-answering assistant.

Current prompt:
"Answer the user's question using the supplied documents."

Failure cases:
1. The assistant guessed an answer that was not in the documents.
2. The assistant answered correctly but did not name the source document.
3. The assistant gave a long answer when a short answer was requested.
4. The assistant treated missing information as if it were confirmed.
5. The assistant ignored the requested table format.

A good answer must:
- Use the supplied documents as its evidence.
- Clearly state when information is unavailable.
- Name the source document when relevant.
- Follow the requested output format.
- Avoid unsupported claims.

Generate three meaningfully different prompt versions.
For each version, explain what changed and which failures it is intended to address.
Do not claim that any version is better until it has been evaluated.
```

The generated prompts are **candidates**, not proven improvements. Evaluate them before choosing a winner.

### Step 3: Score each candidate

Run the original prompt and each candidate on the same development test set. Use the same model, source material, settings, and scoring rules wherever possible.

For example:

| Prompt | Development cases passed | Pass rate |
|---|---:|---:|
| Original | 6/10 | 60% |
| Candidate A | 8/10 | 80% |
| Candidate B | 7/10 | 70% |
| Candidate C | 9/10 | 90% |

These figures are illustrative only. They show how to organize results; they are not real benchmark results.

A simple score is:

`Pass rate = Number of passed cases / Total cases × 100`

Depending on the task, also measure source correctness, unsupported claims, format compliance, latency, and token usage. Do not use a single score if it hides a critical failure, such as unsupported factual claims.

### Step 4: Keep the best candidate and repeat

A basic improvement loop looks like this:

```text
Current prompt
      ↓
Collect failures and expected behavior
      ↓
Generate candidate prompts
      ↓
Evaluate candidates on development tests
      ↓
Inspect scores and failure cases
      ↓
Keep the strongest maintainable candidate
      ↓
Repeat if important failures remain
```

Each round should be guided by actual failure patterns. If every candidate fails to cite sources, improve the source-attribution requirement rather than making unrelated wording changes.

Use a stopping rule, such as reaching the required quality threshold or seeing no meaningful improvement after several rounds. More optimization is not always worth the extra cost.

### Step 5: Select few-shot examples using evidence

**Few-shot prompting** means including a small number of input-output examples in the prompt to demonstrate the desired behavior.

Instead of selecting examples only by intuition, test which examples help performance on the development set.

A practical approach:

1. Build a pool of representative examples.
2. Create candidate prompts with different example combinations.
3. Evaluate each combination on the same development cases.
4. Keep combinations that improve the relevant metrics.
5. Check whether the examples cause failures on other kinds of inputs.

More examples do not always help. They consume context-window space, may increase cost, and can bias the model toward patterns that do not generalize.

### Step 6: Use a held-out test set to avoid overfitting

**Overfitting** happens when a prompt is tuned so closely to the examples used during optimization that it performs poorly on new inputs.

Split your data into two sets:

- **Development set:** used to identify failures, generate candidates, and choose prompt versions.
- **Held-out test set:** kept separate until the final candidate is selected.

For example, use 10 questions to improve the prompt and keep five different questions aside for final evaluation. The held-out questions should not be shared with the model that generates candidates or used to repeatedly revise the prompt.

After selecting a candidate using the development set, evaluate it on the held-out questions. If it performs poorly, investigate the failure. If you then tune the prompt using those held-out questions, they are no longer an independent test set; create a new held-out set for a later evaluation.

A small held-out set gives only limited evidence. Use a larger and more diverse set when reliability matters.

### Step 7: Read and understand the winning prompt

Always inspect the final prompt before using it.

Check that it:
- Expresses the intended behavior clearly.
- Does not contain contradictory or redundant instructions.
- Does not depend on accidental wording from individual test cases.
- Is short and understandable enough for future maintenance.
- Respects security, privacy, and application constraints.
- Performs well on held-out examples, not only development examples.

An opaque prompt that achieves a high development score can be difficult to debug and maintain. Keep a record of the selected prompt and the reason for each important change.

## 4. Simple Example

Imagine your university RAG assistant has five known failures:

- It guesses when a policy is silent.
- It sometimes omits the source document.
- It ignores a requested table.
- It includes unrelated information.
- It confuses a missing detail with a negative answer.

### Optimization experiment

Use 10 development questions to compare the original prompt and three model-generated candidates. Keep five different questions aside for final testing.

Illustrative results:

| Prompt version | Development score | Held-out score |
|---|---:|---:|
| Original | 6/10 (60%) | 3/5 (60%) |
| Candidate A | 8/10 (80%) | 4/5 (80%) |
| Candidate B | 9/10 (90%) | 2/5 (40%) |
| Candidate C | 8/10 (80%) | 4/5 (80%) |

These values are hypothetical. In this example, Candidate B scores highest on the development set but performs poorly on unseen questions. That is a warning that it may have overfit the development cases.

Candidate A and Candidate C perform better on the held-out set in this example. Review their failure cases, inspect the actual prompt text, and consider maintainability and latency before choosing between them.

The key lesson is that **the highest development score is not enough**. The final choice should be based on generalization, correctness, and practical constraints.

## 5. Practical AI Engineering Application

Automatic prompt improvement can be useful in LLM applications, RAG systems, extraction pipelines, and agent workflows where success can be measured against a set of examples.

### Optimization tools: DSPy

DSPy is a framework for programming and optimizing language-model pipelines. Rather than relying entirely on manually written prompt text, you define the task's inputs and outputs, create a module or program, and provide a metric or evaluation function. An optimizer can then search for effective instructions and demonstrations using your examples.

At a high level, the workflow is:

```text
Define the task and input/output signature
                  ↓
Create the LLM program
                  ↓
Prepare examples and an evaluation metric
                  ↓
Run a DSPy optimizer
                  ↓
Evaluate the optimized program
                  ↓
Inspect the result on held-out data
```

The exact optimizer, configuration, and API depend on the DSPy version and the program being optimized. Consult the official DSPy documentation for current setup and usage details.

DSPy does not remove the need for good data or sound evaluation. If the metric rewards the wrong behavior, optimization can produce an undesirable result.

### What can be optimized?

Depending on the tool and workflow, optimization may explore:
- Instruction wording.
- Few-shot demonstrations.
- Example selection or arrangement.
- Some pipeline-level choices in supported optimization setups.

Not every optimizer changes every part of a system. Check what the chosen optimizer actually supports.

### Production considerations

Before adopting an optimized prompt:
- Evaluate it on held-out cases.
- Check critical failures separately from the overall score.
- Measure latency and token usage.
- Save the prompt, configuration, and test results.
- Re-run regression tests whenever the prompt or model changes.
- Keep a readable version that developers can inspect and maintain.

## 6. Key Takeaways

- Automatic prompt improvement uses failure cases and evaluation criteria to generate and compare candidate prompts.
- Generate several candidates, score them on the same development set, and iterate when useful.
- Few-shot examples can be selected based on measured performance instead of intuition alone.
- Keep held-out questions separate from optimization to detect overfitting.
- The best development score does not guarantee the best performance on unseen inputs.
- DSPy can optimize supported LLM programs using examples and evaluation metrics.
- Always read, understand, and test the final prompt before deploying it.

## 7. Common Misconceptions

### "A model-generated prompt is automatically better."

No. It is only a candidate. It may introduce contradictions, unnecessary complexity, or new failure modes. Test it before adopting it.

### "The candidate with the highest development score must be the winner."

No. It may be overfitted to the examples used during optimization. Evaluate the selected candidate on held-out questions.

### "More few-shot examples always improve performance."

No. Additional examples consume context space and may introduce misleading patterns. Measure whether they help.

### "Automatic optimization removes the need for evaluation."

No. Optimization depends on the evaluation metric. Poor metrics can reward the wrong behavior, so review the metric and the results.

### "An optimized prompt does not need human review."

No. Readability, security, maintainability, and behavior on unusual cases still matter.

## 8. Quick Revision

**Q1. What information should you provide when asking a model to improve a prompt?**

The current prompt, failure cases, examples of good answers, and explicit success criteria.

**Q2. What is an automatic prompt improvement loop?**

Generate candidates, evaluate them on a development set, select a candidate, inspect failures, and repeat if necessary.

**Q3. What is few-shot prompting?**

Including a small number of input-output examples in the prompt to demonstrate the desired behavior.

**Q4. What is overfitting in prompt optimization?**

Tuning a prompt to perform well on the development examples while performing poorly on new inputs.

**Q5. Why should you read the winning prompt?**

To check that it is understandable, maintainable, consistent with requirements, and not hiding undesirable behavior.
