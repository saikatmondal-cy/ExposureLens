import os
import sys
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

# Palette
COLOR_NAVY = RGBColor(11, 19, 43)       # #0B132B
COLOR_TEAL = RGBColor(14, 116, 144)     # #0E7490
COLOR_SLATE = RGBColor(51, 65, 85)      # #334155
COLOR_GREEN = RGBColor(16, 185, 129)    # #10B981
COLOR_AMBER = RGBColor(217, 119, 6)     # #D97706
COLOR_PURPLE = RGBColor(124, 58, 237)   # #7C3AED

def set_cell_background(cell, hex_color):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hex_color)
    tc_pr.append(shd)

def set_cell_margins(cell, top=80, bottom=80, left=120, right=120):
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_mar = OxmlElement('w:tcMar')
    for m, val in [('w:top', top), ('w:bottom', bottom), ('w:left', left), ('w:right', right)]:
        node = OxmlElement(m)
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tc_mar.append(node)
    tc_pr.append(tc_mar)

def add_header(doc, text, level=1):
    h = doc.add_heading(text, level=level)
    h.paragraph_format.keep_with_next = True
    h.paragraph_format.space_before = Pt(14 if level == 1 else 9)
    h.paragraph_format.space_after = Pt(3)
    run = h.runs[0]
    if level == 1:
        run.font.name = 'Calibri'
        run.font.size = Pt(15)
        run.font.bold = True
        run.font.color.rgb = COLOR_NAVY
    elif level == 2:
        run.font.name = 'Calibri'
        run.font.size = Pt(12)
        run.font.bold = True
        run.font.color.rgb = COLOR_TEAL
    elif level == 3:
        run.font.name = 'Calibri'
        run.font.size = Pt(10.5)
        run.font.bold = True
        run.font.color.rgb = COLOR_SLATE
    return h

def add_p(doc, text, bold_prefix=None, space_after=3):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.15
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.font.name = 'Calibri'
        r_pre.font.size = Pt(10)
        r_pre.font.bold = True
        r_pre.font.color.rgb = COLOR_NAVY
    r = p.add_run(text)
    r.font.name = 'Calibri'
    r.font.size = Pt(10)
    r.font.color.rgb = COLOR_SLATE
    return p

def add_bullet(doc, text, bold_prefix=None):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.12
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.font.name = 'Calibri'
        r_pre.font.size = Pt(9.5)
        r_pre.font.bold = True
        r_pre.font.color.rgb = COLOR_NAVY
    r = p.add_run(text)
    r.font.name = 'Calibri'
    r.font.size = Pt(9.5)
    r.font.color.rgb = COLOR_SLATE
    return p

def add_callout(doc, text, title="PRESENTER TIP FOR LIVE DEMO", bg_hex="F0FDF4"):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_background(cell, bg_hex)
    set_cell_margins(cell, top=80, bottom=80, left=120, right=120)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after = Pt(2)
    r_title = p.add_run(f"[{title}] ")
    r_title.font.name = 'Consolas'
    r_title.font.size = Pt(9)
    r_title.font.bold = True
    r_title.font.color.rgb = COLOR_TEAL

    r_text = p.add_run(text)
    r_text.font.name = 'Calibri'
    r_text.font.size = Pt(9.5)
    r_text.font.color.rgb = COLOR_SLATE

    sp = doc.add_paragraph()
    sp.paragraph_format.space_before = Pt(0)
    sp.paragraph_format.space_after = Pt(2)

def add_speech_box(doc, text):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_background(cell, "EFF6FF")
    set_cell_margins(cell, top=80, bottom=80, left=120, right=120)
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after = Pt(2)
    r_lbl = p.add_run("What to Say Out Loud While Pointing at the Screen:\n")
    r_lbl.font.name = 'Consolas'
    r_lbl.font.size = Pt(9)
    r_lbl.font.bold = True
    r_lbl.font.color.rgb = COLOR_NAVY
    r_txt = p.add_run(f'"{text}"')
    r_txt.font.name = 'Calibri'
    r_txt.font.size = Pt(9.5)
    r_txt.font.italic = True
    r_txt.font.color.rgb = COLOR_SLATE
    sp = doc.add_paragraph()
    sp.paragraph_format.space_before = Pt(0)
    sp.paragraph_format.space_after = Pt(3)

