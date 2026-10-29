# Memory

## 1. What Is It?

In an AI agent, **memory** is information retained so the system can use it later instead of treating every interaction as completely new.

Memory helps an agent personalize responses, continue ongoing work, and reuse useful details from previous conversations.

Two main categories are:

- **Short-term memory:** Information available during the current conversation or task, such as the current question, recent messages, and intermediate results.
- **Long-term memory:** Information deliberately retained across conversations, such as a user's preferences, important past events, or lessons learned from previous tasks.

Memory is not the same as the model's trained knowledge. A model's parameters contain patterns learned during training; an agent's memory is information stored and retrieved while the application runs.

## 2. Why Does It Matter?

Without memory, an agent may repeatedly ask for information the user has already provided, forget an unfinished task, or fail to apply a stable preference in a later conversation.

Well-designed memory can help an agent:

- Personalize its answers based on relevant user preferences.
- Continue multi-step work across sessions.
- Recall past decisions and outcomes.
- Avoid repeating mistakes by retaining useful lessons.
- Reduce the need for users to provide the same context repeatedly.

However, storing more information does not automatically make an agent better. Irrelevant, incorrect, or outdated memories can make responses worse. Memory needs careful selection, access control, updating, and evaluation.

## 3. How Does It Work?

### A. Short-term versus long-term memory

| Type | Typical lifetime | Example |
|---|---|---|
| **Short-term** | Current conversation or task | The user is asking for help debugging a Python error. |
| **Long-term** | Across conversations, until updated or deleted | The user prefers concise explanations with Python examples. |

Short-term memory may be represented by conversation history, a workflow's state, or intermediate data. In LangGraph, graph state can preserve information while a particular thread is running and, with checkpointing, support resuming it later.

Long-term memory requires a storage mechanism that can be accessed across separate threads or conversations, such as a database or LangGraph's store functionality.

The exact lifetime depends on the application's design. A conversation history is not automatically long-term memory, and a checkpoint for one thread does not automatically provide shared memory across all of a user's conversations.

### B. Three useful kinds of long-term memory

1. **Semantic memory — facts and preferences**
   - Examples: preferred language, team location, or a recurring formatting preference.
   - Purpose: personalize future responses and supply stable context.

2. **Episodic memory — past events**
   - Examples: what was decided in the last planning meeting or what happened during a previous support session.
   - Purpose: recall a specific event, decision, or interaction.

3. **Procedural memory — how to do things**
   - Examples: a reliable sequence for deploying a project or a lesson about how to debug a recurring failure.
   - Purpose: reuse a process or improve future task execution.

These categories are useful design concepts, not necessarily three separate databases. An application may store them in one system with different fields or retrieval rules.

### C. Where memories live

Long-term memories need persistent storage. Common options include:

- A relational database, such as PostgreSQL.
- A document or key-value database.
- A vector database or search index for semantic retrieval.
- LangGraph's store functionality for organizing data across threads.

In LangGraph, checkpoints and long-term stores serve different purposes:

- **Checkpoints** preserve the state of a particular graph thread so it can continue or resume.
- **Long-term stores** let an application save and retrieve information across different threads or conversations.

Organize records by a stable user or tenant identifier. Every read, update, and deletion must be scoped to the correct owner. Never rely only on a model-generated user ID or a value supplied without authorization checks.

A conceptual memory record might look like this:

```json
{
  "user_id": "user-42",
  "type": "preference",
  "key": "preferred_language",
  "value": "Hindi",
  "source": "explicit_user_statement",
  "updated_at": "2026-10-29",
  "confidence": "high"
}
```

This is an illustrative data structure, not a required LangGraph schema. Real systems should use appropriate identifiers, timestamps, validation, and access controls.

### D. When and what to save

Memory can be updated at different times:

- **During the conversation:** Save an important fact soon after it is shared.
- **At the end of a task:** Extract the useful information from the completed interaction.
- **In a background process:** Save selected memories asynchronously so the response is not delayed.

