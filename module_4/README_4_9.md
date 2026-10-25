# Keyword and Hybrid Search

## 1. What Is It?

**Keyword search** finds documents by matching words or terms in a query. It is useful when the exact wording matters, such as a course code, person’s name, product ID, error message, or technical phrase.

**BM25** (Best Matching 25) is a widely used keyword-ranking algorithm. It scores documents based on factors such as:
- How often query terms appear in a document.
- How rare or informative those terms are across the collection.
- How long the document is, with a length adjustment.

**Meaning-based search** (often called semantic search) retrieves passages based on similarity in meaning, commonly by comparing vector embeddings.

**Hybrid search** combines keyword search and meaning-based search, then merges their results into a single ranked list.

In short:

`Keyword search → matches important words`

`Meaning-based search → matches similar meaning`

`Hybrid search → combines both kinds of evidence`

## 2. Why Does It Matter?

Neither search method is best for every question.

Meaning-based search can find a passage that expresses the same idea using different wording. However, it may overlook an exact code, number, name, or phrase.

Keyword search is strong at exact terms, but it may miss a useful passage when the query and passage use different words to express the same idea.

Hybrid search helps cover both cases. It is especially useful for AI applications that search:
- University syllabi, course codes, and regulations.
- Technical documentation, API names, and error messages.
- Product catalogs, model numbers, and identifiers.
- Policies containing exact clauses or defined terms.
- Knowledge bases containing both natural-language explanations and precise labels.

## 3. How Does It Work?

### Step 1: Receive a query

For example:

`What is the attendance requirement for ENCT353?`

The query contains both a general concept (`attendance requirement`) and an exact course code (`ENCT353`).

### Step 2: Run keyword search

A BM25-based retriever scores passages according to their query-term matches and other relevance factors. It can be particularly effective when the exact course code appears in the correct passage.

BM25 does not simply count every matching word equally. Its ranking also considers term rarity and document length.

### Step 3: Run meaning-based search

A semantic retriever converts the query and stored passages into embeddings—numeric representations of their meaning—and compares their similarity.

This can retrieve a passage that says “students must be present for at least 80 percent of classes” even if the query uses the phrase “attendance requirement.”

### Step 4: Merge the rankings

The two retrievers may return different passages and use different scoring systems. Their raw scores are generally not directly comparable.

**Reciprocal Rank Fusion (RRF)** is one way to merge ranked lists using each result's position rather than comparing raw scores.

A common RRF formula is:

`RRF score(document) = Sum over rankings of 1 / (k + rank)`

Where:
- `document` is the passage being ranked.
- `rank` is its position in one result list, starting at 1.
- `k` is a constant that reduces the influence of the exact rank; a common value is 60.
- A document's contributions are added across all result lists in which it appears.

Example with `k = 60`:

- A passage ranked 1st in one list contributes `1 / 61`.
- A passage ranked 5th in one list contributes `1 / 65`.
- If the same passage appears in both lists, its contributions are added.

A passage ranked well by both methods can therefore receive a strong combined score. RRF does not guarantee the correct result; it combines rankings, so retrieval quality still depends on the underlying search methods and indexed content.

### Step 5: Return the combined results

The merged list is passed to the next stage of the RAG pipeline, where the application can select relevant passages and provide them to the language model as context.

`Question → Keyword search + Semantic search → RRF merge → Ranked passages → LLM answer`

## 4. Simple Example

Imagine a university knowledge base contains these passages:

| Passage | Content |
|---|---|
| A | `ENCT353 — Simulation and Modeling. Attendance must be at least 80%.` |
| B | `Students are expected to attend most scheduled classes to meet course participation requirements.` |
| C | `ENCT352 — Software Engineering. The course covers software design and testing.` |

Query:

`What is the attendance requirement for ENCT353?`

Possible behavior:

- **Keyword search:** Passage A is likely to rank highly because it contains `ENCT353` and `attendance`.
- **Meaning-based search:** Passage B may rank highly because it discusses attendance and participation, even without the course code. Passage A may also rank highly if its embedding captures the query's meaning.
- **Hybrid search:** The merged ranking can favor Passage A because it matches the exact course code and the attendance concept.

These are illustrative outcomes, not guaranteed rankings. Actual results depend on the retriever, query processing, document chunking, embedding model, and corpus.

### A small RRF calculation

Suppose Passage A ranks 1st in keyword search and 3rd in semantic search. Passage B ranks 4th in keyword search and 1st in semantic search. Use `k = 60`.

For Passage A:

`RRF(A) = 1 / (60 + 1) + 1 / (60 + 3)`

`RRF(A) ≈ 0.03227`

For Passage B:

`RRF(B) = 1 / (60 + 4) + 1 / (60 + 1)`

`RRF(B) ≈ 0.03202`

