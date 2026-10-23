# Zero-Shot and Few-Shot Prompting

## 1. What Is It?

**Zero-shot prompting** means asking a language model to perform a task using instructions, without giving it examples of the task in the prompt.

**Few-shot prompting** means including a small number of input-output examples to demonstrate the behavior you want. These examples help the model infer the expected pattern, format, tone, or decision rule.

For example:

- Zero-shot: "Classify this support message as Low, Medium, or High urgency."
- Few-shot: Show a few messages with their urgency labels, then ask the model to classify a new message.

The model still generates its answer based on its training and the current prompt. Few-shot examples guide the response; they do not retrain the model's parameters.

## 2. Why Does It Matter?

Choosing between zero-shot and few-shot prompting affects prompt length, consistency, cost, and output quality.

- **Zero-shot prompting** is often a good first choice because it is simple, quick to write, and uses fewer input tokens.
- **Few-shot prompting** can help when the task has subtle rules or the desired output is difficult to explain precisely.
- Good examples make expectations concrete, especially for classification, formatting, tone, and extraction tasks.

Few-shot prompting is not automatically better. Bad examples can confuse the model, introduce bias, or encourage incorrect patterns. The best approach is to test both methods on representative inputs.

## 3. How Does It Work?

### Zero-shot prompting

1. Describe the task clearly.
2. Define the allowed answers or required format, if needed.
3. Provide the input.
4. Let the model produce an answer without task examples.

Example:

```text
Classify the support message as Low, Medium, or High urgency.
High urgency means a serious issue that prevents a customer from using the service.
Medium urgency means an important feature is impaired but a workaround exists.
Low urgency means a general question or minor inconvenience.

Message:
"I cannot log in, and my deadline is in 20 minutes."

Return only one label.
```

The model must apply the definitions directly without seeing sample classifications.

### Few-shot prompting

1. State the task and rules.
2. Provide a few representative input-output examples.
3. Include the new input that needs an answer.
4. Ask the model to follow the demonstrated pattern, not to repeat the examples.

Example:

```text
Classify each support message as Low, Medium, or High urgency.

Examples:
Message: "How do I change my profile picture?"
Urgency: Low

Message: "The export feature is broken, but I can download the data another way."
Urgency: Medium

Message: "I cannot log in, and my deadline is in 20 minutes."
Urgency: High

Now classify this message:
Message: "The dashboard is slow, but I can still complete my work."

Return only one label.
```

A reasonable expected label is `Medium` if the slowness significantly impairs the service, or `Low` if it is only a minor inconvenience. This illustrates why the labeling rules should be precise enough to reduce ambiguity.

### How many examples should you use?

There is no universal ideal number. Start with two to five useful examples, then evaluate whether more examples improve results enough to justify the extra tokens and maintenance.

### Designing good examples

Good few-shot examples should:

- **Match the task:** Use examples that resemble the real inputs the application will receive.
- **Demonstrate the exact output:** If the required answer is a single label, show a single label.
- **Cover meaningful variation:** Include different types of inputs, not several nearly identical examples.
- **Include a tricky case:** Show how to handle a borderline or commonly confused situation.
- **Use correct labels:** Incorrect examples can teach the model the wrong pattern.
- **Avoid unnecessary detail:** Include only what helps explain the intended behavior.

### Quality, variety, and order

Poor or repetitive examples may lead to repetitive or incorrect outputs. A useful set includes representative cases across the categories and makes the differences between labels clear.

Example order can sometimes affect model results. When accuracy matters, test different example orders rather than assuming one order is always best. Keep the task instructions and evaluation inputs unchanged while testing.

## 4. Simple Example

Suppose a support team wants to classify customer messages by urgency.

Use these definitions:

- **High:** The customer cannot use the service, or a time-critical task is blocked.
- **Medium:** An important feature is impaired, but a workable alternative exists.
- **Low:** A general question or minor inconvenience that does not block work.

### Version A: Zero-shot

```text
Classify the message as High, Medium, or Low urgency.

High: The service cannot be used or a time-critical task is blocked.
Medium: An important feature is impaired, but a workaround exists.
Low: A general question or minor inconvenience.

Message:
"I cannot access my account, so I cannot submit my work."

Return only the label.
```

Expected answer: `High`

### Version B: Few-shot

```text
Classify the message as High, Medium, or Low urgency.

High: The service cannot be used or a time-critical task is blocked.
Medium: An important feature is impaired, but a workaround exists.
Low: A general question or minor inconvenience.

Examples:
Message: "Where can I change my notification settings?"
Label: Low

Message: "The report download fails, but I can view the report online."
Label: Medium

Message: "My account is locked and I cannot submit work before the deadline."
Label: High

Now classify:
Message: "The search feature is broken, but I can find the item by browsing manually."

Label:
```

Expected answer: `Medium`, assuming the search feature is important but the manual workaround remains usable.

