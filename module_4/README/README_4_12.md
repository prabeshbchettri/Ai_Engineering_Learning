# Query Transformation

## 1. What Is It?

**Query transformation** means changing a user's original question into one or more search-friendly queries before retrieving documents in a Retrieval-Augmented Generation (RAG) system.

Users may ask vague questions, include unnecessary detail, combine several requests, or use wording that differs from the source documents. A search system may struggle to find the best evidence from the original wording alone.

Query transformation prepares the question for retrieval while preserving the user's intent.

Common techniques include:
- **Query rewriting:** Rewrite the original question as a clearer search query.
- **Multi-query retrieval:** Generate several differently worded queries, search for each, and combine the results.
- **RAG-Fusion:** Use reciprocal rank fusion (RRF) to merge ranked results from multiple queries.
- **HyDE (Hypothetical Document Embeddings):** Generate a hypothetical answer or passage and use its representation to find similar source passages.
- **Question decomposition:** Split a complex question into smaller sub-questions and retrieve evidence for each.

## 2. Why Does It Matter?

Search quality depends partly on how well a query expresses the information being sought. A question can be understandable to a person but still be a poor search query.

For example:

`Can you tell me what happens if someone hands it in late, and does that apply to the software course too?`

The query is vague because “it” and “the software course” may not clearly identify the assignment or course. A rewritten query could make the intended topic more explicit if the conversation or available context supports it.

Query transformation is useful when:
- A question is vague or uses pronouns without clear references.
- The user's wording differs from terminology in the documents.
- One question contains several distinct information needs.
- A single query retrieves only part of the relevant evidence.
- The corpus uses technical language, abbreviations, or formal labels.

It is not necessary for every question. Clear, simple questions may work well with ordinary retrieval, without the added latency and cost of transformation.

## 3. How Does It Work?

### Technique 1: Query rewriting

A language model rewrites the question into a concise, specific search query.

Example:

- Original: `Can you explain what we need to do before submitting the project?`
- Rewritten: `Project submission requirements and pre-submission checklist`

The rewritten version may match headings or phrases in the source documents more closely.

**Important:** Rewriting should clarify the question, not invent missing details. If the intended project or course is unknown, the system should preserve that uncertainty or ask for clarification rather than guessing.

### Technique 2: Multi-query retrieval

One query may not use the same terms as the documents. Multi-query retrieval generates several useful variations of the original question.

Example question:

`How can I apply for a course extension?`

Possible search queries:
1. `Course extension application process`
2. `Requesting an extension to a course deadline`
3. `Policy for extending assignment or coursework deadlines`

The system searches each query, then combines the retrieved passages. Different query variations may uncover different relevant parts of the collection.

Generating many near-identical queries can waste resources and add duplicate or irrelevant results. Query variations should cover genuinely different wording or aspects of the information need.

### Technique 3: RAG-Fusion

**RAG-Fusion** is a multi-query retrieval approach that commonly uses Reciprocal Rank Fusion (RRF) to combine the ranked results from the generated queries.

Instead of comparing raw scores from different searches, RRF combines their rank positions.

A common formula is:

`RRF score(document) = Sum over rankings of 1 / (k + rank)`

Where:
- `rank` is the document's position in a result list, starting at 1.
- `k` is a constant; 60 is a common choice.
- The contributions are added across the ranked lists in which the document appears.

A passage that ranks well across several query variations can receive a strong combined score, even if no individual query puts it first.

RAG-Fusion does not guarantee that the highest-ranked passage is correct. The quality of the generated queries and original retrieval results still matters.

### Technique 4: Search with a draft answer (HyDE)

**HyDE** stands for **Hypothetical Document Embeddings**.

In a typical HyDE workflow:

1. Give the user's question to a language model.
2. Ask it to generate a hypothetical passage that might answer the question.
3. Convert that hypothetical passage into an embedding.
4. Use the embedding to search for similar passages in the real document collection.
5. Give the retrieved source passages—not the hypothetical passage alone—to the answering model.

Why might this help? The hypothetical passage may use the kind of explanatory language found in the documents, even when the original question is short or uses different wording.

**Important:** The hypothetical passage can contain invented or incorrect details. It is a retrieval aid, not evidence. The final answer should be grounded in actual retrieved documents.

HyDE is commonly associated with embedding-based retrieval. It is not the same as searching the corpus using the generated answer as if that answer were verified.

### Technique 5: Question decomposition

Some questions contain several information needs that should be searched separately.

Example:

`What are the prerequisites for ENCT352, when is its final assignment due, and what penalty applies to late submissions?`

Break it into:
1. `Prerequisites for ENCT352`
2. `Final assignment deadline for ENCT352`
3. `Late-submission penalty for ENCT352`

Search for each sub-question independently, gather the evidence, and combine the findings into one answer.

Decomposition is especially useful when each part may be described in a different document or section. The system should track which evidence supports each part and acknowledge any part for which it cannot find sufficient information.

## 4. Simple Example

Imagine a university RAG assistant contains course syllabi, assignment policies, and academic regulations.

The user asks:

`For the software course, what should I finish before submitting, when is it due, and what happens if I submit late?`

This is both ambiguous and multi-part. The phrase “software course” may not uniquely identify a course, and the user asks about requirements, a deadline, and a penalty.

### Plain search

The system searches the original question. It may retrieve general assignment instructions, but miss a deadline or late-penalty rule stored in a different section.

### Query rewriting

If prior conversation or reliable metadata identifies the course as ENCT352, the system might rewrite the query as:

`ENCT352 project submission requirements, assignment deadline, and late-submission penalty`