Passage A ranks slightly higher in this example because its combined positions are marginally stronger. The values are illustrative and show how RRF adds rank-based contributions rather than mixing incomparable raw scores.

## 5. Practical AI Engineering Application

In a Retrieval-Augmented Generation (RAG) application, hybrid search improves the chance of retrieving useful evidence before the language model generates an answer.

A typical workflow is:

1. **Prepare documents:** Extract text and split it into searchable passages (chunks).
2. **Index for keyword search:** Build a lexical index that supports BM25 retrieval.
3. **Index for semantic search:** Generate embeddings for the passages and store them in a vector index.
4. **Retrieve in parallel:** Run the user's query through both retrievers.
5. **Fuse results:** Apply RRF or another suitable ranking-fusion method.
6. **Use the top passages:** Pass selected results to the LLM as context.
7. **Evaluate:** Test whether the right evidence appears near the top of the combined list.

### What hybrid search does and does not do

**It does:**
- Combine exact-term matching with meaning-based retrieval.
- Help with queries containing names, codes, numbers, technical terms, or exact wording.
- Produce one ranked list from multiple retrievers.

**It does not:**
- Guarantee that the correct passage will be retrieved.
- Verify whether a passage is factually correct or up to date.
- Replace good document extraction, chunking, metadata, or evaluation.
- Prevent the LLM from generating an unsupported answer by itself. The RAG pipeline still needs suitable grounding and answer-generation instructions.

### Try it: Compare three search methods

Choose five questions that contain exact names or codes from your own document collection. For each question, run keyword search, meaning-based search, and hybrid search.

Record the results:

| Question | Correct passage found by keyword? | Correct passage found by semantic search? | Correct passage found by hybrid search? |
|---|---|---|---|
| What is the requirement for `ENCT353`? | Yes / No | Yes / No | Yes / No |
| What does policy `REG-04` say about attendance? | Yes / No | Yes / No | Yes / No |
| Which document mentions `SQLiteSaver`? | Yes / No | Yes / No | Yes / No |
| What is the deadline listed as `2026-11-15`? | Yes / No | Yes / No | Yes / No |
| What does error `E1027` mean? | Yes / No | Yes / No | Yes / No |

Replace these example queries with terms that actually exist in your corpus. For a fair comparison:
- Use the same document collection and equivalent retrieval limits.
- Decide in advance what counts as the correct passage.
- Check whether the correct passage appears in the top results, not just whether the answer sounds plausible.
- Record the rank of the correct passage, if found.
- Compare results across all five questions. Five questions are a useful small experiment, not enough to prove that one method is always better.

If hybrid search performs better on exact codes and names, that is evidence it helps your corpus with those query types. If it does not, inspect the keyword index, query processing, fusion settings, and document chunks before assuming hybrid search is ineffective.

## 6. Key Takeaways

- **BM25** is a keyword-ranking method that is useful for exact terms, names, codes, and phrases.
- **Semantic search** finds passages based on meaning, even when the wording differs.
- **Hybrid search** combines keyword and semantic retrieval to cover more query types.
- **Reciprocal Rank Fusion (RRF)** merges ranked lists using rank positions instead of directly comparing raw scores.
- Hybrid search is especially worth testing when users ask about identifiers, technical vocabulary, numbers, or exact wording.
- Evaluate retrieval by checking whether the correct passage appears near the top; hybrid search is not automatically better for every query.

## 7. Common Misconceptions

**Misconception: Semantic search makes keyword search unnecessary.**  
Correction: Semantic search can miss exact identifiers or phrases. Keyword matching remains useful when precise wording matters.

**Misconception: BM25 understands the meaning of a question.**  
Correction: BM25 is primarily a lexical ranking method. It scores term matches and related statistical factors; it does not understand meaning like an embedding-based retriever attempts to.

**Misconception: RRF compares the raw scores from both retrievers.**  
Correction: Standard RRF combines contributions based on rank positions. This is useful because BM25 scores and vector similarity scores can have different scales.

**Misconception: Hybrid search guarantees better answers.**  
Correction: It can improve retrieval, but results depend on the data, indexing, retrievers, fusion method, and evaluation setup. Better retrieval also does not guarantee a correct final answer.

## 8. Quick Revision

**1. What is BM25?**  
A keyword-based ranking algorithm that scores documents using term matches, term rarity, and document-length adjustment.

**2. What is the main advantage of semantic search?**  
It can retrieve passages with similar meaning even when they use different words.

**3. What is hybrid search?**  
A retrieval approach that combines keyword and semantic search results into one ranking.

**4. Why use Reciprocal Rank Fusion?**  
It merges ranked lists by position, avoiding direct comparison of raw scores from different retrieval systems.

**5. When should you test hybrid search?**  
When queries often contain exact names, course codes, IDs, numbers, technical terms, or phrases.
