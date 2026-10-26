# Reranking

## 1. What Is It?

**Reranking** is a retrieval technique that takes an initial list of candidate passages and sorts them again using a more detailed relevance assessment.

In a Retrieval-Augmented Generation (RAG) system, the first search stage retrieves candidate passages from a document collection. A **reranker** then evaluates how relevant each candidate is to the user's question and moves the strongest candidates toward the top.

A common strategy is:

`Retrieve many candidates → Rerank candidates → Send the best few to the LLM`

The first retriever is optimized to search a large collection efficiently. The reranker spends more computation comparing the question with each candidate passage.

## 2. Why Does It Matter?

The first-stage search can retrieve useful information without ranking the best passage first. For example, a passage may share many keywords with a query but fail to answer it, while another passage answers the question directly but appears lower in the results.

Reranking can improve the quality of the context given to the LLM by moving more relevant passages toward the top.

It is useful when:
- Initial search returns many plausible but unevenly relevant passages.
- Questions need a precise answer from technical documentation or policies.
- The correct passage appears in the candidate list but is ranked too low.
- The LLM gives weak or incomplete answers because its retrieved context is noisy.

Reranking cannot recover a passage that the initial retriever did not retrieve. The candidate set must already contain the relevant evidence.

## 3. How Does It Work?

### Step 1: Retrieve a broad candidate set

Run a first-stage retriever, such as BM25 keyword search, vector-based semantic search, or hybrid search.

For example, retrieve the top 20 passages rather than immediately selecting only the top 3. The number is a configuration choice, not a universal rule.

### Step 2: Compare the question with each passage

A reranking model evaluates each question-passage pair.

Many common rerankers use a **cross-encoder**: the model processes the query and candidate passage together and produces a relevance score. Because it can consider their interaction directly, it may recognize that a passage answers the question even when the wording differs.

This differs from a typical bi-encoder embedding search, where the query and passages are embedded separately and compared using a similarity measure.

### Step 3: Sort candidates by reranker score

The reranker assigns a score to each candidate, and the system sorts the candidates from most to least relevant.

These scores are generally ranking signals, not guaranteed probabilities that a passage is correct.

### Step 4: Select the best few passages

Keep only the top-ranked passages—perhaps the top 3 or 5—and pass them to the LLM as context.

`Question → Initial retrieval → Candidate passages → Reranker → Top passages → LLM`

### Step 5: Evaluate whether it helps

Check whether the relevant passage moves higher in the results and whether the final answers improve. Reranking should be evaluated on real questions, not assumed to help simply because a second model was added.

## 4. Simple Example

Suppose a university assistant receives this question:

`What is the late-submission penalty for ENCT352?`

The first-stage search retrieves these passages:

| Initial rank | Passage | Content |
|---:|---|---|
| 1 | A | `ENCT352 assignments must be submitted through the course portal.` |
| 2 | B | `For ENCT352, late assignments lose 10% of the available marks per day.` |
| 3 | C | `ENCT353 covers simulation methods and modeling techniques.` |

The first retriever places Passage A first, perhaps because it matches the course code and assignment terminology. However, Passage B directly answers the question.

A reranker compares the question with each passage and might produce this order:

| Reranked position | Passage | Why it may rank here |
|---:|---|---|
| 1 | B | Directly states the late-submission penalty for ENCT352. |
| 2 | A | Relevant to ENCT352 assignments, but does not state the penalty. |
| 3 | C | Mentions a different course and does not answer the question. |

The system can then send Passage B, plus any other useful context, to the LLM.

These rankings are illustrative, not actual model outputs. Real results depend on the retriever, reranker, passage text, and query.

## 5. Practical AI Engineering Application

A RAG pipeline with reranking commonly follows this workflow:

1. **Prepare and index documents:** Split documents into useful chunks and create keyword and/or vector indexes.
2. **Retrieve candidates:** Use a fast first-stage retriever to collect a relatively broad set of passages.
3. **Rerank candidates:** Score each question-passage pair with a reranking model.
4. **Select context:** Keep the top-ranked passages within the context budget.
5. **Generate the answer:** Give the selected passages to the LLM, with instructions to answer from the evidence.
6. **Evaluate:** Compare retrieval quality and answer quality with and without reranking.

