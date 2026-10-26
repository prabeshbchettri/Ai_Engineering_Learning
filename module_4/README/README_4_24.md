# Who Can See What

## 1. What Is It?

**Access control** determines which users are allowed to view particular information or perform particular actions.

In a Retrieval-Augmented Generation (RAG) application, documents are often split into smaller pieces called **chunks**. The system searches these chunks to find information that can help answer a user's question.

Not every user should be able to retrieve every chunk. For example:

- A student may be allowed to read public course notes.
- A lecturer may also be allowed to read private marking guides.
- A customer in one company must not be able to retrieve another company's documents.

A secure RAG system stores access information, often called **metadata**, alongside each document or chunk. It checks the current user's permissions during retrieval.

## 2. Why Does It Matter?

A RAG assistant can accidentally expose private information if it retrieves restricted content and passes it to the language model.

This can happen even if the final answer does not directly quote the document. The model might summarize it, reveal a fact from it, or include a citation that exposes a restricted document's title.

Access control matters for:

- **Privacy:** Keep personal or confidential information private.
- **Multi-user applications:** Give each user access only to permitted documents.
- **Multi-tenant applications:** Keep separate customers or organizations isolated.
- **Compliance and trust:** Enforce the application's data-access rules consistently.
- **Safe citations and memory:** Prevent titles, snippets, cached answers, or previous conversation context from revealing restricted information.

The central rule is: **a user must not receive information they are not authorized to access, whether it appears in an answer, citation, cache, or conversation history.**

## 3. How Does It Work?

### 3.1 Store access metadata

When documents are added to the knowledge base, store useful metadata with each chunk.

Example:

```python
{
    "text": "The internal project budget is $50,000.",
    "document_id": "budget-001",
    "tenant_id": "company_a",
    "allowed_users": ["user_101", "user_102"],
    "access_level": "restricted"
}
```

Here:

- `text` is the chunk's content.
- `document_id` identifies its source document.
- `tenant_id` identifies the customer or organization that owns it.
- `allowed_users` lists users who may access it in this simplified example.
- `access_level` describes its classification.

Real applications may use roles, groups, ownership rules, or a central authorization service instead of listing every user. The metadata must be trustworthy and updated when permissions change.

### 3.2 Authenticate and authorize the user

These are related but different concepts:

- **Authentication:** Who is the user? For example, verifying a login.
- **Authorization:** What is that user allowed to access?

A user should not be able to gain access simply by changing a user ID or tenant ID sent in a request. The application should derive the user's identity and permissions from a trusted authentication and authorization process.

### 3.3 Filter during retrieval

The secure workflow is:

```text
User signs in
     |
     v
Application verifies identity
     |
     v
Determine permitted documents
     |
     v
Search with access filters
     |
     v
Send only authorized chunks to the model
     |
     v
Generate answer and permitted citations
```

For example, if User A can access public notes but not a private marking guide, the search should exclude chunks from that guide before they reach the model.

**Filtering after retrieval is too late.** If a restricted chunk has already been sent to the model, the model may use its content even if the application later hides the chunk from the user.

### 3.4 Keep customers isolated

Applications serving multiple customers often use a concept called **multi-tenancy**. Each tenant is a separate customer, organization, or workspace.

Every search must enforce the tenant boundary. A request from `company_a` must not retrieve content belonging to `company_b`.

Do not rely only on a tenant ID supplied by the client. Derive the tenant from the authenticated session or validate that the user belongs to the requested tenant. Apply the tenant filter consistently to retrieval, document lookup, caches, conversation history, and citations.

### 3.5 Protect more than the retrieved passages

Access control must cover the entire application:

- **Answers:** Do not generate answers using unauthorized chunks.
- **Citations:** Do not show restricted document titles, snippets, links, or identifiers.
- **Caches:** Do not reuse an answer created for a user with broader permissions unless the cache's authorization rules prove it is safe.
- **Conversation memory:** Do not carry restricted information from one user or tenant into another user's conversation.
- **Document operations:** Apply permissions to direct document retrieval, previews, downloads, and search results, not only vector search.

## 4. Simple Example

Imagine a university RAG assistant with two users:

- **Mina**, a student, can read course notes.
- **Ravi**, a lecturer, can read course notes and a private marking guide.

The knowledge base contains:

| Document | Content | Access |
|---|---|---|
| `course-notes` | The exam covers units 1–4. | Mina and Ravi |
| `marking-guide` | The private marking criteria. | Ravi only |

Mina asks:

```text
What are the private marking criteria?
```

Ravi asks the same question.

### Correct behavior

1. The application authenticates the user.
2. It determines the user's permissions.
3. Search runs with the appropriate access filter.
4. Mina's search excludes the marking guide. The assistant should explain that it cannot find authorized information answering the question.
5. Ravi's search may retrieve the marking guide, so the assistant can answer using it.
6. Citations are generated only from documents Ravi is allowed to access.

