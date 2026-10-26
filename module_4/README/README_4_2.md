# Loading and Cleaning Documents

## 1. What Is It?

**Document loading and cleaning** is the process of extracting text from files or web pages and preparing it so an application can search and use it reliably.

In a RAG system, the model cannot search a PDF or Word file directly just because the file exists. Your application first needs to extract its content, clean obvious noise, and keep useful information about where that content came from.

**Simple idea:** load the document, clean its text without destroying meaning, and keep its source details.

## 2. Why Does It Matter?

Poorly extracted or badly cleaned text can make later search results incomplete or misleading. For example, a PDF table may become scrambled text, or removing all headings may make a paragraph impossible to interpret.

Document preparation matters because it helps you:
- **Preserve meaning:** keep headings, lists, table relationships, and section context.
- **Improve retrieval:** make relevant passages easier to find.
- **Support citations:** identify the original file and section behind an answer.
- **Filter results:** restrict searches by source, date, title, or document type.
- **Maintain an up-to-date collection:** replace changed files and remove deleted ones.

A loader cannot always reconstruct a document's original layout perfectly. Always inspect extracted text, especially for complex PDFs, scanned pages, and tables.

## 3. How Does It Work?

### Step 1: Load documents

A document loader reads a source and extracts its content into a representation your application can process. LangChain has loaders for many common sources, including PDFs, web pages, Word files, and plain-text files.

Examples of loader packages and classes can change as LangChain evolves, so check the documentation for the loader appropriate to your file type. Many integrations are installed as separate packages.

A typical LangChain document contains:
- `page_content`: the extracted text.
- `metadata`: a dictionary of details about the text, such as the source file or page number.

Example of the general shape:

```python
document = {
    "page_content": "Assignments must be submitted before the deadline.",
    "metadata": {
        "source": "course_policy.pdf",
        "page": 2,
        "title": "Course Policy"
    }
}
```

This dictionary is a simplified illustration of the structure, not a complete LangChain loader object.

### Step 2: Recognize scanned documents

Not every PDF contains selectable text. Some PDFs are scans or photos of pages. A normal text extractor may return little or no useful text from them.

For scanned pages, you may need **OCR (Optical Character Recognition)**. OCR detects characters in an image and converts them into text.

Check the result before continuing:
- If the text is readable and complete, normal extraction may be enough.
- If pages return blank text, inspect whether they are scanned.
- If OCR confuses characters, columns, or tables, review or correct the output.

### Step 3: Clean text without losing structure

Cleaning means removing noise while preserving information that changes the meaning.

**Common clutter to remove or correct:**
- Repeated page headers and footers.
- Page numbers accidentally mixed into sentences.
- Unnecessary blank lines or strange spacing.
- Broken words caused by line breaks.
- Repeated text introduced during extraction.

**Structure to preserve:**
- Headings and subheadings.
- Bullet points and numbered steps.
- Table headers and the relationship between each row and column.
- Section boundaries and meaningful paragraph breaks.
- Warnings, footnotes, dates, and other details that affect interpretation.

For example, a table such as:

| Role | Submission deadline |
|---|---|
| Student | Friday, 5 PM |
| Instructor | Monday, 10 AM |

should not be flattened into an ambiguous string such as `Role Submission deadline Student Friday 5 PM Instructor Monday 10 AM` if that makes the row relationships unclear. Keep the table structure or convert it into clear text such as `Student: Friday, 5 PM. Instructor: Monday, 10 AM.`

Avoid aggressive cleaning that removes punctuation, headings, dates, or table labels. Those details may be important evidence when answering questions.

### Step 4: Keep metadata with the text

**Metadata** is information about a document or passage. Store it alongside the extracted text so your application can trace and filter results later.

Useful metadata may include:

| Metadata field | Example | Why it helps |
|---|---|---|
| `title` | `Course Policy` | Helps identify the document |
| `source` | `course_policy.pdf` | Points to the original file |
| `section` | `Late submissions` | Gives context for the passage |
| `date` | `2026-10-20` | Helps identify the document's date or version |
| `page` | `2` | Helps locate the passage in a PDF |
| `document_id` | `policy-001` | Helps track the document across updates |
| `file_hash` | A calculated fingerprint of file content | Helps detect whether a file changed |

Use metadata that matches your collection. Not every source has a page number or a meaningful publication date. Distinguish the document's publication/effective date from the date your system imported it.

### Step 5: Handle updates, duplicates, and deletions

Document collections change. A policy may be updated, the same file may be uploaded twice, or an old document may be deleted.

