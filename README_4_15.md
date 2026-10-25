# RAG over Structured Data

## 1. What Is It?

RAG over Structured Data is an approach that allows an AI application to answer questions using information stored in spreadsheets, tables, and relational databases.

Unlike document-based RAG, which retrieves relevant text passages, structured-data systems can perform calculations, filtering, grouping, and database queries.

One common technique is **Text-to-SQL**, where a language model converts a user's question into SQL (Structured Query Language), the application executes the query against a database, and the model explains the results.

Example:

- User: "How many students scored above 80?"
- Database: Contains student names and marks.
- AI: Generates a SQL query, executes it, and explains the count.

## 2. Why Does It Matter?

Not all useful knowledge is stored in documents. Businesses and applications often store important information in structured formats.

Examples include:

- Student records and examination results.
- Product inventories and sales transactions.
- Customer information and orders.
- Financial records and monthly expenses.
- Website analytics and application metrics.

Traditional vector search is designed to find semantically similar information. It is not inherently designed to calculate exact totals, count records, or reliably apply numerical filters.

For example, searching for passages related to "sales in January" is different from calculating the exact total revenue for January.

Structured-data retrieval helps AI applications answer questions that require precise operations on tabular data.

## 3. How Does It Work?

### Step 1: Store the data in a database

Suppose you have a spreadsheet containing student information.

| student_id | name | department | marks |
|---|---|---|---:|
| 1 | Asha | Computer | 85 |
| 2 | Bikash | Civil | 72 |
| 3 | Mina | Computer | 92 |
| 4 | Rohan | Electrical | 78 |

You can import this spreadsheet into a relational database such as SQLite or PostgreSQL.

A relational database stores information in tables consisting of rows and columns.

### Step 2: Give the model the database schema

The **schema** describes the structure of the database, including table names, column names, and data types.

For example:

- Table: `students`
- `student_id`: Unique student identifier.
- `name`: Student's name.
- `department`: Student's academic department.
- `marks`: Numerical examination score.

Providing descriptions in plain language helps the model understand what the columns represent.

Example values and sample questions paired with their correct SQL queries can further improve query generation.

### Step 3: Convert the question into SQL

The user asks:

`How many Computer Engineering students scored above 80?`

The model generates a SQL query:

```sql
SELECT COUNT(*) AS student_count
FROM students
WHERE department = 'Computer'
  AND marks > 80;
```

The query filters students by department and marks, then counts the matching rows.

For the example data, the result is `2`.

### Step 4: Validate and execute the query

The application checks the generated SQL before executing it.

It should verify that:

- Only permitted tables and columns are accessed.
- Only approved query operations are allowed.
- The query does not contain unauthorized modifications.
- Query execution has appropriate time and resource limits.

The database should use read-only permissions wherever possible.

### Step 5: Interpret the result

The database returns structured results, such as:

```text
student_count
-------------
2
```

The language model can turn this into a natural-language response:

"Two Computer Engineering students scored above 80."

The answer should reflect the actual database result rather than an unsupported guess.

### Step 6: Handle failed or suspicious queries

A generated query may contain invalid column names, incorrect table names, or unsuitable conditions. It may also execute successfully but return no results.

The application can detect these situations and ask the model to correct its query.

A safe correction loop is:

`Question → Generate SQL → Validate → Execute → Check result`

`If successful → Explain the result`

`If unsuccessful → Correct the query → Retry within a fixed limit`

If the query still fails, the application should return a clear error rather than repeatedly trying indefinitely.

### Step 7: Show the evidence

For answers involving calculations or filters, provide the SQL query, relevant figures, or a brief explanation of how the result was obtained.

For example:

- Result: 2 students.
- Filter: Department is Computer and marks are greater than 80.
- Operation: Count the matching records.

This makes it easier for users to verify the answer.

### Step 8: Route the question to the correct source

An AI application may have both document-based RAG and structured-data retrieval.

Use the appropriate source for each question:

| User's question | Appropriate source |
|---|---|
| "Explain the university's attendance policy." | Document search |
| "How many students scored above 80?" | Database query |
| "What is the attendance policy, and how many students meet its requirement?" | Both sources |

A routing component decides whether the question should go to document retrieval, database querying, or both.

This extends the routing approach introduced in the earlier RAG pipeline.

## 4. Simple Example

Consider a product database with the following table:

| product_name | category | price | stock |
|---|---|---:|---:|
| Keyboard | Accessories | 1500 | 12 |
| Mouse | Accessories | 800 | 25 |
| Monitor | Electronics | 18000 | 5 |
| Headphones | Accessories | 2500 | 8 |

A user asks:

`What is the total stock of Accessories products?`

The model generates:

```sql
SELECT SUM(stock) AS total_stock
FROM products
WHERE category = 'Accessories';
```

The database filters the Accessories products and adds their stock quantities:

- Keyboard: 12
- Mouse: 25
- Headphones: 8

Total stock = 12 + 25 + 8 = 45

The application responds:

"There are 45 Accessories items in stock."

The database performs the calculation. The LLM generates the query and explains the result.

### Important SQL operations

| SQL operation | Purpose | Example question |
|---|---|---|
| `SELECT` | Retrieve data | What are the product names? |
| `WHERE` | Filter records | Which products cost more than 1,000? |
| `COUNT()` | Count records | How many products are available? |
| `SUM()` | Add numerical values | What is the total stock? |
| `AVG()` | Calculate an average | What is the average product price? |
| `GROUP BY` | Group records | How many products belong to each category? |
| `ORDER BY` | Sort results | Which product has the highest price? |

