# Chunking

## 1. What Is It?

**Chunking** is the process of splitting a long document into smaller passages called *chunks*. In a RAG system, these chunks can be searched individually, and the most relevant ones can be provided to the language model when a question is asked.

A whole document may contain too much information to search precisely or fit into a prompt. Chunking makes it possible to retrieve a smaller, more relevant part.

**Simple idea:** split a document into passages that are small enough to search but large enough to preserve meaning.

## 2. Why Does It Matter?

Chunking affects what information a retrieval system can find and what context the language model receives.

- **Retrieval precision:** smaller chunks can focus on one specific topic.
- **Context:** larger chunks may include explanations or qualifications that help interpret a passage.
- **Prompt size:** sending a few relevant chunks can use less context than sending an entire document.
- **Answer quality:** a chunk that cuts off a definition, condition, or table row may lead to an incomplete answer.
- **Search usefulness:** chunks that preserve meaningful boundaries are easier to match to questions.

There is no single chunk size that works best for every collection. The best approach depends on the document structure and the questions users will ask.

## 3. How Does It Work?

### Common chunking approaches

#### 1. Fixed-size chunking

Split the text after a set number of characters or tokens, optionally with overlap.

**Example:** create a new chunk every 500 tokens.

**Advantages:**
- Simple to implement.
- Produces chunks with predictable sizes.
- Useful as a baseline for experimentation.

**Limitations:**
- Can split a sentence, explanation, or table in the middle.
- Does not understand the document's meaning or section structure.

#### 2. Sentence- or paragraph-based chunking

Split at sentence or paragraph boundaries rather than cutting at an arbitrary position.

**Advantages:**
- Often keeps sentences and paragraphs intact.
- Can preserve local meaning better than fixed character boundaries.

**Limitations:**
- Paragraphs can vary greatly in length.
- A very long paragraph may still need to be split.

#### 3. Section-based chunking

Use the document's own structure, such as headings, subheadings, and sections.

**Advantages:**
- Keeps related content together.
- Makes it easier to attach the correct section title to each chunk.
- Works well for manuals, reports, policies, and organized notes.

**Limitations:**
- A section may be too long to fit in one chunk.
- Documents with missing or inconsistent headings may need additional processing.

#### 4. Semantic chunking

Split text based on changes in meaning or topic rather than only on length or formatting.

**Advantages:**
- Can keep related ideas together.
- May produce useful chunks when topics change irregularly.

**Limitations:**
- Requires more processing and a way to estimate changes in meaning.
- Can be slower or more complex than simple splitting.
- Its results still need evaluation; it is not automatically better.

### Chunk size: small versus large

| Chunk size | Benefits | Risks |
|---|---|---|
| Small | More focused results; less unrelated text | May lose important context or split an explanation across chunks |
| Large | More surrounding context; fewer broken explanations | May include irrelevant material and make retrieval less precise |

Think about a question such as: **"When are late assignments accepted?"**

A tiny chunk containing only `Late assignments require approval.` may be insufficient if the next sentence explains who can approve them. A much larger chunk containing an entire chapter may include that answer but also lots of unrelated information.

The goal is not to make every chunk as small as possible. It is to make each chunk useful for answering likely questions.

### Overlap: keeping neighboring context

**Overlap** means repeating a small portion of text at the end of one chunk and the beginning of the next.

For example, if a document is split into chunks of 100 tokens with 15 tokens of overlap, neighboring chunks share some text. This can help preserve an idea that crosses a chunk boundary.

Overlap can help when:
- A definition continues into the next sentence.
- A condition or explanation spans a boundary.
- A paragraph is split because it exceeds the desired size.

Too much overlap creates repeated content, increases storage and processing, and may cause search results to contain nearly identical passages. Use enough overlap to reduce broken context, but not so much that most chunks repeat one another.

### Keep metadata attached to every chunk

A chunk should not become anonymous text after splitting. Attach useful metadata so the system can identify where it came from.

For example:

```python
chunk = {
    "page_content": "Late submissions require approval from the instructor.",
    "metadata": {
        "document_title": "University Assignment Policy",
        "section": "Late Submissions",
        "source": "assignment_policy.pdf",
        "page": 4,
        "chunk_id": "assignment_policy_004"
    }
}
```

This is a simplified illustration of a document chunk's structure. In LangChain, document objects commonly use `page_content` and `metadata`.

Metadata helps with:
- Identifying the document and section.
- Filtering search results by source or topic.
- Showing citations or source references.
- Tracking chunks when a document is updated.

### A practical chunking workflow