def build_demo_guide():
    doc = docx.Document()
    
    # Page setup - Margins 0.8 inch
    for s in doc.sections:
        s.top_margin = Inches(0.8)
        s.bottom_margin = Inches(0.8)
        s.left_margin = Inches(0.8)
        s.right_margin = Inches(0.8)

    # Document Header / Title
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(2)
    r_title = p_title.add_run("EXPOSURELENS: COMPLETE LIVE DEMO SCRIPT & FEATURE WALKTHROUGH")
    r_title.font.name = 'Calibri'
    r_title.font.size = Pt(18)
    r_title.font.bold = True
    r_title.font.color.rgb = COLOR_NAVY

    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_before = Pt(0)
    p_sub.paragraph_format.space_after = Pt(6)
    r_sub = p_sub.add_run("A Step-by-Step Practical Presenter Manual for Conducting a Flawless Live Software Demo of All 17 Workspaces Before the Project Review Committee")
    r_sub.font.name = 'Calibri'
    r_sub.font.size = Pt(11.5)
    r_sub.font.bold = True
    r_sub.font.color.rgb = COLOR_TEAL

    # Student metadata table
    tbl_meta = doc.add_table(rows=4, cols=2)
    tbl_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta = [
        ("Presenter Name & Roll No:", "Saikat Mondal (Roll Number: 25168016)"),
        ("Degree & Institution:", "M.Tech in Cyber Security | School of Computer Engineering, KIIT Bhubaneswar"),
        ("Live Demonstration URL:", "https://exposurelens.onrender.com (Public 24/7 HTTPS Production App)"),
        ("Local Fallback Command:", "streamlit run dashboard/app.py (Running on http://localhost:8501)")
    ]
    for idx, (k, v) in enumerate(meta):
        row = tbl_meta.rows[idx]
        c0, c1 = row.cells[0], row.cells[1]
        c0.width = Inches(2.2)
        c1.width = Inches(4.5)
        set_cell_background(c0, "F1F5F9")
        set_cell_background(c1, "FFFFFF")
        set_cell_margins(c0, top=40, bottom=40, left=80, right=80)
        set_cell_margins(c1, top=40, bottom=40, left=80, right=80)
        p0 = c0.paragraphs[0]
        p0.add_run(k).font.bold = True
        p0.runs[0].font.size = Pt(9)
        p0.runs[0].font.color.rgb = COLOR_NAVY
        p1 = c1.paragraphs[0]
        p1.add_run(v).font.size = Pt(9)
        p1.runs[0].font.color.rgb = COLOR_SLATE

    sp = doc.add_paragraph()
    sp.paragraph_format.space_before = Pt(4)

    # -------------------------------------------------------------------------
    # PART 1: PRE-DEMO PREPARATION & 60-SECOND SETUP
    # -------------------------------------------------------------------------
    add_header(doc, "PART 1: Pre-Demo Setup (The 60-Second Readiness Check)", level=1)
    add_p(doc, "Before calling your guide over to your laptop, follow this exact checklist to make sure your demo runs smoothly:")
    add_bullet(doc, "Option A (Live Cloud - Recommended): Open your browser (Google Chrome) and navigate to https://exposurelens.onrender.com. Ensure the top banner shows production status active.", bold_prefix="Step 1: Open the App: ")
    add_bullet(doc, "Option B (Local Fallback): If Wi-Fi is slow, open a terminal in your project folder and run: `.venv\\Scripts\\streamlit run dashboard/app.py`. It opens immediately at `http://localhost:8501`.")
    add_bullet(doc, "Look at the left sidebar. If the stats look empty or you want to start fresh, simply click the big blue button: '🚀 Run Synthetic Scenarios'. In 2 seconds, it executes 15 synthetic API requests (simulating legitimate users, intra-tenant leaks, and cross-tenant attacks) and automatically reconstructs the evidence database.", bold_prefix="Step 2: Generate Fresh Traffic (1 Click): ")
    add_bullet(doc, "You will see a green popup saying: 'Successfully simulated 15 synthetic API requests and reconstructed 4 BOLA exposures with 12 Proof-of-Exposure records!'. Now, you are 100% ready to present.", bold_prefix="Step 3: Confirmation: ")

    # -------------------------------------------------------------------------
    # PART 2: THE "GOLDEN 5-MINUTE" FAST DEMO FLOW
    # -------------------------------------------------------------------------
    add_header(doc, "PART 2: The 'Golden 5-Minute' Fast Live Demo Flow", level=1)
    add_p(doc, "If your guide says: 'You only have 5 minutes, just show me the key working parts', follow this high-impact 5-stop route:")
    
    add_callout(doc,
        "Stop 1: Landing Page -> Click 'Start Investigation Platform'\n"
        "Stop 2: Executive Overview -> Show KPIs & Risk score gauge\n"
        "Stop 3: BOLA Findings & Exposure Relationship Graph -> Show the live attack network map\n"
        "Stop 4: Semantic Delta & Multi-Tenant Isolation (TIFI) -> Show the leaked PAN/medical secrets & the 0.800 danger score\n"
        "Stop 5: Forensic PoE Certificate & AI Report -> Show the cryptographic certificate (1-click PDF) and the 100% Zero-Hallucination verification badge!",
        title="THE 5-MINUTE WINNING DEMO ROUTE"
    )

    # -------------------------------------------------------------------------
    # PART 3: COMPLETE PAGE-BY-PAGE WALKTHROUGH
    # -------------------------------------------------------------------------
    add_header(doc, "PART 3: Complete Page-by-Page Feature Walkthrough (All 17 Workspaces)", level=1)
    add_p(doc, "Here is the comprehensive guide to EVERY SINGLE PAGE in ExposureLens. For each page, you get: what is on screen, what to click, and exactly what to say out loud.")

    pages_info = [
        ("0. The Landing Page (Welcome & Architecture)",
         "The public front door of the application. Shows a sleek dark cyber theme with the project title, candidate credentials, live status badge, high-level architecture cards, and the three simulated enterprise tenants (FinServe Global, HealthFirst Diagnostics, OmniRetail Commerce).",
         "Point to your name and roll number. Then click the large primary button: '🚀 Start Investigation Platform'.",
         "Sir, this is the landing portal of ExposureLens. It introduces the project and our three simulated multi-tenant enterprise clients: a financial institution (FinServe Global), a hospital network (HealthFirst Diagnostics), and a retail chain (OmniRetail Commerce). Let us click 'Start Investigation Platform' to enter the Security Operations Center hub."),

        ("1. 📊 Executive Overview",
         "The high-level CISO executive summary. Features 4 top KPI cards (Overall Security Health Score, High/Critical Incidents, Affected Tenants, Leaked PII Attributes), an interactive Plotly gauge showing threat severity, a breakdown of incidents by business domain, and an attack vector distribution donut chart.",
         "Hover over the gauge meter and point to the 4 KPI cards. Explain the threat level.",
         "Sir, this is our Executive Overview designed for CISOs. At a glance, it shows that out of 15 API requests, 4 unauthorized BOLA attacks succeeded. We see a security health score of 38% (High Risk) because sensitive customer records and hospital diagnostic reports were accessed by unauthorized tenants."),

        ("2. 🚨 BOLA Findings",
         "The incident triage table. Displays every detected BOLA incident with its unique Incident ID (e.g. INC-BOLA-2026-0042), Endpoint URL, Requesting User, Resource Owner, Severity badge (CRITICAL / HIGH), and Timestamp. Clicking on any incident expands a detailed forensic inspector showing raw caller metadata and response samples.",
         "Click on the first incident in the list to expand the inspection drawer. Show the Caller Tenant vs Owner Tenant mismatch.",
         "Sir, this page lists all deterministically flagged BOLA incidents. Notice Incident #0042: User Alice (from FinServe Global) requested Document #2003, which belongs to Charlie (from HealthFirst Diagnostics). Our detector immediately identified that the caller's tenant does not match the resource owner's tenant, flagging it as a Critical cross-tenant breach."),

        ("3. 📋 Exposure Inventory",
         "A structured inventory cataloging all exfiltrated digital assets. Grouped into Orders, Documents, and User Profiles. Displays data sensitivity classifications (PII_FINANCIAL, PHI_HIPAA_PROTECTED, COMMERCIAL_CONFIDENTIAL) and exact compromised attribute counts.",
         "Toggle between the 'Orders' and 'Documents' tabs. Click 'View Raw Payload' to show the extracted JSON data.",
         "Sir, incident responders need to know what assets were stolen. This Exposure Inventory classifies every compromised record. Here under Documents, we see that Document 2003 contains patient biopsy lab results classified as HIPAA Protected Health Information (PHI). We can inspect the exact JSON payload the attacker received."),

        ("4. 👥 Affected Users & Blast Radius",
         "User-centric impact analysis. Shows a cross-tenant compromise matrix: who attacked whom. Identifies the most compromised victim users and rogue users conducting enumeration scans.",
         "Point to the victim cards showing Alice, Bob, Charlie, and Diana. Show the count of compromised records.",
         "Sir, here we see the human impact of the breach. This matrix shows which user accounts were impersonated or targeted. We can see that Charlie's patient records and Bob's executive compensation files were exfiltrated, showing the organizational spread."),

        ("5. 🕸️ Exposure Relationship Graph",
         "An interactive 3D/2D network graph built using NetworkX and Plotly WebGL. Blue nodes represent requesting users, red/purple nodes represent victim data objects, and connecting arrows show the unauthorized data exfiltration paths.",
         "Click and drag inside the Plotly graph to rotate it. Zoom in and hover your mouse over an edge to show the tooltip with incident severity.",
         "Sir, this is our interactive graph-theoretic visualization. Rather than reading raw logs, analysts see the attack topology visually. Blue nodes are the attackers, red nodes are the victim databases. The thickness and color of the arrows represent the sensitivity of the stolen data. We can zoom, pan, and hover over any node in real time."),

        ("6. 🔬 Semantic Property Delta (BOPLA)",
         "Our First Scientific Pillar! A side-by-side comparison workspace. Left column shows 'Delivered Response Keys' from the server; middle column shows 'Authorized Contract Schema'; right column displays the 'Semantic Property Delta' (Delta_leak) highlighted in glowing red tags.",
         "Point to the red tags showing leaked keys like `ssn`, `salary_bracket`, `credit_limit`, and `routing_code`.",
         "Sir, this demonstrates our first scientific novelty—the Semantic Property Delta. Notice that while the user was authorized to see the customer's name, the server accidentally returned hidden database columns: Social Security Number, credit limit, and salary bracket. Our algorithm calculates Delta_leak = Delivered minus Authorized, isolating the exact leaked secrets without manual review."),

        ("7. 🏢 Multi-Tenant Isolation & TIFI",
         "Our Second Scientific Pillar! Displays the Tenant Isolation Failure Index (TIFI) gauge meter, the Cross-Tenant Exfiltration Ratio (R_cross), the Shannon Directional Spillover Entropy (H_spill), and a directional cross-tenant leakage matrix.",
         "Point to the TIFI score of 0.800 (CRITICAL). Point to the directional matrix showing data flowing from HealthFirst Diagnostics to FinServe Global.",
         "Sir, this is our second invention: the Tenant Isolation Failure Index (TIFI). It answers: 'Did tenant boundaries collapse?' In our benchmark, TIFI is 0.800 (Critical Risk). This high entropy score proves that the attacker was not just stealing from one user, but was systematically traversing across completely different corporate tenants."),

        ("8. ⏱️ Attack Timeline & Replayer",
         "A chronological forensic timeline replayer. Features an interactive time scrubber slider. Security analysts can drag the slider to replay the attack step-by-step as it happened minute by minute.",
         "Drag the slider handle across the timeline. Watch the incidents light up sequentially on the screen.",
         "Sir, this Attack Replayer allows forensic investigators to travel back in time. By moving the slider, we can watch the attacker's reconnaissance unfold: first they tested their own order, then they changed the ID to 1002, then they enumerated document 2003. This timeline reconstruction is essential for incident response debriefs."),

        ("9. ⚖️ Risk & Impact Assessment",
         "A multi-dimensional risk calculator. Evaluates financial liability (in INR), regulatory exposure (DPDP / HIPAA / GDPR), and operational disruption scores based on the sensitivity of exfiltrated data.",
         "Show the financial risk score and regulatory penalty breakdown cards.",
         "Sir, this page translates raw technical logs into business risk. It computes that exfiltrating financial asset disclosures and HIPAA medical records elevates the overall incident risk to CRITICAL, exposing the firm to statutory liabilities under Indian and international privacy laws."),

        ("10. 🔐 Forensic PoE Certificate",
         "Our Third Scientific Pillar! Generates a court-admissible Cryptographic Proof-of-Exposure (PoE) Certificate anchored by a SHA-256 Merkle chain. Shows the digital certificate seal, Merkle root hash, block height, and timestamp.",
         "Select an incident from the dropdown. Point to the glowing Certificate. Click the '🖨️ Print / Save as PDF' button to demonstrate the 1-click Chrome native export!",
         "Sir, this is our third scientific contribution: the Proof-of-Exposure Certificate. Every incident is linked into an immutable SHA-256 Merkle hash chain. We can generate an official digital certificate complete with cryptographic root hashes and timestamps. With one click, this button opens Chrome's native print engine to export a court-admissible PDF."),

        ("11. 📜 Regulatory Compliance Notice",
         "Statutory notification generator for India's DPDP Act 2023 and the CERT-In 6-Hour reporting mandate. Pre-populates the official incident notification form with verified compromised counts and affected principal counts.",
         "Click 'Generate CERT-In Filing Notice'. Scroll through the pre-formatted formal disclosure document.",
         "Sir, Indian law mandates that cybersecurity incidents must be reported to CERT-In within 6 hours. ExposureLens automatically compiles this official statutory notice pre-filled with verified forensic counts, enabling compliance in seconds rather than days."),

        ("12. 🛡️ OPA & Virtual Patch Generator",
         "Runtime remediation engine. Generates declarative Open Policy Agent (OPA) Rego policy code, Python security decorators, and SQL tenant-scoping queries to neutralize the BOLA vulnerability instantly.",
         "Scroll through the clean Rego code block on screen. Point to the `allow` rule and `enforce_ownership` decorator.",
         "Sir, fixing code in large microservices takes weeks of testing and redeployment. ExposureLens automatically writes this Open Policy Agent (Rego) policy in real time. By injecting this rule into an API gateway, we block the hacker at the perimeter with zero microservice restarts and zero downtime."),

        ("13. 🔍 Cryptographic Evidence Explorer",
         "A deep-dive ledger inspector. Displays the complete SHA-256 Merkle chain: Block Height, Block Hash, Previous Hash (H_{k-1}), Timestamp, and Normalized Payload Digest. Includes a live chain integrity validator.",
         "Click 'Verify Chain Integrity'. Watch the system verify all blocks and display: '✅ Hash Chain Verified: 100% Tamper-Evident & Intact'.",
         "Sir, here we can inspect the raw cryptographic blockchain. Each block contains the previous block's hash and the SHA-256 digest of the stolen payload. When I click 'Verify Chain Integrity', the system recalculates the entire hash cascade. If anyone modifies even a single comma in the SQLite database, this test fails immediately."),

        ("14. 🤖 AI Incident Reports",
         "Our Fourth Scientific Pillar! Generates dual-mode AI summaries (Executive Briefing + Technical Analysis). Includes our live Zero-Hallucination Faithfulness Verifier badge showing 100.0% Faithfulness and 0.00% Hallucination.",
         "Click 'Generate AI Incident Report'. Point to the green verification badge showing: '✅ Faithfulness Score: 100.0% | Hallucination Score: 0.00%'.",
         "Sir, this is our fourth invention: Zero-Hallucination AI Forensics. While Large Language Models can write clear executive summaries, they frequently hallucinate fake IP addresses or numbers. ExposureLens runs a post-generation regex verification gate that matches every claimed entity against the raw database, guaranteeing 100% truthfulness for legal compliance."),

        ("15. 🧪 Research Evaluation & Benchmark",
         "The scientific evaluation testbed. Displays the empirical performance table across 15 enterprise scenarios: Precision = 1.000, Recall = 1.000, F1-Score = 1.000, and mean processing latency of under 6.2 milliseconds.",
         "Point to the latency breakdown chart and the perfect 1.0 accuracy metrics.",
         "Sir, this is our empirical research benchmark. We evaluated ExposureLens across 15 attack scenarios. It achieved a perfect Precision of 1.0 and Recall of 1.0 with zero false positives. Most importantly, total processing overhead is under 6.2 milliseconds, proving it operates at wire speed without slowing down real-world traffic."),

        ("16. 📄 IEEE Research Paper (LaTeX)",
         "A built-in academic manuscript viewer. Displays our complete research paper titled 'Deterministic Data Exposure Reconstruction and Multi-Tenant Isolation Failure Quantification for BOLA Vulnerabilities' in rendered Markdown with LaTeX mathematical formatting.",
         "Scroll through the abstract, equations, and references. Point to the 'Download LaTeX (.tex)' button.",
         "Sir, our entire research methodology has been written as a formal academic paper formatted for IEEE Transactions on Dependable and Secure Computing. Reviewers can read the mathematical formulation right here or download the complete LaTeX source code."),

        ("17. ⚙️ Settings & Lab Controls",
         "The developer and SOC control panel. Provides controls to purge database logs, seed baseline multi-tenant records, toggle mock vs live LLM endpoints, and adjust system risk thresholds.",
         "Point to the database status pill and the 'Re-seed Database' button.",
         "Sir, this is our administrative control panel. It allows SOC engineers to re-seed demo tenants, reset the audit database, or adjust sensitivity thresholds for different industry environments.")
    ]

    for p_num, p_name, p_ui, p_speech in pages_info:
        add_header(doc, f"Workspace {p_num}: {p_name}", level=2)
        add_p(doc, p_ui, bold_prefix="What is on this screen: ")
        add_p(doc, p_speech, bold_prefix="What to do during demo: ")
        add_speech_box(doc, p_speech)

    # -------------------------------------------------------------------------
    # PART 4: GUIDE CHALLENGE QUESTIONS CHEAT-SHEET
    # -------------------------------------------------------------------------
    add_header(doc, "PART 4: 'What If the Guide Challenges Me?' Live Demo Cheat-Sheet", level=1)
    add_p(doc, "During the live demo, professors love to test you with spontaneous requests. Here is exactly what to click if they throw these 5 classic challenges at you:")

    challenges = [
        ("Guide asks: 'Can you show me where the attack is actually blocked?'",
         "Action: Navigate to Workspace #12 (🛡️ OPA & Virtual Patch Generator). Point to the generated Rego rule: `allow { input.user.tenant_id == input.resource.owner_tenant_id }`. Then explain: 'Sir, we also implemented a patched reference endpoint in our Flask backend: `/api/secure/orders/<id>`. When an unauthorized user requests this route, the server checks ownership and returns HTTP 403 Forbidden immediately.'"),

        ("Guide asks: 'How do I know this data is real and not hardcoded?'",
         "Action: Go to Workspace #2 (🚨 BOLA Findings) or Workspace #3 (📋 Exposure Inventory). Click 'View Raw Payload' on any incident. Point to the JSON showing the real order amount (INR 149,999 for MacBook Pro) and user ID. Then open `backend/database.py` on your laptop to show the exact SQLite tables."),

        ("Guide asks: 'Can you prove the blockchain hash chain actually works?'",
         "Action: Navigate to Workspace #13 (🔍 Cryptographic Evidence Explorer). Click the button: 'Verify Chain Integrity'. The system will recalculate all SHA-256 hashes on the fly and display: '✅ Hash Chain Verified: 100% Tamper-Evident & Intact'."),

        ("Guide asks: 'Why is your TIFI score exactly 0.800?'",
         "Action: Navigate to Workspace #7 (🏢 Multi-Tenant Isolation & TIFI). Point to the two sub-metrics: Cross-Tenant Ratio (R_cross = 0.75) and Shannon Entropy (H_spill = 0.92). Explain: 'Sir, because the attacker didn't just attack one user inside their own company, but reached across into HealthFirst Diagnostics and OmniRetail, the directional entropy is high, driving the composite TIFI to 0.800 (Critical Risk).'"),

        ("Guide asks: 'Where is the AI and how do you prevent hallucinations?'",
         "Action: Navigate to Workspace #14 (🤖 AI Incident Reports). Click 'Generate AI Incident Report'. Point to the green verification badge showing: 'Faithfulness Score: 100.0% | Hallucination Score: 0.00%'. Explain: 'Sir, our regex verification engine extracts every IP, tenant ID, and number from the text and tests them via set-intersection against our SQLite database. Nothing is allowed through without database verification.'")
    ]

    for q_title, q_resp in challenges:
        add_p(doc, q_resp, bold_prefix=f"{q_title} -> ")

    # Save Document
    os.makedirs("Project_Presentation_Preparation", exist_ok=True)
    docx_path = os.path.abspath("Project_Presentation_Preparation/ExposureLens_Live_Demo_and_Feature_Walkthrough.docx")
    pdf_path = os.path.abspath("Project_Presentation_Preparation/ExposureLens_Live_Demo_and_Feature_Walkthrough.pdf")
    doc.save(docx_path)
    print(f"[SUCCESS] Live Demo Guide Word doc saved to: {docx_path} ({os.path.getsize(docx_path):,} bytes)")

if __name__ == "__main__":
    build_demo_guide()