These operations allow the system to answer questions that require exact database operations instead of relying on semantic similarity alone.

## 5. Practical AI Engineering Application

### A. Provide clear database context

Do not give the model only table and column names.

Include:

- Table names and their purpose.
- Column names and plain-language descriptions.
- Data types and relationships between tables.
- A few representative example values.
- Example questions and their expected SQL queries.
- Rules for interpreting dates, prices, categories, and other fields.

This context helps the model generate queries that match the actual database.

### B. Keep database access safe

Generated SQL is untrusted input. Never execute it without validation.

Recommended safeguards:

1. **Read-only credentials:** Give the application a database account that cannot modify or delete data.
2. **Table allowlist:** Permit access only to the tables required for the task.
3. **Query validation:** Parse and inspect the SQL before execution. For a read-only question-answering application, allow only approved read operations.
4. **Row limits:** Restrict how many records a query can return.
5. **Execution limits:** Apply timeouts and resource limits to expensive queries.
6. **Sensitive-data controls:** Restrict access to personal, confidential, or otherwise unauthorized columns.
7. **Error handling:** Avoid exposing database credentials, internal details, or sensitive information in error messages.

A prompt telling the model to generate safe SQL is not a security boundary. Enforce permissions and validation in the application and database.

### C. Handle errors and empty results

Consider a question asking for products costing more than 100,000 when no such products exist.

An empty result does not necessarily mean the SQL is invalid. It may simply mean no records match the condition.

Distinguish between:

- **SQL execution errors:** The query is invalid or cannot be executed.
- **Empty results:** The query executes successfully but finds no matching records.
- **Unexpected results:** The query executes but may use the wrong column, filter, or interpretation.

Retry when a query can reasonably be corrected. Do not treat every empty result as an error, and do not keep retrying a valid query just because the answer is zero.

### D. Show the query and supporting figures

For a trustworthy answer, consider displaying:

- The natural-language answer.
- The SQL query used.
- The returned result or relevant figures.
- A short explanation of the calculation or filters.

Avoid returning large datasets unnecessarily. Show only the evidence needed to support the answer.

### E. Combine document RAG and structured-data retrieval

A practical AI assistant can use a router to decide which source to query.

Example architecture:

`User question → Question router`

- Document question → Retrieve relevant passages.
- Numerical or tabular question → Generate and validate SQL, then execute it.
- Mixed question → Retrieve documents and query the database.

The application then combines the relevant evidence and produces a response.

For example, a university assistant might retrieve an attendance policy from a PDF and query a student database to count students meeting the policy's requirement.

### F. Try It

Choose a spreadsheet related to one of your projects and import it into a small database.

1. Identify five questions that require counts, totals, or filters.
2. Build a Text-to-SQL workflow that generates and executes database queries.
3. Use document search to answer the same questions where the spreadsheet contents are available as text.
4. Compare the answers against manually verified results.
5. Record correctness, execution errors, response time, and whether the method used the right source.

Use this experiment table:

| Question | Correct database result | Text-to-SQL correct? | Document search correct? |
|---|---|---|---|
| Question 1 | Verified result | Yes / No | Yes / No |
| Question 2 | Verified result | Yes / No | Yes / No |
| Question 3 | Verified result | Yes / No | Yes / No |
| Question 4 | Verified result | Yes / No | Yes / No |
| Question 5 | Verified result | Yes / No | Yes / No |

Use the verified database result as the reference for evaluation. Document search may still be useful for questions asking for explanations rather than exact calculations.

## 6. Key Takeaways

- Structured-data RAG answers questions using spreadsheets, tables, and databases.
- Text-to-SQL converts natural-language questions into SQL queries that the application executes.
- Database schema descriptions, example values, and example queries help the model understand the available data.
- Read-only permissions, query validation, table allowlists, row limits, and execution limits help protect the database.
- Query correction should handle genuine errors while distinguishing them from valid empty results.
- Showing SQL queries and supporting figures helps users verify answers.
- Route questions to document search, structured-data retrieval, or both according to the information required.

## 7. Common Misconceptions

### Misconception 1: Vector search can answer every data question.

Vector search is useful for finding semantically relevant content, but exact counting, aggregation, sorting, and filtering are often better handled by a database query.

### Misconception 2: The LLM directly performs the database operation.

In a Text-to-SQL workflow, the LLM generates the query. Application code executes it, and the database performs the requested operation.

### Misconception 3: A read-only prompt makes SQL execution safe.

A prompt alone cannot enforce security. Use read-only database permissions, SQL validation, access restrictions, and execution limits.

### Misconception 4: Every empty result means the query failed.

A valid query may return no matching rows. The system should distinguish empty results from SQL errors.

### Misconception 5: The LLM's explanation proves that the result is correct.

A fluent explanation can still misrepresent the database output. Verify that the answer accurately reflects the returned results and the original question.

## 8. Quick Revision

**1. What is Text-to-SQL?**

A technique in which a model converts a natural-language question into SQL that the application executes against a database.

**2. Why does the model need the database schema?**

To understand available tables, columns, relationships, and the meaning of the stored data.

**3. How can Text-to-SQL be made safer?**

Use read-only credentials, table allowlists, query validation, row limits, and execution timeouts.

**4. How should a system handle a failed query?**

Identify the error, attempt a bounded correction when appropriate, and report failure if the retry limit is reached.

**5. When should an application use both document search and a database?**

When answering a question requires both unstructured information, such as policy documents, and structured facts, such as counts or totals.