Background saving can improve responsiveness, but it introduces a delay before a memory becomes available. If the next step depends on a newly stated fact, save or pass it explicitly before relying on it.

A practical saving workflow is:

1. Review the new interaction.
2. Identify candidate facts, events, or lessons that could be useful later.
3. Prefer explicit, stable, relevant information over passing details.
4. Extract the information into a structured format.
5. Check whether the same memory already exists.
6. Validate the new information and its source.
7. Create, update, or reject the candidate memory.

Do not save every message. A one-time request such as "write a birthday card" usually does not need to become a permanent preference. A direct statement such as "Please use Hindi in future replies" is a much stronger candidate.

Avoid retaining sensitive or unnecessary personal information. Follow the application's privacy policy and the user's choices about what may be stored.

### E. Update facts when they change

Long-term memories can become outdated. If a user says, "My team is in Pune," and later says, "Our team has moved to Mumbai," the agent should not keep presenting Pune as the current location.

A useful update strategy is:

1. Identify the memory that the new statement refers to.
2. Compare the new information with the existing record.
3. Determine whether the statement is a correction, a change over time, or a separate fact.
4. Update the existing record or preserve the historical event where appropriate.
5. Record the time and source if they matter.
6. Ensure future retrieval returns the current fact for current questions.

When two memories disagree, use explicit corrections and reliable, recent evidence rather than blindly combining the records. If the conflict cannot be resolved safely, ask the user.

For example, a past event may remain true even when a current fact changes: "The team was in Pune last year" can coexist with "The team is now in Mumbai." The memory model should distinguish historical facts from current state.

### F. Recall only relevant memories

Retrieval selects stored information that may help answer the current request.

A practical retrieval process is:

1. Identify what information the current request needs.
2. Restrict the search to the authenticated user's records.
3. Retrieve candidates using exact keys, filters, keyword search, semantic search, or a combination.
4. Rank results by relevance and, when appropriate, recency.
5. Check whether a candidate is current and trustworthy.
6. Add only the small set of useful memories to the agent's context.

**Relevance** measures how closely a memory relates to the current task. **Recency** helps when facts change over time, but the newest record is not always the most important. A stable preference may remain useful for years, while an old temporary deadline may no longer matter.

Avoid sending every stored memory to the model. Excessive context increases cost and can distract the model from the current task.

### G. Forgetting and deletion

Users should be able to ask an application to forget a stored memory. A reliable design needs a clear deletion process.

When a memory is deleted:

- Remove it from the active memory store.
- Remove or invalidate corresponding search-index entries and cached copies.
- Ensure future retrieval cannot return the deleted memory.
- Apply the deletion policy to replicas, logs, and backups according to the system's retention and privacy requirements.
- Report honestly what was deleted and what may remain temporarily under documented retention rules.

Some memories can also expire automatically using a time-to-live (TTL), which defines how long a record may remain valid. Expiration is useful for temporary details, but it is not a replacement for handling a direct deletion request.

Deletion across backups and logs can require a documented retention process rather than a single database operation. Do not claim complete deletion unless the system can verify it.

### H. Evaluate whether memory helps

Memory should be tested, not assumed to be useful.

Measure whether the agent:

- Recalls the correct fact in a later conversation.
- Uses relevant memories without inserting unrelated details.
- Replaces outdated facts after a correction.
- Keeps different users' memories separate.
- Avoids inventing memories that were never provided.
- Stops retrieving a memory after it has been deleted.
- Improves task quality compared with the same agent without memory.

Use a small test set with expected outcomes. Include normal cases, conflicting facts, missing information, and deletion requests. Track both useful recall and harmful recall.

## 4. Simple Example

Suppose a user tells an assistant:

1. "Always reply in Hindi."
2. "My team is in Pune."

The assistant extracts two separate memories:

```json
[
  {
    "type": "preference",
    "key": "preferred_language",
    "value": "Hindi"
  },
  {
    "type": "fact",
    "key": "team_location",
    "value": "Pune"
  }
]
```

In a new conversation, the user asks, "Where is my team based?"

