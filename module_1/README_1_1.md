# M1.1 — What an LLM Actually Is

> **Module:** M1.1 — What an LLM Actually Is  
> **Roadmap position:** Module 1, Topic 1  
> **Type:** Theory + Code  
> **Coding requirement:** Light  
> **Difficulty:** Beginner  
> **Priority:** Core

---

## Table of Contents

1. [Overview](#1-overview)
2. [What Is an LLM?](#2-what-is-an-llm)
   - [Technical Definition](#technical-definition)
   - [Plain-English Definition](#plain-english-definition)
   - [Key Terminology](#key-terminology)
   - [Anatomy of an LLM](#anatomy-of-an-llm)
   - [What an LLM Is Not](#what-an-llm-is-not)
3. [Why LLMs Matter](#3-why-llms-matter)
   - [Impact Table](#impact-table)
   - [Real-World Use Cases](#real-world-use-cases)
   - [LLMs Versus Alternatives](#llms-versus-alternatives)
4. [How an LLM Works](#4-how-an-llm-works)
   - [Step-by-Step Mechanism](#step-by-step-mechanism)
   - [The Generation Loop](#the-generation-loop)
   - [Mathematical Foundations](#mathematical-foundations)
   - [Training Versus Inference](#training-versus-inference)
   - [Key Parameters](#key-parameters)
   - [Failure Modes](#failure-modes)
5. [Core Concepts and Techniques](#5-core-concepts-and-techniques)
   - [Next-Token Prediction](#technique-1-next-token-prediction)
   - [Autoregressive Generation](#technique-2-autoregressive-generation)
   - [Decoding Strategies](#technique-3-decoding-strategies)
   - [One Model, Many Tasks](#technique-4-one-model-many-tasks)
   - [Where Capability Comes From](#technique-5-where-capability-comes-from)
6. [Advanced Strategies and Production Patterns](#6-advanced-strategies-and-production-patterns)
7. [Practical Code Examples](#7-practical-code-examples)
   - [Example 1: Autoregressive Generation](#example-1-simulate-autoregressive-text-generation)
   - [Example 2: Decoding](#example-2-explore-how-decoding-changes-token-selection)
   - [Practice Exercise](#practice-exercise)
8. [Common Mistakes and How to Fix Them](#8-common-mistakes-and-how-to-fix-them)
9. [Interview Preparation](#9-interview-preparation)
   - [Conceptual Questions](#conceptual-interview-questions)
   - [Technical Questions](#technical-interview-questions)
   - [Scenario-Based Questions](#scenario-based-interview-questions)
   - [Rapid-Fire Revision](#rapid-fire-revision)
   - [Interview Answer Framework](#interview-answer-framework)
10. [Module Completion Checklist](#10-module-completion-checklist)
11. [Final Takeaway](#11-final-takeaway)

---

# 1. Overview

## What This Module Covers

A Large Language Model (LLM) is a foundational technology behind modern AI assistants, coding assistants, document summarizers, conversational agents, and many generative AI applications.

To become an AI engineer, you must understand not only how to call an LLM through an API, but also what the model computes, how it generates text, where its capabilities originate, and why its outputs are not always reliable.

This module establishes five foundational ideas:

1. **Next-token prediction:** the central objective behind conventional autoregressive language models.
2. **The generation loop:** predicting, selecting, appending, and repeating tokens.
3. **What an LLM is not:** distinguishing model inference from databases, search engines, deterministic programs, and literal answer storage.
4. **One model, many tasks:** understanding how a shared language-model capability supports different applications.
5. **Where capability comes from:** understanding the contributions of data, model scale, compute, architecture, and training.

## One-Line Mental Model

> Think of an LLM as a learned probability model that repeatedly predicts what token should come next, using the preceding context to generate a sequence of tokens.

## Prerequisites

| Prerequisite | Required Understanding |
|---|---|
| Basic Python | Variables, strings, lists, loops, and functions |
| Probability | A probability distribution assigns likelihoods to possible outcomes |
| Basic machine learning | Models learn patterns from data during training |
| Basic linear algebra | Vectors and matrices are useful background, but not required yet |
| Text processing | Text can be split into smaller units called tokens |

## Learning Outcomes

After mastering this module, you should be able to:

- Explain an LLM in plain English and technical terms.
- Describe next-token prediction mathematically.
- Walk through a text-generation loop step by step.
- Explain why an LLM is not inherently a database or search engine.
- Explain how one model performs many different tasks.
- Distinguish training from inference.
- Describe how data quality, compute, model scale, and training methods affect capabilities.
- Implement a simplified next-token prediction demonstration in Python.
- Answer foundational LLM interview questions accurately.

---

# 2. What Is an LLM?

## Technical Definition

A Large Language Model is a neural network trained on large collections of data to learn statistical patterns in token sequences and assign probabilities to possible continuations of a context.

A conventional autoregressive LLM models a sequence using the chain rule of probability:

\[
P(x_1,\ldots,x_n)=\prod_{t=1}^{n}P(x_t\mid x_1,\ldots,x_{t-1})
\]

Where:

- \(x_t\) is the token at position \(t\).
- \(x_1,\ldots,x_{t-1}\) are the preceding tokens.
- \(P(x_t\mid x_1,\ldots,x_{t-1})\) is the conditional probability of the current token given the preceding context.

During training, the model learns parameters that help it predict tokens from context. During inference, it uses those learned parameters to produce probability distributions and generate outputs.

Many modern LLMs use the Transformer architecture, although language models are not defined exclusively by one architecture.

## Plain-English Definition

Imagine reading this sentence:

> The capital of Nepal is ...

You would probably predict the word "Kathmandu."

An LLM performs a more sophisticated version of this process. It converts the preceding text into numerical representations, processes the context through a neural network, and assigns scores to possible next tokens.

For example:

| Candidate Token | Illustrative Probability |
|---|---:|
| Kathmandu | 0.82 |
| Pokhara | 0.05 |
| Nepal | 0.03 |
| Other tokens combined | 0.10 |

These values are illustrative, not measurements from an actual model.

The model then selects a token according to its decoding strategy, appends that token to the context, and predicts again.

**Important:** the model does not necessarily select the most probable token at every step. Sampling strategies can select a less probable token, depending on the probability distribution and decoding settings.

## Key Terminology

| Term | Definition | Why It Matters |
|---|---|---|
| LLM | A large neural language model trained to model token sequences | The central component of many generative AI systems |
| Token | A unit of text processed by a tokenizer | Models operate on tokens rather than raw text directly |
| Tokenizer | Software that maps text to token IDs and back | Affects input length, cost, and context usage |
| Vocabulary | The set of token IDs a model can represent as output | Determines which token units are available |
| Context | The preceding tokens available to the model for its current prediction | Influences the next-token distribution |
| Next-token prediction | Predicting the next token from preceding context | The core objective of autoregressive language modeling |
| Parameters | Learned numerical values inside the neural network | Store the model's learned statistical patterns |
| Logits | Raw scores produced for possible next tokens | Used to calculate token probabilities |
| Softmax | A mathematical transformation from logits to probabilities | Converts scores into a probability distribution |
| Inference | Running a trained model to obtain predictions or outputs | The basis of using an LLM in an application |
| Training | Adjusting model parameters using a learning objective | Develops the model's learned capabilities |
| Decoding | The procedure for selecting output tokens | Controls how the model generates text |
| Context window | The maximum amount of token context a model can process in a particular configuration | Limits how much information can be considered at once |
| Hallucination | An output that presents unsupported or false information | A key reliability problem for AI engineers |
| Autoregressive model | A model that predicts sequence elements conditioned on preceding elements | Explains sequential text generation |

## Anatomy of an LLM

A simplified autoregressive Transformer LLM has the following structure:

```text
Input text
"The capital of Nepal is"
        |
        v
Tokenizer
Text -> token IDs
        |
        v
Embedding and positional information
Token IDs -> numerical representations
        |
        v
Transformer layers
Attention + feed-forward networks + other components
        |
        v
Output projection
One logit per possible next token
        |
        v
Probability distribution and decoding
Choose the next token
        |
        v
Generated token
Append it and repeat
```

This diagram describes a common decoder-only Transformer. Other language-model architectures may differ.

### The Essential Distinction

The neural network does not directly output a finished paragraph in one ordinary next-token prediction step. It produces scores for possible next tokens. A decoding procedure selects a token, and repeated inference steps produce the sequence.

Some implementations optimize this process with caching, batching, or speculative decoding, but the conceptual generation loop remains useful.

## What an LLM Is Not

### An LLM Is Not Inherently a Database

A database stores structured records or documents that can be retrieved through queries. An LLM stores learned numerical parameters.

For example, a university database might contain:

```text
Course: Computer Networks
Credits: 3
Instructor: Example Instructor
```

An LLM might generate a plausible answer about that course from its learned patterns, but that does not establish that the answer matches the university's actual records.

**Engineering implication:** use a database or retrieval system when an answer must be grounded in authoritative records.

### An LLM Is Not Inherently a Search Engine

A search engine retrieves and ranks documents from an index. A standalone LLM generates predictions from its input context and learned parameters.

An application can connect an LLM to a search engine, browser, or retrieval system. In that case, the complete application combines multiple components; the LLM itself has not become the search index.

### An LLM Is Not a Deterministic Program in the Ordinary Rule-Based Sense

A traditional program may implement explicit rules:

```python
def classify_temperature(celsius):
    if celsius >= 38:
        return "Fever"
    return "No fever"
```

Given the same input and execution conditions, this function returns the same result.

An LLM instead computes outputs using learned parameters and a decoding procedure. Its output can vary with sampling, configuration, context, model version, or execution details.

Greedy decoding with fixed settings can be repeatable, but determinism is not a universal guarantee across all serving systems.

### An LLM Is Not a Repository of Verbatim Answers

An LLM can reproduce memorized text in some circumstances. However, its parameters are not normally an indexed collection of every training example and its corresponding answer.

It generates text from learned representations and the current context. Memorization and generalization can both occur.

### An LLM Is Not Automatically a Reasoning Engine With Guaranteed Correctness

An LLM may solve complex problems by learning useful patterns and generating intermediate reasoning or tool requests. Nevertheless, it can produce invalid logic, unsupported claims, arithmetic errors, and convincing explanations for incorrect answers.

The quality of the answer must be evaluated rather than inferred from how confidently it is written.

---

# 3. Why LLMs Matter

## Why This Discipline Exists

Before building applications with LLMs, engineers must understand the mechanism that produces their outputs. Otherwise, it is easy to treat generated text as verified information, expect exact reproducibility, or use a model when a conventional software component would be more appropriate.

Understanding LLM fundamentals helps engineers answer practical questions:

- Should this task use an LLM, a database query, or a deterministic function?
- Why did the model produce an incorrect answer?
- Why does adding relevant context improve some answers?
- Why can a model write code and translate languages using the same architecture?
- Why can a larger model still fail on a simple question?
- When should an application use retrieval, tools, or external validation?

The goal is not merely to understand how a model generates text. It is to understand how to build reliable systems around it.

## Impact Table

| Area | Without Understanding LLMs | With Understanding LLMs |
|---|---|---|
| Application design | Uses an LLM for every problem | Selects the appropriate component for each task |
| Accuracy | Assumes fluent output is correct | Validates claims and grounds answers in evidence |
| Cost | Makes unnecessary model calls | Uses appropriate models and efficient workflows |
| Latency | Ignores repeated generation steps | Understands prompt processing and token generation costs |
| Debugging | Treats every failure as a prompt problem | Investigates context, decoding, data, model behavior, and system design |
| Security | Trusts all model-generated instructions | Applies access controls and treats external content as untrusted |
| Evaluation | Judges outputs by intuition alone | Measures quality using representative test cases |
| Scalability | Builds a single oversized workflow | Separates retrieval, inference, business logic, and validation |

## Real-World Use Cases

These examples illustrate how LLM capabilities are used in products; they do not imply that every product relies exclusively on an LLM.

1. **Conversational assistants — ChatGPT:** generate responses to user questions, follow instructions, summarize information, and assist with problem-solving.
2. **Code generation — GitHub Copilot:** predict code tokens from surrounding code, comments, and other context.
3. **Translation — Google Translate:** language models can map input in one language to output in another; the complete translation system may use different architectures and specialized components.
4. **Document assistance — Notion AI:** rewrite, summarize, extract, and transform text using natural-language instructions.
5. **Search-assisted answering — Perplexity:** combine language generation with retrieval and cited sources to answer questions about external information.
6. **Customer support:** classify incoming requests, draft replies, summarize customer conversations, and route issues to the appropriate team.

## LLMs Versus Alternatives

| Situation | Use an LLM | Use an Alternative | Why |
|---|---|---|---|
| Summarize an unstructured document | Usually yes | Extractive summarization for strict requirements | LLMs can generate concise semantic summaries |
| Retrieve an exact account balance | Only as an interface, if needed | Database or financial API | The value must come from an authoritative source |
| Perform a fixed tax calculation | Usually not for the calculation itself | Tested calculation function or rules engine | Explicit arithmetic is easier to verify |
| Classify nuanced customer messages | Often useful | Traditional classifier or rules for simpler cases | Language context and ambiguity may matter |
| Find the latest news | Use with retrieval or search tools | Search engine or news API | Model parameters alone do not guarantee current information |
| Generate a first draft of code | Often useful | Templates for highly repetitive, fixed code | Language generation helps with flexible requirements |
| Enforce authorization | No, not as the authority | Application access-control logic | Security decisions must not depend solely on generated text |
| Answer questions about private university documents | Use with retrieval and access controls | Search or document lookup alone | Generation can explain retrieved content in natural language |

**Decision principle:** use an LLM when flexible interpretation or generation provides value. Use deterministic components for exact computation, authoritative data access, and enforceable rules. Combine them when a task requires both.

---

# 4. How an LLM Works

## Step-by-Step Mechanism

Consider the prompt:

> Explain machine learning in simple terms.

A typical autoregressive LLM generates a response as follows.

1. **Receive the input.** The application sends the prompt, system instructions, conversation history, and any other included context to the model.
2. **Tokenize the input.** The tokenizer converts the input into token IDs. A token can represent a whole word, part of a word, punctuation, or another text unit.
3. **Convert token IDs into representations.** The model maps tokens into vectors and incorporates positional information so it can process the sequence.
4. **Process the context.** Transformer layers process the representations using attention and feed-forward computations. In a standard causal language model, attention is restricted so a position cannot access future target tokens.
5. **Produce next-token logits.** The model calculates a score for every token in its output vocabulary for the next position.
6. **Convert logits into probabilities.** A softmax transformation can convert the scores into a probability distribution. Temperature and other decoding controls may modify the distribution.
7. **Select a token.** The decoding strategy chooses the next token. Options include greedy decoding, sampling, and top-p sampling.
8. **Append the token.** The selected token is added to the generated sequence. It becomes part of the context for subsequent predictions.
9. **Repeat.** The model predicts another token, selects it, and continues until a stopping condition is met, such as an end-of-sequence token or an output-length limit.
10. **Decode and return the result.** The generated token sequence is converted into text and returned to the application.

## The Generation Loop

```text
Prompt + generated context
          |
          v
Run model forward pass
          |
          v
Calculate next-token distribution
          |
          v
Decode: select a token
          |
          v
Append token to sequence
          |
          v
Stop condition met? ---- Yes ----> Return output
          |
          No
          |
          +-----------------------> Predict again
```

The diagram represents the conceptual process. Production implementations can process multiple sequences together and reuse intermediate computations.

## Mathematical Foundations

### A. Next-Token Probability

Let the input context be:

\[
x_{1:t}=(x_1,x_2,\ldots,x_t)
\]

The model predicts a distribution over the next token:

\[
P(x_{t+1}\mid x_1,\ldots,x_t)
\]

Suppose the context is:

> The sky is

The model might assign the following illustrative probabilities:

| Next Token | Probability |
|---|---:|
| blue | 0.55 |
| clear | 0.18 |
| cloudy | 0.15 |
| falling | 0.02 |
| Other tokens | 0.10 |

These numbers demonstrate the concept rather than actual model measurements.

The model predicts a distribution, not a guaranteed truth. Even a highly probable continuation can be wrong in a particular context.

### B. Logits and Softmax

Let \(z_i\) denote the logit associated with vocabulary token \(i\). The probability of selecting that token can be calculated using softmax:

\[
P(x=i)=\frac{e^{z_i}}{\sum_{j=1}^{V}e^{z_j}}
\]

Where:

- \(z_i\) is the score for token \(i\).
- \(V\) is the vocabulary size.
- The denominator sums exponentiated scores over the vocabulary.

Softmax ensures that probabilities are nonnegative and sum to one, subject to numerical precision.

### C. Training With Cross-Entropy Loss

During standard next-token training, the model is given sequences and learns to predict their next tokens.

For a target token \(x_t\), the negative log-likelihood loss is:

\[
\mathcal{L}_t=-\log P_\theta(x_t\mid x_{<t})
\]

Here, \(\theta\) represents the model parameters and \(x_{<t}\) represents the preceding tokens.

Across a training sequence, a simplified objective is:

\[
\mathcal{L}(\theta)=-\frac{1}{T}
\sum_{t=1}^{T}\log P_\theta(x_t\mid x_{<t})
\]

Training uses optimization algorithms to update parameters and reduce this loss over the training data.

A lower training loss means the model assigns higher probability to observed target tokens on that data. It does **not** automatically mean the model is factually accurate, safe, or good at every downstream task.

### D. How Generation Differs From Training

| Training | Inference |
|---|---|
| Uses training examples | Uses a supplied prompt and context |
| Computes prediction errors against target tokens | Uses predictions to generate output tokens |
| Updates model parameters | Normally keeps model parameters fixed |
| Requires optimization and backpropagation | Requires forward computations and decoding |
| Optimizes a learning objective | Produces an application output |

An application may use inference-time tools, external retrieval, or other additional processing. These are separate from the model's ordinary next-token prediction operation.

## Key Parameters

There is no universal default for every model or API. The values below are common conceptual ranges, not guaranteed settings.

| Parameter | Typical Range or Setting | Increasing It | Decreasing It |
|---|---|---|---|
| Temperature | Commonly 0–2, API-dependent | Flattens the distribution, generally increasing randomness | Sharpens the distribution, generally reducing randomness |
| Top-p | \(0 < p \leq 1\) | Includes more of the probability distribution for sampling | Restricts sampling to a smaller cumulative probability mass |
| Top-k | Positive integer; optional | Allows more candidate tokens | Restricts the candidate set |
| Maximum output tokens | Positive integer, model-dependent | Allows longer responses and potentially more cost | Truncates responses sooner |
| Context length | Model-dependent token limit | Allows more context if the model and service support it | Restricts available context |
| Batch size | Workload-dependent | Can improve throughput but requires more memory | May reduce memory use but lower throughput |
| Model size | Architecture-dependent | Can improve capability when training and data scale appropriately, while increasing resource needs | Reduces resource requirements but may reduce capability |

**Important distinctions:**

- Temperature changes the sampling distribution; it does not retrain the model.
- A temperature of zero often corresponds to greedy-like decoding in APIs, but exact behavior is implementation-dependent.
- Top-p and top-k control sampling candidates. They do not increase the model's underlying knowledge.
- A larger context window does not guarantee that the model will use every part of the context correctly.

## Failure Modes

| Failure | Root Cause | How to Detect | Fix |
|---|---|---|---|
| Hallucination | The model generates plausible but unsupported content | Compare claims with trusted sources | Add retrieval, verification, and abstention behavior |
| Repetitive text | Decoding behavior, prompt structure, or learned repetition patterns | Inspect repeated phrases and token sequences | Adjust decoding, prompts, or repetition controls |
| Truncated answer | Output limit or interruption | Check completion status and ending | Increase limits where appropriate or continue generation |
| Incorrect answer despite clear wording | Insufficient model capability, ambiguous context, or reasoning failure | Test against known answers | Improve context, use tools, evaluate another model |
| Poor response to long context | Lost or underused information, context truncation, or attention limitations | Test relevant facts at different context positions | Retrieve relevant passages and reduce irrelevant context |
| Unstable responses | Sampling, changing context, model versions, or execution differences | Repeat tests with controlled settings | Fix versions and decoding settings; evaluate multiple runs |
| Incorrect tokenization assumptions | Token boundaries differ from words | Inspect token IDs or tokenizer output | Use the model's actual tokenizer |
| Excessive latency | Long prompts, large models, or many generated tokens | Measure time to first token and generation speed | Reduce unnecessary context, optimize serving, or choose a suitable model |

---

# 5. Core Concepts and Techniques

## Technique 1: Next-Token Prediction

**WHAT:** A language-modeling objective in which the model predicts the next token from the preceding context.

**WHY:** Predicting tokens across large and diverse datasets teaches the model patterns in language, syntax, code, facts, and many forms of structured text.

**WHEN:** Whenever you need to explain the basic behavior of an autoregressive LLM or understand how it is trained.

**HOW:**

1. Supply preceding tokens.
2. Compute next-token logits.
3. Convert scores into probabilities.
4. Calculate a training loss or select a token during generation.

**MISTAKE:** Assuming next-token prediction means the model always selects the most probable token or simply copies text from its training data.

### Code Example: A Toy Next-Token Predictor

```python
# Illustrate next-token prediction using a manually defined distribution.
# This is a demonstration, not a trained neural language model.

from collections import defaultdict

# Each context maps to possible next tokens and their probabilities.
next_token_probs = {
    ("the", "sky"): {"is": 0.9, "looks": 0.1},
    ("sky", "is"): {"blue": 0.8, "clear": 0.2},
}

context = ("the", "sky")
distribution = next_token_probs[context]

# Select the highest-probability token.
predicted_token = max(distribution, key=distribution.get)

print("Context:", " ".join(context))
print("Distribution:", distribution)
print("Predicted token:", predicted_token)

# OUTPUT:
# Context: the sky
# Distribution: {'is': 0.9, 'looks': 0.1}
# Predicted token: is
```

The probabilities are hard-coded. A real LLM calculates its distribution using learned neural-network parameters.

## Technique 2: Autoregressive Generation

**WHAT:** Generating a sequence one token at a time, using previously supplied and generated tokens as context.

**WHY:** Each new prediction can depend on the preceding sequence, allowing the model to produce sentences, paragraphs, code, and other token sequences.

**WHEN:** When explaining text generation, output-length limits, stopping conditions, and inference latency.

**HOW:**

1. Initialize the context with a prompt.
2. Predict a distribution for the next token.
3. Select a token using a decoding strategy.
4. Append it to the context.
5. Repeat until a stopping condition is reached.

**MISTAKE:** Thinking the model generates a complete response in a single ordinary next-token prediction. It usually performs multiple sequential generation steps.

### Generation Trace

Starting prompt: `AI engineering is`

| Step | Context Before Prediction | Selected Token |
|---|---|---|
| 1 | `AI engineering is` | `about` |
| 2 | `AI engineering is about` | `building` |
| 3 | `AI engineering is about building` | `reliable` |
| 4 | `AI engineering is about building reliable` | `systems` |

Illustrative final sequence:

`AI engineering is about building reliable systems`

This is one possible generation, not a guaranteed continuation.

## Technique 3: Decoding Strategies

**WHAT:** Decoding is the method used to select the next token from the model's output scores or probability distribution.

**WHY:** The model can assign probabilities to many possible continuations. Decoding determines which continuation is actually generated.

**WHEN:** When tuning output diversity, repeatability, and response style.

**HOW:**

- **Greedy:** select the highest-scoring token.
- **Sampling:** draw a token from a probability distribution.
- **Top-k:** retain the \(k\) highest-scoring candidates before sampling.
- **Top-p:** retain a set of candidates whose cumulative probability reaches a chosen threshold, then sample.

**MISTAKE:** Assuming that higher randomness always improves creativity or that greedy decoding guarantees factual correctness.

| Strategy | Main Behavior | Typical Consideration |
|---|---|---|
| Greedy | Selects the highest-probability token at each step | Repeatable under fixed conditions, but may be repetitive |
| Random sampling | Samples from the distribution | Supports diverse continuations |
| Top-k sampling | Samples among a limited number of candidates | Removes low-ranked candidates |
| Top-p sampling | Samples from a probability-mass-based candidate set | Adapts candidate count to the distribution |
| Beam search | Maintains multiple candidate sequences and scores them | Useful in some sequence tasks; not automatically best for chat |

These strategies affect how the model's learned distribution is used, rather than changing the underlying trained weights.

## Technique 4: One Model, Many Tasks

**WHAT:** A sufficiently capable language model can respond to different tasks through the same underlying next-token prediction mechanism.

**WHY:** Diverse training data exposes the model to many patterns and formats. Instruction tuning and related post-training methods can teach it to follow task instructions.

**WHEN:** When choosing whether to build separate applications or task-specific models for writing, translation, classification, summarization, and coding.

**HOW:**

1. Provide task instructions.
2. Include the relevant input.
3. Specify the expected output format where useful.
4. Let the same model generate a task-appropriate continuation.

**MISTAKE:** Assuming one model performs every task equally well or that prompt wording alone guarantees a correct result.

| Task | Example Prompt | Expected Output |
|---|---|---|
| Writing | `Write a short paragraph about Nepal.` | A paragraph |
| Summarization | `Summarize this report in three sentences: ...` | A condensed version |
| Translation | `Translate "Good morning" into Nepali.` | A translation |
| Coding | `Write a Python function that reverses a string.` | Code |
| Classification | `Classify this review as positive or negative: ...` | A label |
| Question answering | `According to this passage, what is the deadline? ...` | An answer based on the passage |

The task changes, but the underlying model still generates tokens conditioned on its context.

### Why Instruction Tuning Matters

Pretraining exposes a model to broad patterns in data. Instruction tuning further trains it on examples of instructions and appropriate responses, making it more useful as an assistant.

Other post-training methods can further shape behavior, preferences, tool use, and safety. Next-token prediction remains an important foundation, but it is not the only training objective used across modern model development.

## Technique 5: Where Capability Comes From

**WHAT:** Model capability emerges from the interaction of architecture, data, compute, parameter scale, optimization, and post-training.

**WHY:** A model needs sufficient learning capacity, informative training examples, and effective optimization to learn useful patterns.

**WHEN:** When comparing models, interpreting scaling claims, selecting a model for a product, or planning training experiments.

**HOW:**

1. Collect and filter suitable data.
2. Choose an architecture and model size.
3. Allocate training compute.
4. Optimize model parameters against the learning objective.
5. Evaluate on held-out data and relevant tasks.
6. Apply appropriate post-training and safety evaluations.

**MISTAKE:** Assuming that increasing parameter count or compute alone guarantees better results. Data quality, optimization, architecture, inference budget, and evaluation all matter.

### The Main Contributors

| Contributor | How It Helps | Limitation |
|---|---|---|
| Data quality | Provides informative, relevant, and accurate examples | Poor data can teach misleading patterns |
| Data diversity | Exposes the model to varied tasks, domains, and formats | Imbalanced data can create capability gaps |
| Model size | Increases representational capacity | Larger models generally require more resources |
| Training compute | Enables more optimization steps or larger training runs | Inefficient training can waste compute |
| Architecture | Determines how information is represented and processed | No architecture is best for every workload |
| Training procedure | Controls optimization, data exposure, and learning behavior | Poor optimization can undermine otherwise strong components |
| Post-training | Improves instruction following, preferences, and task behavior | Does not eliminate hallucinations or all failure modes |
| Evaluation | Identifies strengths, weaknesses, and regressions | Poor test design creates misleading confidence |

### Scale Versus Capability

A larger model may outperform a smaller one when trained appropriately, but the relationship is not automatic.

A smaller model trained on relevant, high-quality data can outperform a larger model on a narrow specialized task. A larger general model may offer broader capabilities, while requiring greater serving resources.

**Engineering lesson:** choose models based on measured performance on your actual task, not parameter count alone.

---

# 6. Advanced Strategies and Production Patterns

This module focuses on conceptual foundations, but an AI engineer must understand how those foundations affect production system design.

## Pattern 1: Separate Generation From Verification

An LLM can generate a useful response without establishing that its claims are true. A reliable application separates the generation process from checks that validate important outputs.

```text
User request
     |
     v
LLM generates a candidate answer
     |
     v
Validate against rules, evidence, or tools
     |
     v
Return, revise, or abstain
```

Examples of validation:

- Check generated JSON against a schema.
- Run generated arithmetic through a trusted calculation function.
- Verify citations against retrieved documents.
- Run generated code through tests in an isolated environment.
- Check whether a requested operation is authorized before executing it.

Validation does not need to be another LLM call. Deterministic checks are often preferable when the requirements can be expressed as explicit rules.

## Pattern 2: Ground Answers With Retrieval

When a question depends on current or private information, the model may not possess the relevant facts in its parameters.

A retrieval-augmented generation (RAG) system addresses this by retrieving relevant external information and including it in the model's context.

```text
User question
     |
     v
Retrieve relevant documents
     |
     v
Rank and filter passages
     |
     v
Construct grounded prompt
     |
     v
LLM generates an answer
     |
     v
Validate claims and citations
     |
     v
Return answer
```

This pattern is useful for university policies, internal documentation, product manuals, and other changing or organization-specific knowledge.

**Limitations:** retrieval can return irrelevant or outdated documents, and the model can still misinterpret the retrieved content. RAG reduces certain knowledge and grounding problems; it does not guarantee zero hallucinations.

## Pattern 3: Treat Model Output as Untrusted Input

Never assume that generated text is safe to execute or that external content included in the prompt is trustworthy.

Production safeguards include:

- Schema validation for structured output.
- Parameterized database queries.
- Allowlisted tools and operations.
- Explicit authorization checks.
- Sandboxed code execution.
- Limits on tokens, execution time, and tool calls.
- Protection against prompt injection and data exfiltration.
- Logging and monitoring that respect privacy requirements.

For example, a model may suggest a SQL query. The application should still validate the operation and enforce database permissions rather than blindly executing the text.

## Scalability and Performance

**Time to first token (TTFT):** the time between submitting a request and receiving its first generated token.

**Inter-token latency:** the time between successive generated tokens during streaming.

A long prompt can increase the cost of processing the input. Generating more tokens also takes additional decoding work.

Common optimizations include:

- **KV caching:** reuses previously computed attention key and value tensors during autoregressive generation.
- **Continuous batching:** combines requests that are at different generation stages to improve serving utilization.
- **Quantization:** represents weights or other computations with lower-precision formats to reduce resource use, potentially at some quality cost.
- **Speculative decoding:** uses a draft model or another proposal mechanism to accelerate generation when proposed tokens can be efficiently verified.
- **Prompt reduction:** removes irrelevant context and redundant instructions.
- **Model routing:** directs tasks to models that meet the required quality, latency, and cost targets.

These optimizations do not change the basic conceptual distinction between training and inference.

## Reliability and Observability

A production LLM system should track more than whether the API returned HTTP 200.

| Metric | What It Tells You |
|---|---|
| Task success rate | Whether the output satisfies the user's actual requirement |
| Groundedness | Whether factual claims are supported by supplied evidence |
| Output schema validity | Whether structured outputs follow the expected format |
| Refusal quality | Whether the system appropriately declines unsupported or unsafe requests |
| TTFT | How quickly users receive the first token |
| Tokens per second | Generation throughput |
| Cost per successful task | Cost relative to useful outcomes |
| Regression rate | Whether model, prompt, or infrastructure changes degrade performance |

Evaluate the system on representative tasks, including ambiguous inputs, long contexts, adversarial prompts, and cases where the correct response is to say that the information is unavailable.

---

# 7. Practical Code Examples

**Coding requirement: Light.** These examples demonstrate the generation mechanism without pretending to implement a real LLM from scratch.

## Example 1: Simulate Autoregressive Text Generation

**Purpose:** Observe how a sequence grows one token at a time.

**Requirements:** Python 3. No external libraries.

```python
# ── Simulate autoregressive token generation ──

# A tiny manually defined model maps contexts to possible next tokens.
# Real LLMs calculate these distributions using neural networks.
next_token_probs = {
    ("AI",): {"engineering": 1.0},
    ("AI", "engineering"): {"builds": 1.0},
    ("AI", "engineering", "builds"): {"systems": 1.0},
    ("AI", "engineering", "builds", "systems"): {"END": 1.0},
}

def generate(prompt, max_new_tokens=5):
    # Split the prompt into a simple word-based context.
    tokens = prompt.split()

    for _ in range(max_new_tokens):
        context = tuple(tokens)

        # Stop if this toy model has no rule for the current context.
        distribution = next_token_probs.get(context)
        if distribution is None:
            break

        # Greedy decoding: choose the highest-probability token.
        next_token = max(distribution, key=distribution.get)

        # Stop on the toy end marker.
        if next_token == "END":
            break

        # Append the selected token to the context.
        tokens.append(next_token)

    return " ".join(tokens)

print(generate("AI"))

# OUTPUT:
# AI engineering builds systems
```

**What this teaches:** the context changes after each prediction. The next prediction uses the expanded sequence.

**What it does not teach:** neural-network training, attention, learned probabilities, subword tokenization, or the computational cost of a real model.

## Example 2: Explore How Decoding Changes Token Selection

**Purpose:** Compare greedy selection with seeded sampling using a toy probability distribution.

**Requirements:** Python 3. No external libraries.

```python
# ── Demonstrate greedy decoding and probability sampling ──

import random

distribution = {
    "blue": 0.70,
    "clear": 0.20,
    "cloudy": 0.10,
}

def greedy_decode(probabilities):
    # Select the candidate with the highest probability.
    return max(probabilities, key=probabilities.get)

def sample_decode(probabilities, seed=42):
    # A fixed seed makes this toy example reproducible.
    rng = random.Random(seed)

    # Weighted sampling chooses according to the supplied probabilities.
    tokens = list(probabilities.keys())
    weights = list(probabilities.values())

    return rng.choices(tokens, weights=weights, k=1)[0]

print("Greedy:", greedy_decode(distribution))
print("Sampled:", sample_decode(distribution))

# OUTPUT:
# Greedy: blue
# Sampled: blue
```

The sampled token happens to be `blue` for this seed. Other seeds can produce different tokens.

The sampling distribution here is manually specified. In a real LLM, logits and decoding settings determine the distribution used for selection.

## Practice Exercise

Modify Example 1 so that it:

1. Generates from a different prompt.
2. Stops after three new tokens.
3. Uses two possible next tokens for one context.
4. Explains why the same prompt could yield different outputs in a sampling-based implementation.

---

# 8. Common Mistakes and How to Fix Them

## Mistakes Table

| # | Mistake | Root Cause | Symptom | Fix |
|---:|---|---|---|---|
| 1 | Treating an LLM as a database | Confusing learned parameters with explicit records | Incorrect answers about exact records | Retrieve authoritative data |
| 2 | Believing the model always chooses the most probable token | Confusing probability prediction with decoding | Unexpected but plausible continuations | Learn greedy and sampling-based decoding |
| 3 | Assuming the model understands every output it generates | Equating fluent text with correctness | Confident factual errors | Test outputs against evidence and task-specific checks |
| 4 | Believing all LLMs use identical architectures | Overgeneralizing from decoder-only Transformers | Incorrect architectural explanations | Distinguish the language-modeling objective from the architecture |
| 5 | Assuming a larger model is always better | Treating parameter count as the only capability factor | Higher cost without meaningful improvement | Benchmark candidates on representative tasks |
| 6 | Treating temperature as a knowledge parameter | Confusing decoding with training | More varied answers without improved factual accuracy | Tune decoding for the intended behavior |
| 7 | Ignoring tokenization | Treating words and tokens as identical | Incorrect token counts and cost estimates | Use the appropriate tokenizer or API usage data |
| 8 | Assuming next-token training is the only training objective in every modern system | Confusing a foundational objective with a complete training recipe | Oversimplified explanations of assistant behavior | Distinguish pretraining, instruction tuning, and other post-training methods |
| 9 | Assuming retrieval guarantees correctness | Treating retrieved evidence as automatically reliable | Answers based on irrelevant or stale passages | Evaluate retrieval and verify claims |
| 10 | Assuming fixed prompts guarantee fixed outputs | Ignoring decoding and serving conditions | Inconsistent results across runs | Control settings and versions; test repeatability |
| 11 | Ignoring the output limit | Assuming the model always finishes its response | Truncated code or incomplete explanations | Set suitable limits and handle incomplete outputs |
| 12 | Evaluating only a few successful examples | Confirmation bias and weak test coverage | Failures appear after deployment | Use representative evaluation datasets and regression tests |

## Top Three Misconceptions

1. **"An LLM searches its database of answers."**  
   **Truth:** A conventional LLM generates predictions using learned parameters and the current context. It may memorize some training content, and an application may add external retrieval, but neither fact makes the model itself a conventional database.

2. **"Next-token prediction means an LLM only predicts the next word."**  
   **Truth:** The model predicts the next token, which may be a complete word, part of a word, punctuation, or another token unit. Repeated predictions produce a sequence.

3. **"If the model is large enough, it will always produce correct answers."**  
   **Truth:** Capability depends on many factors, including data, architecture, training, context, post-training, and the task. Even highly capable models can produce false or unsupported statements.

## The One Thing Most Engineers Get Wrong

The most consequential mistake is confusing the quality of generated language with the reliability of the underlying answer. An LLM is optimized to produce plausible continuations according to what it has learned and the context it receives; that objective is not identical to verifying every claim against reality. A production AI engineer must therefore distinguish generation from verification and combine the model with retrieval, deterministic tools, evaluation, permissions, and validation wherever the application requires reliable results.

---

# 9. Interview Preparation

These questions cover the foundational understanding expected of an AI engineer working with LLM-powered applications. Practice explaining the core mechanism first, then expand into mathematical and production details.

## Conceptual Interview Questions

### Q1. What is a Large Language Model?

**Answer:**  
A Large Language Model is a neural network trained on large amounts of data to model sequences of tokens. It learns patterns in the training data and uses the preceding context to predict possible next tokens. During generation, it repeatedly selects tokens to produce text, code, or other supported output formats.

### Q2. What is next-token prediction?

**Answer:**  
Next-token prediction is the task of estimating the probability distribution of the next token given the preceding tokens.

\[
P(x_{t+1}\mid x_1,\ldots,x_t)
\]

The model learns to predict tokens from training examples. During inference, a decoding procedure uses the predicted distribution to select the next token.

### Q3. How does an LLM generate a complete paragraph?

**Answer:**  
The model receives a prompt, tokenizes it, and processes the resulting sequence. It produces logits for the next token, which can be converted into probabilities. A decoding strategy selects a token, which is appended to the context. The process repeats until a stopping condition is reached.

### Q4. Is an LLM a database?

**Answer:**  
No. A database stores and retrieves explicit records, whereas an LLM primarily represents learned patterns in neural-network parameters. A model may memorize parts of its training data, but it does not function like a conventional indexed database. When exact or current information is required, an application should retrieve it from an authoritative source.

### Q5. Is an LLM a search engine?

**Answer:**  
Not inherently. A search engine retrieves and ranks documents, while a standalone LLM generates outputs from its context and learned parameters. An AI application can combine both by retrieving documents and asking the model to synthesize an answer.

### Q6. Why can one model perform so many different tasks?

**Answer:**  
A model trained on diverse data learns general patterns in language, code, and other sequences. Task instructions and input context can guide the model toward different kinds of outputs. Instruction tuning can further improve its ability to follow requests. The underlying next-token prediction mechanism can support writing, translation, classification, summarization, and question answering without requiring a separate model for every task.

### Q7. What is the difference between training and inference?

**Answer:**  
Training adjusts the model's parameters to optimize a learning objective using data. Inference uses the trained parameters to produce predictions or outputs. Ordinary inference does not update the model's weights.

### Q8. Why do LLMs hallucinate?

**Answer:**  
The next-token prediction objective does not guarantee factual verification. A model can generate a plausible continuation even when its context lacks sufficient evidence. Hallucinations can also arise from ambiguous prompts, limitations in learned patterns, or reasoning errors. Retrieval, external tools, verification, and calibrated abstention can reduce particular failure modes.

### Q9. Does a larger LLM always perform better?

**Answer:**  
No. Larger models can offer greater representational capacity, but capability also depends on data quality, architecture, training compute, optimization, post-training, and the evaluation task. A smaller specialized model may outperform a larger general model on a particular workload.

### Q10. What is the difference between a token and a word?

**Answer:**  
A word is a linguistic unit, while a token is a unit defined by a model's tokenizer. A token may represent a whole word, part of a word, punctuation, or another sequence element. Consequently, the number of tokens in a passage is not necessarily equal to its word count.

### Q11. What is the difference between logits and probabilities?

**Answer:**  
Logits are the raw scores a model produces for possible next tokens. Softmax can transform these scores into a normalized probability distribution. A decoding strategy then selects a token using that distribution or a transformation of it.

### Q12. What does temperature do?

**Answer:**  
Temperature modifies the sharpness of the probability distribution used for decoding. Lower temperatures generally favor high-probability tokens, while higher temperatures generally increase diversity. Temperature does not retrain the model or guarantee greater factual accuracy.

### Q13. What is an autoregressive model?

**Answer:**  
An autoregressive model represents a sequence by conditioning each element on preceding elements. In a conventional autoregressive language model, the joint sequence probability is expressed as a product of conditional next-token probabilities.

### Q14. Why can the same prompt produce different answers?

**Answer:**  
Sampling-based decoding can select different tokens from the same distribution. Differences may also arise from model versions, hidden context, system instructions, tool results, or nondeterministic serving behavior. Fixed settings can improve repeatability, but exact reproducibility depends on the implementation.

### Q15. Does next-token prediction mean that an LLM cannot reason?

**Answer:**  
No. Next-token prediction describes a training objective and generation mechanism, not a complete statement about every capability that can emerge. A model can learn patterns useful for multi-step problem-solving and generate intermediate steps. However, this does not guarantee valid reasoning or correct conclusions.

## Technical Interview Questions

### Q16. Write the Mathematical Expression for Autoregressive Language Modeling

**Answer:**

Using the chain rule:

\[
P(x_1,\ldots,x_T)=\prod_{t=1}^{T}P(x_t\mid x_{<t})
\]

For a standard causal language model, the training objective often minimizes average negative log-likelihood:

\[
\mathcal{L}(\theta)=-\frac{1}{T}\sum_{t=1}^{T}
\log P_\theta(x_t\mid x_{<t})
\]

Here, \(x_{<t}\) represents the preceding tokens and \(\theta\) represents model parameters.

### Q17. Why Are Causal Masks Used in Decoder-Only Transformers?

**Answer:**  
Causal masks prevent a token position from attending to future token positions during standard autoregressive training and inference. This preserves the condition that the model must predict the next token using only permitted preceding context, rather than seeing the target's future information.

### Q18. How Can a Model Learn Grammar Without Explicit Grammar Rules?

**Answer:**  
During training, the model repeatedly receives examples in which token sequences have statistical and structural patterns. Optimization adjusts its parameters to improve predictions. Across sufficiently diverse data, the model can learn representations that capture regularities associated with grammar, syntax, and other structures without requiring every rule to be manually programmed.

### Q19. Why Is Next-Token Prediction Not Enough to Guarantee a Helpful Assistant?

**Answer:**  
A model can learn to predict ordinary text without necessarily following instructions, respecting preferences, or behaving safely. Instruction tuning and other post-training techniques can shape these behaviors. System design, tool restrictions, evaluation, and safety controls remain necessary because post-training does not guarantee perfect compliance or correctness.

### Q20. What Is the Difference Between Model Parameters and Context?

**Answer:**  
Parameters are the learned numerical values inside the model. Context is the sequence of tokens supplied for the current prediction, including the prompt and previously generated tokens. Parameters are normally fixed during inference, while context grows as generation proceeds.

### Q21. How Would You Explain Hallucinations to a Product Manager?

**Answer:**  
An LLM can produce a convincing answer without having verified that the answer is true. For example, it might invent a university deadline when no deadline was provided. For important information, we should retrieve authoritative records, require supporting evidence, validate the response, and allow the system to say that it cannot determine the answer.

### Q22. How Would You Decide Between a Smaller and Larger Model for a Production Application?

**Answer:**  
I would define task-specific quality, latency, cost, reliability, and security requirements. I would evaluate candidate models on a representative dataset, compare performance and operational costs, and test important failure cases. I would choose the smallest model that reliably meets the requirements unless the larger model provides enough additional value to justify its cost.

## Scenario-Based Interview Questions

### Scenario 1: The Model Invents a University Exam Date

**Question:** How would you fix the problem?

**Strong answer:**  
I would identify the authoritative source for exam dates, retrieve the relevant record, and provide that information as context. I would instruct the model to answer only when supported by the retrieved evidence and to abstain when no reliable record exists. I would validate the answer against the source and test cases involving missing or conflicting dates.

### Scenario 2: Your Chatbot Gives Different Answers to the Same Question

**Question:** Is this necessarily a bug?

**Strong answer:**  
Not necessarily. Sampling, changing context, model versions, and serving behavior can produce variations. I would inspect the request context, model version, decoding settings, and tool outputs. If repeatability is required, I would control these factors and evaluate the resulting system, while recognizing that fixed settings do not guarantee identical behavior in every environment.

### Scenario 3: Your Application Needs Exact Inventory Quantities

**Question:** Would you ask the LLM to predict the stock count?

**Strong answer:**  
No. I would retrieve the quantity from the inventory database or API. The LLM could interpret the question and explain the retrieved result, but the authoritative quantity should come from the system of record.

### Scenario 4: A Smaller Model Costs Less but Occasionally Fails on Complex Questions

**Question:** What would you do?

**Strong answer:**  
I would evaluate the failure rate and the impact of those failures. Depending on the requirements, I might route complex queries to a stronger model, use retrieval or deterministic tools, or introduce validation and retry logic. I would compare the cost per successful task rather than choosing solely by the cost of an individual model call.

## Rapid-Fire Revision

Try answering each question before revealing the explanation.

<details>
<summary><strong>1. What does an autoregressive LLM predict?</strong></summary>

**Answer:** The next token, conditioned on preceding context.

It predicts a distribution for the next token, rather than necessarily generating an entire answer in one step.
</details>

<details>
<summary><strong>2. What normally changes during training?</strong></summary>

**Answer:** Model parameters.

Optimization updates learned parameters to improve the training objective.
</details>

<details>
<summary><strong>3. What does temperature change?</strong></summary>

**Answer:** The decoding distribution.

Temperature affects how concentrated or diverse token selection is.
</details>

<details>
<summary><strong>4. Where should an exact current stock count come from?</strong></summary>

**Answer:** An authoritative inventory system.

The source of truth should be the inventory database or API.
</details>

<details>
<summary><strong>5. What does RAG add to an LLM application?</strong></summary>

**Answer:** Retrieved external context.

RAG retrieves relevant information to ground generation.
</details>

<details>
<summary><strong>6. Does a larger model always win?</strong></summary>

**Answer:** No. Evaluate it on the actual task.

Data, training, architecture, and workload all affect performance.
</details>

## Interview Answer Framework

For a broad question such as "Explain how an LLM works," use this sequence:

1. **Definition:** It is a neural language model that learns patterns in token sequences.
2. **Objective:** It learns to predict tokens from preceding context.
3. **Mechanism:** It tokenizes input, processes representations, calculates logits, and selects tokens.
4. **Generation:** It appends tokens and repeats until a stopping condition.
5. **Limitations:** Its predictions are not guaranteed to be factually correct.
6. **Engineering implications:** Use retrieval, tools, validation, and evaluation when reliability matters.

This framework helps you demonstrate conceptual understanding without losing the interviewer in unnecessary details.

---

# 10. Module Completion Checklist

Use this checklist before moving to the next roadmap module.

- [ ] Explain an LLM in one or two sentences without using vague claims about intelligence.
- [ ] Write and explain the autoregressive probability equation.
- [ ] Explain logits, softmax, and next-token probabilities.
- [ ] Describe the predict → choose → append → repeat generation loop.
- [ ] Distinguish an LLM from a database, search engine, and deterministic program.
- [ ] Explain why one model can support multiple tasks.
- [ ] Distinguish pretraining, inference, and post-training.
- [ ] Explain the effects of data, model scale, compute, and training quality.
- [ ] Explain hallucinations and why retrieval does not guarantee correctness.
- [ ] Complete both Python examples and modify the generation loop.
- [ ] Answer the conceptual and scenario-based interview questions without reading the notes.

When all checklist items are complete, test your understanding with a fresh example before proceeding.

---

# 11. Final Takeaway

An LLM learns patterns from data and uses those patterns to predict tokens from context. Repeated predictions generate its output. Understanding that mechanism—and the difference between plausible generation and verified information—is the foundation for engineering reliable LLM-powered systems.

---

## Suggested Next Step

After M1.1, study the next roadmap topic in sequence. Keep each module in its own folder so the repository remains easy to navigate, review, and maintain.