If the course cannot be identified reliably, the system should ask which course the user means or search without pretending the identity is known.

### Multi-query retrieval

The system generates separate searches for:
- `ENCT352 project submission checklist`
- `ENCT352 assignment deadline`
- `ENCT352 late-submission policy`

It retrieves passages for each query and merges the results. RAG-Fusion can use RRF to rank passages that perform well across multiple searches.

### Question decomposition

The system explicitly treats the request as three sub-questions:
1. What must be completed before submission?
2. When is the assignment due?
3. What is the late-submission penalty?

It retrieves evidence for each part, then combines the supported findings into one answer.

### Where HyDE fits

If the question's wording is very different from the wording used in the syllabus, HyDE could generate a hypothetical passage about submission requirements and use its embedding to find similar source passages.

The hypothetical passage must not be treated as the final answer or as proof of the course's actual rules.

## 5. Practical AI Engineering Application

A practical RAG system can choose a query-transformation technique based on the type of question.

| Question type | Technique to try | Main purpose |
|---|---|---|
| Clear, simple question | Plain search | Avoid unnecessary extra work. |
| Vague or poorly phrased question | Query rewriting | Clarify the search wording. |
| One topic with several possible phrasings | Multi-query retrieval + RRF | Retrieve evidence using different terms. |
| Short query that poorly matches document language | HyDE | Use a hypothetical passage to guide semantic retrieval. |
| Several distinct requests in one question | Question decomposition | Search for each part separately. |

A possible workflow is:

1. **Classify the question:** Decide whether it is clear, ambiguous, multi-faceted, or likely to need alternative wording.
2. **Choose a transformation:** Rewrite, generate multiple queries, use HyDE, or decompose the question.
3. **Retrieve evidence:** Search the indexed documents for each query or sub-question.
4. **Combine results:** Use RRF or another suitable method when merging ranked lists.
5. **Check coverage:** Verify that the retrieved evidence addresses every part of the original question.
6. **Generate the answer:** Answer from actual source passages and state when evidence is missing.

### The cost trade-off

Query transformation can add language-model calls, retrieval operations, embedding computations, and latency.

- Rewriting often adds a model call before search.
- Multi-query retrieval adds searches and result-merging work.
- RAG-Fusion adds rank-fusion work after multi-query retrieval.
- HyDE adds generation and embedding work before retrieval.
- Decomposition can require separate searches and more answer synthesis.

The exact cost depends on the implementation. These techniques can improve difficult queries, but they may not help simple queries enough to justify the overhead. A system can use conditional routing to apply more expensive methods only when needed.

### Try it: Compare retrieval strategies

Choose three ambiguous questions and one multi-part question from your own knowledge base. Compare plain search, multiple queries, and question decomposition.

| Question | Plain search: useful passage found? | Multi-query: useful passage found? | Decomposition: all parts covered? |
|---|---|---|---|
| Ambiguous question 1 | Yes / No | Yes / No | N/A |
| Ambiguous question 2 | Yes / No | Yes / No | N/A |
| Ambiguous question 3 | Yes / No | Yes / No | N/A |
| Multi-part question | Yes / No | Yes / No | Yes / No |

For a fair comparison:
- Use the same document collection and initial retrieval settings.
- Identify the expected evidence before running the experiment.
- Check the passages retrieved, not just whether the generated answer sounds plausible.
- For multi-part questions, verify each requested part separately.
- Record latency and, if applicable, model usage or cost.

Four questions are a useful starting experiment, not enough to establish broad performance claims. Add more examples if you want to decide which strategy should be used by default.

## 6. Key Takeaways

- Query transformation changes a question into one or more search-friendly queries while preserving its intent.
- Query rewriting clarifies a single query; multi-query retrieval explores different phrasings.
- RAG-Fusion combines ranked results from multiple queries, commonly with Reciprocal Rank Fusion.
- HyDE uses a hypothetical passage to guide retrieval, but that passage is not verified evidence.
- Question decomposition turns a multi-part request into smaller searches whose findings can be combined.
- Every extra transformation can add latency and cost, so choose the technique based on the question and test whether it improves retrieval.

## 7. Common Misconceptions

**Misconception: A rewritten query can safely fill in missing information.**  
Correction: Rewriting should preserve intent. If an essential detail is unknown, the system should ask for clarification or retain the uncertainty rather than inventing an answer.

**Misconception: The hypothetical answer in HyDE is factual evidence.**  
Correction: It is generated to help locate similar passages. The final response should rely on actual retrieved sources.

**Misconception: More queries always produce better retrieval.**  
Correction: Additional queries can improve coverage, but they can also introduce noise, duplicate passages, latency, and cost.

**Misconception: Question decomposition is just rewriting the original question.**  
Correction: Rewriting clarifies the query; decomposition separates a question into distinct information needs that may require independent searches.

**Misconception: Every user question needs query transformation.**  
Correction: Simple questions may work well with direct retrieval. Use more expensive techniques when they solve a demonstrated retrieval problem.

## 8. Quick Revision

**1. What is query transformation?**  
Changing a user's question into one or more queries designed to retrieve relevant evidence more effectively.

**2. What is RAG-Fusion?**  
A multi-query retrieval approach that combines ranked results, commonly using Reciprocal Rank Fusion.

**3. What is HyDE?**  
A method that generates a hypothetical passage and uses its embedding to search for similar real passages.

**4. When should you decompose a question?**  
When it contains multiple distinct requests that may need separate searches and evidence.

**5. Why not use every technique for every question?**  
Each technique can add model calls, processing time, and cost, and simple queries may not benefit enough to justify the overhead.
