# Measuring Retrieval

## 1. What Is It?

**Retrieval** is the search step in an AI application that finds relevant passages from a collection of documents. In a retrieval-augmented generation (RAG) system, the retrieved passages are then provided to the language model to help it answer a question.

**Retrieval evaluation** measures whether the search system finds useful evidence for a question. It is important to test retrieval separately from answer generation: if the right passage is missing from the search results, a prompt alone cannot reliably make the model use that passage.

## 2. Why Does It Matter?

A RAG answer depends partly on the evidence retrieved for it. If search returns irrelevant passages or misses the passage containing the answer, the model may give an incomplete answer, make unsupported claims, or be unable to answer.

Measuring retrieval helps you:

- **Find search problems directly:** Distinguish retrieval failures from problems in the model's generated answer.
- **Compare search approaches:** Check whether meaning-based search, hybrid search, or reranking finds better evidence.
- **Tune document chunking:** Find out whether chunk sizes and boundaries help or hurt search quality.
- **Choose embeddings and query techniques:** Compare alternatives using the same questions.
- **Avoid guessing:** Use a test set and metrics instead of relying on a few impressive examples.

Good retrieval does not guarantee a good final answer, but poor retrieval can prevent the model from producing one.

## 3. How Does It Work?

### Step 1: Create a retrieval test set

For each test question, identify the passage or passages that contain the information needed to answer it. These are the **relevant passages** or **relevant evidence** for that question.

Example:

| Question | Relevant passage |
|---|---|
| When is the scholarship application due? | Passage P12: “Applications must be submitted by 15 May.” |
| Which documents are required? | Passage P18: “Applicants must provide an academic transcript and proof of enrollment.” |

A question can have more than one relevant passage. Record all passages that count as relevant before comparing search methods.

### Step 2: Run retrieval

Send each question to the search system and record the ranked results. The ranking matters because the first few results are usually the passages most likely to be given to the model.

For each question, check whether the relevant passage appears among the top results.

### Step 3: Measure Recall@k

**Recall@k** measures how often retrieval finds the relevant evidence within the first `k` results.

For a simple test where each question has one required passage:

`Recall@k = Number of questions with the required passage in the top k results / Total number of questions`

Example: You test 20 questions. For 16 questions, the required passage appears among the top 5 results.

`Recall@5 = 16 / 20 = 0.80 = 80%`

This means the search system found the required passage in the top five results for 80% of the test questions.

When a question has multiple relevant passages, the calculation depends on the chosen definition. A common version averages, across questions, the fraction of relevant passages retrieved in the top `k` results:

`Recall@k for one question = Relevant passages in the top k / Total relevant passages for that question`

State which definition you use so results can be compared fairly.

### Step 4: Measure precision

**Precision** measures how much of the retrieved material is relevant rather than noise.

For a set of retrieved passages:

`Precision = Number of retrieved passages judged relevant / Total number of retrieved passages`

Example: A search returns 10 passages, and 6 are judged relevant.

`Precision = 6 / 10 = 0.60 = 60%`

Higher precision means fewer irrelevant passages are being returned. This matters because irrelevant context can distract the model or introduce conflicting information.

Precision and recall describe different things:

- **Recall:** Did the search find the evidence it needed to find?
- **Precision:** How much of the returned evidence was useful?

A system can have high recall but low precision if it finds the right passage among many irrelevant ones. It can have high precision but low recall if its few results are useful but it misses other needed evidence.

### Step 5: Compare approaches fairly

Compare retrieval options on the **same test questions**, with the same relevance labels and the same evaluation procedure.

Useful comparisons include:

- **Chunk size and overlap:** How documents are divided into searchable passages.
- **Embedding models:** How text is converted into vectors for meaning-based search.
- **Search type:** Meaning-based (dense vector) search versus keyword search or hybrid search.
- **Reranking:** Reordering initial search results using a second relevance-scoring step.
- **Query techniques:** Changes to the search query, such as rewriting it to make the user's intent clearer.

Change one major variable at a time where practical. Otherwise, it may be difficult to know which change caused a metric to improve or decline.

