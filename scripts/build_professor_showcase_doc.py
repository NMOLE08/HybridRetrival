"""Build a concise, presentation-ready Word guide for the Phase 2 showcase."""
from pathlib import Path

from docx import Document
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "deliverables" / "Professor_Showcase_Guide.docx"
NAVY = "17365D"
PALE_BLUE = "EAF2F8"
LIGHT_GRAY = "D9D9D9"


def shade(cell, fill):
    props = cell._tc.get_or_add_tcPr()
    item = OxmlElement("w:shd")
    item.set(qn("w:fill"), fill)
    props.append(item)


def borders(cell):
    props = cell._tc.get_or_add_tcPr()
    border = props.first_child_found_in("w:tcBorders")
    if border is None:
        border = OxmlElement("w:tcBorders")
        props.append(border)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        element = border.find(qn(f"w:{edge}"))
        if element is None:
            element = OxmlElement(f"w:{edge}")
            border.append(element)
        element.set(qn("w:val"), "single")
        element.set(qn("w:sz"), "4")
        element.set(qn("w:color"), LIGHT_GRAY)


def set_cell_text(cell, value, bold=False, white=False):
    cell.text = ""
    paragraph = cell.paragraphs[0]
    paragraph.paragraph_format.space_after = Pt(2)
    paragraph.paragraph_format.space_before = Pt(2)
    run = paragraph.add_run(value)
    run.bold = bold
    run.font.size = Pt(9)
    run.font.color.rgb = RGBColor(255, 255, 255) if white else RGBColor(0, 0, 0)
    cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    borders(cell)


def add_table(document, headers, rows, widths):
    table = document.add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"
    table.autofit = False
    for index, header in enumerate(headers):
        cell = table.rows[0].cells[index]
        cell.width = Inches(widths[index])
        shade(cell, NAVY)
        set_cell_text(cell, header, bold=True, white=True)
    for row_index, row in enumerate(rows):
        cells = table.add_row().cells
        for index, value in enumerate(row):
            cells[index].width = Inches(widths[index])
            if row_index % 2:
                shade(cells[index], PALE_BLUE)
            set_cell_text(cells[index], value)
    document.add_paragraph().paragraph_format.space_after = Pt(3)
    return table


def add_bullet(document, text):
    paragraph = document.add_paragraph(style="List Bullet")
    paragraph.paragraph_format.space_after = Pt(3)
    paragraph.add_run(text)


def add_number(document, text):
    paragraph = document.add_paragraph(style="List Number")
    paragraph.paragraph_format.space_after = Pt(4)
    paragraph.add_run(text)


def add_section(document, title):
    paragraph = document.add_paragraph(style="Heading 1")
    paragraph.add_run(title)
    paragraph.paragraph_format.space_before = Pt(13)
    paragraph.paragraph_format.space_after = Pt(6)


def add_text(document, text, bold_lead=None):
    paragraph = document.add_paragraph()
    paragraph.paragraph_format.space_after = Pt(6)
    paragraph.paragraph_format.line_spacing = 1.08
    if bold_lead and text.startswith(bold_lead):
        paragraph.add_run(bold_lead).bold = True
        paragraph.add_run(text[len(bold_lead):])
    else:
        paragraph.add_run(text)


def configure(document):
    section = document.sections[0]
    section.top_margin = Inches(0.7)
    section.bottom_margin = Inches(0.65)
    section.left_margin = Inches(0.75)
    section.right_margin = Inches(0.75)
    styles = document.styles
    styles["Normal"].font.name = "Aptos"
    styles["Normal"].font.size = Pt(10.5)
    styles["Normal"]._element.rPr.rFonts.set(qn("w:ascii"), "Aptos")
    styles["Normal"]._element.rPr.rFonts.set(qn("w:hAnsi"), "Aptos")
    for name, size in (("Title", 22), ("Heading 1", 15), ("Heading 2", 12)):
        style = styles[name]
        style.font.name = "Aptos Display" if name == "Title" else "Aptos"
        style.font.size = Pt(size)
        style.font.color.rgb = RGBColor(0, 0, 0)
        style._element.rPr.rFonts.set(qn("w:ascii"), style.font.name)
        style._element.rPr.rFonts.set(qn("w:hAnsi"), style.font.name)
    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    footer.add_run("Professor Showcase Guide | Phase 2 Exploratory Study").font.size = Pt(8)