1. Load and clean the document.
2. Identify its structure, such as headings, paragraphs, lists, and tables.
3. Choose a splitting method suitable for that structure.
4. Set a target chunk size and, if needed, a small overlap.
5. Attach document and section metadata to each chunk.
6. Inspect sample chunks for missing context, broken sentences, or repeated text.
7. Test retrieval with realistic questions and adjust the settings.

Chunking is not a one-time universal setting. It is a design choice that should be tested against the documents and questions in your application.

## 4. Simple Example

Imagine the source document says:

> Late assignments are accepted only with instructor approval. Students must contact the instructor before submitting late work. Requests are reviewed individually.

### Fixed-size split

If the split happens in the middle of the text, one chunk might contain:

```text
Late assignments are accepted only with instructor approval. Students must contact
```

The next chunk might begin:

```text
the instructor before submitting late work. Requests are reviewed individually.
```

Each chunk contains useful text, but the split may separate connected ideas.

### Paragraph- or section-based split

A structure-aware chunk could keep the full explanation together:

```text
Section: Late Assignments

Late assignments are accepted only with instructor approval. Students must contact
the instructor before submitting late work. Requests are reviewed individually.
```

This chunk gives a reader more context without needing the rest of the document.

### What should you choose?

If the document has clear headings, section-based chunking is a sensible starting point. If it is a long stream of text with no reliable structure, fixed-size or sentence-based splitting may be more practical. In either case, inspect the chunks and test them with questions users are likely to ask.

## 5. Practical AI Engineering Application

For a beginner RAG project, start with a simple, repeatable experiment:

- Select one document that represents the kind of material your application will handle.
- Split it using a fixed-size method.
- Split the same document using headings or sections.
- Keep the target size reasonably comparable where possible.
- Attach title, section, source, and chunk ID metadata.
- Read sample chunks to see whether they make sense independently.
- Ask realistic questions and check which approach retrieves the most useful passages.

Avoid assuming that one chunking strategy is best for every file. A policy document with clear sections may benefit from section-aware chunking, while an unstructured transcript may need sentence-based or fixed-size splitting.

## 6. Try It: Compare Two Chunking Methods

Choose one document and split it in two ways:

1. **Fixed-size chunking:** use a target size and a small overlap.
2. **Section-based chunking:** split according to headings and sections, splitting unusually long sections further if necessary.

Read five chunks from each method. For every chunk, ask:

- Can a reader understand it without seeing the whole document?
- Does it contain a complete idea or cut off a sentence or explanation?
- Is there too much unrelated information?
- Is the document title and section attached?
- Would this chunk help answer a realistic question about the document?

Record your observations:

| Check | Fixed-size chunks | Section-based chunks |
|---|---|---|
| Most chunks make sense on their own? | | |
| Sentences or explanations cut off? | | |
| Too much unrelated text? | | |
| Useful section metadata present? | | |
| Best fit for the document? | | |

Choose based on the results, not just on which method is easier to implement.

## 7. Common Misconceptions

- **"Smaller chunks are always better."** No. Small chunks can omit qualifications and surrounding context.
- **"Larger chunks are always better."** No. Large chunks may include noise and reduce retrieval precision.
- **"Overlap fixes every boundary problem."** No. It can help preserve nearby context, but it cannot repair poor document extraction or badly chosen boundaries.
- **"All documents should use the same chunk size."** Not necessarily. Policies, books, tables, and transcripts have different structures.
- **"Chunk text is enough on its own."** Metadata is important for source tracking, filtering, and citations.
- **"Semantic chunking is automatically the best method."** No. It can add complexity and should be compared with simpler methods.

## 8. Key Takeaways

- Chunking splits long documents into smaller passages that can be searched and supplied to a model.
- Common approaches include fixed-size, sentence/paragraph-based, section-based, and semantic chunking.
- Small chunks are focused but may lose context; large chunks carry context but can add noise.
- A little overlap can reduce context loss at boundaries, while too much overlap creates repetition.
- Attach document title, section, source, and other useful metadata to each chunk.
- Evaluate chunking using real questions and inspect the passages returned by retrieval.

## 9. Quick Revision

**Question:** What is chunking?

**Answer:** Splitting a long document into smaller passages that can be searched and used as context.

**Question:** Name four chunking approaches.

**Answer:** Fixed-size, sentence/paragraph-based, section-based, and semantic chunking.

**Question:** What is the main trade-off between small and large chunks?

**Answer:** Small chunks can improve focus but lose context; large chunks preserve more context but may include irrelevant information.

**Question:** What is overlap?

**Answer:** Repeating a small amount of text between neighboring chunks to help preserve context across split boundaries.

**Question:** Why attach metadata to every chunk?

**Answer:** To preserve its source and section, enable filtering, support citations, and track updates.

**Learning outcome:** You should be able to choose a chunking approach that fits your documents and the questions people will ask about them.
