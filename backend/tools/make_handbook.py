from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer

OUTPUT = Path(__file__).parent.parent / "docs" / "pdf" / "employee_handbook.pdf"

styles = getSampleStyleSheet()
title_style = ParagraphStyle("Title2", parent=styles["Title"], fontSize=24, spaceAfter=30)
h1 = ParagraphStyle("H1", parent=styles["Heading1"], fontSize=18, spaceAfter=12)
h2 = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=14, spaceAfter=10)
body = ParagraphStyle("Body2", parent=styles["BodyText"], fontSize=11, leading=15, spaceAfter=8)

CONTENT = [
    (title_style, "Trenkwalder Employee Handbook"),
    (body, "Version 2.0 — Effective January 2026"),
    (
        body,
        "This handbook provides an overview of company policies and guidelines for all employees. Please read it carefully and refer back to it as needed.",
    ),
    "pagebreak",
    (h1, "1. Vacation and Leave"),
    (
        body,
        "All full-time employees accrue 2.08 vacation days per month, totaling 25 days per year. Vacation requests must be submitted through the HR portal at least two weeks in advance. Your direct manager must approve the request before it is confirmed.",
    ),
    (
        body,
        "Unused vacation days can be carried over to the following year, up to a maximum of 5 days. Any days beyond the carry-over limit will expire on March 31st of the following year. Employees are encouraged to use their vacation time for rest and personal well-being.",
    ),
    (
        body,
        "In exceptional circumstances, employees may request to cash out up to 5 unused vacation days per year, subject to management approval. The payout is calculated at the employee's regular daily rate.",
    ),
    (
        body,
        "Part-time employees accrue vacation days proportionally based on their contracted hours. For example, an employee working 50% receives 12.5 vacation days per year.",
    ),
    (h1, "2. Sick Leave"),
    (
        body,
        "Employees who are unable to work due to illness must notify their manager by 9:00 AM on the first day of absence. A medical certificate is required for absences longer than three consecutive working days.",
    ),
    (
        body,
        "The company provides full salary continuation for up to six weeks of illness per calendar year, in accordance with Austrian labor law. After six weeks, the health insurance fund takes over payments at a reduced rate.",
    ),
    (
        body,
        "Employees returning from extended sick leave (more than four weeks) may be asked to participate in a return-to-work meeting with their manager and HR to ensure a smooth transition back to their duties.",
    ),
    "pagebreak",
    (h1, "3. Remote Work Policy"),
    (
        body,
        "Employees may work remotely up to three days per week, subject to their role requirements and manager approval. Remote work arrangements should be agreed upon in advance and documented in the HR system.",
    ),
    (
        body,
        "While working remotely, employees are expected to be available during core hours (10:00 AM to 4:00 PM CET) and responsive on company communication channels (Slack, email). Meetings should be attended via video when possible.",
    ),
    (
        body,
        "The company provides a one-time home office equipment allowance of €500 for monitors, keyboards, chairs, or other ergonomic equipment. Receipts must be submitted to the finance department within 30 days of purchase.",
    ),
    (
        body,
        "Employees working from abroad require prior approval from HR and must ensure compliance with local tax and work permit regulations. Remote work from outside the EU is limited to a maximum of 30 days per calendar year.",
    ),
    (h1, "4. Expenses and Reimbursements"),
    (
        body,
        "Business-related expenses must be pre-approved by your manager. Submit expense reports through the finance portal within 30 days of incurring the expense, along with original receipts or digital copies.",
    ),
    (
        body,
        "Travel expenses are reimbursed according to the company travel policy: economy class for flights under 6 hours, rail preferred for distances under 500 km, and hotel rates capped at €150 per night in major cities. Meals during business travel are reimbursed up to €50 per day.",
    ),
    (
        body,
        "Personal expenses, entertainment costs without business justification, and expenses submitted without proper documentation will not be reimbursed. Repeated policy violations may result in loss of expense privileges.",
    ),
    "pagebreak",
    (h1, "5. Professional Development"),
    (
        body,
        "Trenkwalder invests in the growth of its employees. Each employee has an annual learning budget of €1,500 for courses, conferences, certifications, or books related to their role. Requests should be discussed with your manager during the regular 1:1 meetings.",
    ),
    (
        body,
        "The company also offers internal training sessions, mentorship programs, and access to online learning platforms. Employees are encouraged to dedicate at least two hours per month to professional development activities.",
    ),
    (
        body,
        "Certification costs (exam fees, study materials) are fully covered if the certification is relevant to the employee's current role or planned career path within the company. Discuss with HR before registering.",
    ),
    (h1, "6. Code of Conduct Summary"),
    (
        body,
        "All employees are expected to act with integrity, respect, and professionalism. Discrimination, harassment, and bullying are strictly prohibited. Violations should be reported through the designated channels, and the company prohibits retaliation against reporters.",
    ),
    (
        body,
        "Confidential company and client information must be protected at all times. Do not share internal data with unauthorized parties. Use strong passwords, enable two-factor authentication, and lock your workstation when leaving your desk.",
    ),
    (
        body,
        "For the full Code of Conduct, please refer to the separate Code of Conduct document available on the company intranet.",
    ),
]


def build() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(OUTPUT), pagesize=A4, topMargin=50, bottomMargin=50)
    story = []
    for item in CONTENT:
        if item == "pagebreak":
            story.append(PageBreak())
        else:
            style, text = item
            story.append(Paragraph(text, style))
            story.append(Spacer(1, 4))
    doc.build(story)
    print(f"Created {OUTPUT} ({OUTPUT.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    build()
