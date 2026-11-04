import os
import sys
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

# Colors
COLOR_NAVY = RGBColor(11, 19, 43)       # Deep Dark Navy (#0B132B)
COLOR_TEAL = RGBColor(14, 116, 144)     # Cyan/Teal Accent (#0E7490)
COLOR_SLATE = RGBColor(51, 65, 85)      # Slate Body (#334155)
COLOR_GREEN = RGBColor(16, 185, 129)    # Terminal Emerald (#10B981)
COLOR_PURPLE = RGBColor(124, 58, 237)   # Deep Purple (#7C3AED)
COLOR_CRIMSON = RGBColor(185, 28, 28)   # Alert Red (#B91C1C)

def set_cell_background(cell, hex_color):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hex_color)
    tc_pr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
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
        run.font.size = Pt(16)
        run.font.bold = True
        run.font.color.rgb = COLOR_NAVY
    elif level == 2:
        run.font.name = 'Calibri'
        run.font.size = Pt(12.5)
        run.font.bold = True
        run.font.color.rgb = COLOR_TEAL
    elif level == 3:
        run.font.name = 'Calibri'
        run.font.size = Pt(11)
        run.font.bold = True
        run.font.color.rgb = COLOR_SLATE
    return h

def add_p(doc, text, bold_prefix=None, space_after=4):
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
    p.paragraph_format.space_after = Pt(2.5)
    p.paragraph_format.line_spacing = 1.12
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

def add_callout(doc, text, title="KEY CONCEPT FOR VIVA", bg_hex="F0FDF4"):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_background(cell, bg_hex)
    set_cell_margins(cell, top=100, bottom=100, left=150, right=150)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    r_title = p.add_run(f"[{title}] ")
    r_title.font.name = 'Consolas'
    r_title.font.size = Pt(9.5)
    r_title.font.bold = True
    r_title.font.color.rgb = COLOR_TEAL

    r_text = p.add_run(text)
    r_text.font.name = 'Calibri'
    r_text.font.size = Pt(9.5)
    r_text.font.color.rgb = COLOR_SLATE

    sp = doc.add_paragraph()
    sp.paragraph_format.space_before = Pt(0)
    sp.paragraph_format.space_after = Pt(3)

def add_qa_box(doc, q_num, question, answer, core_insight=None):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_background(cell, "F8FAFC")
    set_cell_margins(cell, top=120, bottom=120, left=150, right=150)

    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after = Pt(3)
    r_q = p.add_run(f"Q{q_num}: {question}")
    r_q.font.name = 'Calibri'
    r_q.font.size = Pt(10.5)
    r_q.font.bold = True
    r_q.font.color.rgb = COLOR_NAVY

    p_ans = cell.add_paragraph()
    p_ans.paragraph_format.space_before = Pt(1)
    p_ans.paragraph_format.space_after = Pt(3)
    p_ans.paragraph_format.line_spacing = 1.15
    r_lbl = p_ans.add_run("How to Answer Confidently: ")
    r_lbl.font.name = 'Calibri'
    r_lbl.font.size = Pt(9.5)
    r_lbl.font.bold = True
    r_lbl.font.color.rgb = COLOR_TEAL

    r_ans = p_ans.add_run(answer)
    r_ans.font.name = 'Calibri'
    r_ans.font.size = Pt(9.5)
    r_ans.font.color.rgb = COLOR_SLATE

    if core_insight:
        p_ins = cell.add_paragraph()
        p_ins.paragraph_format.space_before = Pt(2)
        p_ins.paragraph_format.space_after = Pt(2)
        r_ins_lbl = p_ins.add_run("Core One-Liner to Remember: ")
        r_ins_lbl.font.name = 'Consolas'
        r_ins_lbl.font.size = Pt(9)
        r_ins_lbl.font.bold = True
        r_ins_lbl.font.color.rgb = COLOR_GREEN
        r_ins = p_ins.add_run(f'"{core_insight}"')
        r_ins.font.name = 'Calibri'
        r_ins.font.size = Pt(9)
        r_ins.font.italic = True
        r_ins.font.color.rgb = COLOR_NAVY

    sp = doc.add_paragraph()
    sp.paragraph_format.space_before = Pt(0)
    sp.paragraph_format.space_after = Pt(4)

