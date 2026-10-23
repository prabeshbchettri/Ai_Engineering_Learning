# Testing and Improving Prompts

## 1. What Is It?

Prompt testing checks whether a prompt produces useful, accurate, and consistent answers across a range of inputs. Prompt improvement, also called prompt iteration, means revising a prompt based on observed failures and testing it again.

A prompt may sound clear but still fail on unusual questions, missing information, or conflicting requirements. Testing evaluates performance using evidence instead of relying on one impressive answer.

## 2. Why Does It Matter?

Prompts influence how an AI application behaves. A change that improves one answer can make other answers worse, so prompt changes should be evaluated systematically.

Testing helps you:
- Find vague or contradictory instructions.
- Detect failures on edge cases and missing information.
- Compare prompt versions fairly.
- Check required output fields and source references.
- Measure consistency across repeated runs.
- Avoid choosing a prompt based on a few successful examples.

Testing does not prove a system will always be correct. A test set covers only the cases it contains, so expand it as new failure types appear.

## 3. How Does It Work?

### Common reasons prompts fail

| Problem | What it means | Possible improvement |
|---|---|---|
| Vague instructions | The task can be interpreted in different ways | State the task and success criteria precisely |
| Contradictory rules | Instructions require incompatible behavior | Resolve the conflict and prioritize requirements |
| Missing context | Necessary information is absent | Supply context or define how to handle unknowns |
| Poor examples | Examples do not represent expected cases | Use clear, representative examples |
| Unclear output format | The required structure is unspecified | Give a template or explicit format |
| Overly broad scope | Too many unrelated tasks are combined | Narrow the task or divide it into stages |

### Step 1: Build a small test set

A **test set** is a collection of inputs used to evaluate a system. Include:

- **Normal cases:** common questions the assistant should answer.
- **Edge cases:** unusual, ambiguous, or multi-condition inputs.
- **Unanswerable cases:** questions whose answers are absent from the supplied information.
- **Known failures:** examples that caused problems before.
- **Format checks:** cases that verify required structures, labels, or citations.

For each case, record the input and expected behavior. For open-ended questions, the expected result can be a checklist of required facts, prohibited claims, and expected sources rather than an exact sentence.

Example test set for a university document assistant:

| ID | Question | Expected behavior |
|---|---|---|
| T1 | What time does the library open? | Give the opening time stated in the document |
| T2 | What ID is required to borrow a book? | Name the required ID |
| T3 | Is the library open on Saturday? | Say Saturday hours are not specified if the document does not state them |
| T4 | Which document supports the answer? | Name the source document |
| T5 | Summarize the library rules in two bullets | Give two relevant bullets without adding unsupported rules |

These are illustrative cases. Base real expected answers on the actual source documents.

### Step 2: Write two prompt versions

Create a baseline prompt and an improved version. Change specific instructions so you can investigate what caused any difference.

**Version A — baseline**

```text
Answer the user's question using the supplied documents.
```

**Version B — improved**

```text
Answer the user's question using only the supplied documents.

Rules:
- Use simple, direct language.
- Do not invent information that is missing from the documents.
- If the answer is not stated or cannot be established from the documents, say so.
- Name the source document that supports the answer.
- Follow the output format requested by the user.
```

Version B adds source restrictions, a policy for missing information, source attribution, and output-format guidance. Testing must establish whether it actually performs better.

### Step 3: Score answers simply

Use the least complicated evaluation method that can reliably check the requirement.

**1. Exact-match checks**

Use code for fixed values such as a course code, date, or category. Normalize harmless differences such as letter case and surrounding spaces when appropriate.

```python
def exact_match(actual, expected):
    return actual.strip().casefold() == expected.strip().casefold()

print(exact_match("  ENCT353 ", "enct353"))  # True
```

Exact matching is unsuitable when multiple different answers can be correct.

**2. Rule-based checks**

Use simple checks for explicit requirements, such as whether an answer contains a required source name or label.

```python
def names_source(answer, source_name):
    return source_name.casefold() in answer.casefold()

answer = "According to the Library Policy document, students need an ID."
print(names_source(answer, "Library Policy"))  # True
```

A simple text check can produce false positives: an answer might mention a source without its claims being supported. Use each check only for requirements it can meaningfully verify.

**3. Human or model grading**

For open-ended answers, use a rubric to assess qualities that are difficult to check with exact matching, such as relevance, completeness, clarity, and evidence support.

A simple rubric can assess:
- **Correctness:** Does the answer match the source?
- **Completeness:** Does it cover the necessary points?
- **Grounding:** Are factual claims supported by the documents?
- **Format compliance:** Does it follow the required structure?

Define the scoring scale in advance. For example, use 0 for fail and 1 for pass on each binary criterion. A human reviewer or separate model grader can apply the rubric. Model graders can also make mistakes, so review a sample of their judgments.

### Step 4: Compare versions on the same questions

Run both versions against the same test cases, with the same model, source material, settings, and evaluation rules.

Do not compare Version A on easy questions with Version B on different or harder questions. That is not a fair comparison.

A simple score is:

`Pass rate = Number of passed checks / Total number of checks × 100`

For example, if a prompt passes 8 of 10 test cases:

`Pass rate = 8 / 10 × 100 = 80%`

If each case has multiple criteria, decide whether you are measuring case-level success or individual criterion-level success. Apply the same definition to every version.

### Step 5: Check consistency with repeated runs

LLM outputs may vary between runs depending on the model, sampling settings, provider, and system behavior. Run each prompt more than once on the same test set.