## 4. Simple Example

Suppose you have 20 test questions and have marked the passage that should answer each question. You compare three retrieval pipelines using Recall@5.

| Retrieval approach | Questions with required passage in top 5 | Recall@5 |
|---|---:|---:|
| Meaning-based search | 13 out of 20 | 65% |
| Hybrid search | 16 out of 20 | 80% |
| Hybrid search with reranking | 18 out of 20 | 90% |

These are illustrative numbers, not benchmark results. In this example, hybrid search finds the required passage for three more questions than meaning-based search, and reranking finds it for two more than hybrid search alone.

Before deciding that reranking is better for your application, also inspect the failures and check precision. A higher Recall@5 does not automatically mean the top five passages are all useful, or that the final generated answers are correct. Measure the approaches on your own test set.

## 5. Practical AI Engineering Application

In a RAG pipeline, retrieval evaluation should be a separate stage from evaluating the generated answer.

`Question → Retriever → Ranked passages → Retrieval metrics → LLM answer → Answer evaluation`

A practical workflow is:

1. Build a fixed set of representative questions.
2. Mark the relevant passage or passages for each question.
3. Run each retrieval configuration against the same questions.
4. Save the ranked results and calculate Recall@5.
5. Judge whether retrieved passages are relevant and calculate precision using a clearly defined method.
6. Inspect questions where the required evidence was missed.
7. Change a retrieval setting and run the same test set again.
8. Compare the results, then separately evaluate the final answers.

For your exercise, compare:

- Meaning-based search.
- Hybrid search.
- Hybrid search with reranking.

Keep the question set and relevance labels unchanged across all three approaches. Record both the metric and a few examples of successes and failures.

### Try it

1. Choose a set of test questions from your own documents.
2. Label the passage or passages needed to answer each question.
3. Run meaning-based search and calculate Recall@5.
4. Run hybrid search and calculate Recall@5.
5. Run hybrid search with reranking and calculate Recall@5.
6. Compare the results and inspect questions where each approach missed the evidence.
7. Check precision as well, so you do not focus only on finding the right passage while ignoring irrelevant results.

## 6. Key Takeaways

- Evaluate retrieval separately because the answer generator cannot reliably use evidence that search never returned.
- Recall@k measures whether relevant evidence appears within the top `k` search results.
- Precision measures the proportion of retrieved passages that are relevant.
- Recall and precision capture different aspects of retrieval quality; neither tells the whole story alone.
- Compare chunking, embeddings, search types, reranking, and query techniques using the same test set.
- Inspect individual failures as well as metric values.
- Better retrieval can support better answers, but it does not guarantee correct generation.

## 7. Common Misconceptions

### “If the final answer is wrong, the LLM must be the problem.”

The search step may have failed to retrieve the necessary evidence. Evaluate retrieval and answer generation separately to identify the cause.

### “Higher Recall@5 means every retrieved passage is useful.”

Recall@5 only checks whether relevant evidence appears in the top five results under your chosen definition. It does not measure how much irrelevant content is present.

### “Precision and recall mean the same thing.”

Recall measures how much relevant evidence was found. Precision measures how much of the retrieved material was relevant.

### “A method that wins on a few questions is definitely better.”

A few examples may be unrepresentative. Compare methods on the same labeled test set, review failures, and consider the needs of your application.

## 8. Quick Revision

**Q1. Why should retrieval be evaluated separately from generation?**  
Because missing evidence can cause a poor answer even when the prompt and model are reasonable.

**Q2. What does Recall@5 measure?**  
Whether the relevant passage or passages are found within the first five results, using a clearly defined recall calculation.

**Q3. What does precision measure?**  
The proportion of retrieved passages that are judged relevant.

**Q4. How can you compare meaning-based search, hybrid search, and reranking fairly?**  
Run them on the same test questions with the same relevance labels and evaluation method.

**Q5. Does high retrieval recall guarantee a correct final answer?**  
No. The model can still misunderstand, omit, or misuse the retrieved evidence.
