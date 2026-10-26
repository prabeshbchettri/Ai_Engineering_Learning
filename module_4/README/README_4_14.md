# Self-Correcting RAG

## 1. What Is It?

Self-Correcting RAG is a Retrieval-Augmented Generation (RAG) system that checks whether the retrieved information and generated answer are good enough. If the retrieved passages are irrelevant or the answer is unsupported, the system can retry the search, rewrite the query, retrieve additional evidence, or admit that it does not know.

Two related approaches are:

- **Corrective RAG (CRAG):** Evaluates retrieved documents and decides whether to use them, search again, or use another source.
- **Self-RAG:** Uses reflection to assess retrieval and generated answers, helping the system decide whether its response is adequately supported.

Both approaches aim to improve RAG reliability, but they are not identical methods.

## 2. Why Does It Matter?

A basic RAG pipeline can retrieve irrelevant passages and still generate an answer. The answer may sound convincing even when the evidence does not support it.

Self-correction helps an AI application:

- Detect irrelevant or weak retrieval results.
- Improve search queries when the initial search fails.
- Check whether generated answers are supported by evidence.
- Find missing information through multiple searches.
- Control costs and execution time by limiting retries.

It is useful for document assistants, knowledge-base chatbots, research tools, and question-answering applications.

Self-correction can reduce errors, but it does not guarantee that every answer is correct.

## 3. How Does It Work?

A self-correcting RAG pipeline adds evaluation and decision-making steps to the normal RAG workflow.

### Step 1: Receive the question

Example:

`What is the company's parental-leave policy for new employees?`

### Step 2: Retrieve passages

The retriever searches a document collection or vector database and returns passages that appear relevant to the question.

### Step 3: Grade the retrieved passages

A grader evaluates whether the retrieved passages contain useful information for answering the question.

The grader can be an LLM, a relevance model, or another scoring method.

Possible outcomes:

- **Relevant:** The passages contain useful evidence.
- **Partially relevant:** Some information is useful, but important details are missing.
- **Irrelevant:** The passages do not meaningfully help answer the question.

Relevance is not the same as factual correctness. A passage can be relevant but inaccurate or outdated.

### Step 4: Correct weak retrieval (Corrective RAG)

If the retrieved passages are weak, the system can:

1. Rewrite the original query to make the information need clearer.
2. Search again using the rewritten query.
3. Search another approved source if necessary.
4. Stop if it cannot find sufficient evidence within the retry limit.

If the passages are relevant, the system proceeds to answer generation.

### Step 5: Generate an answer

The LLM receives the original question and the selected passages. It generates an answer using the available evidence.

### Step 6: Check the generated answer (Self-RAG-style reflection)

Before returning the answer, check two things:

- **Grounding:** Are the important claims supported by the retrieved passages?
- **Question relevance:** Does the answer actually address the user's question?

If the answer fails either check, the system can retrieve more evidence or generate another answer.

If sufficient evidence remains unavailable, the system should communicate that limitation instead of inventing an answer.

A simple answer-checking loop is inspired by Self-RAG's reflection principles, but it is not necessarily a complete implementation of the Self-RAG method.

### Step 7: Search in steps (Multi-hop retrieval)

Some questions require multiple related facts that cannot be found in one search.

For example, answering "Who is responsible for maintaining this service, and what is their incident-response policy?" may require two searches:

1. Search for the team responsible for the service.
2. Use the team name to search for its incident-response policy.
3. Combine the retrieved facts into one answer, ensuring that both claims are supported.

This process is called **multi-hop retrieval**. Each search targets information that is still missing.

### Step 8: Know when to stop

Set a maximum number of retries so the system cannot search indefinitely.

For example:

- Initial retrieval: 1 attempt.
- Query rewriting: Up to 2 retries.
- If evidence is still insufficient: Stop and report that limitation.

The maximum number of attempts should be enforced in code, not left entirely to the LLM.

### Complete workflow

`Question → Retrieve passages → Grade retrieval`

`If relevant → Generate answer → Check grounding and relevance`

`If weak → Rewrite query → Retrieve again`

`If the retry limit is reached → Return an uncertainty message`

This process lets the application change its next action based on intermediate results.

## 4. Simple Example

Suppose a company-policy chatbot receives this question:

`How many days of parental leave can a new employee take?`

The initial search retrieves a passage about annual leave. It does not answer the question.

The self-correcting system proceeds as follows:

1. **Grade the passages:** The grader identifies the annual-leave passage as irrelevant.
2. **Rewrite the query:** The system searches for `parental leave eligibility and duration for employees in their first year`.
3. **Retrieve again:** The second search returns a passage describing parental-leave eligibility and duration.
4. **Check the evidence:** The system verifies that the passage addresses new employees and provides the requested duration.
5. **Generate the answer:** It responds with the documented duration and any relevant eligibility conditions.
6. **Stop safely if needed:** If the second search also fails, the system reports that the available documents do not contain enough information.

The important difference from basic RAG is that the system evaluates the search results rather than automatically trusting the first retrieval.

### A Small Python Example

The following example demonstrates the retrieval retry logic. The functions for retrieving, grading, rewriting, and checking are placeholders that you would implement using your chosen retriever and model.