### What reranking improves

Reranking can:
- Improve the ordering of candidate passages.
- Push directly relevant evidence above loosely related passages.
- Reduce irrelevant context sent to the LLM when only the top few results are selected.
- Help the LLM produce more grounded answers when the correct evidence was retrieved but ranked too low.

### What reranking does not do

Reranking does not:
- Search the entire corpus by itself in a typical two-stage pipeline.
- Recover relevant passages missing from the candidate set.
- Guarantee factual or correct answers.
- Replace good chunking, metadata, filters, or the initial retriever.
- Automatically reduce total system cost or latency.

### The cost and trade-off

Reranking usually adds an extra model call or inference stage. It must evaluate multiple candidates, which can increase latency and computational cost. The impact depends on the model, candidate count, passage length, hardware, and whether inference is local or hosted.

| Approach | Main advantage | Main trade-off |
|---|---|---|
| Initial retrieval only | Faster and simpler | Relevant passages may rank too low. |
| Retrieval plus reranking | Often improves candidate ordering | Adds computation, latency, and potentially cost. |

Reranking is most useful when the first-stage retriever finds the correct passage but does not rank it highly enough. If initial retrieval is already precise and the final answers are good, reranking may add little value.

### Try it: Compare results on five weak questions

Choose five questions for which your assistant previously answered poorly. For each question, compare the top 3 passages before and after reranking.

| Question | Correct passage in initial top 3? | Correct passage in reranked top 3? | Did the answer improve? |
|---|---|---|---|
| Question 1 | Yes / No | Yes / No | Yes / No |
| Question 2 | Yes / No | Yes / No | Yes / No |
| Question 3 | Yes / No | Yes / No | Yes / No |
| Question 4 | Yes / No | Yes / No | Yes / No |
| Question 5 | Yes / No | Yes / No | Yes / No |

For a fair comparison:
- Use the same questions, document collection, and initial retrieval settings.
- Retrieve the same candidate set before reranking.
- Record the rank of the correct passage before and after reranking.
- Check the actual passages, not just their scores.
- Compare final answer quality and measure latency where possible.

Five questions are a useful debugging exercise, but they are too few to establish reliable overall performance. If reranking does not help, check whether the correct passage was present in the initial candidate set. If it was missing, improve the initial retrieval stage first.

## 6. Key Takeaways

- Reranking sorts an initial set of retrieved passages using a more detailed relevance assessment.
- A common two-stage pipeline retrieves broadly first, then reranks candidates and keeps the best few.
- Cross-encoder rerankers evaluate the question and each passage together.
- Reranking can improve relevance, but it cannot recover evidence absent from the candidate set.
- The extra model stage can increase latency and computational cost.
- Test reranking on real weak questions and compare passage rankings, final answers, and latency.

## 7. Common Misconceptions

**Misconception: Reranking searches the entire document collection again.**  
Correction: In a typical two-stage pipeline, the first retriever creates the candidate set. The reranker sorts only those candidates.

**Misconception: A high reranker score proves a passage is correct.**  
Correction: The score is a relevance signal, not a guarantee of factual accuracy or answer correctness.

**Misconception: Reranking always improves RAG.**  
Correction: It helps only when its ranking decisions improve the selected context. If initial retrieval is already precise, the benefit may be small.

**Misconception: Reranking is free because it uses fewer passages than the full corpus.**  
Correction: It still evaluates multiple query-passage pairs and adds processing time and computational cost.

## 8. Quick Revision

**1. What is reranking?**  
A second-stage process that reorders retrieved candidate passages by their relevance to a question.

**2. Why retrieve broadly before reranking?**  
To give the reranker several potentially useful candidates from which it can select the strongest evidence.

**3. What does a cross-encoder reranker do?**  
It processes the question and a candidate passage together to estimate their relevance.

**4. What is reranking's main limitation?**  
It cannot rank a relevant passage that the initial retriever never retrieved.

**5. What costs can reranking add?**  
Additional latency and computational cost, and potentially monetary cost when using a hosted model.
