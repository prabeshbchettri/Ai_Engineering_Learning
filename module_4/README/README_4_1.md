# When to Use RAG

## 1. What Is It?

**Retrieval-Augmented Generation (RAG)** is a way to help a language model answer questions using information retrieved from external documents instead of relying only on what the model learned during training.

A basic RAG system:
1. Receives a question.
2. Searches a collection of documents for relevant passages.
3. Adds those passages to the model's prompt.
4. Asks the model to answer using the supplied information.

**Simple idea:** retrieve useful information first, then generate an answer from it.

## 2. Why Does It Matter?

A language model may not know your private files, may have outdated knowledge, or may not be able to fit a large document collection into one prompt. RAG helps connect the model to information relevant to the current question.

RAG is useful when you need to:
- **Use private documents:** answer questions about company policies, course notes, manuals, or personal PDFs.
- **Use frequently changing information:** retrieve current information from a maintained source.
- **Search large collections:** find a few useful passages instead of sending every document to the model.
- **Provide sources:** show which passages support an answer so a user can verify it.

RAG does not automatically guarantee correctness. The retrieved passages must be relevant, and the model must interpret them properly.

## 3. How Does It Work?

### The basic RAG pipeline

1. **Question:** The user asks something, such as, "What is the assignment submission policy?"
2. **Retrieval:** The system searches available documents and selects passages likely to answer the question.
3. **Prompt construction:** The system places the question and retrieved passages into the prompt.
4. **Generation:** The language model produces an answer based on the provided context.
5. **Source display (when implemented):** The application shows the documents or passages used to support the answer.

In a production system, documents are often prepared and indexed before questions arrive. Retrieval then searches that prepared collection. You do not need to build the full indexing process to understand when RAG is useful.

### What problems does RAG solve?

| Problem | How RAG helps |
|---|---|
| The model cannot access private documents by itself | Retrieves relevant content from those documents |
| Information changes over time | Searches an updated source instead of depending only on training knowledge |
| The collection is too large for one prompt | Sends selected passages rather than the entire collection |
| Users need to verify an answer | Can return supporting passages or document references |

RAG is not the only solution. A small document can often be supplied directly in the prompt, and live information may sometimes be obtained through an API or tool call.

### When should you not use RAG?

RAG may be unnecessary when:

- **The model already has enough information:** Explaining what a Python list is usually does not require searching your documents.
- **The task only transforms supplied text:** Summarizing, translating, correcting grammar, or rewriting a paragraph usually needs no retrieval if the text is already in the prompt.
- **The information fits comfortably in one prompt:** For a short policy or small document, providing the full text may be simpler and more reliable than building a retrieval system.
- **The task is mainly calculation or deterministic processing:** A calculator, normal Python code, or a database query may be a better fit than retrieving passages and asking an LLM to reason about them.

RAG adds complexity: you must prepare documents, retrieve the right passages, manage context length, and evaluate retrieval quality. Use it when those benefits justify the extra work.

### Two main kinds of RAG failure

A RAG answer can be wrong for at least two different reasons:

1. **Retrieval failure — the system finds the wrong information.** The relevant passage may not be retrieved, or the returned passages may be unrelated or incomplete. Even a capable model cannot reliably answer from evidence it never receives.
2. **Generation failure — the model misuses the information it receives.** The correct passage may be present, but the model can misunderstand it, overlook a key detail, or make a claim that the passage does not support.

To troubleshoot a wrong answer, inspect both the retrieved passages and the final response. Do not assume every failure is caused by the language model.

## 4. Simple Example

Imagine your university has this assignment policy:

> Assignments must be submitted through Google Classroom before 11:59 PM on the due date. Late submissions require approval from the course instructor.

You ask: **"Can I submit an assignment late without approval?"**

### Without RAG

If the model has not been given your university's policy, it may guess based on general knowledge. Its answer might not match your actual rules.

### With RAG

1. The system searches the university policy documents.
2. It retrieves the passage about late submissions.
3. It sends that passage and your question to the model.
4. The model answers: "No. According to the supplied policy, late submissions require approval from the course instructor."

The answer is grounded in the provided passage. A good application can also display the policy document as a source.

## 5. Practical AI Engineering Application

Suppose you are building a question-answering assistant for university documents.

- If you have just one short PDF, first try sending its text with the question directly to the model.
- If you have hundreds of long PDFs, retrieval can help select only the passages relevant to each question.
- If assignment policies change, make sure the document collection or index is updated.
- If answers are wrong, check whether the correct passage was retrieved before changing the prompt or model.
- If users need trustworthy answers, display sources and test whether the answer is actually supported by them.

**Practical rule:** start with the simplest approach that works. Add RAG when document size, privacy, freshness, or source requirements make retrieval valuable.

## 6. Try It: Send a Long Document Whole

Choose a long document that you are allowed to use. Ask a question whose answer appears somewhere inside it, and send the entire document with the question to your model.

Record the following:

| Measurement | What to record |
|---|---|
| Tokens | Input and output tokens, if the provider reports them |
| Cost | Estimated or reported cost; if using a free local model, note that monetary API cost may be zero |
| Time | Time from sending the request until the answer is returned |
| Answer quality | Whether the answer is correct and supported by the document |

Then ask yourself:
- Did the entire document fit within the model's context limit?
- Was the request slower or more expensive than expected?
- Would retrieving a few relevant passages reduce the amount of text sent?
- Is the document small enough that sending it whole is still the easiest option?

This experiment is a baseline, not a complete RAG comparison. If you later build RAG, compare it against the same questions and document.

## 7. Common Misconceptions

- **"Every question needs RAG."** No. General questions and simple text transformations often do not need retrieval.
- **"RAG eliminates hallucinations."** No. It can provide relevant evidence, but retrieval and generation can both fail.
- **"RAG means sending every document to the model."** No. The point is usually to retrieve a small, relevant subset.
- **"If the answer is wrong, the model is always at fault."** No. The system may have retrieved the wrong passages.
- **"RAG is always better than putting a document in the prompt."** No. For a short document, sending it directly may be simpler.

## 8. Key Takeaways

- RAG means retrieving relevant information and providing it to a model before it generates an answer.
- It is especially useful for private, frequently updated, large, or source-sensitive document collections.
- It is often unnecessary when the model already knows enough, the task only transforms supplied text, or the full context fits comfortably in one prompt.
- RAG has two major failure points: retrieving the wrong evidence and generating an incorrect answer from the evidence.
- Test the simple full-document approach before deciding that a problem needs RAG.

## 9. Quick Revision

**Question:** What are the main steps in a basic RAG pipeline?

**Answer:** Receive a question → retrieve relevant passages → add them to the prompt → generate an answer → optionally show sources.

**Question:** Name two situations where RAG is useful.

**Answer:** Answering questions about private documents and searching a large collection of frequently updated information.

**Question:** Name two situations where RAG may be unnecessary.

**Answer:** Explaining a common concept the model already knows, or rewriting text that is already supplied in the prompt.

**Question:** What are the two main kinds of RAG failure?

**Answer:** Retrieval failure (the wrong passages are found) and generation failure (the model misuses or misinterprets the retrieved passages).

**Learning outcome:** You should be able to decide whether a problem genuinely needs RAG and explain what each step of its pipeline does.