```python
def self_correcting_retrieval(
    question, retrieve, grade, rewrite, max_retries=2
):
    query = question

    for attempt in range(max_retries + 1):
        passages = retrieve(query)

        # Check whether the retrieved passages are relevant.
        if passages and grade(question, passages):
            return passages

        # Stop when the maximum number of attempts is reached.
        if attempt == max_retries:
            break

        # Improve the search query before trying again.
        query = rewrite(question, query, passages)

    return []


def answer_question(
    question, retrieve, grade, rewrite, generate, check_answer
):
    passages = self_correcting_retrieval(
        question,
        retrieve,
        grade,
        rewrite,
        max_retries=2,
    )

    if not passages:
        return "I could not find enough relevant evidence."

    answer = generate(question, passages)

    # Check grounding and whether the answer addresses the question.
    if check_answer(question, passages, answer):
        return answer

    return "I could not verify an answer from the available evidence."
```

**Important points:**

- `retrieve()` searches for passages.
- `grade()` checks whether the passages are relevant.
- `rewrite()` creates a better search query.
- `max_retries=2` allows one initial search and up to two additional attempts.
- `generate()` creates an answer from the retrieved evidence.
- `check_answer()` evaluates whether the answer is supported and relevant.

The code illustrates the control flow rather than a complete working RAG application. The placeholder functions must be connected to actual models and retrieval tools.

## 5. Practical AI Engineering Application

To add self-correction to an existing RAG pipeline, implement the following steps.

### Implementation plan

1. **Add a retrieval grader.** Use an LLM or relevance model to determine whether the retrieved passages help answer the original question.
2. **Define a relevance threshold.** If using numeric scores, select a threshold and validate it against test examples.
3. **Add query rewriting.** When retrieval is weak, ask the model to create a more specific query without changing the user's original intent.
4. **Retrieve again.** Search the same index or an approved alternative source.
5. **Add an answer grader.** Check whether the final answer is supported by evidence and answers the original question.
6. **Enforce retry limits.** Bound the number of searches and answer-generation attempts.
7. **Evaluate the results.** Compare performance before and after self-correction.

### Try It: Improve Your Existing RAG Pipeline

Add a step that grades retrieved passages and rewrites the query when those passages are weak.

Run the five questions your pipeline currently answers worst. Record whether the retry improves retrieval and whether the final answer is supported by the evidence.

Use this table to evaluate the experiment:

| Question | Initial retrieval relevant? | Did retry improve retrieval? | Final answer supported? |
|---|---|---|---|
| Question 1 | Yes / No | Yes / No / N/A | Yes / No |
| Question 2 | Yes / No | Yes / No / N/A | Yes / No |
| Question 3 | Yes / No | Yes / No / N/A | Yes / No |
| Question 4 | Yes / No | Yes / No / N/A | Yes / No |
| Question 5 | Yes / No | Yes / No / N/A | Yes / No |

Measure more than whether the model produces an answer. Track:

- Retrieval relevance.
- Answer correctness and evidence support.
- Number of retries.
- Response latency.
- Model and retrieval costs.

A retry is useful when it improves evidence quality or answer correctness enough to justify its additional cost and delay.

### What It Does and Does Not Do

**It does:**

- Detect likely retrieval failures.
- Retry with a better query or another source.
- Check whether answers are supported by available evidence.
- Stop when sufficient evidence cannot be found within the configured limit.

**It does not:**

- Guarantee that retrieved documents are factually correct.
- Guarantee that an LLM-based grader will always judge correctly.
- Replace good document preparation, retrieval design, or testing.
- Justify unlimited retries or inventing missing facts.

### Connection to AI Agents

A normal RAG pipeline follows a mostly fixed sequence of retrieval and generation steps.

A self-correcting pipeline can inspect intermediate results and choose what to do next: retry retrieval, rewrite the query, gather another fact, or stop.

This is an introduction to agentic behavior because the system selects its next action based on intermediate results. However, a bounded correction loop is not automatically a complete AI agent.

## 6. Key Takeaways

- Self-Correcting RAG checks retrieval and generated answers rather than blindly trusting them.
- Corrective RAG evaluates retrieved documents and decides whether to use them, retrieve again, or consult another source.
- Self-RAG uses reflection to assess retrieval and generation decisions.
- Multi-hop retrieval gathers connected facts through a sequence of targeted searches.
- Answer evaluation should check both evidence support and relevance to the original question.
- Retry limits control execution time and costs and prevent endless loops.
- Testing difficult questions helps establish whether self-correction actually improves the system.

## 7. Common Misconceptions

### Misconception 1: Relevant passages must be correct.

Not necessarily. Relevance indicates that a passage may help answer the question. It does not prove that the information is accurate or up to date.

### Misconception 2: Query rewriting always improves retrieval.

A rewritten query may retrieve better, similar, or worse passages. The system must evaluate the new results.

### Misconception 3: A grounded answer is always a complete answer.

An answer may accurately summarize one passage but omit another fact needed to answer the question fully. Check both grounding and question relevance.

### Misconception 4: More retries always produce better answers.

Additional retries can increase cost and latency and may introduce irrelevant information. Set a limit and measure whether each retry adds value.

## 8. Quick Revision

**1. What is the purpose of Self-Correcting RAG?**

To detect weak retrieval or unsupported answers and take a bounded corrective action.

**2. What does Corrective RAG evaluate?**

The quality and relevance of retrieved documents, then decides whether to use them, retrieve again, or consult another source.

**3. What should an answer grader check?**

Whether the answer's important claims are supported by evidence and whether it addresses the user's question.

**4. What is multi-hop retrieval?**

A sequence of searches where information found in one step helps retrieve the next missing fact.

**5. Why should retries be limited?**

To prevent endless loops and control latency and model costs while allowing the system to stop when evidence is insufficient.