The agent retrieves the relevant `team_location` memory and answers that the team is based in Pune. It also uses the Hindi preference when responding, because that preference is relevant to the response style.

Later, the user says, "Our team has moved to Mumbai."

The memory system should update the current `team_location` value to `Mumbai`. In a later conversation, the agent should answer Mumbai, not Pune. If the application needs historical information, it can separately record that the team was previously in Pune.

This example illustrates the complete cycle:

```text
Conversation
    |
Extract useful information
    |
Check existing memories
    |
Create or update stored records
    |
New conversation
    |
Retrieve relevant memories
    |
Generate a personalized answer
```

## 5. Practical AI Engineering Application

In a LangGraph agent, short-term state and long-term memory can work together.

- **Short-term state:** Tracks information needed for the current graph run, such as recent messages, intermediate results, and current task status.
- **Long-term store:** Holds selected facts, events, and lessons that can be retrieved in future conversations.

A practical architecture:

```text
User message
    |
    v
Load current conversation state
    |
    v
Retrieve relevant long-term memories
    |
    v
Build model context
    |
    v
Generate response or perform task
    |
    v
Extract useful memory candidates
    |
    v
Validate and deduplicate
    |
    v
Create, update, or ignore memories
```

### Implementation checklist

1. Choose persistent storage for long-term memory.
2. Assign each authenticated user a stable namespace or ownership key.
3. Define a structured memory schema, including type, key, value, source, and timestamps where useful.
4. Decide which information is worth saving and which should be excluded.
5. Implement retrieval with relevance and recency checks.
6. Implement update, conflict-resolution, expiration, and deletion policies.
7. Add memory retrieval to the agent's workflow before generating a response.
8. Evaluate correct recall, outdated recall, cross-user leakage, and forgetting behavior.

In LangGraph, use checkpointing for thread state and a long-term store for memories that must be available across threads. Consult the current LangGraph documentation for version-specific APIs and configuration.

Memory improves continuity and personalization, but it does not guarantee truth. Stored information may be mistaken, incomplete, or outdated, so the agent must check relevance and reliability before using it.

## 6. Key Takeaways

- **Short-term memory** supports the current conversation or task; **long-term memory** carries useful information across conversations.
- Long-term memory can contain semantic facts, episodic events, and procedural lessons.
- Checkpoints preserve thread state, while a long-term store supports memory across threads.
- Save selected, useful information in a structured form instead of retaining every message.
- Organize memories by authenticated user and retrieve only what is relevant.
- Update outdated facts, resolve conflicts carefully, and support expiration and deletion.
- Evaluate both helpful recall and harmful recall, including whether deleted information stays unavailable.

## 7. Common Misconceptions

- **"The model automatically remembers every conversation."** Not unless the application provides a memory mechanism and stores the information.
- **"Conversation checkpoints and long-term memory are the same."** Checkpoints preserve a thread's state; long-term memory is designed for reuse across conversations or threads.
- **"More memory is always better."** Irrelevant or outdated information can harm answers and increase context costs.
- **"The newest memory always wins."** A new statement may refer to a different time or may be unreliable. Resolve conflicts using context and source.
- **"Deleting one database record guarantees complete deletion everywhere."** Search indexes, caches, replicas, logs, and backups may also require a deletion process.
- **"If an agent recalls something, it must be true."** Memory retrieval returns stored information, not a guarantee that the information is correct.

## 8. Quick Revision

**Q1. What is the difference between short-term and long-term memory?**  
Short-term memory supports the current conversation or task; long-term memory preserves selected information across conversations.

**Q2. What are semantic, episodic, and procedural memories?**  
Semantic memory stores facts, episodic memory stores past events, and procedural memory stores useful methods or lessons.

**Q3. How should memories be separated between users?**  
Use authenticated user identities and enforce access controls on every memory operation.

**Q4. How should an agent handle an updated fact?**  
Identify the existing record, validate the correction, update the current value, and preserve history only when useful.

**Q5. How do you test a memory system?**  
Test correct recall, relevance, updates, user separation, outdated information, and deletion across future conversations.
