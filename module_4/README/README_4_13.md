# Routing and Adaptive RAG

## 1. What Is It?

**Routing** is the process of deciding what should happen to a user's question before the system answers it. In a Retrieval-Augmented Generation (RAG) application, a router can decide whether to answer directly, search a knowledge source, or use a more advanced retrieval strategy.

**Adaptive RAG** means choosing the retrieval and answering strategy for each question instead of using the same process every time.

For example:

- "Hi!" → Answer directly.
- "What is the university's attendance policy?" → Search the relevant documents.
- "Compare the attendance rules across these three regulations" → Transform the question or run a more involved search.

The goal is to use the simplest strategy that is likely to produce a good answer.

## 2. Why Does It Matter?

A RAG system does not need to search documents for every question.

Routing helps an AI application:

- **Reduce unnecessary retrieval:** Greetings and ordinary conversational follow-ups may not need a document search.
- **Find the right information:** Questions can be directed to the appropriate collection, database, tool, or search method.
- **Improve answer quality:** Searching irrelevant documents can introduce distracting context.
- **Control cost and latency:** More complex retrieval steps take additional time and may require extra model calls.
- **Handle different levels of difficulty:** Simple questions can use a lightweight path, while difficult questions can receive more retrieval effort.

Routing does not guarantee a correct answer. The routing decision itself can be wrong, so it should be evaluated.

## 3. How Does It Work?

A basic adaptive RAG workflow can be represented as:

`User question → Router → Selected strategy → Answer`

### Step 1: Receive the question

The system receives a user's message, such as "What is the deadline for registration?"

### Step 2: Classify the question's needs

The router estimates which action is appropriate. A simple system might use three routes:

| Route | When to use it | Next action |
|---|---|---|
| Answer directly | Greetings, simple conversation, or questions answerable without the private knowledge base | Generate a response without retrieval |
| Simple search | A clear question that likely needs information from a known collection | Retrieve relevant passages, then answer using them |
| Transform and search | Ambiguous, multi-part, or difficult questions that may benefit from better search queries | Rewrite or expand the query, search, combine results, then answer |

These are example categories, not universal rules. A follow-up question may still require retrieval if its answer depends on earlier document context.

### Step 3: Select the correct source, if needed

Some applications have multiple sources, such as:

- University regulations
- Course syllabi
- Research papers
- A product database

The router can select the source most likely to contain the answer. The application then searches that source rather than searching every collection unnecessarily.

### Step 4: Retrieve information using the selected strategy

For **simple search**, the system searches with the original question.

For **transform and search**, the system may rewrite the question into clearer search queries, create multiple query variations, or combine ranked results. This extra work is useful when the original query is difficult to search effectively.

For **answer directly**, retrieval is skipped.

### Step 5: Generate and check the answer

When retrieval is used, the language model should answer using the retrieved evidence and communicate when the evidence is insufficient. Skipping retrieval should not mean guessing facts that require private or up-to-date information.

### Step 6: Evaluate the router

Test it with questions of different types. Check whether the selected route makes sense and whether the final answer is useful. Track incorrect routes as well as answer quality, latency, and cost.

## 4. Simple Example

Imagine a university assistant that can answer general conversation and search university PDFs.

Here is a small Python example using transparent rules to demonstrate the routing idea:

```python
def choose_route(question: str) -> str:
    text = question.lower().strip()

    # Simple conversational messages can be answered directly.
    greetings = {"hi", "hello", "hey", "good morning"}
    if text in greetings:
        return "answer directly"

    # Complex questions may benefit from query transformation.
    complex_signals = [
        "compare",
        "difference between",
        "across multiple",
        "in all documents",
        "and explain why",
    ]
    if any(signal in text for signal in complex_signals):
        return "transform and search"

    # Other questions are sent to ordinary document search.
    return "simple search"


questions = [
    "Hi!",
    "What is the registration deadline?",
    "Compare the rules in the syllabus and university regulations.",
]

for question in questions:
    print(question, "->", choose_route(question))
```

Possible output:

```text
Hi! -> answer directly
What is the registration deadline? -> simple search
Compare the rules in the syllabus and university regulations. -> transform and search
```