def build():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc = Document()
    configure(doc)

    title = doc.add_paragraph(style="Title")
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.add_run("Identifier Preserving Hybrid Retrieval")
    subtitle = doc.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    subtitle.paragraph_format.space_after = Pt(15)
    subtitle.add_run("Professor Showcase Guide and Question Preparation").italic = True

    add_text(doc, "This guide explains the project in plain language for a short professor presentation. The study evaluates whether a small, explainable identifier-aware reranking step can improve technical document search while preserving reproducibility, source attribution, and honest limitations.")

    add_section(doc, "One Minute Introduction")
    add_text(doc, "My project studies technical document search, especially searches containing exact identifiers such as CVE vulnerability IDs or hardware model names. Ordinary semantic search can understand meaning, but it can confuse similar technical identifiers. I compare lexical search, semantic search, hybrid retrieval, and an identifier-aware reranking method that penalizes documents with a conflicting explicit identifier.")
    add_text(doc, "The project is an exploratory empirical study. It does not claim independent validation or universal superiority. Its contribution is a transparent, reproducible way to examine identifier-sensitive technical search.")

    add_section(doc, "The Problem")
    add_text(doc, "Technical documents often use identifiers whose exact value matters. For example, a query for CVE-2023-46747 should not be answered by a semantically similar vulnerability record for a different CVE. A useful technical search system needs both semantic understanding and identifier precision.")
    add_text(doc, "Research question: Does a small identifier-aware adjustment improve hybrid technical-document retrieval compared with lexical, semantic, and standard hybrid baselines?")

    add_section(doc, "Short Forms and Terms")
    add_table(doc, ["Term", "Meaning", "Why it matters here"], [
        ("CVE", "Common Vulnerabilities and Exposures", "A standardized vulnerability identifier, such as CVE-2023-46747."),
        ("TF-IDF", "Term Frequency Inverse Document Frequency", "A lexical method that gives weight to discriminative words and exact terms."),
        ("MiniLM", "A compact pretrained language model", "Creates embeddings that represent the semantic meaning of queries and documents."),
        ("RRF", "Reciprocal Rank Fusion", "Combines ranked lists from TF-IDF and MiniLM without mixing incompatible raw score scales."),
        ("MRR@10", "Mean Reciprocal Rank at 10", "Rewards placing the first known relevant document near the top ten results."),
        ("Recall@5", "Recall at 5", "Measures whether a known relevant document appears in the top five."),
        ("nDCG@10", "Normalized Discounted Cumulative Gain at 10", "Rewards relevant results that occur near the top of the ranking."),
        ("API", "Application Programming Interface", "A way for software components to communicate; the demo exposes local search endpoints."),
        ("Qrels", "Query relevance judgments", "Records known relevant, irrelevant, or unknown query-document relationships."),
    ], [1.05, 2.15, 3.4])

    add_section(doc, "Dataset and Evaluation Design")
    add_text(doc, "The Phase 2 corpus contains 150 source-attributed technical documents. The final eligible exploratory subset contains 30 queries: 12 development queries and 18 held-out test queries. It has 32 known positive query-document pairs.")
    add_text(doc, "Development queries were used to select the method configuration. The held-out test queries were not used for parameter selection. Before test evaluation, the code, dataset, configuration, model revision, seed, and hashes were frozen.")
    add_text(doc, "The labels are author-produced, incomplete, and not independently validated. Unjudged pairs are treated as unknown rather than automatically irrelevant. This is essential to present honestly.")

    add_section(doc, "The Four Retrieval Systems")
    add_text(doc, "1. TF-IDF lexical retrieval. TF-IDF ranks documents using words and exact tokens. It is strong when the user supplies a precise identifier but can miss paraphrases and conceptual similarity.")
    add_text(doc, "2. MiniLM semantic retrieval. The project uses the pretrained sentence-transformers/all-MiniLM-L6-v2 model. No new model was trained. It converts queries and documents into numerical embedding vectors and retrieves documents with similar meaning. Its weakness is that semantically related technical records can still contain the wrong exact ID.")
    add_text(doc, "3. RRF hybrid retrieval. RRF combines the TF-IDF and MiniLM rankings. The project uses k = 60. It is a transparent baseline because it combines rank positions rather than assuming lexical and semantic scores have the same scale.")
    add_text(doc, "4. Identifier-aware reranking. This starts with RRF and checks explicit identifiers in the query and documents. It can reward a direct match and penalize a conflicting identifier from the same family. The displayed explanation shows the detected match, conflict decision, adjustment, and movement relative to RRF.")

    add_section(doc, "Mathematical Method")
    add_text(doc, "Reciprocal Rank Fusion score: RRF(d) = sum over retrieval systems i of 1 / (k + rank_i(d)). Here, d is a document, rank_i(d) is the rank of d under system i, and k = 60 is a smoothing constant.")
    add_text(doc, "Identifier-aware score: Score(d, q) = RRF(d) + lambda_match times Match(d, q) minus lambda_conflict times Conflict(d, q). Match is the fraction of requested identifiers found in the document. Conflict is 1 when an explicit competing identifier is detected and 0 otherwise.")

    add_section(doc, "Configuration Selection")
    add_text(doc, "The candidate values were selected in advance and evaluated only on development queries. Match weights were 0, 0.003, 0.006, and 0.012. Conflict penalties were 0, 0.003, and 0.006.")
    add_text(doc, "The frozen selected configuration was RRF k = 60, match weight = 0, and conflict penalty = 0.003. The zero match weight is an honest result: on the development set, the selected method did not need a match bonus. Its measured change came from penalizing explicit conflicts.")

    add_section(doc, "Held Out Test Results")
    add_table(doc, ["System", "MRR at 10", "Recall at 5", "nDCG at 10"], [
        ("TF-IDF", "0.8667", "0.8889", "0.8844"),
        ("MiniLM", "0.7278", "0.8333", "0.7801"),
        ("RRF", "0.8074", "1.0000", "0.8544"),
        ("Identifier-aware reranking", "1.0000", "1.0000", "1.0000"),
    ], [2.75, 1.25, 1.25, 1.25])
    add_text(doc, "On the 18 held-out queries, the identifier-aware method had an MRR@10 difference of 0.1926 compared with RRF, with five gains, zero losses, and thirteen ties. A paired bootstrap interval was [0.0556, 0.3481]. These are descriptive results, not a broad claim of statistical significance or generalization.")

    add_section(doc, "Live Demo Walkthrough")
    for step in [
        "Open the local demo and state that all four systems search the same 150 source-attributed documents.",
        "Use the default CVE-2023-46747 query.",
        "Show TF-IDF, MiniLM, and RRF side by side. Explain that MiniLM can retrieve semantically related CVEs even when they are not the exact requested CVE.",
        "Show the identifier-aware column. The correct CVE moves from RRF rank 4 to rank 1, while results with conflicting CVE identifiers receive a small negative adjustment of 0.003.",
        "Open a source link to show provenance, then point to the visible author-annotated exploratory-study disclaimer.",
    ]:
        add_number(doc, step)

    add_section(doc, "Limitations to State Clearly")
    for point in [
        "This is an exploratory study, not an independently annotated confirmatory benchmark.",
        "The eligible subset is small: 30 queries, including 18 held-out test queries.",
        "The evaluated subset is CVE-only, so it does not establish generalization to ESP32 or other technical identifier families.",
        "Labels are author-produced, and many query-document pairs remain unknown rather than judged negative.",
        "The system uses a pretrained MiniLM model and does not train a new neural network.",
        "A larger independently annotated benchmark is the essential next step.",
    ]:
        add_bullet(doc, point)

    add_section(doc, "Questions You May Be Asked")
    add_table(doc, ["Question", "Prepared answer"], [
        ("What is the main contribution?", "An explainable post-ranking layer that preserves technical identifiers after hybrid retrieval, together with a reproducible experimental workflow."),
        ("Why not use only TF-IDF?", "TF-IDF is strong for exact IDs, but semantic retrieval helps when users describe a concept using different wording."),
        ("Why not use only MiniLM?", "MiniLM understands meaning but can confuse closely related technical records with different identifiers."),
        ("Why use RRF?", "It combines lexical and semantic rankings without requiring their raw scores to share the same scale."),
        ("Did you train MiniLM?", "No. I used the existing pretrained all-MiniLM-L6-v2 model without fine-tuning."),
        ("Why is the match weight zero?", "Development-only selection found that a small conflict penalty was sufficient for the selected configuration. I report that outcome honestly."),
        ("Did you tune on the test set?", "No. The held-out test split was evaluated only after configuration and artifacts were frozen."),
        ("Are the results statistically significant?", "I report descriptive paired bootstrap intervals, but do not make a broad significance claim because the sample is small and annotations are author-produced."),
        ("What does author-annotated mean?", "The project author assigned the relevance labels. They have not been independently validated."),
        ("What is the next step?", "Create a larger independently annotated benchmark, add more identifier families, and evaluate generalization beyond CVEs."),
        ("What happens when a query has no identifier?", "The reranker leaves the RRF order unchanged because there is no explicit identifier evidence to apply."),
        ("Can this become a real product?", "Yes, as a lightweight transparent post-ranking layer, but it needs broader independent evaluation and monitoring before production use."),
    ], [2.1, 4.4])

    add_section(doc, "Closing Statement")
    add_text(doc, "This project shows a practical direction for identifier-heavy technical search: combine lexical and semantic evidence, then explicitly protect against conflicting identifiers. The result is a reproducible exploratory study with promising measured behavior on a small held-out subset, while clearly documenting the evidence and generalization limits.")
    doc.save(OUTPUT)
    print(OUTPUT)


if __name__ == "__main__":
    build()
