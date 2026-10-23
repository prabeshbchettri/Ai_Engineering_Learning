# Module 3, Topic 7: Versions, Cost and Caching

**Unit:** 3.7  
**Day:** 24

## What Is It?

Prompt versioning, cost tracking, and prompt caching are practices that help you maintain reliable AI applications while controlling their operating costs.

- **Prompt versioning** means saving prompts as named, traceable versions instead of silently overwriting them.
- **Cost tracking** means measuring the tokens, estimated API cost, and response time associated with each prompt version.
- **Prompt caching** means reusing the processing of an unchanged prompt prefix when a model provider supports it. Depending on the provider, cached input tokens may cost less and may reduce latency.

The goal is not simply to make a prompt produce better answers. It is to find a version that offers an appropriate balance of quality, speed, reliability, and cost.

## Why Does It Matter?

A prompt change can improve answer quality while also increasing token use or slowing responses. Without version history and measurements, it is difficult to tell whether the change was worthwhile—or to reproduce a previous result.

These practices help you:

- Reproduce results by identifying the exact prompt and model used.
- Roll back a change that makes responses worse.
- Compare prompt versions using the same test questions.
- Estimate the cost of running an application at scale.
- Reduce repeated input processing when provider caching is available.

For example, an extra 200 input tokens may seem insignificant in one request. Across thousands of requests, unnecessary context can become a meaningful expense.

## How Does It Work?

### 1. Version prompts like code

Store each prompt version in a file or version-control system such as Git. Record useful metadata alongside it:

- Prompt version or Git commit
- Model name and, where available, model version
- Date and purpose of the change
- Evaluation results
- Token usage, estimated cost, and latency
- Relevant generation settings, such as temperature and maximum output tokens

Avoid changing a prompt in place without preserving the previous version. A result is reproducible only when you can identify the prompt and relevant model settings that produced it. Model providers can update model behavior over time, so recording the model identifier and test date is useful.

Example project layout:

```text
ai-project/
├── prompts/
│   ├── answer_v1.txt
│   └── answer_v2.txt
├── evaluations/
│   └── prompt_comparison.csv
└── README.md
```

For a team project, Git history can show exactly what changed and why.

### 2. Compare more than quality

Evaluate prompt versions on the same set of questions and track multiple measures.

| Measure | What it tells you |
|---|---|
| Quality | Whether the response is correct, relevant, and useful |
| Input tokens | How much prompt and context text is sent to the model |
| Output tokens | How much text the model generates |
| Estimated cost | The expected charge using the provider's applicable rates |
| Latency | How long the request takes |
| Consistency | Whether repeated runs produce acceptably similar results |

Token prices can differ for input, output, cached input, and model tiers. Use the provider's current pricing and the actual usage fields returned by its API when possible. Do not assume that fewer tokens always means lower total cost: output generation and other provider-specific charges may also matter.

A simple comparison table might look like this. **These figures are illustrative, not measured results.**

| Prompt version | Quality score | Input tokens/request | Cost/request | Response time |
|---|---:|---:|---:|---:|
| V1 | 8.2/10 | 1,000 | $0.0020 | 1.4 s |
| V2 | 8.4/10 | 1,800 | $0.0038 | 1.8 s |

V2 scores slightly higher, but costs almost twice as much and is slower. Whether that trade-off is worthwhile depends on how important the quality improvement is to the application.

### 3. Trim what is not helping

Reduce unnecessary prompt content while preserving the instructions and context needed for a good answer.

Look for:

- Repeated rules stated in several ways.
- Long explanations that do not affect the output.
- Irrelevant conversation history or retrieved documents.
- Examples that do not represent real use cases.
- Instructions that contradict each other.

Make one change at a time and test it against the same evaluation set. Shorter prompts are not automatically better; removing a useful constraint may increase errors or make outputs less consistent.

For a RAG application, retrieve and include relevant passages rather than adding the entire document collection to every request.

### 4. Understand prompt caching

Some model providers support caching for repeated prompt prefixes. If a request begins with the same eligible content as an earlier request, the provider may reuse processing for that prefix rather than processing it from scratch.

A useful prompt structure is:

1. **Stable prefix:** system instructions, fixed policies, output format, and other content that rarely changes.
2. **Variable suffix:** the user's question, current conversation details, and request-specific context.

Example:

```text
SYSTEM INSTRUCTIONS (stable)
You are a university academic assistant.
Answer using the provided university sources.
If the sources do not support an answer, say so.
Return a concise answer and list relevant sources.

REQUEST-SPECIFIC CONTENT (changes each request)
Question: What are the prerequisites for this course?
Relevant sources:
[retrieved passages for this question]
```