### What does this example teach?

1. The router examines the question before choosing an answering path.
2. A greeting avoids an unnecessary document search.
3. A clear factual question goes to ordinary retrieval.
4. A comparison question gets a more involved retrieval strategy.

**Important limitation:** This is a teaching example, not a robust production router. Fixed keywords can miss complex questions or misclassify simple ones. A real application may use a language model, a classifier, explicit rules, or a combination. It should be tested against representative questions.

## 5. Practical AI Engineering Application

When building a RAG application, routing can be implemented before the retrieval component.

A practical architecture might look like this:

```text
                         User question
                               |
                            Router
                  _____________|_____________
                 |             |             |
           Answer directly  Simple search  Transform + search
                 |             |             |
                 |       Retrieve passages  Rewrite queries
                 |             |             |
                 |             |       Search and combine
                 |             |             |
                 |_____________|_____________|
                               |
                         Final response
```

### A practical implementation plan

1. **Define the routes.** Start with `answer directly`, `simple search`, and `transform and search`.
2. **Specify routing criteria.** Describe when each route should be selected, including when document evidence is required.
3. **Connect each route to an action.** Direct answers skip retrieval; simple search uses the original query; transformed search adds query-improvement steps.
4. **Keep source selection explicit.** If several collections exist, identify which source each search route should use.
5. **Build a test set.** Create 20 representative questions, including greetings, ordinary factual questions, ambiguous queries, multi-part questions, and questions that require multiple documents.
6. **Review the decisions.** Record the expected route and actual route for every question. Investigate mistakes instead of assuming the router is correct.
7. **Measure the trade-offs.** Compare route accuracy, answer quality, latency, and cost. A cheaper route is not better if it regularly produces poor answers.

### Example evaluation table

| Question | Expected route | Why |
|---|---|---|
| "Hello!" | Answer directly | No document lookup is needed |
| "What is the exam date in the notice?" | Simple search | A specific document fact is needed |
| "Compare the exam rules in two notices." | Transform and search | Multiple sources and a more careful search may help |

The expected route depends on the application's available knowledge and requirements. For example, a greeting that includes a request about a private document should not automatically bypass retrieval.

### What routing does and does not do

**Routing does:**
- Choose the next action or information source.
- Avoid retrieval when it is unnecessary.
- Allocate more retrieval effort to questions that need it.

**Routing does not:**
- Retrieve documents by itself.
- Guarantee that the selected route is correct.
- Guarantee factual answers or prevent hallucinations on its own.

## 6. Key Takeaways

- Routing chooses the action or source that should handle a question.
- Adaptive RAG selects a strategy based on the question instead of always using one fixed pipeline.
- Direct answering, simple retrieval, and transformed retrieval are useful example routes.
- More retrieval effort can help difficult questions, but it adds time and cost.
- Evaluate routing decisions and final answers using a representative test set.

## 7. Common Misconceptions

### "Every question should go through RAG."

No. Greetings and questions that do not need private or external evidence can often be answered directly. However, even a short question may require retrieval if it asks about a specific document.

### "The most advanced retrieval strategy always gives the best answer."

Not necessarily. Extra query transformations and searches can add latency, cost, and irrelevant results. Use them when they are likely to improve the answer.

### "A router is always an LLM."

No. Routing can use simple rules, a traditional classifier, an LLM, or a combination. Choose based on the complexity of the task and the reliability required.

### "If the route is correct, the answer must be correct."

No. The selected search can still retrieve poor evidence, and the model can still misunderstand or misrepresent it. Evaluate the complete pipeline.

## 8. Quick Revision

**1. What is routing in a RAG system?**  
Choosing the appropriate action, search strategy, or information source for a question.

**2. What makes RAG adaptive?**  
The system changes its strategy according to the needs and difficulty of each question.

**3. When is direct answering appropriate?**  
When the question does not require retrieved knowledge, such as a simple greeting or general conversation.

**4. Why use query transformation?**  
To improve searches for unclear, complex, or multi-part questions when the extra work is worthwhile.

**5. How can you test a router?**  
Create a varied set of questions, specify the expected route for each, compare the router's choices, and review answer quality, latency, and cost.