def build_nids_guide():
    doc = docx.Document()
    
    # Margins
    for s in doc.sections:
        s.top_margin = Inches(1.0)
        s.bottom_margin = Inches(1.0)
        s.left_margin = Inches(1.0)
        s.right_margin = Inches(1.0)

    # Title Block
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(2)
    r_title = p_title.add_run("NETWORK INTRUSION DETECTION (NIDS): PROJECT GUIDE & VIVA MANUAL")
    r_title.font.name = 'Calibri'
    r_title.font.size = Pt(20)
    r_title.font.bold = True
    r_title.font.color.rgb = COLOR_NAVY

    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_before = Pt(0)
    p_sub.paragraph_format.space_after = Pt(8)
    r_sub = p_sub.add_run("Enhanced Network Intrusion Detection Using Hybrid Autoencoder and Feature-Selective Machine Learning on CIC-IDS2017 Traffic Data")
    r_sub.font.name = 'Calibri'
    r_sub.font.size = Pt(12)
    r_sub.font.bold = True
    r_sub.font.color.rgb = COLOR_TEAL

    # Metadata Table
    tbl_meta = doc.add_table(rows=5, cols=2)
    tbl_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_data = [
        ("Research Paper Title:", "Enhanced Network Intrusion Detection Using Hybrid Autoencoder and Feature-Selective Machine Learning on CIC-IDS2017 Traffic Data"),
        ("Authors & Affiliation:", "Saikat Mondal, Surya Pritam Satpathy, Sachin Kailas Borse | School of Computer Engineering, KIIT Deemed to be University"),
        ("Dataset Evaluated:", "CIC-IDS2017 Benchmark (Canadian Institute for Cybersecurity, 8 Attack Vectors)"),
        ("Key Architecture:", "Deep Hybrid Autoencoder (Unsupervised Latent Extraction) + Feature Selection + Ensemble Random Forest"),
        ("Target Publication:", "IEEE International Conference on Research in Computational Intelligence and Communication Networks (ICRCICN 2027)")
    ]
    for idx, (lbl, val) in enumerate(meta_data):
        row = tbl_meta.rows[idx]
        c0, c1 = row.cells[0], row.cells[1]
        c0.width = Inches(2.2)
        c1.width = Inches(4.3)
        set_cell_background(c0, "F1F5F9")
        set_cell_background(c1, "FFFFFF")
        set_cell_margins(c0, top=60, bottom=60, left=100, right=100)
        set_cell_margins(c1, top=60, bottom=60, left=100, right=100)
        p0 = c0.paragraphs[0]
        p0.add_run(lbl).font.bold = True
        p0.runs[0].font.size = Pt(9.5)
        p0.runs[0].font.color.rgb = COLOR_NAVY
        p1 = c1.paragraphs[0]
        p1.add_run(val).font.size = Pt(9.5)
        p1.runs[0].font.color.rgb = COLOR_SLATE

    sp = doc.add_paragraph()
    sp.paragraph_format.space_before = Pt(6)
    sp.paragraph_format.space_after = Pt(6)

    # -------------------------------------------------------------------------
    # SECTION 1: THE BIG PICTURE
    # -------------------------------------------------------------------------
    add_header(doc, "1. The Big Picture: Explained Simply for Anyone", level=1)
    add_p(doc, "Imagine you are explaining this project to a first-year student or to your project guide who wants to understand the exact motivation without getting lost in mathematical jargon:")

    add_callout(doc,
        "Think of a busy international airport. Every minute, thousands of passengers walk through the security gate. "
        "A traditional security guard (Signature-Based NIDS) has a book of photos of known wanted criminals. "
        "If a criminal changes their hairstyle, wears sunglasses, or is a brand-new criminal (zero-day exploit), the guard lets them pass! "
        "Now, you decide to use Machine Learning to watch for 'suspicious behavior' (Anomaly Detection). "
        "But for every passenger, you are recording 80 different measurements: height, shoe size, heartbeat, walking speed, luggage weight, etc. "
        "Your system gets completely overwhelmed by 80 columns of noisy data—it lags, slows down, and starts sounding false alarms on innocent passengers. "
        "This project solves that exact problem using a two-step brain filter: "
        "First, an Autoencoder compresses those 80 noisy measurements into a compact cheat-sheet of core patterns. "
        "Second, a Feature Selection filter removes any remaining useless variables, leaving only the sharpest attack signals. "
        "Finally, an ensemble classifier makes the decision with 99.93% accuracy and almost zero false alarms (0.10% FAR).",
        title="THE AIRPORT SECURITY & CHEAT-SHEET ANALOGY (REMEMBER THIS FOR VIVA)"
    )

    add_header(doc, "1.1 Signature-Based vs Anomaly-Based NIDS", level=2)
    add_bullet(doc, "Signature-Based Detection (e.g., Snort, Suricata): Compares incoming packets against a static database of known attack signatures. Very fast, but completely blind to zero-day exploits, mutated malware, and encrypted payloads.")
    add_bullet(doc, "Anomaly-Based Detection (Machine Learning): Establishes a mathematical baseline of 'normal' traffic and flags any statistically significant deviation as an intrusion. Capable of catching zero-day attacks, but historically plagued by high False Positive Rates (FPR).")

    add_header(doc, "1.2 The 'Curse of Dimensionality' in Network Traffic", level=2)
    add_p(doc, "Modern network flow extractors (like CICFlowMeter) generate over 80 statistical features per packet flow (inter-arrival times, packet length variance, flow duration, flag counts). Feeding 80 raw features into shallow ML models (SVM, Decision Trees) causes three fatal problems:", bold_prefix="The Problem: ")
    add_bullet(doc, "Computational Latency: In a 10 Gbps network, the ML model cannot keep up with wire speed.")
    add_bullet(doc, "Multicollinearity & Noise: Many features are redundant (e.g., total bytes forward vs total packets forward) or contain random noise, which misleads the classifier.")
    add_bullet(doc, "Overfitting: The model memorizes training noise instead of learning genuine attack patterns, failing when tested on unseen network flows.")

    add_header(doc, "1.3 What is an Autoencoder (AE)?", level=2)
    add_p(doc, "An Autoencoder is a specialized neural network designed for unsupervised representation learning. Think of it as an expert book summarizer:")
    add_bullet(doc, "The Encoder: Compresses an 80-page document into a compact 16-page 'summary' (the bottleneck latent space z).")
    add_bullet(doc, "The Decoder: Takes that 16-page summary and tries to reconstruct the original 80-page document.")
    add_bullet(doc, "The Loss Function: Measures how much was lost in reconstruction (Mean Squared Error). If the decoder can accurately reconstruct the original data from the 16-page summary, it proves that the 16 latent variables captured the fundamental underlying structure of the network traffic while throwing away stochastic noise!")

    add_header(doc, "1.4 Why a 'Hybrid' Approach? (Autoencoder + Feature Selection)", level=2)
    add_p(doc, "Most researchers do one of two things: they either do Feature Selection on raw data (which misses complex non-linear relationships), OR they feed raw Autoencoder latent features directly into a classifier (which still retains non-discriminative latent noise).")
    add_p(doc, "Our innovation is a unified sequential hybrid pipeline: We first use the Autoencoder to capture non-linear structural manifolds, and THEN apply Feature Selection on the latent space to prune any uninformative latent dimensions. This double-filtering achieves maximum signal-to-noise ratio.", bold_prefix="Our Key Innovation: ")

    # -------------------------------------------------------------------------
    # SECTION 2: THE CORE PROBLEM SOLVED
    # -------------------------------------------------------------------------
    add_header(doc, "2. The Core Problem This Project Solves", level=1)
    add_p(doc, "When your guide asks: 'Why did you build this? What is the practical value of your research?', explain these three key operational challenges:")

    add_p(doc, "In enterprise Security Operations Centers (SOCs), analysts receive thousands of intrusion alerts every day. If 95% of them are false alarms, analysts suffer from 'alert fatigue' and start ignoring warnings. A single overlooked true positive can result in a catastrophic ransomware breach. By reducing the False Alarm Rate (FAR) to just 0.10%, our model restores analyst trust.", bold_prefix="Problem 1: SOC Alert Fatigue & False Alarm Rate (FAR): ")

    add_p(doc, "Standard Principal Component Analysis (PCA) performs linear dimensionality reduction. However, modern network protocols (HTTP/2, TLS handshakes, packet inter-arrival distributions) exhibit highly non-linear, chaotic dynamics. The deep autoencoder successfully captures non-linear manifolds that PCA completely misses.", bold_prefix="Problem 2: Non-Linear Traffic Dynamics: ")

    add_p(doc, "While end-to-end deep neural networks (like Deep LSTMs or CNNs) can detect intrusions, they are computationally heavy and require GPU clusters for inference. Our hybrid architecture uses the deep autoencoder for offline latent extraction, and a lightweight Random Forest ensemble for online classification, enabling low-latency deployment at the network edge.", bold_prefix="Problem 3: Real-Time Edge Viability: ")

    # -------------------------------------------------------------------------
    # SECTION 3: TECHNICAL PIPELINE & IMPLEMENTATION
    # -------------------------------------------------------------------------
    add_header(doc, "3. The Technical Pipeline: How It Works Step-by-Step", level=1)
    add_p(doc, "Here is the exact algorithmic workflow of the proposed system:")

    add_header(doc, "Step 1: Dataset Acquisition & Data Hygiene (CIC-IDS2017)", level=2)
    add_bullet(doc, "Dataset Choice: We selected the CIC-IDS2017 benchmark generated by the Canadian Institute for Cybersecurity. It covers 5 days of realistic background traffic and 8 contemporary attack classes: DoS/DDoS (Slowloris, Hulk, GoldenEye), PortScan, Brute Force (SSH, FTP), Web Attacks (SQLi, XSS), Infiltration, and Botnets.")
    add_bullet(doc, "Handling Missing & Infinite Values: Network flow statistics often produce divide-by-zero errors (e.g., flow bytes per second when duration is zero). We purged all `NaN` and `Inf` values to ensure mathematical stability.")
    add_bullet(doc, "Z-Score Normalization (StandardScaler): Features like flow duration (ranging in millions of microseconds) would dominate features like flag counts (0 or 1). We normalized every continuous variable to have zero mean (mu = 0) and unit variance (sigma = 1): z = (x - mu) / sigma.")
    add_bullet(doc, "Train/Test Partition: Evaluated using an 80/20 train-test partition with random shuffling to eliminate temporal sequence bias.")

    add_header(doc, "Step 2: Unsupervised Representation Learning (Deep Autoencoder)", level=2)
    add_bullet(doc, "Encoder Architecture: Maps high-dimensional input vector x in R^D to compressed bottleneck latent code z in R^d (where d << D).")
    add_bullet(doc, "Decoder Architecture: Reconstructs the original vector x_hat in R^D from the latent code z.")
    add_bullet(doc, "Loss Minimization: Trained using Adam optimizer to minimize Mean Squared Error (MSE) reconstruction loss: L(x, x_hat) = (1/n) * sum_{i=1}^n (x_i - x_hat_i)^2.")
    add_bullet(doc, "Result: The encoder discards high-frequency stochastic noise while preserving the underlying topological manifold of normal and malicious traffic.")

    add_header(doc, "Step 3: Strategic Feature Selection on Latent Space", level=2)
    add_bullet(doc, "Latent Filtering: Unlike conventional systems that perform feature selection on raw data, we evaluate the predictive utility of the learned latent embeddings.")
    add_bullet(doc, "Information-Theoretic Metric: Using Mutual Information / Gini Importance, latent variables that have low variance or zero correlation with attack labels are pruned.")
    add_bullet(doc, "Benefit: Strips away redundant latent dimensions, maximizing the classification margin and reducing inference latency.")

    add_header(doc, "Step 4: Supervised Ensemble Classification (Random Forest)", level=2)
    add_bullet(doc, "Model: Random Forest multi-tree ensemble classifier operating on the refined latent feature manifold.")
    add_bullet(doc, "Voting Mechanism: Aggregates decision trees using bootstrap aggregating (bagging) to stabilize decision boundaries and prevent overfitting.")
    add_bullet(doc, "Output: Binary classification decision: Normal Traffic vs Malicious Intrusion.")

    # -------------------------------------------------------------------------
    # SECTION 4: WHAT WE ACHIEVED (EXPERIMENTAL RESULTS)
    # -------------------------------------------------------------------------
    add_header(doc, "4. What We Achieved: Empirical Results & Analysis", level=1)
    add_p(doc, "The performance of the hybrid framework was validated on the CIC-IDS2017 benchmark. Here are the exact numbers reported in the research paper:")

    tbl_results = doc.add_table(rows=6, cols=3)
    tbl_results.alignment = WD_TABLE_ALIGNMENT.CENTER
    res_headers = ["Evaluation Metric", "Experimental Value", "Practical Operational Meaning"]
    for i, h in enumerate(res_headers):
        cell = tbl_results.rows[0].cells[i]
        set_cell_background(cell, "0B132B")
        set_cell_margins(cell, top=80, bottom=80, left=100, right=100)
        p = cell.paragraphs[0]
        run = p.add_run(h)
        run.font.bold = True
        run.font.color.rgb = RGBColor(255, 255, 255)
        run.font.size = Pt(9.5)

    res_rows = [
        ("Accuracy", "99.93%", "Overall probability that a network flow is correctly categorized."),
        ("Precision", "99.93%", "When the model flags an intrusion, it is genuinely malicious 99.93% of the time."),
        ("Recall (Sensitivity)", "99.95%", "The system successfully detects 9,995 out of every 10,000 actual cyber attacks."),
        ("F1-Score", "99.94%", "Harmonic mean of precision and recall, proving an optimal balance between catching attacks and avoiding false alarms."),
        ("False Alarm Rate (FAR)", "0.10%", "Only 1 out of every 1,000 normal network flows is erroneously flagged, eliminating SOC alert fatigue."),
    ]
    for row_idx, data in enumerate(res_rows, start=1):
        for col_idx, text in enumerate(data):
            cell = tbl_results.rows[row_idx].cells[col_idx]
            set_cell_background(cell, "F8FAFC" if row_idx % 2 == 1 else "FFFFFF")
            set_cell_margins(cell, top=60, bottom=60, left=100, right=100)
            p = cell.paragraphs[0]
            run = p.add_run(text)
            run.font.size = Pt(9)
            run.font.color.rgb = COLOR_GREEN if col_idx == 1 else (COLOR_NAVY if col_idx == 0 else COLOR_SLATE)
            if col_idx in (0, 1):
                run.font.bold = True

    sp = doc.add_paragraph()
    sp.paragraph_format.space_before = Pt(6)

    add_header(doc, "Confusion Matrix Analysis (Figure 3 in Paper)", level=2)
    add_p(doc, "On the test partition of ~197,500 unseen network flows:")
    add_bullet(doc, "True Negatives (Normal classified as Normal): 98,000 flows.")
    add_bullet(doc, "True Positives (Attack classified as Attack): 99,500 flows.")
    add_bullet(doc, "False Positives (Normal falsely flagged as Attack): ~100 flows (FAR = 0.10%).")
    add_bullet(doc, "False Negatives (Attacks missed): ~45 flows (Miss rate = 0.05%).")
    add_bullet(doc, "Total Misclassifications: Only 145 out of 197,500 test samples!")

    # -------------------------------------------------------------------------
    # SECTION 5: TECHNOLOGIES USED & WHY
    # -------------------------------------------------------------------------
    add_header(doc, "5. Technologies We Used & Why", level=1)
    add_bullet(doc, "Python 3: The industry standard for scientific machine learning and data science.")
    add_bullet(doc, "TensorFlow / Keras: Utilized to construct and train the deep autoencoder architecture with custom reconstruction loss functions and GPU acceleration.")
    add_bullet(doc, "Scikit-Learn: Used for data scaling (`StandardScaler`), feature selection routines, train-test splitting, and Random Forest ensemble modeling.")
    add_bullet(doc, "Pandas & NumPy: High-throughput memory-mapped data ingestion and manipulation of multi-gigabyte CSV telemetry files.")
    add_bullet(doc, "Matplotlib / Seaborn: Generation of ROC curves, confusion matrices, and performance bar charts.")

    # -------------------------------------------------------------------------
    # SECTION 6: HONEST CRITIQUE & NEXT STEPS
    # -------------------------------------------------------------------------
    add_header(doc, "6. Honest Critique of Current Paper Draft & What Needs Polishing", level=1)
    add_p(doc, "To prepare for questions from your guide, you must be 100% transparent about the difference between the current draft paper and a final published IEEE manuscript:")

    add_callout(doc,
        "The manuscript you have right now is an INTERMEDIATE DRAFT. "
        "It contains valid experimental results (99.93% accuracy, 0.10% FAR), but the document formatting and structure "
        "need final polish before submission to IEEE ICRCICN 2027.",
        title="CURRENT STATUS: WORKING DRAFT",
        bg_hex="FFFBEB"
    )

    add_header(doc, "Points to Fix in the Research Paper (Guide Defense Talking Points):", level=2)
    add_bullet(doc, "Template Conversion: The draft is currently 15 pages in single-column. It needs to be migrated to the official IEEE 2-column format (max 6 pages).")
    add_bullet(doc, "Add Section 2 (Related Work): The draft accidentally jumps from Section 1.3 to Section 3. You should explain to your guide: 'We have compiled recent 2021-2025 literature on Deep NIDS which will be inserted as Section II: Related Work in the IEEE 2-column camera-ready version.'")
    add_bullet(doc, "Ablation Study Table: Reviewers will want to see the performance of Random Forest alone vs Autoencoder alone vs the combined Hybrid model. We will include this ablation table in the final submission.")
    add_bullet(doc, "Binary vs Multiclass Scoping: Explain that binary classification was chosen as Phase 1 (high-speed frontline triage at the network boundary). Phase 2 of our research will introduce multi-label classification to pinpoint specific attack families (DoS vs PortScan vs Web Attacks).")

    # -------------------------------------------------------------------------
    # SECTION 7: EXHAUSTIVE VIVA Q&A DEFENSE GUIDE
    # -------------------------------------------------------------------------
    add_header(doc, "7. Comprehensive Guide & Reviewer Viva Q&A Guide", level=1)
    add_p(doc, "Here are 12 of the most probable questions your guide or external examiners will ask regarding this NIDS research:")

    qa_nids = [
        ("Why use an Autoencoder instead of standard Principal Component Analysis (PCA)?",
         "PCA is strictly a linear transformation that projects data onto orthogonal eigenvectors. However, network traffic telemetry exhibits highly non-linear, chaotic distributions due to varying packet sizes, protocol negotiations, and attack payload patterns. Autoencoders use non-linear activation functions (such as ReLU or Sigmoid) across multiple hidden layers, allowing them to capture complex non-linear manifolds that PCA completely misses.",
         "PCA is linear; Autoencoders learn complex non-linear traffic representations."),

        ("Why apply Feature Selection AFTER the Autoencoder instead of before?",
         "If you apply feature selection to raw data, you evaluate features independently, which ignores non-linear multi-feature interactions. Conversely, an Autoencoder maps the entire feature space into a compressed latent manifold, capturing those non-linear interactions. However, the latent bottleneck can still retain non-informative variance. Applying feature selection on the latent space ensures that we only feed the most discriminative latent dimensions into the classifier.",
         "AE captures non-linear interactions; FS then prunes remaining latent noise."),

        ("Why did you choose the CIC-IDS2017 dataset instead of KDD-99 or NSL-KDD?",
         "KDD-99 and NSL-KDD are over 25 years old and reflect outdated 1990s traffic patterns that are irrelevant to modern networks. CIC-IDS2017 is a recognized contemporary benchmark developed by the Canadian Institute for Cybersecurity. It incorporates modern application-layer protocols, realistic background benign traffic, and 8 diverse modern attack families (including DDoS, Slowloris, Heartbleed, and Web Attacks).",
         "CIC-IDS2017 reflects modern 21st-century attack vectors; KDD-99 is obsolete."),

        ("What loss function is used to train the Autoencoder, and why?",
         "We used Mean Squared Error (MSE) reconstruction loss: L(x, x_hat) = (1/n) * sum (x_i - x_hat_i)^2. In an autoencoder, the objective is to reconstruct the input x as closely as possible at the output layer x_hat. Minimizing MSE forces the network to learn a compressed representation in the bottleneck layer that retains maximum information with minimum distortion.",
         "MSE loss measures the reconstruction error between raw input and decoded output."),

        ("Why is the False Alarm Rate (FAR) of 0.10% so important in cybersecurity?",
         "In modern enterprise networks processing millions of flows per minute, a false alarm rate of even 2% would generate tens of thousands of false alerts daily. This causes severe 'alert fatigue', leading SOC analysts to miss real attacks. Our model achieves a FAR of 0.10%, meaning only 1 in 1,000 benign flows is flagged, making it viable for practical real-world operations.",
         "A low FAR of 0.10% prevents alert fatigue and preserves analyst resources."),

        ("Why did you perform Binary Classification instead of Multi-class Classification?",
         "In high-speed production networks, the primary operational priority is real-time frontline triage: immediately separating malicious packets from benign traffic with minimum latency. Our binary model acts as this high-throughput filter. In the future scope of our research, flows flagged as malicious can be routed to a secondary, specialized multiclass model to categorize the exact attack family.",
         "Binary classification provides high-speed frontline triage at wire speed."),

        ("How did you handle the class imbalance in CIC-IDS2017?",
         "In raw CIC-IDS2017, benign traffic accounts for over 80% of all flows. To prevent the classifier from developing a majority-class bias toward benign traffic, we extracted a balanced stratified subset of normal and attack samples (~197,500 test flows) for our experimental evaluation. In operational deployment, Random Forest class weights can be adjusted to penalize false negatives.",
         "Stratified balanced sampling was used to prevent majority-class bias."),

        ("Why did you choose Random Forest as the final classifier instead of a Deep Neural Network?",
         "Deep neural networks require significant computational resources and GPU acceleration for inference, introducing latency. Random Forest is an ensemble of decision trees that executes extremely fast inference on CPU, handles tabular numerical features exceptionally well, provides natural resilience against overfitting via bagging, and is suitable for edge-router deployment.",
         "Random Forest provides microsecond CPU inference and resistance to overfitting."),

        ("What preprocessing steps were applied to the raw CSV files?",
         "First, we cleaned the data by purging instances containing missing (NaN) or infinite values caused by zero-duration flows. Second, we applied Z-score standardization (StandardScaler) to normalize continuous variables to zero mean and unit variance. Third, categorical labels were one-hot encoded, and data was randomly shuffled to prevent temporal sequence bias.",
         "Cleaning NaN/Inf values, Z-score standard scaling, and random shuffling."),

        ("How does this model prevent overfitting?",
         "Overfitting is prevented at three distinct stages: (1) The bottleneck layer of the autoencoder acts as a structural regularizer by constraining information capacity; (2) Feature selection removes noisy, low-variance latent dimensions; and (3) Random Forest uses bootstrap aggregation (bagging) and feature subsetting across multiple decision trees to minimize model variance.",
         "Three-stage regularization: AE bottleneck, feature pruning, and RF bagging."),

        ("What are the limitations of this study?",
         "Currently, the evaluation is based on offline flow-level CSV datasets rather than live raw PCAP packet streams. Second, the model performs binary categorization rather than multi-class attack attribution. Third, like all ML-based systems, model drift can occur over time as adversarial techniques evolve, requiring periodic retraining on updated traffic profiles.",
         "Offline dataset evaluation, binary scope, and vulnerability to long-term model drift."),

        ("What are your future research directions?",
         "Our roadmap includes: (1) Extending the pipeline to multi-label classification to identify specific attack families; (2) Implementing online incremental learning to adapt to zero-day traffic shifts without retraining from scratch; and (3) Deploying the model onto edge hardware (such as Raspberry Pi or NVIDIA Jetson) to measure real-time throughput on a physical 10 Gbps switch.",
         "Multi-class attack classification, incremental online learning, and edge hardware deployment.")
    ]

    for q_idx, (q, a, core) in enumerate(qa_nids, start=1):
        add_qa_box(doc, q_idx, q, a, core_insight=core)

    # Save Document
    os.makedirs("Project_Presentation_Preparation", exist_ok=True)
    out_file = os.path.join("Project_Presentation_Preparation", "Network_Intrusion_Detection_Project_Complete_Guide.docx")
    doc.save(out_file)
    print(f"[SUCCESS] NIDS Complete Guide successfully written to: {out_file} ({os.path.getsize(out_file):,} bytes)")

if __name__ == "__main__":
    build_nids_guide()
