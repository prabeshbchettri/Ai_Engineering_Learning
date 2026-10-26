# Why Evals, and Reading Your Failures

## 1. What Is It?

**Evaluation (evals)** is the systematic process of checking how well an AI application performs on representative examples. Instead of deciding that an application is good because a few answers look convincing, you test it on a set of questions, inspect the results, and track recurring problems.

**Reading failures** means examining actual model answers that are incorrect, misleading, incomplete, irrelevant, or otherwise unsuitable. This helps you discover what is going wrong before choosing what to improve.

## 2. Why Does It Matter?

AI applications can produce plausible-sounding answers that are still false or unsafe. For example, an airline chatbot might invent a refund policy that the airline does not offer. A few successful test questions would not reveal this risk.

Systematic evaluation helps you:

- **Find problems early:** Discover unreliable behavior before users depend on it.
- **Compare changes:** Check whether a new prompt, model, or retrieval pattern improves results or creates new failures.
- **Prioritize fixes:** Spend time on the most frequent or harmful problems rather than guessing.
- **Track progress:** Re-run the same examples after changes to see whether performance improves.
- **Build trust responsibly:** Gather evidence about what the application does well and where it remains unreliable.

AI testing differs from ordinary software testing in important ways:

| Traditional software checks | AI application evaluation |
|---|---|
| A fixed input often has an exact expected output. | Several answers may be acceptable, depending on the task. |
| Behavior is often deterministic. | Model outputs may vary between runs. |
| Pass/fail checks can cover many requirements. | Often needs examples, scoring criteria, and human review. |
| A test may check exact values or rules. | A test may assess correctness, relevance, completeness, or whether claims are supported by sources. |

Traditional automated tests are still useful for AI applications—for example, checking that an API returns valid JSON. They just do not measure answer quality by themselves.

## 3. How Does It Work?

A practical evaluation process follows this loop:

1. **Define what good looks like.** Decide what a successful answer must do. For a document question-answering app, criteria might include factual correctness, relevance, completeness, and support from the supplied documents.
2. **Build a set of examples.** Collect representative questions and, where possible, reference answers or clear scoring guidelines. Include ordinary questions, difficult questions, and questions the system should not answer confidently.
3. **Run the application.** Send the examples through the same pipeline that real users use, such as prompt construction, retrieval, and model generation.
4. **Score the answers.** Apply suitable checks or rating criteria. Some checks can be automated; others need human judgment.
5. **Read the failures.** Inspect actual answers rather than relying only on an overall score. Write a short note explaining what went wrong in each answer.
6. **Group similar problems.** Combine individual failure notes into a small number of useful categories.
7. **Prioritize and improve.** Fix the most frequent or highest-impact problems first. Change one part of the system where practical so you can understand the effect.
8. **Run the evaluation again.** Compare the new results with the previous ones and check whether the fix helped without introducing regressions.

### Read before you measure

For an early review, inspect around **20–30 real answers**. For each problematic answer, write a one-line description of the failure. Then group the notes into **3–5 failure types** and count how often each occurs.

This first review helps you choose useful evaluation metrics. Measuring a convenient score before understanding the actual failures can hide the problems users care about.

### Example failure categories

| Failure type | What it looks like |
|---|---|
| Unsupported claim | The answer invents a fact or policy not supported by the available evidence. |
| Retrieval failure | The system does not retrieve the document passage needed to answer. |
| Incomplete answer | The answer misses an important part of the question. |
| Irrelevant answer | The answer discusses a related topic but does not answer the question. |
| Unnecessary refusal or overconfidence | The system refuses an answer it could support, or presents uncertain information as certain. |

These are starting categories, not a universal taxonomy. Adapt them to the behavior of your own application.

## 4. Simple Example

Suppose you have a university FAQ assistant that answers questions using university documents. You test it with 20 questions and inspect every response.

Example notes from the review:

- Question 1: Invented a deadline that was not in the document.
- Question 2: Retrieved the rules for undergraduate students instead of postgraduate students.
- Question 3: Explained the eligibility rules but omitted the required documents.
- Question 4: Gave a long explanation without answering the question directly.
- Question 5: Correctly said the document did not contain the requested information.