### What does this show?

Both prompts may produce the correct answer. The few-shot version additionally demonstrates the labels and shows how a workaround affects the decision. Whether that extra guidance improves accuracy must be checked with a test set rather than assumed.

## 5. Practical AI Engineering Application

In an AI application, you can begin with zero-shot prompting and add examples if evaluation reveals inconsistent outputs.

A simple workflow is:

```text
Define the task and labels
          ↓
Test a zero-shot prompt
          ↓
Evaluate on representative inputs
          ↓
Are results good enough?
      ↙           ↘
    Yes             No
     ↓               ↓
Keep it       Add useful examples
                     ↓
              Test again and compare
```

### LangChain few-shot prompt template

LangChain provides few-shot prompt templates that keep examples separate from the main instructions. This makes examples easier to review, replace, and expand.

The following example uses `FewShotPromptTemplate` to build a text prompt:

```python
from langchain_core.prompts import FewShotPromptTemplate, PromptTemplate

examples = [
    {
        "message": "How do I change my profile picture?",
        "label": "Low",
    },
    {
        "message": "The export feature is broken, but I can download the data another way.",
        "label": "Medium",
    },
    {
        "message": "My account is locked and I cannot submit work before the deadline.",
        "label": "High",
    },
]

example_prompt = PromptTemplate.from_template(
    "Message: {message}\nLabel: {label}"
)

few_shot_prompt = FewShotPromptTemplate(
    examples=examples,
    example_prompt=example_prompt,
    prefix=(
        "Classify each support message as Low, Medium, or High urgency.\n"
        "High means the service is unusable or a time-critical task is blocked.\n"
        "Medium means an important feature is impaired but a workaround exists.\n"
        "Low means a general question or minor inconvenience."
    ),
    suffix="Message: {message}\nLabel:",
    input_variables=["message"],
    example_separator="\n\n",
)

prompt_text = few_shot_prompt.format(
    message="The search feature is broken, but I can browse manually."
)

print(prompt_text)
```

What the code does:

- `examples` stores sample messages and their labels as data.
- `example_prompt` defines how each example should be displayed.
- `FewShotPromptTemplate` combines the task instructions, formatted examples, and new message.
- `suffix` defines where the new input appears.
- `format(...)` fills in the new message and returns the completed prompt text.

This code constructs a prompt; it does not call a language model. To generate a classification, pass the resulting prompt to a compatible model or use a suitable LangChain chain.

### How to evaluate zero-shot versus few-shot

Use the same 10 support messages for both prompt versions, and create the correct label for each message before testing.

1. Run the zero-shot prompt on all 10 messages.
2. Record its predictions and count correct labels.
3. Run the few-shot prompt on the same 10 messages.
4. Count correct labels again.
5. Compare the results and inspect which cases changed.

Accuracy = Number of correct predictions / Total number of predictions

For example, if a prompt correctly classifies 8 of 10 messages:

Accuracy = 8 / 10 = 0.8 = 80%

A small 10-message test is a useful learning exercise, but it is not enough to prove that a prompt will perform equally well on all future messages. Use varied, representative data for stronger evaluation.

## 6. Key Takeaways

- Zero-shot prompting uses instructions without task examples.
- Few-shot prompting includes examples to demonstrate the expected behavior or output pattern.
- Start with zero-shot prompting; add examples when they solve a specific problem.
- Good examples are accurate, representative, varied, and consistent with the requested output format.
- Include a tricky or borderline case when it clarifies an important decision.
- Example order can affect results, so test it when reliability matters.
- Compare both approaches on the same labeled test inputs before deciding which is better.

## 7. Common Misconceptions

**Misconception 1: Few-shot prompting retrains the model.**

It does not update the model's parameters. The examples are included in the current prompt to guide the response.

**Misconception 2: More examples always improve quality.**

More examples use more tokens and can add noise. A few carefully selected examples may be more useful than many repetitive ones.

**Misconception 3: Zero-shot prompting is always worse.**

Clear instructions may be enough for many common tasks. Test the simpler approach first.

**Misconception 4: Examples only teach the model facts.**

Examples can demonstrate output format, tone, category boundaries, and how to handle particular cases.

**Misconception 5: One successful example proves the prompt works.**

A prompt should be tested across multiple inputs, including ambiguous and difficult cases.

## 8. Quick Revision

**1. What is zero-shot prompting?**

Asking the model to perform a task using instructions but without examples of that task.

**2. What is few-shot prompting?**

Providing a small number of input-output examples to guide the model's response.

**3. When should you add examples?**

When instructions alone do not reliably produce the desired format, tone, or decisions.

**4. What makes a good few-shot example?**

It is accurate, representative, clearly labeled, and demonstrates the intended output.

**5. How do you compare zero-shot and few-shot prompting?**

Test both on the same labeled inputs and compare their accuracy and error types.
