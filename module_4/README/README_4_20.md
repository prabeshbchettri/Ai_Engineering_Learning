# Evaluating RAG Answers

## 1. What Is It?

Evaluating Retrieval-Augmented Generation (RAG) means checking whether the system retrieves useful information, uses that information faithfully, and answers the user's actual question. Instead of judging only the final response, evaluate each part of the pipeline separately and then test the complete user experience.

A RAG system should produce answers that are correct, complete, supported by evidence, clearly cited, and delivered in an appropriate tone and format. Quality should also be considered alongside response time and cost.

## 2. Why Does It Matter?

A RAG answer can fail for different reasons:

- **Retrieval failure:** Search did not find the passages needed to answer the question.
- **Prompt or context assembly failure:** The right information was retrieved but was missing, poorly arranged, or unclear in the prompt sent to the model.
- **Generation failure:** The model received the correct passages but still misunderstood them, ignored them, or made unsupported claims.
- **User-experience failure:** The answer may be factually sound but incomplete, poorly formatted, missing working citations, or written in the wrong tone.

These failures need different fixes. Changing the model will not solve a retrieval problem, and improving retrieval will not fix a model that cannot faithfully use the correct evidence.

## 3. How Does It Work?

### Step 1: Evaluate retrieval by itself

Give a set of test questions to the search component. Check whether the passages it returns contain the information needed to answer each question.

Useful measures include recall and precision:

- **Recall:** How often does retrieval find the relevant information that should have been found?
- **Precision:** How much of the retrieved information is actually relevant?

If relevant passages are missing from the results, investigate chunking, embeddings, search settings, metadata filters, hybrid search, or reranking.

### Step 2: Evaluate the model by itself

Give the model the correct passages directly, without relying on the search component. Ask it to answer using only those passages.

Check whether the answer:

- Stays faithful to the supplied evidence.
- Avoids unsupported claims.
- Includes the important details.
- Clearly states when the evidence is insufficient.

If the model fails even with the correct passages, the main problem is likely in generation, instructions, context presentation, or the model itself—not retrieval.

### Step 3: Evaluate the complete RAG pipeline

Run the same questions through the full system: question → retrieval → prompt construction → model response → citations.

Check three core areas:

1. **Retrieval relevance:** Did search find passages that contain the needed information?
2. **Faithfulness:** Are the answer's claims supported by the retrieved passages?
3. **Answer relevance:** Does the answer directly address the user's question?

These checks measure different things. A response can be relevant to the question but contain unsupported claims. It can also be faithful to the passages while failing to answer the question completely.

### Step 4: Evaluate the user experience

Review whether users receive answers that are:

- Correct and complete enough for the task.
- Supported by citations that point to the right sources.
- Easy to understand and organized appropriately.
- Written in the requested tone and format.
- Delivered with acceptable speed and cost.

For example, a technically correct answer with broken citations may still be a poor user experience.

### Step 5: Measure cost and speed

Track these alongside answer quality:

- **Latency:** How long one question takes to process.
- **Cost per question:** The total cost of retrieval, model calls, and other services.
- **Number of model calls:** Important for workflows that rewrite, verify, or self-correct answers.

Self-correction may improve quality, but it often adds extra calls and increases both latency and cost. Compare the quality improvement with the additional expense.

### Step 6: Use evaluation tools carefully

Libraries such as **DeepEval** and **RAGAS** can help evaluate RAG systems. Depending on the selected metrics and configuration, they can assess aspects such as retrieval quality, faithfulness, and answer relevance.

Do not treat a score as a complete verdict. Understand what each metric measures, inspect failed examples, and validate automated judgments against human-reviewed answers. Automated LLM-based judges can also make mistakes.

## 4. Simple Example

Imagine a university FAQ assistant answering:

**Question:** “What documents are required to apply for a scholarship?”

The correct source passage says applicants need a transcript, proof of income, and a completed application form.

