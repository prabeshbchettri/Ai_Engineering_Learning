# Test Sets and Scoring

## 1. What Is It?

A **test set** is a collection of examples used to check how well an AI application performs. For an LLM application, each example might contain a question, the expected answer, and the source passage that supports it.

A **golden test set** is a carefully reviewed collection of trusted examples from your own documents. It acts as a reference for evaluating changes to prompts, models, retrieval, or the wider application pipeline.

**Scoring** means applying defined criteria to decide whether each output meets the expected behavior. Scoring can use ordinary code, an LLM acting as a judge, or human review.

## 2. Why Does It Matter?

Without a stable test set, it is difficult to tell whether a change actually improves your application. A new prompt may fix one answer but break another. A different model may sound more fluent while becoming less faithful to your documents.

A well-built test set helps you:

- **Measure quality consistently:** Test new versions against the same examples.
- **Catch regressions:** Find cases that used to work but now fail.
- **Check important behaviors:** Test facts, answer formats, and whether claims are supported by evidence.
- **Cover your own documents:** Use questions that reflect what your application is actually expected to answer.
- **Make evaluation more efficient:** Reuse reviewed examples instead of judging every change from scratch.

A test set is only as useful as its quality and coverage. A small set can reveal problems, but it cannot guarantee that the system will handle every possible user question.

## 3. How Does It Work?

### Step 1: Build a golden test set

Create a list of representative questions from your own documents. For each example, store:

- **Question:** What a user might ask.
- **Expected answer:** The correct answer or essential facts the response should include.
- **Supporting passage:** The exact section of the source document that supports the answer.
- **Optional metadata:** Document name, topic, difficulty, or expected answer type.

Example:

| Field | Example |
|---|---|
| Question | When is the scholarship application due? |
| Expected answer | The application is due on 15 May. |
| Supporting passage | “Applications must be submitted by 15 May.” |
| Source | Scholarship policy, section 2 |

The expected answer helps check correctness. The supporting passage helps check whether the response is grounded in the source.

### Step 2: Grow the test set carefully

Use a combination of approaches:

1. **Write questions by hand.** Start with common, important questions and difficult cases.
2. **Ask a model to suggest more.** Provide relevant document passages and ask for questions that can be answered from them.
3. **Verify every suggestion.** Check that each question is clear, answerable, relevant, and supported by the cited passage. Correct or reject weak suggestions.
4. **Keep the set organized.** Store examples in a consistent format, such as JSON, CSV, or a spreadsheet.
5. **Add real failures.** When your application fails on a useful real-world question, consider adding it to the test set after reviewing the correct answer and source.

Do not accept model-generated questions automatically. A model may invent details, write ambiguous questions, or produce questions that the supplied documents cannot answer.

### Step 3: Choose a scoring method

There are three common ways to score answers.

| Method | Best suited for | Example |
|---|---|---|
| Code-based checks | Exact facts, required fields, formats, and simple rules | Does the response contain the correct policy date? Is the output valid JSON? |
| LLM-as-a-judge | Meaning-based criteria that are difficult to express as simple rules | Does the answer address the question? Is every claim supported by the passages? |
| Human review | Subtle, ambiguous, high-impact, or difficult-to-judge cases | Is the answer misleading even though individual statements seem plausible? |

Use the simplest reliable method for each check. Code is usually more predictable for exact requirements. A model judge can assess meaning, but its decisions can also be wrong. Human review remains important for validating the evaluation process.

### Step 4: Decide whether you need an answer key

Not every evaluation needs a reference answer.

**Reference-based checks** compare the output with a known answer or expected facts.

Example: The expected application deadline is 15 May. Check whether the answer gives that date.

**Reference-free checks** assess an answer using other evidence or a defined criterion without requiring one exact expected answer.

Example: Given a question, an answer, and the retrieved passages, decide whether the answer is supported by those passages.

A reference-free check still needs a clear rule and relevant evidence. “No answer key” does not mean “no standard for judging.”

### Step 5: Write a focused judge

An **LLM judge** is a model instructed to assess another model's answer against a specific criterion.

For reliable results:

- Ask **one clear question at a time**, such as whether the answer is supported by the supplied passages.
- Provide the question, answer, and relevant passages.
- Define what counts as pass and fail.
- Request a simple `PASS` or `FAIL` result rather than an arbitrary score out of 10.
- Tell the judge not to treat unsupported claims as supported just because they sound plausible.
- Specify how to handle missing evidence or uncertainty.

A focused judge is easier to inspect and compare with human decisions than one asked to judge correctness, relevance, tone, completeness, and safety all at once.

### Step 6: Validate the judge

A judge that has not been checked can give misleading evaluation results.

1. Select 20 representative answers.
2. Score each answer yourself using the same pass/fail rule.
3. Ask the judge to score those answers independently.
4. Compare the human decisions with the judge's decisions.
5. Count agreements and disagreements.
6. Read the disagreements, improve the judge's instructions, and test again.

Agreement rate can be calculated in plain text:

`Agreement rate = Number of matching decisions / Total decisions × 100`

For example, if the judge and your review agree on 17 of 20 answers:

`Agreement rate = 17 / 20 × 100 = 85%`

This is an illustrative calculation, not a guarantee that the judge is reliable. Also inspect the types of disagreement. Missing a serious unsupported claim may matter more than disagreeing over a minor wording issue. Agreement with one reviewer does not prove correctness, so use clear criteria and consider a second reviewer for high-impact evaluations.

## 4. Simple Example

Suppose you are building a university FAQ assistant that answers from an official scholarship policy.

The source passage says:

> “Applications must be submitted by 15 May. Applicants must provide their academic transcript.”

Your golden test example could be:

```json
{
  "question": "What is the scholarship deadline?",
  "expected_answer": "Applications must be submitted by 15 May.",
  "supporting_passage": "Applications must be submitted by 15 May.",
  "source": "Scholarship policy"
}
```

Now imagine the assistant answers:

> “Applications close on 15 May. Applicants should also submit a recommendation letter.”

You can evaluate this response in more than one way:

- **Code check:** Check whether the required date, `15 May`, appears in the answer. This checks one exact fact but does not assess the whole answer.
- **LLM judge:** Ask whether every factual claim in the answer is supported by the supplied passage. The deadline is supported, but the recommendation-letter claim is not. The answer should fail this criterion.
- **Human review:** Confirm that the extra claim could mislead an applicant and decide whether the evaluation categories need to record an unsupported addition.

Notice that matching the expected deadline does not automatically make the whole response correct. Different checks assess different properties.

## 5. Practical AI Engineering Application

For an LLM or retrieval-augmented generation (RAG) application, keep your golden test set in a version-controlled file and run it after changes to prompts, models, retrieval settings, or document processing.

A simple evaluation workflow is:

`Golden test set → Run application → Collect answers → Apply code checks and judge → Review disagreements → Improve → Re-run`

A practical test record can include:

| Field | Purpose |
|---|---|
| `question` | Input sent to the application |
| `expected_answer` | Reference answer or key facts, if available |
| `supporting_passages` | Evidence used to answer the question |
| `actual_answer` | Output produced by the application |
| `code_check` | Result of deterministic checks |
| `judge_result` | Pass/fail result from the judge |
| `human_result` | Your independently reviewed result |
| `notes` | Explanation of failures or disagreements |

Keep the judge's criterion separate from other criteria. For example, “supported by the passages” is different from “fully answers the question.” An answer can be supported but incomplete, or complete-sounding but unsupported.

### Try it

1. Select a few passages from your own documents.
2. Write questions and expected answers by hand.
3. Use a model to suggest additional questions, then verify every one.
4. Save the reviewed examples as your golden test set.
5. Write a judge that answers one question: **“Is the answer supported by the supplied passages?”**
6. Test the judge on 20 answers and score those answers yourself using the same rule.
7. Count the agreements and disagreements, inspect the disagreements, and improve the judge's instructions.

## 6. Key Takeaways

- A golden test set contains carefully reviewed questions and trusted reference information drawn from your own documents.
- Model-generated questions can help expand the set, but every suggestion must be checked before use.
- Use code for exact facts and formats, an LLM judge for meaning-based criteria, and human review for subtle or high-impact cases.
- Some checks need a reference answer; others can assess whether an answer is supported by supplied evidence.
- Give an LLM judge one clear criterion and request a simple pass/fail decision.
- Validate the judge against around 20 answers scored independently by a human.
- Count disagreements and inspect them; agreement alone does not prove the judge is correct.

## 7. Common Misconceptions

### “A model can generate a test set and verify it automatically.”

A model can suggest useful questions, but it can also invent facts or create unanswerable questions. Review each example against the original documents.

### “If the answer matches the answer key, it must be good.”

A matching fact does not guarantee that the rest of the answer is complete, relevant, or supported. Use checks that correspond to the quality you want to measure.

### “An LLM judge is always objective.”

A judge can misread evidence, miss unsupported claims, or apply its instructions inconsistently. Compare its decisions with human review and refine the rubric.

### “A judge's high agreement rate proves it is reliable.”

Agreement is useful evidence, but the sample may be small or unrepresentative. Inspect disagreement types and ensure important failure cases are included.

## 8. Quick Revision

**Q1. What is a golden test set?**  
A reviewed collection of test questions with trusted answers and supporting evidence from your own documents.

**Q2. How can you expand a test set efficiently?**  
Write questions by hand, ask a model for suggestions, and verify every suggestion before keeping it.

**Q3. What are the three main scoring approaches?**  
Code-based checks, an LLM acting as a judge, and human review.

**Q4. Does every evaluation require a reference answer?**  
No. Some checks can assess whether an answer is supported by supplied passages without comparing it with one exact answer.

**Q5. How should you validate an LLM judge?**  
Score 20 answers yourself, compare your decisions with the judge's, count agreements and disagreements, and refine the instructions.
