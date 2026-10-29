# Saving Progress and Asking for Approval

## 1. What Is It?

Reliable agents need to remember what they have done, recover when interrupted, and ask permission before taking important actions.

In LangGraph, these ideas are commonly implemented with:

- **Checkpointing:** Saving the graph's state at points during execution.
- **Resuming:** Continuing a paused or interrupted run from saved state instead of starting over.
- **Human-in-the-loop (HITL):** Pausing a workflow so a person can review and approve or reject a proposed action.
- **Idempotency:** Designing an action so that repeating the same request does not accidentally repeat its real-world effect.

These mechanisms are useful when an agent performs multi-step work or uses tools that change something outside the model, such as creating a support ticket, sending a message, or updating a record.

## 2. Why Does It Matter?

An agent may take several steps before finishing. A process can fail, a server can restart, or a person may need to review a sensitive action.

Without persistence and approval controls:

- A failure may force the workflow to repeat completed work.
- A user may have to restart a long task manually.
- An agent might make an important change without human review.
- Retrying a request may create duplicate tickets, payments, or messages.

Saving state, resuming runs, requesting approval, and making operations safe to retry help make agentic systems more reliable and controllable.

## 3. How Does It Work?

### A. Save progress with checkpoints

A graph's **state** is the information it carries between steps. It might include the user's request, search results, a draft response, the next action, and whether approval has been received.

A **checkpoint** is a saved snapshot of that state. With a configured LangGraph checkpointer, the graph can save state as execution progresses.

Typical flow:

1. Receive the task.
2. Run a node and update the graph state.
3. Save a checkpoint through the configured checkpointer.
4. Continue to the next node.
5. If execution is interrupted, use the saved checkpoint to recover the run.

Checkpointing requires a checkpointer and an appropriate thread identifier. A thread ID lets LangGraph associate checkpoints with a particular conversation or workflow run. Production systems should use a persistent checkpointer suitable for their deployment; an in-memory checkpointer is generally for development and testing and does not survive a process restart.

### B. Resume instead of restarting

When a workflow is interrupted, resume it using the same thread identifier and the saved checkpoint.

The graph can continue from its saved state rather than rebuilding the entire workflow from the beginning. The exact resume behavior depends on where execution stopped and how the graph is designed.

A checkpoint is not the same as a complete backup of every external system. If a tool successfully performs an action but the workflow fails before recording that result, the workflow may not know whether the action happened. This is one reason external actions need careful retry handling.

### C. Pause for human approval

A **human-in-the-loop** step gives a person control over an action that should not happen automatically.

A common workflow is:

1. The agent prepares a proposed action.
2. The graph pauses before the action-changing tool runs.
3. The application displays the proposed action to a reviewer.
4. The reviewer approves or rejects it.
5. The graph resumes and follows the appropriate branch.

For example, an agent may draft a support ticket automatically but wait for approval before submitting it.

In LangGraph, an interrupt can pause execution and expose information for review. With checkpointing configured, the workflow can later resume using a command that supplies the reviewer's decision or other input. The application must clearly present the pending action and validate the decision. Do not treat arbitrary model-generated text as approval.

### D. Make actions safe to retry

An **idempotent** operation has the same intended effect when repeated with the same input as when performed once.

For example, setting a ticket's status to `closed` repeatedly should leave it closed. By contrast, a tool that creates a new ticket every time it is called is not automatically idempotent: a retry could create duplicates.

Ways to reduce duplicate side effects include:

- Give each logical operation a stable idempotency key or request ID.
- Check whether the operation has already been completed before creating a new resource.
- Store and reuse the result associated with that operation ID.
- Use the external service's idempotency mechanism when available.
- Record action status and handle uncertain outcomes carefully.

A simple check followed by a create can still have a race condition if two requests run at the same time. Where possible, enforce uniqueness in the database or service rather than relying only on an application-level check.

## 4. Simple Example

Imagine a support assistant that prepares a ticket and must ask a person before submitting it.

### Workflow

```text
Receive request
      |
Prepare ticket
      |
Save state / checkpoint
      |
Ask for human approval
      |
      +---- Rejected ----> Record rejection and stop
      |
      +---- Approved ---> Check whether ticket already exists
                                |
                         Create or reuse ticket
                                |
                              Finish
```

### Example of an idempotent ticket-creation pattern

The following is conceptual Python illustrating the idea. It is not a complete LangGraph application and does not call a real ticketing API.