| Test | Result | Likely interpretation |
|---|---|---|
| Retrieval-only test | Search returns a passage about admission but not the scholarship documents | Retrieval failure |
| Model-only test | The correct scholarship passage is supplied, but the model invents a recommendation letter requirement | Generation or instruction failure |
| Full-pipeline test | Search finds the correct passage, but the assembled prompt omits it | Prompt/context assembly failure |
| User-experience test | The answer lists the correct documents but its citation opens the wrong page | Citation or user-experience failure |

This example shows why the final answer alone does not always reveal the cause of a problem.

## 5. Practical AI Engineering Application

Use this workflow to evaluate a RAG project:

1. **Prepare a test set.** Write realistic questions and identify the source passages that should support their answers.
2. **Score retrieval.** Check whether search returns the required evidence for each question.
3. **Score the model separately.** Supply the correct passages directly and check whether the model answers faithfully.
4. **Score the full pipeline.** Measure retrieval relevance, faithfulness, and answer relevance on the same test set.
5. **Inspect the five worst answers.** For each one, record whether the main fault was retrieval, prompt/context assembly, or generation.
6. **Check citations and presentation.** Confirm citations work and support the associated claims; review completeness, tone, and formatting.
7. **Record speed and cost.** Track latency, cost per question, and model-call count.
8. **Fix the actual cause and retest.** Change the relevant component, rerun the same test set, and compare results.

A simple failure log can use these columns:

| Question | Retrieval relevant? | Faithful? | Answers question? | Main failure source | Latency/cost notes |
|---|---|---|---|---|---|
| Scholarship documents | No | Not applicable or low confidence | No | Retrieval | Search returned admission content |
| Scholarship documents | Yes | No | Partly | Model/instructions | Model invented a requirement |
| Scholarship documents | Yes | Yes | Yes | Citation/user experience | Citation points to the wrong page |

Use consistent criteria when scoring answers. If you use DeepEval or RAGAS, document the metric and its meaning so scores remain interpretable over time.

## 6. Key Takeaways

- Evaluate retrieval, generation, the complete pipeline, and the user experience separately.
- The three core RAG checks are retrieval relevance, faithfulness, and answer relevance.
- Test the model with correct passages to separate generation problems from search problems.
- For every failed answer, identify whether retrieval, prompt/context assembly, or generation caused the failure.
- Working citations, completeness, tone, and format are part of quality.
- Track latency and cost alongside answer quality.
- DeepEval and RAGAS can help, but you must understand what each metric measures and review examples.

## 7. Common Misconceptions

- **“A good final answer means retrieval worked well.”** Not necessarily. The model may answer from prior knowledge or guess despite poor retrieval.
- **“If the answer is relevant, it must be faithful.”** Relevance and faithfulness are different checks.
- **“A high evaluation score proves the system is reliable.”** Scores depend on the metric, test set, and judge quality; inspect real failures.
- **“Only factual correctness matters.”** Citations, completeness, clarity, tone, format, latency, and cost also affect usefulness.
- **“Every failure is a model problem.”** Search, prompt construction, and citation handling can fail independently.

## 8. Quick Revision

**Q1. What are the three core RAG checks?**  
Retrieval relevance, faithfulness, and answer relevance.

**Q2. Why test the model with the correct passages?**  
To find out whether it can answer faithfully when retrieval is not the problem.

**Q3. What should you identify for each failed answer?**  
Whether the failure came from retrieval, prompt/context assembly, or generation.

**Q4. What should be measured besides answer quality?**  
Latency, cost per question, and—where relevant—the number of model calls.

**Q5. What is the purpose of tools such as DeepEval and RAGAS?**  
They help measure RAG quality, but each metric must be understood and interpreted carefully.

**Try it:** Score your test set on retrieval relevance, faithfulness, and answer relevance. Then review your five worst answers and record whether search, prompt/context assembly, or the model was at fault.

**Outcome:** You can evaluate a RAG system part by part and pinpoint where each failure comes from.