The model should not be given Mina's restricted document and then merely told not to mention it. The restricted content should never enter her model context in the first place.

## 5. Practical AI Engineering Application

### 5.1 Apply filters before model generation

The following is conceptual Python pseudocode. It illustrates the security order; `vector_store.search()` and the filter syntax depend on the vector database you use.

```python
def answer_question(user, question):
    permissions = authorization_service.get_permissions(user.id)

    chunks = vector_store.search(
        question=question,
        filters={
            "tenant_id": permissions.tenant_id,
            "allowed_groups": {"$in": permissions.groups},
        },
    )

    prompt = build_prompt(question, chunks)
    answer = language_model.generate(prompt)

    return validate_answer_and_citations(answer, chunks)
```

Important points:

- The application obtains permissions from a trusted service.
- Search applies tenant and access filters before returning chunks.
- Only retrieved, authorized chunks are passed to the model.
- The final response and its citations are checked.

This is an illustrative design, not copy-paste code for a specific vector database. In a real system, the filter expression must match the database's documented API and the chosen access-control model.

### 5.2 Use a clear authorization model

Common approaches include:

- **User-based access:** Only specified users can read a document.
- **Role-based access:** Permissions depend on roles such as student, lecturer, or administrator.
- **Group-based access:** Users in a permitted team can access the document.
- **Tenant-based access:** Data is restricted to a customer or organization.

An application can combine these approaches. Choose the simplest model that accurately represents your access rules, and enforce it consistently.

### 5.3 Secure citations

A citation can reveal information even when the answer itself seems harmless. For example, a restricted title such as `Executive_Layoff_Plan.pdf` may disclose confidential activity.

Therefore:

- Build citations only from authorized retrieved chunks.
- Check authorization again before opening a citation link or fetching a source document.
- Avoid exposing restricted titles, snippets, storage paths, or identifiers.
- Do not assume that an unpredictable document ID is a substitute for authorization.

### 5.4 Secure caches and conversation memory

Suppose User A asks a question and receives an answer based on a private document. If User B asks the same question, returning User A's cached answer could leak the private information.

To prevent this:

- Include the relevant tenant and authorization context in cache design, or cache only results safe for all users.
- Re-check permissions before serving cached content.
- Keep conversation histories separated by user and tenant.
- Do not share summaries or memory across users unless the application explicitly authorizes that sharing.
- Consider permission changes: previously allowed data may no longer be accessible.

A cache key based only on the question is generally insufficient for private RAG data.

### 5.5 Try it: Test two users

Create two test users and two documents in a local environment:

- User A can access `public-notes`.
- User B can access `public-notes` and `restricted-notes`.

Ask both users a question that can only be answered by `restricted-notes`.

Check the following:

| Test | Expected result |
|---|---|
| User A's answer | Does not reveal information from `restricted-notes` |
| User A's citations | Does not expose its title, snippet, link, or identifier |
| User B's answer | Can use the restricted document if authorized |
| User B's citations | Can reference the restricted document |
| Tenant isolation | Neither user can retrieve another tenant's documents |
| Cache and memory | User A cannot receive User B's restricted answer through reuse |

Use synthetic documents and test accounts. Test the search results as well as the final answer: a hidden citation does not prove that restricted chunks were excluded before generation.

## 6. Key Takeaways

- Authentication identifies the user; authorization determines what they may access.
- Store reliable access metadata with documents or chunks.
- Apply permission and tenant filters during retrieval, before content reaches the model.
- Protect answers, citations, caches, conversation memory, and direct document access.
- Never trust a client-supplied user or tenant ID without validating it.
- Test access with users who have different permissions, including their citations and cached results.

## 7. Common Misconceptions

**Misconception: Hiding a restricted passage after generation makes the system secure.**  
The model may already have read and used the restricted content. Exclude unauthorized chunks during retrieval.

**Misconception: A vector database automatically understands user permissions.**  
A vector database only enforces the filters and security mechanisms configured for it. Your application must supply correct authorization rules.

**Misconception: Only the answer can leak private information.**  
Citations, document titles, cached responses, conversation history, and error messages can also reveal information.

**Misconception: A tenant ID from the frontend can be trusted.**  
A client can modify request values. Derive or validate tenant access using trusted server-side identity and authorization data.

## 8. Quick Revision

**Q1. What is access control?**  
Rules that determine which users can access particular information or actions.

**Q2. Why must permissions be checked during retrieval?**  
Because unauthorized content should never reach the model's context.

**Q3. What is the difference between authentication and authorization?**  
Authentication verifies who a user is; authorization determines what they can access.

**Q4. What is tenant isolation?**  
Ensuring that one customer or organization's data cannot be accessed by another.

**Q5. Name three non-answer places where private data can leak.**  
Citations, caches, and conversation memory.
