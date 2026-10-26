# Smarter Chunks and Filters

## 1. What Is It?

In Retrieval-Augmented Generation (RAG), a search system retrieves pieces of documents and sends relevant information to a language model (LLM). The way documents are split, described, and filtered affects what the system can find.

**Chunking** means splitting a document into smaller passages called chunks so they can be indexed and searched.

**Smarter chunking and filtering** improve retrieval by:
- Searching precise chunks while preserving the larger section needed to answer a question.
- Adding document and section information to each chunk.
- Keeping tables and structured content understandable.
- Extracting useful search filters from a user's question, such as product name, date, or document type.

The goal is not simply to retrieve a passage that looks relevant. It is to retrieve the right evidence and give the LLM enough context to use it correctly.

## 2. Why Does It Matter?

A chunk that is too large may contain lots of unrelated text, making retrieval less precise. A chunk that is too small may lose important details, such as what a pronoun refers to, which course a rule applies to, or which column a table value belongs to.

Poorly handled tables can become confusing text. Missing metadata can make a relevant passage difficult to identify. Searching without filters can return documents about the wrong product, date, or document type.

Smarter chunking and filtering are useful for:
- University regulations, course syllabi, and lecture notes.
- Product manuals, catalogs, and technical documentation.
- Policies and reports organized by section and date.
- Tables containing prices, schedules, measurements, or comparisons.
- Knowledge bases with many versions or types of documents.

## 3. How Does It Work?

### Step 1: Split documents into useful chunks

Split long documents into passages small enough to search precisely, while keeping related ideas together.

For example, a section about attendance rules should ideally remain together rather than being split so that the percentage is separated from the rule it describes.

There is no single ideal chunk size for every dataset. The right size depends on the document structure, the questions users ask, and the retrieval system.

### Step 2: Search small, send big

A useful pattern is **small-to-big retrieval**:

1. Split a document into small, focused chunks for indexing.
2. Search those chunks to find a precise match.
3. Link each small chunk to its parent section or larger surrounding passage.
4. Return the relevant larger section, or enough surrounding text, to the LLM.

Example:

- Small searchable chunk: `Late submissions lose 10% per day.`
- Parent context: `Assignment Policy — For ENCT352, assignments submitted after the deadline lose 10% of the available marks per day, up to the stated course limit.`

The small chunk can match the query precisely, while the larger context clarifies which course and policy the rule applies to.

This approach is sometimes called parent-document or parent-child retrieval. Implementations vary: the retrieved child chunk may point to a parent section, a neighboring window of text, or another context unit.

### Step 3: Add context to each chunk

Add a short, accurate context line that identifies where the chunk came from.

For example:

```text
Document: ENCT352 Software Engineering Syllabus
Section: Assessment and Assignment Policy
Content: Late submissions lose 10% of the available marks per day.
```

This context can help retrieval when the passage alone is vague. It can also help the LLM interpret the retrieved evidence.

Useful metadata may include:
- Document title or ID.
- Section heading.
- Course, product, or department.
- Publication date or version.
- Document type, such as syllabus, policy, manual, or report.

Keep metadata accurate and concise. Do not add labels or facts that are not supported by the source document.

### Step 4: Preserve tables and structured content

Tables often lose meaning when extracted as plain text. A value such as `Rs. 500` is not useful if the associated product or column heading disappears.

Whenever practical:
- Keep small, meaningful tables together in one chunk.
- Preserve column headers and row labels.
- Convert complex tables into clear text descriptions or structured records.
- Include units, dates, and relevant footnotes.
- Keep a reference to the source table or section.

Example table:

| Product | Price | Effective date |
|---|---:|---|
| Model A | Rs. 500 | 2026-10-01 |
| Model B | Rs. 750 | 2026-10-01 |

A readable text representation could be:

```text
Table: Product prices effective 2026-10-01.
Model A costs Rs. 500.
Model B costs Rs. 750.
```

This representation preserves the relationship between each product and its price. For large tables, it may be better to create several row-based chunks that repeat the table title and column meanings, or to store rows as structured records that can be queried directly.

Do not blindly split a table across chunks without retaining its headers and relationships.

### Step 5: Extract filters from the question

A user's question often includes clues about which documents should be searched.

For example:

`What does the 2025 installation manual say about Model X?`

Potential filters:
- Product: `Model X`
- Document type: `installation manual`
- Date or version: `2025`

The application can extract these constraints using rules, a language model, or a structured query parser, then apply them to document metadata before or during retrieval.

A simplified workflow is:

```text
User question
    ↓
Extract search terms and filters
    ↓
Apply filters to document metadata
    ↓
Search eligible chunks
    ↓
Return relevant passages with context
    ↓
Generate an answer
```

Filters restrict which documents are eligible for retrieval. Search then ranks the eligible content by relevance. Filters only work when the metadata exists, is accurate, and uses consistent values.

If a filter is uncertain or too restrictive, the application should consider asking the user to clarify or retrying with a broader search. It should not silently invent missing metadata.

## 4. Simple Example

Imagine a product knowledge base contains manuals and price tables for several products.

The user asks:

`What was the price of Model A in the price list dated 2026-10-01?`

The system has these records:

