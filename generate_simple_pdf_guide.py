import os
import sys
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
import win32com.client

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

def add_callout(doc, text, title="EVERYDAY REAL-LIFE ANALOGY", bg_hex="F0FDF4"):
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
    r_lbl = p.add_run("What to Say to Your Guide in 30 Seconds:\n")
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

def add_terms_table(doc, terms_list):
    tbl = doc.add_table(rows=len(terms_list) + 1, cols=3)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers = ["Technical Term on PPT", "Everyday Plain English Meaning", "Real-Life Example"]
    for i, h in enumerate(headers):
        c = tbl.rows[0].cells[i]
        set_cell_background(c, "0B132B")
        set_cell_margins(c, top=60, bottom=60, left=90, right=90)
        p = c.paragraphs[0]
        r = p.add_run(h)
        r.font.bold = True
        r.font.size = Pt(9)
        r.font.color.rgb = RGBColor(255, 255, 255)
    
    col_widths = [Inches(1.8), Inches(2.6), Inches(2.1)]
    for row_idx, (t, m, ex) in enumerate(terms_list, start=1):
        for col_idx, text in enumerate([t, m, ex]):
            c = tbl.rows[row_idx].cells[col_idx]
            c.width = col_widths[col_idx]
            set_cell_background(c, "F8FAFC" if row_idx % 2 == 1 else "FFFFFF")
            set_cell_margins(c, top=50, bottom=50, left=80, right=80)
            p = c.paragraphs[0]
            r = p.add_run(text)
            r.font.size = Pt(8.5)
            r.font.color.rgb = COLOR_NAVY if col_idx == 0 else COLOR_SLATE
            if col_idx == 0:
                r.font.bold = True
    sp = doc.add_paragraph()
    sp.paragraph_format.space_before = Pt(0)
    sp.paragraph_format.space_after = Pt(3)