```python
tickets_by_request_id = {}

def create_ticket(request_id: str, title: str) -> dict:
    # Return the existing result if this logical request was handled.
    if request_id in tickets_by_request_id:
        return tickets_by_request_id[request_id]

    # In a real system, call the ticket service here.
    ticket = {
        "ticket_id": f"TICKET-{len(tickets_by_request_id) + 1}",
        "title": title,
    }

    # Save the result under a stable ID so retries reuse it.
    tickets_by_request_id[request_id] = ticket
    return ticket


first = create_ticket("request-123", "Cannot access account")
retry = create_ticket("request-123", "Cannot access account")

assert first == retry
print(first)
```

**What this demonstrates:**

1. `request_id` identifies one logical request, not each attempt to run it.
2. The first call creates and stores a ticket result.
3. A repeated call with the same ID returns the stored result rather than creating another ticket.
4. A real production implementation should use durable storage and, ideally, an atomic uniqueness constraint or the ticket service's idempotency support. The in-memory dictionary is lost when the process exits and is not safe for concurrent workers.

### Approval behavior

- **Approve:** Resume the workflow and allow the ticket-creation step to run.
- **Reject:** Resume through a rejection branch, record the decision, and do not call the ticket-creation tool.
- **Interrupt or crash:** Recover from the saved checkpoint, then verify whether any external action already occurred before retrying it.

## 5. Practical AI Engineering Application

When building a LangGraph agent that uses tools, combine the mechanisms according to the risk of the task.

| Requirement | Practical design |
|---|---|
| Preserve progress | Configure a checkpointer and a stable thread ID. |
| Recover after interruption | Resume from the saved checkpoint and handle the interrupted node deliberately. |
| Require approval | Put an interrupt or review step before the side-effecting tool. |
| Reject safely | Route rejection to a branch that does not execute the tool. |
| Prevent duplicate actions | Use stable operation IDs, idempotency keys, and durable records. |
| Audit decisions | Store who approved or rejected, what was proposed, and when the decision occurred. |

### Suggested implementation workflow

1. Build the graph with separate preparation, approval, action, and completion steps.
2. Configure checkpointing and use a consistent thread ID for the same workflow.
3. Pause before a tool that changes external state, such as sending an email or creating a ticket.
4. Display the exact action and relevant details to the reviewer.
5. Validate the reviewer's approval or rejection before resuming.
6. Make the action tool idempotent or use the external service's idempotency feature.
7. Test approval, rejection, interruption, resumption, and repeated execution.

**Important distinction:** Checkpointing saves workflow state; it does not automatically undo external actions. Human approval provides a control point; it does not itself prevent duplicates. Idempotency helps make retries safe; it does not decide whether an action is authorized. Reliable systems combine these protections.

## 6. Key Takeaways

- **Checkpointing** saves graph state so a workflow can recover after interruption.
- **Resuming** continues a run from saved state, usually associated with a stable thread ID.
- **Human-in-the-loop approval** lets a person review an action before a sensitive tool executes.
- A rejected action must follow a path that does not execute the side-effecting tool.
- **Idempotency** helps prevent retries from creating duplicate real-world effects.
- A checkpoint does not guarantee that an external action did or did not happen; verify uncertain outcomes before retrying.

## 7. Common Misconceptions

- **“Saving state means every external action is saved or rolled back.”** No. Checkpoints capture graph state, not a transactional backup of external services.
- **“A retry is always safe.”** No. A repeated tool call can create duplicate resources unless the action is designed for retries.
- **“The model can approve its own action.”** Human-in-the-loop approval requires a genuine decision from the designated reviewer or approval system.
- **“An in-memory checkpointer survives a restart.”** Generally not. Use a persistent checkpointer for recovery across process restarts.
- **“Rejecting means stopping the entire system.”** Not necessarily. The graph can record the rejection, explain it, or ask the user for a revised request without executing the rejected action.

## 8. Quick Revision

**Q1. What is a checkpoint?**  
A saved snapshot of workflow state that supports recovery and resumption.

**Q2. Why does a LangGraph workflow need a thread ID?**  
It associates checkpoints with the specific conversation or workflow run being resumed.

**Q3. Where should human approval happen?**  
Before the side-effecting tool executes, with the proposed action clearly shown to the reviewer.

**Q4. What does idempotency protect against?**  
Unintended duplicate effects when the same logical operation is retried.

**Q5. Does checkpointing prevent duplicate tickets by itself?**  
No. The ticket-creation operation also needs reliable retry handling, such as an idempotency key or durable uniqueness check.
