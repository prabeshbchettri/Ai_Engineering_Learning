# Automatic Regression Tests

## 1. What Is It?

Automatic regression testing means rerunning a fixed set of tests whenever you change your AI application to check whether its behavior has become worse. For a RAG or LLM application, these tests may evaluate answer quality, retrieval performance, citation correctness, cost, and response time.

The goal is to compare every new version against a known baseline so that a prompt edit, configuration change, or model update does not silently introduce failures.

## 2. Why Does It Matter?

LLM applications can change behavior when you update a prompt, model, retrieval setting, chunking strategy, or other configuration. A change that improves one example may make many other answers worse.

Without regression tests, you may not notice the damage until users report it. Automated tests provide an early warning and help you make changes with evidence rather than relying on a few manual checks.

## 3. How Does It Work?

### Step 1: Keep the test and configuration together

Store the information needed to reproduce an evaluation:

- Test questions and expected answers or reference passages.
- Prompt templates and relevant system instructions.
- Retrieval and generation settings.
- Model names and versions.
- Evaluation metric definitions and thresholds.
- Results, timestamps, and version identifiers.

Version-control the files where practical. Avoid storing secrets such as API keys in source control. If a model or service changes without a fixed version, record the available identifier and evaluation date.

### Step 2: Establish a baseline

Run the test set against the current best version and save its results. This is your baseline.

For every later change, compare the new results with this baseline. Do not judge a change only by whether it runs successfully or performs well on one example.

A baseline may include several measures, such as:

- Answer quality or faithfulness.
- Retrieval recall or relevance.
- Citation correctness.
- Average latency.
- Cost per question.

### Step 3: Run tests after every relevant change

Trigger the evaluation whenever you change a prompt, model, retrieval setting, or other behavior-affecting configuration. This can be done locally with a single command and later in a continuous integration (CI) workflow.

Set acceptance rules before running the tests. For example, reject a change if the quality score falls below the baseline by more than an allowed tolerance, or if a critical citation test fails.

A simplified quality gate is:

`if new_quality_score < minimum_acceptable_score: fail the test run`

The exact threshold depends on your application. For important systems, use hard rules for critical failures and tolerances for metrics that naturally vary.

### Step 4: Add new failures to the test set

Whenever you discover a real failure, turn it into a regression test. Include the question, expected behavior, and the evidence or rule used to judge the answer.

This makes the test set grow over time. A fix that solves one failure can then be checked against previous failures, reducing the chance that the same mistake returns.

### Step 5: Compare quality, cost, and speed together

A change can improve answer quality but also increase latency or cost. Review the trade-offs together rather than optimizing a single score.

For example, a self-correction step might improve faithfulness but require another model call. Decide whether the quality gain justifies the extra cost and delay for your application's users.

## 4. Simple Example

Suppose a university FAQ RAG assistant has a baseline answer-quality score of 0.90. The team edits its prompt to make answers shorter.

| Version | Quality score | Average response time | Cost per question | Decision |
|---|---:|---:|---:|---|
| Baseline | 0.90 | 1.8 seconds | $0.010 | Current best |
| New prompt | 0.84 | 1.6 seconds | $0.009 | Reject: quality dropped |
| Revised prompt | 0.91 | 1.7 seconds | $0.010 | Consider accepting after reviewing failures |

These figures are illustrative. The shorter prompt improves speed and cost slightly, but the first change reduces quality enough to fail the quality gate. The revised prompt should still be checked for critical failures and citation correctness before acceptance.

## 5. Practical AI Engineering Application

Start with a small, repeatable evaluation script:

1. **Create a fixed test set.** Include representative questions and known failure cases.
2. **Save the baseline.** Record the current version's scores, settings, model identifier, latency, and cost.
3. **Write one evaluation command.** It should run the test set, calculate the selected metrics, compare results with the acceptance thresholds, and exit with a failure status when a rule is violated.
4. **Test the quality gate.** Deliberately make a prompt worse and run the command. Confirm that the test run fails.
5. **Add the command to CI.** Run it automatically when relevant code or configuration changes are submitted.
6. **Keep adding regressions.** When a new failure appears, add it to the test set before or alongside fixing it.
7. **Review trade-offs.** Compare quality, cost, and speed before accepting a change.
8. **Update the baseline deliberately.** Only replace the baseline after reviewing the new version and deciding it is the new accepted version.

A simple project structure could look like this:

```text
rag-app/
├── app/
│   ├── prompts.py
│   └── rag_pipeline.py
├── evals/
│   ├── test_questions.json
│   ├── baseline.json
│   └── run_evals.py
├── config/
│   └── eval_settings.yaml
├── requirements.txt
└── README.md
```

The exact structure can vary. The important point is that tests, relevant configuration, baseline results, and evaluation code are easy to find and version together.

A basic command might look like:

```bash
python evals/run_evals.py
```

The script should return a non-zero exit code when a required quality threshold is missed. That allows a CI system to mark the change as failed instead of silently accepting it.

## 6. Key Takeaways

- Regression tests check whether a change makes an AI application worse.
- Keep test questions, prompts, settings, model identifiers, and results together so evaluations are reproducible.
- Compare every new version against a known, accepted baseline.
- Run tests whenever prompts, models, or relevant settings change.
- Set explicit acceptance thresholds and fail the test run when they are violated.
- Add every newly discovered failure to the test set.
- Evaluate quality, cost, and speed together.
- Update the baseline only after reviewing and accepting the new version.

## 7. Common Misconceptions

- **“If the application runs, the change is safe.”** A successful run does not prove that answer quality stayed the same.
- **“Testing a few examples is enough.”** A fixed, representative test set is more likely to reveal regressions across different question types.
- **“The baseline should update automatically after every run.”** Doing so can normalize a bad change. Update it deliberately after review.
- **“Only quality matters.”** Latency, cost, citations, and critical failure cases can also determine whether a change is acceptable.
- **“Regression tests prevent every possible failure.”** They catch failures covered by the test set and checks; keep improving the tests as new problems appear.

## 8. Quick Revision

**Q1. What is a regression test?**  
A repeatable test that checks whether a change has made existing behavior worse.

**Q2. What should be saved to reproduce an evaluation?**  
The test set, prompts, relevant settings, model identifiers, metric definitions, and results.

**Q3. What is a baseline?**  
The saved result of a known, accepted version used to judge later changes.

**Q4. What should happen when a change fails the quality gate?**  
The evaluation should fail and the change should be reviewed before it is accepted.

**Q5. Why add new failures to the test set?**  
So future changes are checked against them and the same mistake is less likely to return.

**Try it:** Create a single command that runs your test set and fails if the score falls below your baseline. Deliberately make your prompt worse, run the command, and confirm that it fails.

**Outcome:** You can catch regressions automatically and avoid making your application worse without noticing.