def build_simple_pdf_guide():
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
    r_title = p_title.add_run("EXPOSURELENS: SLIDE-BY-SLIDE SIMPLE ENGLISH GUIDE & COMPLETE TERMINOLOGY HANDBOOK")
    r_title.font.name = 'Calibri'
    r_title.font.size = Pt(18)
    r_title.font.bold = True
    r_title.font.color.rgb = COLOR_NAVY

    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_before = Pt(0)
    p_sub.paragraph_format.space_after = Pt(6)
    r_sub = p_sub.add_run("A Non-Technical Guide Explaining Every Single Slide, Everyday Analogy, and Cyber Security Term for M.Tech Major Project Defense")
    r_sub.font.name = 'Calibri'
    r_sub.font.size = Pt(11.5)
    r_sub.font.bold = True
    r_sub.font.color.rgb = COLOR_TEAL

    # Student metadata table
    tbl_meta = doc.add_table(rows=4, cols=2)
    tbl_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta = [
        ("Candidate Name & Roll Number:", "Saikat Mondal (Roll Number: 25168016)"),
        ("Degree & Institution:", "M.Tech in Cyber Security | School of Computer Engineering, KIIT Bhubaneswar"),
        ("Project Title:", "ExposureLens: AI-Assisted Data Exposure Reconstruction & Blast Radius Analysis for BOLA"),
        ("Public Live Cloud App:", "https://exposurelens.onrender.com | GitHub: github.com/saikatmondal-cy/ExposureLens")
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

    # =========================================================================
    # PART 1: SLIDE-BY-SLIDE WALKTHROUGH
    # =========================================================================
    add_header(doc, "PART 1: Slide-by-Slide Walkthrough (Explained in Plain English)", level=1)
    add_p(doc, "This section breaks down all 11 slides of your PowerPoint deck. For every slide, you get: (1) What it means in plain English, (2) A real-life story/analogy, (3) A table explaining EVERY technical word on that slide, and (4) The exact 30-second speech you can deliver to your guide.")

    # -------------------------------------------------------------------------
    # SLIDE 1
    # -------------------------------------------------------------------------
    add_header(doc, "SLIDE 1: Title & Academic Credentials", level=2)
    add_p(doc, "This is your opening introduction slide. You are introducing yourself, your college (KIIT), and your software (ExposureLens). You are establishing that this is not just homework—it is a live, working cybersecurity tool.")
    add_callout(doc, "Imagine you are an inventor who built a new kind of flight black-box recorder for websites. Before you show how it works, you introduce yourself and show everyone that the invention is already built and working live.", title="SLIDE 1 ANALOGY")
    
    s1_terms = [
        ("ExposureLens", "The official name of our software project.", "Like 'CCTV' or 'Black Box' for website data."),
        ("BOLA", "Broken Object Level Authorization. A bug where a website lets User A view User B's private files just by changing a number in the link.", "Like a hotel room key that opens someone else's room."),
        ("Reconstruction", "Rebuilding the exact data that the hacker saw and stole.", "Like piecing together a shredded document to see what was read."),
        ("Blast Radius", "Measuring how far the damage spread across different companies.", "Like calculating how many houses caught fire from one spark."),
        ("Multi-Tenant", "A website or software where many different companies share the same computer server.", "Like an apartment building where many families share the same main gate and water supply."),
        ("Render Cloud", "The online server company where our project is running live 24/7.", "Like hosting a live website on the internet so anyone can open it.")
    ]
    add_terms_table(doc, s1_terms)
    add_speech_box(doc, "Good morning, Respected Guide and Examiners. My name is Saikat Mondal, Roll Number 25168016. Today, I am presenting ExposureLens. In simple words, it is a digital detective and black-box recorder for web applications that detects hidden data leaks, figures out whose data was stolen, and writes a tamper-proof forensic report about it. Our software is live on the cloud and open-source on GitHub.")

    # -------------------------------------------------------------------------
    # SLIDE 2
    # -------------------------------------------------------------------------
    add_header(doc, "SLIDE 2: Research Motivation & Problem Statement", level=2)
    add_p(doc, "This slide explains WHY we made ExposureLens. It explains the 'Silent Theft' paradox: why traditional firewalls fail, and why scanners only warn you before an attack but are completely useless after a real attack happens.")
    add_callout(doc, "Think of a hotel guest who is given a key to Room 101. But he walks to Room 102, turns the knob, and it opens! He steals the suitcase from Room 102. The security guard in the lobby saw nothing wrong because the thief was a registered guest who entered through the front door with an ID. That is BOLA.", title="SLIDE 2 ANALOGY: THE HOTEL KEYCARD")

    s2_terms = [
        ("OWASP API #1", "The Open Web Application Security Project's list of the top 10 most dangerous security bugs. BOLA is ranked #1 worldwide.", "Like the FBI's #1 most wanted cyber vulnerability."),
        ("HTTP 200 OK", "The standard code a website sends when a page loads successfully without any error.", "Like a green checkmark saying 'Everything worked fine!'"),
        ("Silent Breach Paradox", "A disaster where sensitive data is stolen, but the computer logs say 'HTTP 200 OK', so no alarm ever rings.", "A thief who steals diamonds using a key, so the burglar alarm never sounds."),
        ("WAF (Web Application Firewall)", "A security shield that inspects website traffic to block obvious hacking strings like SQL injection or virus code.", "A security guard checking bags at the mall for weapons."),
        ("API Gateway", "The front door through which all phone apps and websites talk to backend databases.", "The receptionist at a building who checks your visitor badge."),
        ("DAST / SAST Scanners", "Automated software tools that look for bugs in code before a website goes live.", "A car inspection checklist before you buy a car. It tells you a tire is loose, but it can't tell you who stole your luggage after an accident!"),
        ("Post-Exploitation Void", "The complete lack of tools to answer: 'What data leaked? Who owned it? How many companies were damaged?' after an attack happens.", "Calling the police after a burglary and discovering nobody knows what items are missing.")
    ]
    add_terms_table(doc, s2_terms)
    add_speech_box(doc, "Sir, normal firewalls only look for obvious bad things, like a virus or SQL injection. But in a BOLA attack, the hacker logs in like a normal customer. Then, they simply change an ID number in the link—like changing 101 to 102—and the website politely hands over someone else's private data! The firewall logs a clean '200 OK', completely blind to the theft. Traditional scanners only test for bugs beforehand; they cannot tell you what leaked during an actual breach. ExposureLens solves this post-exploitation blindspot.")

    # -------------------------------------------------------------------------
    # SLIDE 3
    # -------------------------------------------------------------------------
    add_header(doc, "SLIDE 3: Research Novelty & Four Scientific Pillars", level=2)
    add_p(doc, "This slide presents our 4 big inventions that make ExposureLens unique. It answers the examiner's question: 'What did you create that didn't exist before?'")
    add_callout(doc, "ExposureLens is like an advanced medical ICU kit: (1) It diagnoses the exact poison that leaked, (2) It measures how many organs were infected, (3) It locks the blood sample in a tamper-proof evidence tube, and (4) It writes a doctor's report that never makes up fake symptoms.", title="SLIDE 3 ANALOGY: THE ICU DIAGNOSTIC KIT")

    s3_terms = [
        ("Semantic Property Delta (Delta_leak)", "A mathematical formula that subtracts the allowed data from the delivered data to find the exact private secrets that leaked.", "Delivered = {Name, Phone, SSN}. Allowed = {Name}. Leaked Secret = {Phone, SSN}."),
        ("BOPLA (OWASP API3:2023)", "Broken Object Property-Level Authorization. Even if you are allowed to see a record, the server accidentally sends hidden private fields like salaries or passwords.", "Ordering a water bottle and the waiter accidentally leaves his store keys on your table."),
        ("TIFI Metric", "Tenant Isolation Failure Index. A score from 0.0 to 1.0 measuring whether data leakage was small (0.1) or an entire building collapse (0.9).", "Like the Richter Scale for earthquake damage."),
        ("Shannon Entropy", "A mathematical concept from physics and information theory that measures randomness or disorder.", "Measuring whether leaked water stayed in one room or flooded the entire floor."),
        ("Proof-of-Exposure (PoE)", "Locking attack records into a blockchain so nobody can change or deny what happened.", "A wax seal on a royal letter that breaks if anyone touches it."),
        ("SHA-256 Merkle Chain", "A digital fingerprint technique where every record is tied to the previous record's fingerprint.", "A metal bicycle chain: you cannot remove one link without breaking the entire chain."),
        ("Zero-Hallucination AI", "Using AI to write reports, but running every word through a strict fact-checker so it never makes up fake numbers.", "A journalist whose every sentence must be proven by a photograph before printing.")
    ]
    add_terms_table(doc, s3_terms)
    add_speech_box(doc, "Sir, our research contribution stands on four scientific pillars: First, the Semantic Property Delta isolates the exact secret attributes that leaked. Second, our TIFI metric calculates a 0-to-1 score of multi-tenant boundary damage. Third, our Proof-of-Exposure engine chains every incident into an immutable SHA-256 ledger for court admissibility. And fourth, our AI engine writes statutory reports that achieve 100% faithfulness by fact-checking every claim against raw database logs.")

    # -------------------------------------------------------------------------
    # SLIDE 4
    # -------------------------------------------------------------------------
    add_header(doc, "SLIDE 4: System Architecture & End-to-End Pipeline", level=2)
    add_p(doc, "This slide shows how the software is built inside. It shows the 3 stages: listening to traffic, analyzing the leak, and producing the report and fix.")
    add_callout(doc, "Think of an airport baggage scanner: Stage 1 takes an X-ray of the bag as it rolls on the conveyor belt. Stage 2 analyzes the X-ray to spot dangerous items. Stage 3 rings the alarm, prints an incident ticket, and locks the conveyor belt.", title="SLIDE 4 ANALOGY: AIRPORT BAGGAGE SCANNER")

    s4_terms = [
        ("Decoupled Architecture", "Building software in separate modules so that if one piece needs an update, the rest of the system keeps running smoothly.", "Like Lego blocks that click together rather than a single solid block of plastic."),
        ("Telemetry Ingestion", "Quietly collecting data about every click, request, and download without slowing down the website.", "A car's odometer recording your mileage as you drive."),
        ("JWT (JSON Web Token)", "A digital passport that an app gives you when you log in. It contains your name, user ID, and company.", "A wristband at a music festival showing you paid for entry."),
        ("Bearer Token", "A key you show in your web browser headers that says: 'I am logged in, let me through'.", "Holding up your concert VIP wristband to the guard."),
        ("SQLite", "A lightweight, self-contained database that stores information in a single file on your computer.", "A digital filing cabinet that requires zero installation."),
        ("Streamlit", "A modern Python framework for building interactive web apps and dashboards for data scientists.", "The graphical display screen showing meters, graphs, and buttons."),
        ("SOC (Security Operations Center)", "The mission control room where cybersecurity analysts watch monitors for attacks.", "The security room in a bank with 20 TV screens showing CCTV feeds.")
    ]
    add_terms_table(doc, s4_terms)
    add_speech_box(doc, "Sir, our architecture is divided into three decoupled stages: Stage 1 ingests traffic non-invasively, reading the user's digital passport (JWT) and response payloads. Stage 2 is our detection brain: it checks object ownership, calculates property deltas, and constructs the attack graph. Stage 3 mints the cryptographic proof, creates a virtual patch, and provides real-time visibility on our Streamlit SOC dashboard shown on the right.")

    # -------------------------------------------------------------------------
    # SLIDE 5
    # -------------------------------------------------------------------------
    add_header(doc, "SLIDE 5: Deterministic BOLA Detection & Semantic Property Delta", level=2)
    add_p(doc, "This slide explains how our detection math works without guessing. It shows how we catch both object theft (BOLA) and secret property leaks (BOPLA), backed by a live screenshot of incident `INC-BOLA-2026-0042`.")
    add_callout(doc, "A detective doesn't guess who committed a crime. He checks the ID card, checks the owner on the deed of the house, and if they don't match, it is an illegal trespass. That is deterministic logic.", title="SLIDE 5 ANALOGY: THE TRESPASS DETECTIVE")

    s5_terms = [
        ("Context Tuple (C)", "A bundle of 6 facts checked for every request: <Caller User, Caller Company, Caller Role, Target Resource, Owner Company, Data Sent>.", "Checking: (1) Who asked? (2) Which company are they from? (3) Whose file is it?"),
        ("Deterministic Logic", "A strict mathematical rule that gives a clear 100% YES or NO answer, without fuzzy guessing or probability.", "A calculator multiplying 2 x 2 = 4 (it is never 3.9 or 4.1)."),
        ("PII (Personally Identifiable Information)", "Sensitive personal data that can identify an individual, like Social Security Numbers, phone numbers, or home addresses.", "Your Aadhaar card or PAN card number."),
        ("JSON Schema", "The official blueprint of what a website's response is supposed to look like.", "A restaurant menu showing what dishes come with your meal."),
        ("Attribute Leakage", "When internal database columns (like credit limit or password hash) accidentally spill out into the user's browser.", "A waiter accidentally giving you the restaurant's daily earnings ledger.")
    ]
    add_terms_table(doc, s5_terms)
    add_speech_box(doc, "Sir, we avoid fuzzy guessing. Every request is tested against an authorization context tuple: if the caller's company does not match the resource owner's company, it is deterministically flagged as BOLA. Furthermore, our Semantic Delta compares the returned JSON against the official contract. In the real incidents in our system, an attacker from FinServe Global requested a HealthFirst Diagnostics medical document. While normal logs showed an ordinary response, ExposureLens isolated the leaked secrets: patient names, diagnostic biopsy findings, and prescribed oncology regimens.")

    # -------------------------------------------------------------------------
    # SLIDE 6
    # -------------------------------------------------------------------------
    add_header(doc, "SLIDE 6: Tenant Isolation Failure Index (TIFI) & Blast Radius", level=2)
    add_p(doc, "This slide explains how we measure the spread of an attack across companies. It explains our formula called **TIFI** and shows our interactive spiderweb attack graph.")
    add_callout(doc, "If a water pipe leaks inside Apartment 4, only Apartment 4 has a wet carpet. But if the leak breaks through the walls and floods Apartments 5, 6, and 7, the entire building's isolation has failed. TIFI measures that spread.", title="SLIDE 6 ANALOGY: THE APARTMENT WATER LEAK")

    s6_terms = [
        ("Tenant", "A company or client organization using a shared cloud software.", "Company 1 (FinServe Global) and Company 2 (HealthFirst Diagnostics) sharing the same cloud server."),
        ("Cross-Tenant Leak", "When an attacker from Company A successfully steals private records belonging to Company B.", "A financial user from FinServe Global accessing oncology patient biopsy records in HealthFirst Diagnostics."),
        ("Directional Spillover", "Tracking the direction in which data flowed (e.g. from HealthFirst Diagnostics to FinServe Global).", "Tracking where stolen goods traveled from the victim to the receiver."),
        ("Asymmetric Blast Radius", "When one company attacks many, but only certain victims suffer catastrophic damage.", "A fire that burns down three specific rooms while leaving others untouched."),
        ("Network Graph", "A visual map of dots (nodes = companies) and connecting arrows (edges = stolen data).", "A flight route map showing which cities have flights connecting them.")
    ]
    add_terms_table(doc, s6_terms)
    add_speech_box(doc, "Sir, in cloud SaaS, knowing the number of stolen records is not enough—we must know if company walls broke down. TIFI combines the ratio of cross-company theft with Shannon entropy. If an attack is isolated to one company, TIFI is low. If it spreads across multiple companies, TIFI shoots up toward 1.0. In our benchmark, TIFI was 0.80, indicating a critical-severity systemic breach. The interactive graph on the right visually maps the exact attack path.")

    # -------------------------------------------------------------------------
    # SLIDE 7
    # -------------------------------------------------------------------------
    add_header(doc, "SLIDE 7: Cryptographic Proof-of-Exposure (PoE) Blockchain", level=2)
    add_p(doc, "This slide explains how we protect evidence so it can stand up in a court of law. It shows our digital fingerprint chain and court-admissible certificate.")
    add_callout(doc, "Imagine an official government land registry book where every page is stamped with an indelible numbered seal. If someone rips out Page 42 or changes the owner's name with white-out, the serial numbers and seals don't line up, proving fraud immediately.", title="SLIDE 7 ANALOGY: THE INDELIBLE LAND REGISTRY")

    s7_terms = [
        ("Chain of Custody", "A legal record showing who collected evidence, when, and proving that nobody altered it since.", "A sealed police evidence bag signed by the investigating officer."),
        ("Non-Repudiation", "A mathematical guarantee that a person or company cannot say: 'I didn't do it' or 'That log is fake'.", "A signed, notarized registered post receipt."),
        ("Digital Fingerprint (Hash)", "A 64-character mathematical code generated from text. If even one letter changes, the fingerprint completely transforms.", "Human fingerprint: unique to that exact data."),
        ("Genesis Block", "The very first, permanently locked block in a blockchain that starts the chain.", "The cornerstone of a building laid on day one."),
        ("Merkle Root", "A single master digital fingerprint that summarizes thousands of individual transactions.", "The summary total at the bottom of a 50-page ledger."),
        ("Tamper-Evident", "A property where any attempt to modify or delete data leaves an obvious, permanent broken mark.", "A security sticker on a new iPhone box that rips when opened.")
    ]
    add_terms_table(doc, s7_terms)
    add_speech_box(doc, "Sir, during data breach lawsuits, defense lawyers often claim server logs were retroactively edited by system administrators. Without mathematical proof, regular log files lack legal weight. ExposureLens chains every reconstructed incident into an immutable SHA-256 Merkle ledger. Any modification to local database records breaks the cryptographic hash cascade immediately. The system generates a verifiable Forensic Certificate with Merkle roots, ready for judicial scrutiny.")

    # -------------------------------------------------------------------------
    # SLIDE 8
    # -------------------------------------------------------------------------
    add_header(doc, "SLIDE 8: Statutory Regulatory Compliance & Automated Virtual Patching", level=2)
    add_p(doc, "This slide explains how our tool protects companies from massive government fines (₹250 Crores) and how it blocks hackers in seconds using an automated digital barrier (Virtual Patch).")
    add_callout(doc, "If a pipe bursts in your kitchen, you don't wait 3 weeks for an architect to redesign the house plumbing. You immediately put a clamp on the leak to stop the flooding! That is a Virtual Patch.", title="SLIDE 8 ANALOGY: THE EMERGENCY PIPE CLAMP")

    s8_terms = [
        ("India DPDP Act 2023", "India's Digital Personal Data Protection Act. A strict law penalizing companies up to ₹250 Crores for failing to protect citizen data.", "India's official data privacy law, similar to Europe's GDPR."),
        ("CERT-In 6-Hour Rule", "The Indian Computer Emergency Response Team's mandatory rule requiring cyber incidents to be reported within 6 hours.", "Calling the fire brigade within minutes of a fire starting."),
        ("GDPR (Articles 33 & 34)", "European Union data privacy law requiring companies to notify authorities within 72 hours of a breach.", "Europe's strict data privacy regulation."),
        ("Virtual Patching", "Adding a firewall rule at the front gate to block a hacker immediately, without needing to rewrite or turn off the website code.", "Putting a padlock on a broken door while waiting for the carpenter."),
        ("Open Policy Agent (OPA)", "An industry-standard open-source engine that makes authorization decisions at the front gate.", "A bouncer holding a guest list at a VIP club."),
        ("Rego", "The clean programming language used by Open Policy Agent to write security rules.", "Writing rules like: 'If caller company is not owner company, DENY access'.")
    ]
    add_terms_table(doc, s8_terms)
    add_speech_box(doc, "Sir, under India's DPDP Act 2023, failing to prevent data leaks carries fines up to 250 Crores INR, and CERT-In mandates reporting within 6 hours. ExposureLens prepares pre-populated statutory notification notices in milliseconds. Furthermore, traditional code fixes take weeks to test and deploy. ExposureLens synthesizes Open Policy Agent Rego virtual patches on the fly, blocking the exploit path at the perimeter with zero microservice downtime.")

    # -------------------------------------------------------------------------
    # SLIDE 9
    # -------------------------------------------------------------------------
    add_header(doc, "SLIDE 9: AI Forensic Reporting & Zero-Hallucination Audit", level=2)
    add_p(doc, "This slide explains how we use Artificial Intelligence safely. It shows why raw AI cannot be trusted with forensic reports, and how our fact-checking gate guarantees 100% truthfulness.")
    add_callout(doc, "Imagine an AI assistant writes a police report about a car crash, but invents a fake license plate number! In court, that fake detail ruins the entire case. ExposureLens puts a strict fact-checker behind the AI to ensure every single word is backed by database proof.", title="SLIDE 9 ANALOGY: THE COURT STENOGRAPHER")

    s9_terms = [
        ("LLM (Large Language Model)", "Advanced AI models like GPT-4 or Gemini that can read, write, and summarize text in human English.", "An ultra-smart digital copywriter."),
        ("AI Hallucination", "When an AI confidently invents fake facts, non-existent IP addresses, or wrong numbers.", "A student making up a fake quote during an oral exam because they forgot the real one."),
        ("Ground-Truth Bounding", "Forcing the AI to only write facts that exist in the raw database records.", "Telling a witness: 'You may only answer what is written in this signed police report'."),
        ("Faithfulness Score (100%)", "A mathematical score proving that 100% of the facts cited by the AI match the underlying database.", "Scoring 100/100 on an open-book history test."),
        ("Entity Extraction", "A computer script that scans text to find and pull out all IP addresses, company names, timestamps, and numbers.", "Using a yellow highlighter to mark all names and phone numbers in a letter.")
    ]
    add_terms_table(doc, s9_terms)
    add_speech_box(doc, "Sir, while Large Language Models can write clear executive summaries, they frequently hallucinate fake numbers or IP addresses, which is unacceptable in legal filings. ExposureLens implements a deterministic verification gate: after the AI drafts the report, our parser extracts every entity claim and verifies it against our raw database. Our live application achieves 100% Faithfulness and 0% Hallucination, providing mathematical confidence that the report is legally sound.")

    # -------------------------------------------------------------------------
    # SLIDE 10
    # -------------------------------------------------------------------------
    add_header(doc, "SLIDE 10: Experimental Evaluation & Research Benchmark", level=2)
    add_p(doc, "This slide presents our report card. It shows how we tested our software against 15 real-world attack scenarios, and proves it runs in under 6.2 milliseconds.")
    add_callout(doc, "Before an airplane is certified to fly, it is tested in wind tunnels through 15 severe storm scenarios. ExposureLens was tested against 15 attack simulations across banking, healthcare, and retail to prove it never misses an attack.", title="SLIDE 10 ANALOGY: THE WIND TUNNEL TEST")

    s10_terms = [
        ("Precision (1.000)", "How often the alarm is real. A score of 1.0 means zero false alarms on innocent users.", "Out of 100 alarms, all 100 were real thieves."),
        ("Recall / Sensitivity (1.000)", "How good the tool is at catching every attack. A score of 1.0 means it caught 100% of attacks.", "Out of 100 thieves who tried to enter, all 100 were caught."),
        ("F1-Score (1.000)", "The balanced average of Precision and Recall. 1.0 is a perfect score.", "Getting an A+ on both catching bad guys and leaving innocent people alone."),
        ("Latency (< 6.2 ms)", "The time it takes to process an incident. 6.2 milliseconds is 0.0062 seconds!", "Faster than a camera shutter or a human eye blink (which takes 100–400 ms)."),
        ("Wire Speed", "Processing network packets so fast that internet traffic never slows down.", "A toll booth with high-speed FASTag where cars never have to stop."),
        ("IEEE TDSC", "IEEE Transactions on Dependable and Secure Computing. One of the most prestigious cybersecurity research journals in the world.", "A top-tier academic gold medal for cybersecurity research.")
    ]
    add_terms_table(doc, s10_terms)
    add_speech_box(doc, "Sir, we tested ExposureLens across 15 enterprise scenarios simulating healthcare, fintech, and ERP APIs. Because our detection engine binds strict authorization contexts, it achieved a perfect Precision of 1.0, Recall of 1.0, and F1-score of 1.0, with zero false positives. Crucially, total processing latency is under 6.2 milliseconds per incident, meaning it operates at wire speed. These results form the core of our research paper prepared for IEEE TDSC.")

    # -------------------------------------------------------------------------
    # SLIDE 11
    # -------------------------------------------------------------------------
    add_header(doc, "SLIDE 11: Live Deployment, Limitations & Future Roadmap", level=2)
    add_p(doc, "This is your closing slide. You show your live working website, your GitHub repo, honestly state current limitations, and explain what you will build next.")
    add_callout(doc, "A great scientist doesn't just show their invention; they show that it is running in the real world, honestly explain what it cannot do yet, and show the roadmap for version 2.0.", title="SLIDE 11 ANALOGY: THE ROADMAP")

    s11_terms = [
        ("Live Deployment", "Running on a real public internet cloud server where anyone in the world can test it right now.", "A real store open on the street, not just a 3D blueprint on a computer."),
        ("Healthcheck", "An automated pulse check (`/_stcore/health`) that continuously verifies the website is alive and working.", "A hospital heart rate monitor showing a steady, healthy heartbeat."),
        ("REST API", "The most common way modern websites send data using standard HTTP URLs and JSON.", "Standard post office envelopes with addresses written in plain text."),
        ("GraphQL", "A newer API style where users can request custom, deeply nested data trees.", "A custom buffet where you pick exact ingredients instead of a fixed combo meal."),
        ("Linux eBPF Probes", "A cutting-edge technology that lets you run security filters inside the core brain (kernel) of the Linux operating system without touching application code.", "Installing a sensor directly inside an engine's fuel line for zero-delay monitoring."),
        ("CI/CD 'Shift-Left'", "Testing code for security bugs automatically every time a developer saves their work, before it ever reaches production.", "Checking every airplane bolt in the factory before the plane ever leaves the hangar.")
    ]
    add_terms_table(doc, s11_terms)
    add_speech_box(doc, "To conclude, Sir: ExposureLens is fully operational and deployed live on Render at exposurelens.onrender.com, with all 25 modules open on GitHub. In accordance with rigorous academic standards, we acknowledge our current scope: it is optimized for REST/JSON APIs and requires gateway telemetry. In our future work, we are developing Linux eBPF kernel probes for zero-overhead packet interception and CI/CD shift-left testing. ExposureLens successfully transforms silent BOLA breaches into verifiable, deterministic proof. Thank you, Sir, I invite your questions.")

    # =========================================================================
    # PART 2: THE MASTER A-Z CYBERSECURITY DICTIONARY
    # =========================================================================
    add_header(doc, "PART 2: The Master A-Z Dictionary of Cyber Security & Project Terms", level=1)
    add_p(doc, "Here is a quick-reference alphabetical dictionary of every technical buzzword, abbreviation, and concept used in your defense. Study these so that no matter what term your guide asks about, you can answer in one clear sentence!")

    dict_terms = [
        ("API (Application Programming Interface)", "The software messenger that connects websites and mobile apps to backend databases.", "A restaurant waiter taking orders to the kitchen and bringing back food."),
        ("API Gateway", "A single entrance door that manages, inspects, and throttles all incoming API traffic.", "The security gate at an embassy checking badges before people enter."),
        ("BOLA (Broken Object Level Authorization)", "An access control bug where an app fails to check whether a logged-in user actually owns the object they are asking for.", "Using your apartment key to unlock your neighbor's front door."),
        ("BOPLA (Broken Object Property-Level Auth)", "When an API allows access to an object, but accidentally returns private internal fields like passwords, SSNs, or salary bands.", "Buying a used book and finding a secret handwritten diary inside."),
        ("Blast Radius", "The total scope and spread of damage caused by a security breach across users, assets, and companies.", "The radius of a fire spreading across neighboring buildings."),
        ("CERT-In (Cyber Emergency Response Team)", "The Indian government nodal agency responsible for cybersecurity incident response and national defense.", "The cyber police of India."),
        ("CERT-In 6-Hour Mandate", "The strict legal requirement in India that companies must report cyber incidents within 6 hours of discovery.", "Mandatory reporting of an accident to authorities without delay."),
        ("Chain of Custody", "A chronological forensic paper trail showing the collection, custody, and transfer of digital evidence.", "A sealed police evidence bag signed by the investigating officer."),
        ("CI/CD (Continuous Integration / Deployment)", "An automated software assembly line that tests and deploys code whenever changes are committed.", "An automated car factory testing every brake before shipping."),
        ("DAST (Dynamic App Security Testing)", "Testing a running website from the outside by sending simulated attack payloads.", "Trying all the windows of a house to see if any are unlocked."),
        ("Decoupled Microservices", "Designing an application as independent, modular components that communicate over lightweight networks.", "A team of specialists where the plumber, electrician, and painter work independently."),
        ("Deterministic Detection", "Detection based on absolute mathematical and logical rules, producing 100% reproducible outcomes without guesswork.", "A calculator computing 2 + 2 = 4."),
        ("Digital Certificate", "A cryptographically signed digital document proving identity, timestamp, and data integrity.", "A government passport with an official holographic seal."),
        ("DPDP Act 2023", "India's Digital Personal Data Protection Act, imposing penalties up to ₹250 Crores for data privacy failures.", "India's national privacy law protecting citizen data."),
        ("eBPF (Extended Berkeley Packet Filter)", "A revolutionary Linux kernel technology allowing sandboxed programs to run inside the OS kernel for line-rate monitoring.", "A tiny sensor placed directly inside a car engine's fuel line."),
        ("F1-Score", "The harmonic balance between Precision (avoiding false alarms) and Recall (catching all attacks).", "A balanced school grade rewarding both high test scores and zero missed assignments."),
        ("Faithfulness Score", "The mathematical percentage of claims in an AI-generated report that are 100% verified by raw database logs.", "An open-book test score verifying every statement against the textbook."),
        ("Flask", "A lightweight, flexible Python web framework used to build RESTful microservice APIs.", "A simple, reliable engine for running web applications."),
        ("GDPR (General Data Protection Regulation)", "The European Union's comprehensive data privacy law mandating breach notifications within 72 hours.", "Europe's strict data protection law."),
        ("Genesis Block", "The very first, hardcoded block in a cryptographic blockchain that acts as the anchor for all future blocks.", "The first brick laid at the foundation of a building."),
        ("GraphQL", "An alternative API query language that allows clients to request exact, deeply nested fields in a single query.", "A custom buffet where you pick the exact ingredients you want."),
        ("Hallucination (AI)", "When an AI model invents fictional facts, nonexistent IP addresses, or wrong numbers with high confidence.", "A student making up a fictional quote in an essay."),
        ("Hash / SHA-256", "A mathematical algorithm turning any amount of data into a unique 64-character digital fingerprint.", "Human fingerprint: unique to that exact data."),
        ("Heuristic Detection", "Detection based on statistical patterns, probabilities, or educated guesses rather than strict rules.", "Guessing it might rain because the sky looks grey."),
        ("HTTP 200 OK", "The standard web server response indicating that a web request was received and processed successfully.", "A thumbs-up saying 'Everything is fine'."),
        ("JWT (JSON Web Token)", "A cryptographically signed digital passport containing a user's ID, role, and expiration timestamp.", "An electronic keycard showing your hotel room number and checkout date."),
        ("Latency", "The time delay between sending a web request and receiving a response, measured in milliseconds.", "The delay between pressing a light switch and the bulb turning on."),
        ("Merkle Tree / Hash Chain", "A cryptographic structure where data blocks are linked together by hashes, making tampering impossible.", "A chain where every link is welded to the previous link."),
        ("Multi-Tenant", "An architecture where multiple independent organizations share the same application and database infrastructure.", "An office building where different companies rent separate offices on the same floor."),
        ("Non-Repudiation", "A security guarantee that a sender or author cannot deny having sent or modified a piece of data.", "A signature witnessed by a public notary."),
        ("OPA (Open Policy Agent)", "An open-source, cloud-native engine that enforces declarative security policies at runtime.", "A security guard checking guest list rules at the door."),
        ("OWASP", "The Open Web Application Security Project, a global non-profit establishing software security standards.", "The World Health Organization of software security."),
        ("PII (Personally Identifiable Information)", "Any data that can be used to distinguish or trace an individual's identity (e.g. SSN, PAN, phone).", "Your official government ID number."),
        ("Precision", "The fraction of flagged security alerts that were genuine attacks rather than false alarms.", "Out of 10 times a smoke alarm went off, how many times was there a real fire?"),
        ("Recall (Sensitivity)", "The fraction of actual cyber attacks that were successfully caught by the security system.", "Out of 10 real thieves who entered the building, how many did the guard catch?"),
        ("Rego", "The declarative policy language used by Open Policy Agent to define fine-grained authorization rules.", "A simple rulebook written in plain logic."),
        ("REST (Representational State Transfer)", "The standard architectural style for web services communicating over HTTP with JSON payloads.", "Sending standardized letters in the mail."),
        ("SAST (Static App Security Testing)", "Analyzing source code without executing it to find security vulnerabilities.", "Proofreading a book manuscript for typos before printing."),
        ("Semantic Property Delta", "The mathematical set difference between delivered JSON keys and authorized contract keys.", "Delivered minus Allowed equals Leaked Secrets."),
        ("Shannon Entropy", "A mathematical measure of randomness, disorder, or dispersion in a set of probabilities.", "Measuring how widely water splattered across the floor."),
        ("Shift-Left Security", "Moving security testing earlier in the software development lifecycle rather than waiting until production.", "Checking the brakes in the factory rather than on the highway."),
        ("SQLite", "A self-contained, serverless, zero-configuration SQL database engine stored in a single computer file.", "A digital ledger that needs no internet connection or server setup."),
        ("Streamlit", "An open-source Python framework for rapidly building data science and cybersecurity dashboards.", "A control panel dashboard showing live meters and dials."),
        ("TIFI (Tenant Isolation Failure Index)", "A mathematical metric in [0, 1] combining cross-tenant exfiltration with Shannon entropy to quantify boundary collapse.", "A damage score showing whether an attack affected one company or destroyed all walls."),
        ("Virtual Patching", "Implementing a security policy at the gateway to block an exploit immediately without modifying application code.", "Putting a temporary clamp on a pipe leak while waiting for replacement parts."),
        ("WAF (Web Application Firewall)", "A perimeter security system that inspects incoming HTTP traffic for malicious patterns like SQLi and XSS.", "A metal detector at the airport terminal entrance."),
        ("Wire Speed", "Processing and inspecting network traffic at the native physical speed of the network cables without adding delay.", "Cars passing through a toll plaza without having to slow down.")
    ]
    add_terms_table(doc, dict_terms)

    # Save Word document
    os.makedirs("Project_Presentation_Preparation", exist_ok=True)
    docx_path = os.path.abspath("Project_Presentation_Preparation/ExposureLens_PPT_Simple_Explanations_and_Terms.docx")
    pdf_path = os.path.abspath("Project_Presentation_Preparation/ExposureLens_PPT_Simple_Explanations_and_Terms.pdf")
    doc.save(docx_path)
    print(f"[SUCCESS] Word document saved to: {docx_path} ({os.path.getsize(docx_path):,} bytes)")

    # Convert to PDF using Microsoft Word COM
    print(f"Converting Word document to PDF via Word COM -> {pdf_path}...")
    try:
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = False
        doc_com = word.Documents.Open(docx_path)
        doc_com.SaveAs(pdf_path, 17) # 17 = wdFormatPDF
        doc_com.Close()
        word.Quit()
        if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 0:
            print(f"[SUCCESS] High-resolution PDF generated: {pdf_path} ({os.path.getsize(pdf_path):,} bytes)")
        else:
            print("[ERROR] PDF generation failed or file is empty.")
    except Exception as e:
        print("[ERROR] Word COM conversion failed:", e)

if __name__ == "__main__":
    build_simple_pdf_guide()