Keeping stable content at the beginning can help caching when the provider's caching rules support that arrangement. However, **caching is provider-dependent**. Providers may require a minimum prefix length, particular request patterns, or explicit cache settings. Cache eligibility, retention, pricing, and latency benefits vary. Check the provider's documentation and usage metadata instead of assuming that every repeated prompt is cached.

Caching can reduce the cost of eligible input tokens, but it does not necessarily reduce output-token charges. It also does not replace prompt evaluation or prompt versioning.

## Simple Example: Compare Prompt Versions

Imagine two versions of a university assistant prompt:

- **V1:** Includes a long, repeated explanation of how to answer.
- **V2:** Keeps the essential instructions, removes redundant wording, and puts stable instructions before the question and retrieved passages.

Test both versions on the same 10 questions. Record quality, input and output tokens, cost, and response time. If caching is supported, run requests in a way that allows you to observe whether the provider reports cached input tokens; do not compare one warm-cache run with one cold-cache run without recording that difference.

A basic experiment log could contain:

```text
Prompt version: V2
Model: <record the exact model identifier>
Test set: 10 fixed questions
Quality: <record the evaluation score>
Input tokens: <record actual usage>
Output tokens: <record actual usage>
Estimated cost: <calculate using current pricing>
Response time: <record elapsed time>
Cache usage: <record provider-reported cache usage, if available>
```

The placeholders should be replaced with measured results. Do not assume caching occurred just because the prompt starts with fixed text.

## Practical AI Engineering Application

In an AI engineering project—such as a RAG assistant or an agent—you can build a repeatable prompt evaluation workflow:

1. Save the current prompt as a version-controlled file.
2. Choose a fixed set of representative questions, including edge cases and questions the system should refuse to answer from insufficient evidence.
3. Run the same tests with each candidate prompt and record the model identifier and settings.
4. Collect quality scores, token usage, cost, and latency.
5. Check provider-reported cache usage when caching is available.
6. Compare the results and keep the version that meets your quality requirements at an acceptable cost.
7. Re-run the evaluation whenever the prompt, model, retrieval logic, or important settings change.

For an application receiving thousands of requests, estimate monthly cost from measured usage and expected traffic. Keep development and evaluation data separate from sensitive production information, and avoid logging secrets or unnecessary personal data.

## Key Takeaways

- Treat prompts as versioned project assets, not disposable strings.
- Record the model and settings associated with every evaluation.
- Measure quality, token usage, cost, latency, and consistency together.
- Remove redundant text carefully and validate changes against a fixed test set.
- Put stable prompt content before changing content when it fits the provider's caching behavior.
- Verify caching through provider documentation and usage metadata.
- Choose the prompt that meets the application's quality needs at an acceptable operational cost.

## Common Misconceptions

**“The shortest prompt is always the cheapest and best.”**  
A shorter prompt may save input tokens, but removing important context can harm answer quality and increase retries or downstream work.

**“Putting fixed instructions first guarantees caching.”**  
No. The provider must support caching, and its eligibility rules must be met. Confirm actual cache usage.

**“A better quality score always means a better prompt.”**  
Not necessarily. The improvement may be too small to justify a large cost or latency increase.

**“A prompt version alone makes an experiment reproducible.”**  
You should also record the model identifier, relevant settings, test set, date, and evaluation method.

## Quick Revision

1. **What is prompt versioning?**  
   Saving named prompt revisions so you can trace changes, compare results, and roll back when needed.

2. **Which measurements should you compare?**  
   Quality, input and output tokens, estimated cost, latency, and—where relevant—consistency and cache usage.

3. **Why place stable content first?**  
   It can create a repeated prefix that is eligible for provider-supported prompt caching.

4. **Does caching always happen?**  
   No. It depends on the provider, model, request structure, and caching rules.

5. **What is the goal of optimization?**  
   Maintain the required answer quality while reducing unnecessary cost and delay.

## Day 24 Try It

Reorder your system prompt so all fixed instructions come first and changing content comes last. Run 10 representative requests and compare the original and revised versions.

Record:

- Quality score
- Input and output tokens
- Estimated cost
- Response time
- Cache usage reported by the provider, if available

Use the same questions and model settings for a fair comparison. If the provider supports prompt caching, follow its documented testing method and record whether requests were cold or warm. Keep the revised prompt only if the measurements show an acceptable trade-off.

**Outcome:** Maintain a versioned prompt history and make prompts more cost-efficient without making their answers worse.
