from fpdf import FPDF
import re

def sanitize_text(text):
    """
    Clean unicode + remove markdown formatting
    """
    replacements = {
        "’": "'",
        "‘": "'",
        "“": '"',
        "”": '"',
        "–": "-",
        "—": "-",
        "…": "...",
    }

    for k, v in replacements.items():
        text = text.replace(k, v)

    # Remove markdown bold/italic
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)   # **bold**
    text = re.sub(r"\*(.*?)\*", r"\1", text)       # *italic*
    text = re.sub(r"__(.*?)__", r"\1", text)       # __bold__

    return text


class CurriculumPDF(FPDF):
    def header(self):
        self.set_fill_color(30, 30, 60)
        self.rect(0, 0, 210, 25, 'F')

        self.set_text_color(255, 255, 255)
        self.set_font("Arial", "B", 18)
        self.cell(0, 15, "CurricuForge", ln=True, align="C")
        self.set_font("Arial", size=10)
        self.cell(0, 5, "AI-Generated Learning Document", ln=True, align="C")
        self.ln(10)

        self.set_text_color(0, 0, 0)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 9)
        self.set_text_color(120)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

    def section_title(self, title):
        self.set_fill_color(230, 230, 250)
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, sanitize_text(title), ln=True, fill=True)
        self.ln(3)

    def section_body(self, text):
        text = sanitize_text(text)
        self.set_font("Arial", size=11)

        for line in text.split("\n"):
            # Auto-detect headings
            if line.strip().endswith(":"):
                self.set_font("Arial", "B", 12)
            else:
                self.set_font("Arial", size=11)

            self.multi_cell(0, 7, line)

        self.ln(4)


def export_curriculum_pdf(title, curriculum_text, rubric_text=None):
    pdf = CurriculumPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 12, sanitize_text(title), ln=True)
    pdf.ln(5)

    pdf.section_title("Curriculum / Roadmap")
    pdf.section_body(curriculum_text)

    if rubric_text:
        pdf.add_page()
        pdf.section_title("Rubric & Bloom's Taxonomy")
        pdf.section_body(rubric_text)

    path = "curriculum.pdf"
    pdf.output(path)
    return path


