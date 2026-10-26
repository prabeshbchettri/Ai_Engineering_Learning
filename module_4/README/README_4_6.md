# Vector Databases

## 1. What Is It?

A **vector database** stores vector embeddings and the information associated with them. An embedding is a list of numbers produced by an embedding model to represent the meaning of text.

In a retrieval system, documents are often split into smaller pieces called **passages** or **chunks**. Each passage can be stored with:
- Its embedding
- The original passage text
- Metadata, such as document name, section, document type, and date

When a user asks a question, the system embeds the question and searches for stored passage embeddings that are close to it. This is called **similarity search**.

Examples of vector storage options include PostgreSQL with the `pgvector` extension and vector database services. LangChain can help connect embedding models, document objects, and vector stores.

## 2. Why Does It Matter?

Vector databases are useful when an AI application needs to retrieve relevant information from a large collection of text.

Common uses include:
- **Retrieval-Augmented Generation (RAG):** retrieve relevant passages before asking an LLM to answer.
- **Document assistants:** search policies, manuals, reports, and class notes.
- **Semantic search:** find passages related in meaning, even when they do not use exactly the same words.
- **Filtered retrieval:** search within a particular document type, department, date range, or other metadata.

A vector database helps store and search embeddings efficiently. It does not generate the answer by itself; an LLM may use the retrieved passages to write an answer.

## 3. How Does It Work?

### Step 1: Split documents into passages

Long documents are divided into smaller chunks. Smaller passages make it easier to retrieve the specific section that answers a question.

### Step 2: Generate an embedding for each passage

An embedding model converts each passage into a numeric vector.

`Passage text → Embedding model → Passage embedding`

Passages with similar meanings often have embeddings that are close under a chosen distance or similarity measure. The exact quality depends on the embedding model and the text.

### Step 3: Store the passage, embedding, and metadata

A stored record might contain:

| Field | Example | Purpose |
|---|---|---|
| `id` | `passage-001` | Identifies the record |
| `text` | `Employees can request annual leave...` | Original passage |
| `embedding` | `[0.12, -0.08, ...]` | Supports semantic search |
| `document` | `employee-handbook.pdf` | Source document |
| `section` | `Leave Policy` | Location in the document |
| `document_type` | `policy` | Enables filtering |
| `date` | `2026-01-15` | Supports date-based filtering |

Metadata is not the same as an embedding. The embedding represents text for similarity search; metadata describes the passage and can be used to narrow the search.

### Step 4: Embed the user's question

The query is passed through the compatible embedding model to produce a query vector.

`User question → Same embedding model → Query embedding`

Use an embedding model compatible with the one used to index the passages. If the model or its embedding configuration changes, existing vectors may need to be regenerated.

### Step 5: Search for similar passages

The database compares the query embedding with stored embeddings using a distance or similarity measure, such as cosine distance or Euclidean distance. It returns the closest matches.

A simple conceptual workflow is:

`Question → Query embedding → Vector search → Relevant passages → LLM answer`

### Step 6: Apply metadata filters

A filter limits which records can be returned. For example, a question can search only passages whose `document_type` is `policy`, or only passages dated after a chosen date.

- **Without a filter:** search across all eligible passages.
- **With a filter:** search only passages matching the metadata conditions.

Filtering behavior and performance depend on the database, index, and query plan. A filter is not a replacement for semantic similarity; it restricts the set of records considered or returned.

### Step 7: Understand approximate nearest-neighbor search

Comparing a query with every stored vector is called an exhaustive or exact search. It can become expensive as the collection grows.

Many vector databases support **approximate nearest-neighbor (ANN) search**. ANN indexes use structures that help find likely close vectors without comparing the query with every record.

- **Benefit:** faster search for large collections.
- **Trade-off:** the results may miss some of the true nearest vectors.
- **Alternative:** exact search can be useful for small collections or when exact ranking is important.

The speed and recall depend on the index type, configuration, data, filters, and query. Approximate search is not automatically better for every dataset.

### Step 8: Keep stored passages current

When source documents change, keep the vector store synchronized:

1. **Add:** split and embed new content, then insert it.
2. **Update:** replace or re-index affected passages and their metadata.
3. **Delete:** remove passages that no longer exist in the source.
4. **Track identity:** use stable IDs or source identifiers to know which stored passages belong to a document.
5. **Avoid duplicates:** make ingestion repeatable so rerunning a pipeline does not create unnecessary duplicate records.

If a change affects only one document, it is often possible to reprocess that document rather than rebuild the entire collection. If the embedding model changes, however, the existing collection may need a broader re-embedding process.

## 4. Simple Example

Imagine a university assistant that stores these passages:

| Passage | Document type | Text |
|---|---|---|
| A | `policy` | `Students may apply for leave through the student portal.` |
| B | `lecture_note` | `Vector embeddings represent text as numeric vectors.` |
| C | `policy` | `Exam deferrals require approval from the department.` |

A student asks: **"How can I request leave?"**

1. The embedding model converts the question into a vector.
2. The vector database searches for passages with similar meaning.
3. Passage A may rank highly because it describes requesting leave.
4. If the search is filtered to `document_type = policy`, only policy passages are eligible.
5. The application can send the retrieved passage to an LLM to formulate an answer grounded in that text.