- **Duplicates:** use stable document identifiers or file hashes to detect repeated copies.
- **Updated files:** reprocess the changed file and replace or version its previous content.
- **Deleted files:** remove its passages from the searchable collection, or mark them inactive so they are no longer returned.
- **Version tracking:** retain a version or effective date when older versions must remain available for historical questions.
- **Repeatable processing:** make the pipeline safe to run again without creating duplicate copies every time.

If the document text is stored in a vector database or search index, update that index too. Removing a file from the original folder alone may not remove previously indexed passages.

## 4. Simple Example

Suppose you load a university PDF containing a policy about late assignments.

**Raw extracted text:**

```text
UNIVERSITY POLICY                         Page 4
Late submissions
Assignments must be submitted by 11:59 PM
on the due date.
UNIVERSITY POLICY                         Page 4
```

The repeated header and page number are clutter, while the heading and deadline are meaningful.

**Cleaned text:**

```text
Section: Late submissions

Assignments must be submitted by 11:59 PM on the due date.
```

**Attached metadata:**

```python
metadata = {
    "title": "University Policy",
    "source": "university_policy.pdf",
    "section": "Late submissions",
    "page": 4,
    "document_date": "2026-10-20"
}
```

Now the passage is easier to understand, and an application can identify the source and section when returning an answer. The date is illustrative; in a real project, use the actual date stated by the document or record the import date separately.

## 5. Practical AI Engineering Application

For a small document-ingestion project, organize the pipeline into clear stages:

1. **Discover:** find supported files in your input folder.
2. **Load:** extract text using an appropriate loader.
3. **Inspect:** identify empty pages, broken tables, scanned pages, and extraction errors.
4. **Clean:** remove repeated clutter while preserving meaning and structure.
5. **Attach metadata:** add source, title, section, page, and relevant dates.
6. **Track identity:** assign a stable ID and optionally calculate a file hash.
7. **Save or index:** store the processed documents so they can be searched later.
8. **Synchronize changes:** replace updated content and remove deleted content from the searchable collection.

Keep the original files unchanged. Store cleaned text separately so you can audit or repeat the process if the cleaning rules need improvement.

## 6. Try It: Load Your Three Messiest Documents

Choose three documents you are allowed to use, ideally with different challenges—for example, a PDF with tables, a Word document with headings, and a scanned PDF or a web page.

For each document:

- Load it with a suitable LangChain document loader.
- Read the extracted text rather than assuming extraction succeeded.
- Record where headings, lists, tables, page breaks, or columns were damaged.
- Check whether a scanned page needs OCR.
- Remove repeated headers or footers only when you can identify them safely.
- Attach useful metadata, including title, source, section, and date when available.
- Run the process a second time and check whether it creates duplicate records.

Use a checklist like this:

| Check | Notes |
|---|---|
| Text extracted correctly? | |
| Any blank or unreadable pages? | |
| Headings and lists preserved? | |
| Tables still understandable? | |
| Repeated headers/footers removed safely? | |
| Source and section metadata attached? | |
| Duplicate or outdated version detected? | |

The goal is not to make the text look perfect at any cost. The goal is to preserve the original meaning and make the source traceable.

## 7. Common Misconceptions

- **"A PDF always contains extractable text."** No. Scanned PDFs may need OCR.
- **"Cleaning means removing as much text as possible."** No. Headings, table labels, dates, and lists often carry meaning.
- **"The text alone is enough."** Often not. Source, section, page, and date information are valuable for filtering and citations.
- **"Deleting the original file automatically removes it from search."** Not necessarily. Previously indexed passages may need to be removed separately.
- **"A loader always extracts a document perfectly."** No. Complex layouts and tables require inspection.

## 8. Key Takeaways

- Loaders extract text from PDFs, web pages, Word files, and other sources.
- Scanned pages may require OCR before their text can be searched.
- Clean repeated clutter, but preserve headings, lists, tables, and meaningful boundaries.
- Store useful metadata such as title, source, section, page, and date alongside the text.
- Detect duplicates, reprocess updated files, and remove deleted content from the search index.
- Inspect real extraction results instead of assuming the document was processed correctly.

## 9. Quick Revision

**Question:** What does a document loader do?

**Answer:** It extracts content from a source and makes it available for the application to process.

**Question:** What is OCR?

**Answer:** Optical Character Recognition converts text in images or scanned pages into machine-readable text.

**Question:** Why should you preserve headings and table structure?

**Answer:** They provide context and relationships that help keep the extracted content meaningful.

**Question:** Why attach metadata to each document or passage?

**Answer:** Metadata supports filtering, source tracking, citations, and update management.

**Question:** What must happen when a source document is deleted?

**Answer:** Its previously indexed content should also be removed or marked inactive in the searchable collection.

**Learning outcome:** You should be able to turn a real document collection into clean, traceable text that is ready for searching.
