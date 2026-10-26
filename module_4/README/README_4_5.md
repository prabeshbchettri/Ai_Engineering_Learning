# Embeddings and Semantic Search

## 1. What Is It?

An **embedding** is a list of numbers (a vector) that represents information such as a sentence, paragraph, image, or question. An embedding model converts the input into this numerical representation so that items with related meanings can often be placed near each other in the vector space.

**Semantic search** uses these representations to find passages that are similar in meaning to a question, rather than matching only the exact words.

**Simple idea:** convert text into vectors, then search for vectors that are close to the question's vector.

## 2. Why Does It Matter?

People often ask questions using different words from those used in a document. A keyword search may miss a passage if the wording does not match, while semantic search can sometimes find it because the meaning is similar.

For example, a document might say, "Learners must hand in their coursework before the deadline." A user might ask, "When do I need to submit my assignment?" The words differ, but the meaning is related.

Embeddings help AI applications:
- Search documents by meaning, not only exact keywords.
- Find relevant passages for a RAG pipeline.
- Group similar text or identify related items.
- Compare questions and passages using a mathematical similarity score.

Semantic search is not perfect. Exact names, codes, numbers, rare terms, and highly specialized wording may need keyword search or a hybrid approach that combines semantic and lexical search.

## 3. How Does It Work?

### Step 1: Convert passages into embeddings

An embedding model processes each passage and returns a vector of numbers.

For illustration, a model might represent a passage with a tiny vector such as:

```text
"Reset your password" -> [0.21, 0.74, -0.10]
```

Real embeddings typically contain many more dimensions. The three numbers above are only a simplified example; they are not a real model output.

### Step 2: Convert the question into an embedding

The search question is passed through the compatible embedding model too.

```text
"How do I change my login password?" -> [0.19, 0.70, -0.08]
```

Because the example question and passage have similar meanings, their vectors might be close together.

### Step 3: Compare the vectors

A similarity measure estimates how closely two vectors are related. A common choice is **cosine similarity**, which compares the direction of two vectors.

For two vectors A and B:

```text
cosine similarity = (A dot B) / (length(A) * length(B))
```

Here, `A dot B` means multiply corresponding values and add the products. `length(A)` and `length(B)` are the vector lengths.

Cosine similarity is often closer to 1 for vectors pointing in similar directions, around 0 for orthogonal vectors, and closer to -1 for vectors pointing in opposite directions. The exact interpretation depends on the model and its embedding space. Some systems use other metrics, such as dot product or Euclidean distance.

### Step 4: Return the closest passages

The system compares the question vector with passage vectors and returns the passages with the highest similarity scores (or the smallest distances, when using a distance metric).

A simplified search flow:

1. Split documents into passages.
2. Create an embedding for each passage.
3. Store each vector with its text and metadata.
4. Embed the user's question.
5. compare the question vector with stored passage vectors.
6. Return the most relevant matches.

A vector database can store embeddings, search large collections efficiently, and preserve metadata. But you can first implement the basic comparison yourself to understand what the database is doing.

### Build semantic search by hand

You do not need a vector database for a tiny example. You can store a few passages and their embeddings in a list, then calculate a similarity score for each passage.

A simple conceptual Python outline:

```python
passages = [
    "Reset your account password in Settings.",
    "The library closes at 6 PM.",
    "Change your login credentials from the security page."
]

# 1. Use an embedding model to embed each passage.
# 2. Embed the user's question with the same model.
# 3. Calculate similarity between the question and each passage.
# 4. Sort by similarity and inspect the top results.
```

The comments are intentional: the embedding function and similarity calculation depend on the model and library you choose. The important learning task is to see that every passage and the question are represented in the same vector space before they are compared.

## 4. Choosing an Embedding Model

An embedding model should be evaluated against the text and questions your application actually handles.

Consider these factors:

| Factor | What to check |
|---|---|
| Retrieval quality | Does it return passages that truly answer your test questions? |
| Cost | Is there a charge for embedding inputs, and what will your document volume cost? |
| Speed | How quickly can it embed documents and user questions? |
| Language support | Does it work well with the languages and scripts your users use? |
| Model size and deployment | Can you run it locally, or do you need an external API? |
| Limits and dimensions | What input length, throughput, and vector dimensions does it support? |

### Hindi and mixed Hindi-English text

If users may ask questions in Hindi, English, or mixed Hindi-English (often called Hinglish), test the model using that exact kind of content. Multilingual support claims alone do not guarantee good results for every script, spelling style, or code-switching pattern.

Build a small test set with:
- Questions written in English.
- Questions written in Hindi.
- Mixed Hindi-English questions.
- Passages that use different words from the questions.
- Exact names, codes, and numbers.

Compare the retrieved results rather than choosing a model based only on popularity or benchmark scores.

## 5. Do Not Mix Embedding Models