The filter changes the eligible documents; the vector similarity determines which eligible passages are most relevant.

### Minimal Python example: represent the search logic

This small example illustrates metadata filtering and ranking conceptually. It does **not** create embeddings or connect to a real vector database.

```python
passages = [
    {
        "text": "Students may apply for leave through the student portal.",
        "document_type": "policy",
        "similarity": 0.92,
    },
    {
        "text": "Vector embeddings represent text as numeric vectors.",
        "document_type": "lecture_note",
        "similarity": 0.61,
    },
    {
        "text": "Exam deferrals require department approval.",
        "document_type": "policy",
        "similarity": 0.48,
    },
]

def search_passages(passages, document_type=None, top_k=2):
    candidates = passages

    if document_type is not None:
        candidates = [
            passage
            for passage in candidates
            if passage["document_type"] == document_type
        ]

    ranked = sorted(
        candidates,
        key=lambda passage: passage["similarity"],
        reverse=True,
    )

    return ranked[:top_k]


print("Without filter:")
for result in search_passages(passages):
    print(result["text"])

print("\\nPolicy passages only:")
for result in search_passages(passages, document_type="policy"):
    print(result["text"])
```

**What this demonstrates:**
- `document_type` is metadata used to restrict the candidates.
- `similarity` is a placeholder score, not a score calculated from real embeddings.
- Sorting ranks the eligible passages, and `top_k` limits the number returned.

A real vector database calculates similarity or distance from embeddings and may use an approximate index for faster retrieval.

## 5. Practical AI Engineering Application

### Typical RAG ingestion and retrieval workflow

**Ingestion**

1. Load source documents.
2. Split documents into passages.
3. Attach metadata such as source ID, document type, section, and date.
4. Generate an embedding for each passage.
5. Store passage text, embedding, and metadata in a vector store such as PostgreSQL with `pgvector`.

**Retrieval**

1. Receive the user's question.
2. Embed the question with the compatible embedding model.
3. Search the vector store for the nearest passages.
4. Apply metadata filters when required.
5. Send the selected passages and the question to the LLM.
6. Generate an answer based on the retrieved context.

### Using LangChain

LangChain provides abstractions for document objects, embedding models, and vector stores. Exact setup and method names depend on the installed LangChain integration and package versions, so check the current documentation for the chosen store.

A LangChain document commonly contains:
- `page_content`: the passage text
- `metadata`: details such as document type, source, section, and date

The vector-store integration manages storing and searching embeddings, while the database persists the records. Metadata filtering syntax varies by integration.

### What vector databases do and do not do

| A vector database does | A vector database does not automatically do |
|---|---|
| Store embeddings and associated records | Understand text exactly as a human does |
| Retrieve semantically similar passages | Guarantee that retrieved passages are correct |
| Support metadata filters, depending on the store | Guarantee that a filter is supported in every syntax or index |
| Provide exact or approximate vector search options, depending on the system | Generate a final natural-language answer |
| Support insert, update, and delete operations | Keep itself synchronized with source documents unless the application implements that process |

### Try it

1. Load all your passages into the vector store.
2. Run one question without a metadata filter.
3. Run the same question with a filter such as `document_type = "policy"`.
4. Compare the returned passage text, source documents, and relevance.
5. Add or update a source document, re-ingest its affected passages, and verify that search reflects the change.
6. If your database supports ANN indexes, compare search speed and result quality with an exact-search configuration where practical.

Check the actual results rather than assuming filtering or approximate search always improves relevance. A restrictive filter can exclude the best answer if the metadata is missing or incorrect.

## 6. Key Takeaways

- A vector database stores embeddings alongside passage text and metadata.
- Embeddings support semantic similarity search; metadata supports filtering and source tracking.
- A query is embedded before it can be compared with stored passage embeddings.
- Approximate nearest-neighbor indexes can speed up large searches, sometimes at the cost of missing relevant neighbors.
- Add, update, and delete operations keep the vector store synchronized with changing documents.
- In a RAG system, the vector database retrieves context; the LLM uses that context to generate an answer.

## 7. Common Misconceptions

- **"A vector database stores only vectors."** It can also store passage text, IDs, and metadata, depending on the system and design.
- **"The closest passage is always the correct answer."** Similarity is a retrieval signal, not proof of correctness.
- **"Metadata filtering and vector search are the same."** Vector search ranks by embedding similarity; metadata filters restrict records using attributes.
- **"Approximate search always returns the exact nearest passages."** It is designed to find likely neighbors quickly and can miss some results.
- **"Updating a source file automatically updates its vectors."** Your ingestion pipeline must detect changes and update or delete affected records.

## 8. Quick Revision

**1. What is an embedding?**  
A numeric vector representing information such as the meaning of a passage.

**2. Why store metadata with each passage?**  
To identify its source and filter searches by attributes such as document type, section, or date.

**3. What is approximate nearest-neighbor search?**  
A method for finding likely close vectors faster than exhaustive comparison, with a possible loss in retrieval accuracy.

**4. What is the difference between vector search and metadata filtering?**  
Vector search ranks passages by embedding similarity; metadata filtering limits the eligible passages using their stored attributes.

**5. Do source document changes automatically update a vector database?**  
No. An ingestion or synchronization process must add, update, or delete the affected records.