You group the failures and count them:

| Failure type | Number of failures |
|---|---:|
| Unsupported claims | 6 |
| Retrieval errors | 5 |
| Incomplete answers | 4 |
| Irrelevant or indirect answers | 2 |
| **Total failed answers** | **17** |

In this illustrative example, 17 of the 20 answers were marked as having a problem. The counts describe this small test set; they do not prove how the assistant will perform on every future question.

The review suggests that unsupported claims and retrieval errors deserve attention first. You would then inspect those examples in more detail to determine the causes. For example, retrieval errors might come from confusing document metadata, weak search results, or missing content. Do not assume the cause from the category alone.

## 5. Practical AI Engineering Application

You can apply evaluation to an LLM application built with a prompt, tools, retrieval, or a more complex workflow.

A simple workflow is:

`Test questions → AI application → Answers → Failure notes → Categories and counts → Fixes → Re-test`

For a LangChain application, for example, keep a fixed set of representative inputs and run them through the same chain or workflow after changes. Record the input, output, expected behavior or reference answer, score, and failure note.

A useful starter evaluation record might contain:

| Field | Purpose |
|---|---|
| Question | The input being tested |
| Expected behavior | What a good answer should do |
| Actual answer | What the application produced |
| Result or score | Whether it met the criteria |
| Failure type | The category of the problem, if any |
| Notes | A short explanation of the issue |

### What should you measure?

Choose measurements based on the failures you observe:

- If answers invent facts, assess factual correctness and whether claims are supported by the provided sources.
- If the wrong passages are retrieved, evaluate retrieval quality separately from answer generation.
- If answers omit required information, assess completeness against a checklist or reference answer.
- If answers miss the question, assess relevance.
- If outputs must follow a schema, use automated checks for the required structure and fields.

**Important distinction:** A score is a signal, not a complete explanation. A high average score can hide a serious failure affecting a small but important group of users. Read examples and consider the severity of each problem, not just how often it occurs.

### Try it

1. Run 20 questions through your current AI pipeline.
2. Read each answer carefully.
3. Write a one-line note for every answer that is not right.
4. Group the notes into 3–5 failure types.
5. Count each type.
6. Choose one frequent or high-impact failure to investigate and fix.
7. Run the same questions again and compare the results.

## 6. Key Takeaways

- A few good-looking answers do not prove that an AI application is reliable.
- AI outputs can vary, and answer quality often needs more than a simple exact-match check.
- Start by reading real answers and documenting what went wrong.
- Group failures into a small number of categories and count them.
- Choose metrics and fixes based on observed failures and their impact.
- Re-run the same evaluation set after changes to check for improvement and regressions.
- The evaluation loop is: define success → build examples → run → score → inspect failures → improve → repeat.

## 7. Common Misconceptions

### “If the answer sounds confident, it is probably correct.”

Confidence and fluency do not guarantee factual accuracy. Check important claims against reliable evidence or the application's source material.

### “One accuracy score tells me everything.”

A single score can hide different failure types and serious edge cases. Combine suitable measurements with inspection of individual answers.

### “AI outputs vary, so testing is pointless.”

Variation makes systematic testing more important, not less. Use representative test sets, suitable scoring criteria, and repeated runs when variability itself matters.

### “I should choose metrics before looking at examples.”

Start by understanding actual failures. That evidence helps you select measurements that reflect real user needs.

## 8. Quick Revision

**Q1. What are evals?**  
A systematic way to assess an AI application's performance using examples and defined criteria.

**Q2. Why is testing AI different from testing ordinary deterministic code?**  
Outputs may vary, and many answers require judgment about correctness, relevance, completeness, or evidence rather than exact matching.

**Q3. What should you do before choosing metrics?**  
Read around 20–30 real answers, note the failures, and group similar problems.

**Q4. How many failure types should you start with in this exercise?**  
Around 3–5 useful categories.

**Q5. What is the evaluation loop?**  
Define success → build examples → run → score → inspect failures → improve → repeat.