| Version | Run 1 | Run 2 | Mean pass rate |
|---|---:|---:|---:|
| A | 7/10 (70%) | 8/10 (80%) | 75% |
| B | 9/10 (90%) | 8/10 (80%) | 85% |

These numbers are illustrative, not actual benchmark results. Version B has a higher average in this example, but it still fails some cases. Review the failures before choosing it.

Two runs are useful for a small exercise but provide limited evidence. Higher-stakes applications need broader tests and often more repeated runs.

### Step 6: Improve one thing at a time

1. Identify failed test cases.
2. Group failures by cause, such as missing context, unsupported claims, or format violations.
3. Update the prompt to address a specific cause.
4. Rerun the same test set.
5. Check that the change did not cause regressions on previously successful cases.
6. Add tests for newly discovered failure patterns.

Changing one main factor at a time makes it easier to understand why results changed. If several changes are necessary, record them.

## 4. Simple Example

Imagine you are building a RAG assistant that answers questions from university PDFs. Every factual answer should name its source and avoid guessing when the documents do not contain an answer.

### Test cases

| Question | What a passing answer must do |
|---|---|
| What is the course code? | Return the code stated in the document |
| What is the assignment deadline? | Return the stated deadline |
| Is the exam online? | Answer only if the document establishes this |
| Which document states the rule? | Name the supporting document |
| What is the lecturer's phone number? | Say the information is unavailable if it is absent from the documents |

Use actual facts and document contents when building your real test set.

### Evaluation sheet

For each prompt version and run, record:
- Number of test cases passed.
- Number of unsupported factual claims.
- Number of answers missing a required source.
- Average response time, if latency matters.
- Input and output tokens, if token usage matters.

Example results:

| Metric | Version A | Version B |
|---|---:|---:|
| Test cases passed | 7/10 | 9/10 |
| Unsupported claims | 2 | 0 |
| Missing source names | 4 | 1 |

These figures are hypothetical and only demonstrate how to organize results.

### Choose based on evidence

Version B appears stronger in this example because it passes more cases and has fewer unsupported claims and missing source names. Before adopting it, inspect failures, repeat the experiment, and check whether the prompt has become unnecessarily slow or expensive.

## 5. Practical AI Engineering Application

Prompt evaluation matters when building LLM applications, RAG assistants, agents, extraction systems, and production workflows.

### Example RAG evaluation workflow

```text
Create representative questions
            ↓
Write expected answers and checks
            ↓
Run Prompt A and Prompt B
            ↓
Save answers, timing, and token usage
            ↓
Score using code, rules, or a rubric
            ↓
Compare results across repeated runs
            ↓
Inspect failures and revise the prompt
            ↓
Rerun tests before releasing changes
```

### Useful metrics

| Metric | What it tells you |
|---|---|
| Pass rate | How many defined test cases meet the success criteria |
| Exact-match accuracy | How often a fixed expected answer matches |
| Grounding or citation compliance | Whether claims are supported and required sources are named |
| Consistency | How much performance varies across repeated runs |
| Latency | How long a response takes |
| Token usage | How much text the model processes and generates |

Choose metrics that match the task. Exact match may work well for extracting a course code, while document question-answering also needs checks for factual support and completeness.

### Keep an experiment log

Record the prompt version, date, model, settings, test-set version, results, and known limitations. This makes comparisons repeatable and helps distinguish prompt changes from changes elsewhere in the system.

For production systems, keep a separate set of held-out examples that you do not repeatedly use while tuning. This helps reveal whether improvements generalize beyond the cases used to revise the prompt.

## 6. Key Takeaways

- Prompts often fail because of vague instructions, contradictions, missing context, poor examples, or unclear output requirements.
- Build a test set containing normal cases, edge cases, unanswerable questions, and known failures.
- Use exact-match code for fixed answers, rule-based checks for explicit requirements, and a rubric or grader for subjective judgments.
- Compare prompt versions on the same questions with the same model and settings.
- Run each version repeatedly to measure consistency rather than relying on one result.
- Review failures and rerun regression tests after meaningful changes.
- Choose prompts using measured quality and relevant cost or latency, not intuition alone.

## 7. Common Misconceptions

### "One excellent answer proves the prompt is good."

No. A prompt can succeed on one question and fail on many others. Evaluate a representative set of cases.

### "A higher pass rate means every answer is safe and correct."

No. The test set may not cover important situations, and the scoring method may miss subtle errors. Review failures and add tests over time.

### "A model grader is always objective."

No. A model grader can misinterpret answers or prefer a particular style. Use a clear rubric, keep grading conditions consistent, and review a sample of its decisions.

### "If I improve one test case, the prompt is automatically better."

No. A change may improve one case while causing regressions elsewhere. Compare performance across the full test set.

### "Two runs prove consistency."

No. Two runs are a useful starting exercise, but they provide limited evidence. More runs and broader tests give a stronger picture of reliability.

## 8. Quick Revision

**Q1. What are common reasons prompts fail?**

Vague instructions, contradictory rules, missing context, poor examples, and unclear output formats.

**Q2. What should a small prompt test set include?**

Normal questions, edge cases, unanswerable questions, known failures, and format checks.

**Q3. When should you use exact-match checks?**

When there is a fixed expected value or answer that can be compared reliably.

**Q4. Why must prompt versions be tested on the same questions?**

So score differences reflect the prompt versions rather than differences in test difficulty.

**Q5. Why run each prompt more than once?**

To observe variation between runs and avoid choosing a prompt based on a lucky result.