**Passages and queries must use compatible embeddings from the same embedding model and configuration.**

Different models learn different vector spaces. A vector from one model cannot generally be compared meaningfully with a vector from another model, even if the vectors have the same number of dimensions.

If you change the embedding model, you usually need to:
1. Re-embed all stored passages with the new model.
2. Rebuild or update the vector index.
3. Ensure new user questions use that same model.
4. Re-test retrieval quality.

Do not assume that equal vector dimensions mean two models' embeddings are compatible. Record the model name and relevant configuration with your index so you know how it was built.

## 6. Where Semantic Search Fails

Semantic search is strong at matching related meanings, but it can be weaker when the exact character sequence matters.

Common challenges include:

- **Exact names:** a rare person's or organization’s name may not retrieve reliably.
- **Product codes and IDs:** `AB-1200` and `AB-120O` may look similar but identify different products.
- **Numbers and dates:** a semantically similar passage may still contain the wrong amount, version, or deadline.
- **Rare technical terms:** uncommon terminology may be poorly represented.
- **Negation and precise conditions:** passages with similar wording may differ in an important condition, such as "allowed" versus "not allowed."
- **Cross-language variation:** multilingual or mixed-language queries may not match as well as expected.

For these cases, consider **hybrid search**, which combines semantic similarity with keyword or exact-match retrieval. You can also apply metadata filters for known fields such as product ID, document date, or category.

Always check whether a retrieved passage actually answers the question. Similarity means relatedness according to the model, not guaranteed correctness.

## 7. Simple Example

Imagine these three passages:

1. "Reset your account password in Settings."
2. "The library closes at 6 PM."
3. "Change your login credentials from the security page."

The user asks: **"How can I update the password I use to sign in?"**

A keyword search might miss one of the password passages if the exact terms do not overlap. Semantic search converts the question and passages into vectors and may rank passages 1 and 3 highly because they discuss the same task.

Now consider the question: **"Which product has code AB-1200?"** A semantic search may find a passage about a similar product, but it might not reliably distinguish `AB-1200` from a nearby code. Exact keyword search or a database lookup is safer for that part of the task.

## 8. Try It: Compare Meaning-Based and Exact Search

Prepare a small collection of passages and test two questions:

1. **Meaning-based question:** phrase a question in your own words without copying the passage's wording.
2. **Exact-match question:** include a precise product name, ID, or code that appears in one passage.

For each question:
- Embed every passage using one embedding model.
- Embed the question using that same model.
- Rank passages by similarity.
- Record the top results and inspect their actual content.
- Compare the semantic results with a simple keyword search.

Use a table to record your findings:

| Test | Expected passage found? | Were top results relevant? | What did you learn? |
|---|---|---|---|
| Question phrased in your own words | | | |
| Question with an exact product name or code | | | |

Try additional wording variations, especially in the languages your users may use. For a small hand-built exercise, calculate similarities directly; a vector database is not necessary yet.

## 9. Common Misconceptions

- **"An embedding is the meaning itself."** It is a numerical representation learned by a model; it does not capture every detail perfectly.
- **"The closest vector must be the correct answer."** Similarity is a ranking signal, not a guarantee.
- **"Semantic search replaces keyword search."** It can complement keyword search, especially for exact names, codes, and numbers.
- **"Any two embedding vectors can be compared."** Vectors generally need to come from the same compatible embedding space.
- **"The best embedding model is always the most popular one."** The best choice depends on your actual documents, languages, questions, costs, and latency needs.

## 10. Key Takeaways

- Embeddings turn text into numerical vectors that represent learned features of meaning.
- Semantic search embeds both passages and the question, then ranks passages by similarity or distance.
- A small hand-built search helps you understand vector comparison before adding a vector database.
- Compare embedding models using retrieval quality, cost, speed, deployment needs, and language support.
- Use compatible embeddings for both stored passages and queries; changing models usually requires re-embedding the collection.
- Semantic search may struggle with exact names, product codes, numbers, and rare terms; hybrid search or exact lookup can help.

## 11. Quick Revision

**Question:** What is an embedding?

**Answer:** A list of numbers representing text or another input in a model's vector space.

**Question:** How does semantic search work?

**Answer:** It embeds passages and the user's question, compares their vectors, and returns the closest passages.

**Question:** Why should you not mix embeddings from unrelated models?

**Answer:** Different models generally create different vector spaces, so their vectors are not directly comparable in a meaningful way.

**Question:** What should you evaluate when choosing an embedding model?

**Answer:** Retrieval quality, cost, speed, language support, deployment requirements, and input limits.

**Question:** When can semantic search struggle?

**Answer:** With exact names, product codes, numbers, rare terms, and other cases where precise matching matters.

**Learning outcome:** You should be able to explain semantic search, compare embedding models, and identify questions that may need keyword or exact-match retrieval.