| Document | Type | Date | Content |
|---|---|---|---|
| Price List 2026-10-01 | Price list | 2026-10-01 | Model A costs Rs. 500. |
| Price List 2026-09-01 | Price list | 2026-09-01 | Model A costs Rs. 480. |
| Model A Installation Manual | Manual | 2026-10-01 | Instructions for installing Model A. |

### Plain search

The system searches all chunks for terms such as `Model A` and `price`. It may find both price lists, and possibly other documents mentioning the product. The correct result might appear, but older or less relevant records can compete for attention.

### Search with extracted filters

The system identifies:

```text
Product: Model A
Document type: Price list
Date: 2026-10-01
```

It filters the collection to eligible documents and then searches their content. The October price list is the appropriate source for the question.

### Add context to the retrieved chunk

Instead of returning only:

```text
Model A costs Rs. 500.
```

Return:

```text
Document: Price List 2026-10-01
Document type: Price list
Effective date: 2026-10-01
Table: Product prices
Content: Model A costs Rs. 500.
```

The added context makes the product, date, and source clear to the LLM.

This is a simplified example. Actual results depend on the quality of the metadata, how filters are extracted, and how the search system applies them.

## 5. Practical AI Engineering Application

A robust RAG ingestion and retrieval workflow can use these practices:

1. **Parse documents:** Extract text, headings, tables, dates, and document identifiers.
2. **Create structured chunks:** Split text along meaningful boundaries such as headings and paragraphs.
3. **Attach metadata:** Store document ID, title, section, type, date, and other useful attributes.
4. **Preserve parent relationships:** Keep a mapping from each searchable chunk to its larger section or context window.
5. **Index the content:** Store chunk text for keyword search and/or embeddings for semantic search, along with metadata.
6. **Interpret the question:** Extract relevant terms and constraints, such as product, date range, course code, or document type.
7. **Filter and retrieve:** Restrict the candidate set using reliable metadata, then rank the eligible chunks.
8. **Expand context:** Fetch the parent section or neighboring content when needed.
9. **Generate and evaluate:** Give the LLM the relevant context and test whether it answers correctly with the right evidence.

### What these techniques do and do not do

**They do:**
- Improve the balance between precise retrieval and sufficient answer context.
- Make isolated passages easier to interpret.
- Preserve relationships in tables and structured data.
- Narrow searches using explicit constraints in the question.

**They do not:**
- Guarantee correct retrieval or answers.
- Replace accurate document parsing and metadata.
- Make an incorrect filter safe; an overly restrictive filter can hide the right document.
- Mean every chunk should be as small as possible or every table must be converted to prose.
- Replace direct database queries when the task requires exact calculations or structured operations over tabular data.

### Try it: Compare plain search with filtered search

Choose three questions that mention a specific product, date, or document type. Use a collection where the relevant metadata is available.

| Question | Plain search: correct source found? | Filtered search: correct source found? | Notes |
|---|---|---|---|
| What is the price of Model A in the 2026-10-01 price list? | Yes / No | Yes / No | |
| What does the 2025 installation manual say about Model X? | Yes / No | Yes / No | |
| Which policy dated 2026-09-01 describes attendance rules? | Yes / No | Yes / No | |

Replace the examples with questions suited to your own corpus. For each method:
- Keep the underlying document collection the same.
- Check whether the correct source appears in the retrieved results.
- Record the rank of the correct passage, if found.
- Inspect whether filters excluded relevant documents or removed irrelevant ones.
- Check whether the final context includes enough surrounding information to answer the question.

Three questions are a small practical experiment, not proof that filtered search always performs better. A filter helps only when it accurately captures the user's intent and the document metadata supports it.

## 6. Key Takeaways

- Small, focused chunks can improve search precision, while returning a larger parent section can preserve the context needed by the LLM.
- Add accurate document titles, section names, dates, and other useful metadata to chunks.
- Preserve table headers, row labels, units, and relationships when extracting structured content.
- Extract filters such as product, date, and document type from the user's question when appropriate.
- Apply filters carefully: incorrect or overly restrictive filters can hide the right evidence.
- Evaluate both retrieval accuracy and whether the returned context is sufficient to answer the question.

## 7. Common Misconceptions

**Misconception: Smaller chunks are always better.**  
Correction: Small chunks can be precise, but they may lose context. Choose chunk boundaries based on document structure and real questions, and consider retrieving a larger parent section.

**Misconception: Adding metadata guarantees retrieval quality.**  
Correction: Metadata helps only when it is accurate, relevant, indexed or filterable, and used appropriately.

**Misconception: Converting every table into plain sentences is always best.**  
Correction: Text descriptions can help language models, but large or calculation-heavy tables may be better represented as structured records or queried directly.

**Misconception: Filters always improve search.**  
Correction: Correct filters can remove irrelevant documents. Incorrect filters can exclude the right source, so uncertain constraints should be handled carefully.

## 8. Quick Revision

**1. What is chunking?**  
Splitting documents into smaller passages that can be indexed and searched.

**2. What does “search small, send big” mean?**  
Retrieve a precise small chunk, then provide its parent section or surrounding context to the LLM.

**3. Why add document and section context to chunks?**  
It helps identify the source and makes passages that are vague on their own easier to retrieve and interpret.

**4. How should tables be prepared for RAG?**  
Preserve headers, labels, units, and row relationships; use readable text or structured records when appropriate.

**5. What is a search filter?**  
A constraint—such as product, date, or document type—that limits which documents are eligible for retrieval.
