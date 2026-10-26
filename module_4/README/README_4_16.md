# Graph RAG and Choosing a RAG Pattern

## 1. What Is It?

**Graph RAG** is a Retrieval-Augmented Generation (RAG) approach that uses a knowledge graph to represent entities and the relationships between them.

A knowledge graph stores information as:

- **Entities:** People, organizations, products, concepts, or other things.
- **Relationships:** Connections between entities.
- **Properties:** Additional details about entities or relationships.

For example:

- Entity: `Prabesh`
- Relationship: `studies`
- Entity: `Computer Engineering`

This can be represented as:

`Prabesh → studies → Computer Engineering`

Unlike basic vector RAG, which retrieves passages based on semantic similarity, Graph RAG can retrieve information by following relationships between entities.

The best RAG pattern depends on the type of question, the data, and the retrieval problem you need to solve.

## 2. Why Does It Matter?

Traditional vector RAG works well when the answer is contained in one or a few relevant text passages. However, some questions require connecting information across multiple entities or relationships.

For example:

**Question:** Which projects use a technology developed by a company that collaborates with our organization?

Answering this may require several steps:

1. Identify the organization.
2. Find the companies it collaborates with.
3. Identify the technologies developed by those companies.
4. Find projects that use those technologies.

A simple vector search might retrieve relevant passages but fail to connect all the relationships correctly.

Graph RAG can represent these connections explicitly, making it useful for relationship-heavy questions.

However, Graph RAG is not automatically better than vector RAG. It requires a suitable graph, additional processing, and more maintenance.

## 3. How Does It Work?

A typical Graph RAG workflow includes the following steps.

### Step 1: Extract Entities and Relationships

Process source documents to identify entities and the relationships between them.

Example source text:

"Company A developed Product X. Product X is used by Project Y."

Extracted relationships:

- `Company A → developed → Product X`
- `Project Y → uses → Product X`

### Step 2: Build the Knowledge Graph

Store entities as nodes and relationships as edges.

Conceptually:

`Company A → Product X ← Project Y`

The graph can also store properties such as dates, descriptions, and entity identifiers.

### Step 3: Convert the Question into a Retrieval Plan

Understand what entities and relationships the user's question requires.

For example:

"Which projects use products developed by Company A?"

The retrieval process needs to find products developed by Company A and then find projects that use those products.

### Step 4: Retrieve Related Information

Search the graph for the relevant entities and follow the necessary relationships.

Depending on the system, retrieval may also use vector search, keyword search, or database queries.

### Step 5: Generate the Answer

Provide the retrieved facts and their source information to the LLM.

The LLM generates an answer grounded in the retrieved evidence. The application should preserve source references so the answer can be checked.

## 4. Understanding Different RAG Patterns

Different retrieval patterns solve different problems.

| RAG Pattern | Best Suited For | Example |
|---|---|---|
| Basic Vector RAG | Finding semantically relevant passages | "Explain our refund policy." |
| Hybrid Search | Combining semantic search and keyword matching | Finding a document containing a specific error code |
| Reranking | Improving the ordering of retrieved passages | Selecting the most relevant passages from many candidates |
| Multi-Query RAG | Searching using different formulations of a question | Searching for information about both "car" and "vehicle" |
| Multi-Hop RAG | Answering questions requiring multiple retrieval steps | "Who manages the team that owns this service?" |
| Self-Correcting RAG | Evaluating retrieval results and retrying when appropriate | Searching again when the retrieved passages do not answer the question |
| Structured Data RAG | Answering questions using tables or relational databases | "How many orders were placed last month?" |
| Graph RAG | Retrieving connected entities and relationships | "Which projects use technologies developed by our partners?" |

These patterns can be combined when necessary. For example, a system may use hybrid search to retrieve candidate documents, rerank them, and then use a knowledge graph to connect related entities.

## 5. Simple Example

Imagine a university assistant with the following information:

- Computer Science Club organizes the AI Workshop.
- Prabesh is a member of the Computer Science Club.
- The AI Workshop takes place in Room 101.

A knowledge graph could represent these relationships:

```text
Prabesh
   |
   | member_of
   v
Computer Science Club
   |
   | organizes
   v
AI Workshop
   |
   | takes_place_in
   v
Room 101
```

Now consider this question:

**"Where is the workshop organized by Prabesh's club held?"**

The system can follow these relationships:

1. Find the club that Prabesh belongs to.
2. Find the workshop organized by that club.
3. Find the location of the workshop.
4. Return `Room 101`, supported by the retrieved relationships.

This example shows how a graph can connect information that is distributed across several facts.

## 6. When Should You Use Graph RAG?

Graph RAG is worth considering when:

- Questions depend on relationships between multiple entities.
- Information is distributed across many documents.
- Users frequently ask multi-step relationship questions.
- Entity connections are important to the accuracy of the answer.
- A maintained knowledge graph can provide value beyond ordinary document retrieval.

Graph RAG may be unnecessary when:

- Most questions can be answered from a single passage.
- The documents are straightforward and largely independent.
- A basic vector or hybrid search system already performs well.
- Building and maintaining a graph would cost more than the benefits it provides.

**Practical rule:** Start with the simplest retrieval approach that solves the problem reliably. Add graph retrieval when relationship-based questions justify the extra complexity.

## 7. How to Choose the Right RAG Pattern

Choose a pattern based on the failure you observe.

| Observed Problem | Pattern to Consider |
|---|---|
| Relevant passages are not being found | Improve chunking, embeddings, or search |
| Exact terms or identifiers are missed | Hybrid search |
| Good passages appear too low in the results | Reranking |
| One version of a question retrieves poor results | Multi-Query RAG |
| The answer requires connecting facts across multiple steps | Multi-Hop RAG or Graph RAG |
| Retrieved passages do not answer the question | Self-Correcting RAG |
| The answer requires counts, filtering, or aggregation | Structured Data RAG |
| The question depends on explicit relationships between entities | Graph RAG |

These are starting points, not rigid rules. More than one pattern may be appropriate for a particular problem.

## 8. Practical AI Engineering Application

Suppose you are building a university assistant that answers questions about courses, teachers, departments, projects, and prerequisites.

A basic vector RAG system may answer:

"What does the course description say about prerequisites?"

A graph-based system may be more useful for:

"Which courses require a course taught by the teacher responsible for this department?"

A possible architecture is:

1. Store university documents in a document store.
2. Create embeddings for document passages.
3. Extract relevant entities and relationships.
4. Store the relationships in a graph database.
5. Identify whether a question needs document retrieval, graph traversal, structured queries, or a combination.
6. Retrieve supporting evidence.
7. Generate an answer with source references.
8. Evaluate answer correctness, retrieval quality, and response time.

Do not send every question through every retrieval system. Route questions to the approach that fits their information requirements.

## 9. Common Misconceptions

### Misconception 1: Graph RAG replaces vector RAG.

**Correction:** Graph RAG and vector RAG solve overlapping but different problems. They can be used together.

### Misconception 2: A knowledge graph automatically makes answers correct.

**Correction:** The graph may contain missing, outdated, or incorrectly extracted relationships. Its data quality and retrieval logic must be evaluated.

### Misconception 3: Every multi-step question needs Graph RAG.

**Correction:** Some multi-step questions can be handled with iterative vector retrieval or other methods. Use a graph when explicit entity relationships provide a meaningful advantage.

### Misconception 4: The most advanced RAG architecture is always the best.

**Correction:** More components introduce more complexity, cost, latency, and possible failure points. Choose based on measured requirements.

## 10. Key Takeaways

- Graph RAG uses a knowledge graph to represent entities and their relationships.
- Nodes represent entities, while edges represent relationships.
- Graph retrieval can help answer questions that require connecting related facts.
- Vector RAG retrieves semantically relevant passages; graph retrieval follows relationships.
- Different RAG patterns address different retrieval problems.
- RAG patterns can be combined when there is a clear reason to do so.
- Begin with a simple system, evaluate its failures, and add complexity only when it improves performance.

## 11. Quick Revision

**Q1. What is Graph RAG?**

A RAG approach that uses a knowledge graph to retrieve information through entities and their relationships.

**Q2. What are nodes and edges?**

Nodes represent entities. Edges represent relationships between those entities.

**Q3. When is Graph RAG useful?**

When answering questions requires connecting related entities or following multiple relationships.

**Q4. Is Graph RAG always better than vector RAG?**

No. The appropriate method depends on the question, data, and system requirements.

**Q5. How should you choose a RAG pattern?**

Identify the retrieval problem, select a suitable approach, and evaluate it using representative questions.

**Final principle:** Choose the RAG architecture based on the problem you need to solve, not on how sophisticated the architecture sounds.