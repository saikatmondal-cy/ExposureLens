# ExposureLens: M.Tech Cyber Security Major Project Defense
## Master 10-Minute Presentation Script & Examiner Q&A Defense Guide

---

### **Candidate & Project Metadata**
- **Candidate Name:** Saikat Mondal
- **Roll Number:** 25168016
- **Degree:** Master of Technology (M.Tech) in Cyber Security
- **Department:** School of Computer Engineering
- **Institution:** Kalinga Institute of Industrial Technology (KIIT Deemed to be University), Bhubaneswar
- **Academic Session:** 2024–2026
- **Project Title:** *ExposureLens: AI-Assisted Data Exposure Reconstruction and Blast Radius Analysis for Broken Object Level Authorization (BOLA)*
- **Live Deployment:** [https://exposurelens.onrender.com](https://exposurelens.onrender.com)
- **Open Source Repository:** [https://github.com/saikatmondal-cy/ExposureLens](https://github.com/saikatmondal-cy/ExposureLens)
- **Target Presentation Duration:** 9 minutes 45 seconds (Leaving 5–10 minutes for Q&A)

---

## ⏱️ Presentation Timing Roadmap

| Slide # | Title | Target Time | Cumulative Time |
| :---: | :--- | :---: | :---: |
| **Slide 1** | Title & Academic Credentials | 0:45 | 0:45 |
| **Slide 2** | Research Motivation & Problem Statement | 0:55 | 1:40 |
| **Slide 3** | Research Novelty & Four Scientific Pillars | 1:00 | 2:40 |
| **Slide 4** | System Architecture & End-to-End Pipeline | 0:55 | 3:35 |
| **Slide 5** | Deterministic BOLA Detection & Semantic Property Delta | 0:55 | 4:30 |
| **Slide 6** | Tenant Isolation Failure Index (TIFI) & Blast Radius | 1:00 | 5:30 |
| **Slide 7** | Cryptographic Proof-of-Exposure (PoE) Blockchain | 0:50 | 6:20 |
| **Slide 8** | Statutory Regulatory Compliance & Automated Virtual Patching | 0:55 | 7:15 |
| **Slide 9** | AI Forensic Reporting & Zero-Hallucination Audit | 0:55 | 8:10 |
| **Slide 10** | Experimental Evaluation & Research Benchmark | 0:50 | 9:00 |
| **Slide 11** | Live Deployment, Limitations & Future Roadmap | 0:45 | **9:45** |

---

## 🎙️ Word-for-Word Presentation Script

---

### **Slide 1: Title & Academic Credentials (0:00 - 0:45)**
*Visual: Dark navy terminal interface with neon cyan and green status cards, candidate profile, live production URLs.*

> **"Respected members of the evaluation committee, external examiners, and faculty members:**
>
> Good morning. My name is **Saikat Mondal**, Roll Number **25168016**, pursuing my Master of Technology in Cyber Security at the School of Computer Engineering, KIIT Bhubaneswar.
>
> Today, I am proud to present my M.Tech Major Project thesis: **'ExposureLens: AI-Assisted Data Exposure Reconstruction and Blast Radius Analysis for Broken Object Level Authorization'**.
>
> ExposureLens is an end-to-end cybersecurity system engineered to address the critical post-exploitation blindspot in modern multi-tenant cloud APIs. The entire project is not merely a theoretical framework; it is fully engineered, published open-source on GitHub, and deployed live on Render at `https://exposurelens.onrender.com`.
>
> Allow me to take you through our research motivation, mathematical foundations, system implementation, and empirical results."

---

### **Slide 2: Research Motivation & Problem Statement (0:45 - 1:40)**
*Visual: The 'HTTP 200 OK' paradox graphic, vulnerability comparison matrix, and ExposureLens research mandate.*

> **"Turning to Slide 2: Why did we build ExposureLens?**
>
> In modern microservice and SaaS ecosystems, **Broken Object Level Authorization (BOLA)** ranks as the **#1 vulnerability on the OWASP API Security Top 10**. Over 40% of all cloud data breaches originate from BOLA flaws.
>
> The fundamental dilemma with BOLA is what I formulate as the **'HTTP 200 OK Silent Breach Paradox'**. Traditional Web Application Firewalls (WAFs) and API Gateways inspect syntax, regex signatures, and authentication tokens. But when an attacker manipulates a resource ID in a URL—for instance, changing `/api/v1/patient/1001` to `1002`—the request carries a valid bearer token, standard HTTP headers, and a valid payload. The gateway logs a clean `HTTP 200 OK`, completely blind to the fact that Tenant A has just exfiltrated Tenant B's confidential records.
>
> Furthermore, current vulnerability scanners (DAST and SAST) operate purely *pre-exploitation*—they simply report whether an endpoint is vulnerable. They cannot answer the questions incident responders and legal counsel desperately need: *What exact sensitive fields escaped? Which tenants were cross-contaminated? What is the statutory liability under the DPDP Act or GDPR?*
>
> ExposureLens was conceived to close this post-exploitation observability void."

---

### **Slide 3: Research Novelty & Four Scientific Pillars (1:40 - 2:40)**
*Visual: 4 glowing neon cyber cards presenting the mathematical formulations of Delta, TIFI, PoE, and Faithfulness.*

> **"On Slide 3, I present the four scientific pillars that constitute the research novelty of ExposureLens:**
>
> 1. **Semantic Property Delta ($\Delta_{\text{leak}}$):** Rather than treating data leaks as monolithic blobs, we define $\Delta_{\text{leak}} = \mathcal{P}_{\text{delivered}} \setminus \mathcal{P}_{\text{authorized}}$. This isolates the exact sensitive attributes leaked, distinguishing standard BOLA from Broken Object Property-Level Authorization (OWASP API3:2023 BOPLA).
>
> 2. **Tenant Isolation Failure Index (TIFI):** We introduce an empirical, entropy-weighted metric bounded in $[0.0, 1.0]$. TIFI synthesizes the cross-tenant exfiltration ratio with Shannon directional spillover entropy, quantifying whether a breach was localized or represents systemic multi-tenant dissolution.
>
> 3. **Cryptographic Proof-of-Exposure (PoE):** We construct an immutable SHA-256 Merkle hash chain that anchors every exfiltrated payload, timestamp, and tenant identity. This yields tamper-evident, court-admissible forensic certificates with unbroken chain of custody.
>
> 4. **Zero-Hallucination AI Forensics:** We combine the generative power of LLMs with deterministic regex-based ground-truth verification. Every IP address, tenant name, and record count in statutory reports is bound to database ground truth, achieving a **100% faithfulness score** with **0.00% hallucination**."

---

### **Slide 4: System Architecture & End-to-End Pipeline (2:40 - 3:35)**
*Visual: Modular 3-tier architecture diagram on left, live screenshot of the Executive Observability Workspace on right.*

> **"Slide 4 illustrates our modular three-tier system architecture, alongside a live capture of our Executive Observability Workspace.**
>
> In **Stage 1 (Telemetry Ingestion)**, our Flask API middleware non-invasively captures API requests, decoding caller JWT claims—including caller identity, tenant ID, and role—and ingesting responses into a high-performance SQLite store.
>
> In **Stage 2 (Forensic Core & Graph Engine)**, the BOLA Detection Engine deterministically binds authorization contexts. The Semantic Delta Engine evaluates response schemas against authorized OpenAPI contracts, while the Graph Processor builds directed tenant-to-tenant attack graphs.
>
> In **Stage 3 (Verification & Virtual Patching)**, our engine mints SHA-256 Proof-of-Exposure blocks, synthesizes Open Policy Agent Rego virtual patches, and triggers our Zero-Hallucination AI copilot.
>
> As shown in the live dashboard screenshot on the right, the SOC team receives real-time visibility into overall security score, tenant exposure distributions, and active attack vectors."

---

### **Slide 5: Deterministic BOLA Detection & Semantic Property Delta (3:35 - 4:30)**
*Visual: Mathematical context tuple, BOPLA attribute breakdown, and genuine screenshot of the BOLA Incident Inspector.*

> **"In Slide 5, we delve into our deterministic detection algorithm.**
>
> Instead of relying on unreliable probabilistic scoring, ExposureLens evaluates every transaction against an authorization context tuple:
> $\mathcal{C} = \langle \text{User\_ID}, \text{Tenant}_{\text{caller}}, \text{Role}, \text{Resource\_ID}, \text{Tenant}_{\text{owner}}, \text{Payload} \rangle$.
> A BOLA violation is deterministically flagged if the caller's tenant does not match the resource owner's tenant, or if an unauthorized user accesses another entity's object without administrative delegation.
>
> Crucially, our Semantic Property Delta engine evaluates the delivered JSON keys against authorized contracts. In the live incident shown on the right—`INC-BOLA-2026-0042`—caller `dev_user` from Cyberdyne accessed an Acme Corp record. While standard logs showed a basic user retrieval, ExposureLens isolated four leaked properties: Social Security Number, salary bracket, credit limit, and internal routing codes.
>
> This gives security teams immediate clarity on exact data loss."

---

### **Slide 6: Tenant Isolation Failure Index (TIFI) & Blast Radius (4:30 - 5:30)**
*Visual: Mathematical derivation of R_cross, H_spill, unified TIFI formula, and genuine screenshot of the Exposure Graph.*

> **"Slide 6 presents our second core contribution: the Tenant Isolation Failure Index (TIFI).**
>
> In multi-tenant cloud environments, the severity of a breach depends on organizational boundary stability. We model this through two mathematical terms:
> First, the **Cross-Tenant Exfiltration Ratio ($\mathcal{R}_{\text{cross}}$)**, measuring the volume of traffic that crosses tenant perimeters.
> Second, the **Directional Spillover Entropy ($\mathcal{H}_{\text{spill}}$)**, which applies Shannon entropy to exfiltration probabilities:
> $$\mathcal{H}_{\text{spill}} = - \sum_{j \neq i} p_{i \to j} \log_2(p_{i \to j})$$
>
> When multiplied, they yield the unified TIFI metric in $[0.0, 1.0]$.
> In our benchmark attack suite, ExposureLens measured a **TIFI of 0.800**, indicating a critical-severity systemic failure where an adversary exfiltrated records across multiple unrelated customer tenants.
>
> On the right, you see our interactive directed attack graph where node sizing corresponds to data sensitivity and edge colors reflect exfiltration severity."

---

### **Slide 7: Cryptographic Proof-of-Exposure (PoE) Blockchain (5:30 - 6:20)**
*Visual: State block hashing equation, Merkle chain diagram, and genuine screenshot of the Forensic Certificate.*

> **"Moving to Slide 7, we address the legal integrity of incident response.**
>
> In regulatory inquiries and data breach lawsuits, adversaries often argue that server logs were retroactively manipulated. Without mathematical proof of non-repudiation, traditional log files fail judicial scrutiny.
>
> ExposureLens solves this by chaining every reconstructed incident into an immutable **SHA-256 Merkle Ledger**. Each block $B_k$ hashes the incident timestamp, the prior block's hash $H_{k-1}$, the normalized SHA-256 digest of the raw payload, and caller-tenant identifiers. The chain is anchored at a deterministic Genesis Block.
>
> As shown in the live application screenshot on the right, ExposureLens generates a **Verifiable Forensic Certificate** with cryptographic seals, Merkle root digests, and block heights. Any tampering with stored database records invalidates the hash chain immediately."

---

### **Slide 8: Statutory Regulatory Compliance & Automated Virtual Patching (6:20 - 7:15)**
*Visual: DPDP Act 2023, CERT-In, GDPR timelines, and declarative Open Policy Agent (OPA) Rego policy code.*

> **"Slide 8 focuses on regulatory execution and automated virtual patching.**
>
> Under the **India Digital Personal Data Protection (DPDP) Act 2023**, Sections 8(5) and 8(6) mandate immediate breach notification to the Data Protection Board and data principals, with statutory penalties reaching up to **₹250 Crores (~$30M USD)**. Furthermore, **CERT-In directions** mandate incident reporting within **6 hours**.
>
> ExposureLens automatically generates pre-populated statutory incident disclosure notices ready for filing with CERT-In and the DPB, complete with verified record counts and timeline reconstructions.
>
> Furthermore, traditional code fixes take days to test and deploy. ExposureLens synthesizes **Open Policy Agent (OPA) Rego virtual patches** on the fly—shown on the right. By injecting these rules into an API Gateway or Envoy sidecar, organizations neutralize the BOLA vulnerability in runtime memory with **zero microservice downtime**."

---

### **Slide 9: AI Forensic Reporting & Zero-Hallucination Audit (7:15 - 8:10)**
*Visual: AI grounding architecture, faithfulness formula, and genuine screenshot of the AI Incident Report.*

> **"On Slide 9, we tackle artificial intelligence governance in digital forensics.**
>
> Large Language Models can summarize complex cyber incidents into clear executive briefs. However, off-the-shelf LLMs frequently hallucinate—inventing fictitious IP addresses, inflated victim numbers, or nonexistent timestamps. In legal and forensic reporting, hallucination is unacceptable.
>
> To resolve this, ExposureLens implements a **Deterministic Ground-Truth Verification Gate**. After the AI generates the incident report, a verification parser extracts every entity claim—IPs, timestamps, tenant IDs, and breached record counts—and tests them against the underlying SQLite database.
>
> We calculate the Faithfulness Score:
> $$\mathcal{S}_{\text{faithful}} = \frac{|\mathcal{T}_{\text{AI}} \cap \mathcal{T}_{\text{ground\_truth}}|}{|\mathcal{T}_{\text{AI}}|} \times 100\%$$
>
> In our live production application, shown on the right, ExposureLens achieved a **100.0% Faithfulness Score** and a **0.00% Hallucination Score**, providing mathematical confidence that the report is legally sound."

---

### **Slide 10: Experimental Evaluation & Research Benchmark (8:10 - 9:00)**
*Visual: 15-scenario benchmark suite, latency breakdown, and genuine screenshot of the Research Benchmark Workspace.*

> **"Slide 10 highlights our experimental validation and research contributions.**
>
> We evaluated ExposureLens across **15 diverse multi-tenant attack scenarios** simulating healthcare FHIR APIs, multi-tenant ERP platforms, and fintech banking gateways.
>
> Because our detection logic operates on exact authorization context binding rather than probabilistic heuristics:
> - **Precision:** $1.000$ (Zero false positives across normal enterprise workflows)
> - **Recall:** $1.000$ (100% detection of all unauthorized object-level traversals)
> - **F1-Score:** $1.000$
>
> From a performance overhead standpoint:
> - Telemetry Ingestion: $1.42 \text{ ms}$
> - Semantic Delta Processing: $3.81 \text{ ms}$
> - Cryptographic PoE Minting: $0.84 \text{ ms}$
> - **Total End-to-End Latency:** $< 6.2 \text{ ms}$ per incident.
>
> This demonstrates that ExposureLens introduces negligible overhead and can operate at enterprise wire speeds. These findings form the basis of our completed research manuscript prepared for IEEE Transactions on Dependable and Secure Computing."

---

### **Slide 11: Live Deployment, Limitations & Future Roadmap (9:00 - 9:45)**
*Visual: Render cloud verification, GitHub open-source attribution, honest academic limitations, and eBPF roadmap.*

> **"To conclude on Slide 11:**
>
> ExposureLens is fully operational and deployed live on Render at `https://exposurelens.onrender.com`, backed by 25 production modules openly available on GitHub.
>
> In accordance with sound academic methodology, we acknowledge our current research scope:
> - ExposureLens is currently optimized for REST/JSON APIs; complex nested GraphQL queries require abstract syntax tree translation.
> - Passive telemetry ingestion requires API gateway access logs or middleware integration.
>
> In our future roadmap, we are actively implementing:
> 1. **Linux eBPF kernel probes** to capture socket-level telemetry out-of-band with zero application overhead.
> 2. **CI/CD Shift-Left plugins** for GitHub Actions to prevent BOLA regressions prior to deployment.
> 3. **Public blockchain notarization** (on Ethereum or Polygon) for decentralized, multi-cloud non-repudiation.
>
> ExposureLens successfully bridges the post-exploitation void in API security, transforming silent BOLA breaches into verifiable, deterministic, and legally admissible forensic evidence.
>
> Thank you, respected examiners. I am now open to your questions."

---

## 🛡️ Comprehensive Examiner Q&A Defense Guide

Here are the most challenging technical and academic questions examiners may ask during your M.Tech defense, along with precise, mathematically sound responses:

---

### **Q1: "Why can't traditional Web Application Firewalls (WAFs) or API Gateways prevent BOLA?"**
**Answer:**
> "Traditional WAFs (such as ModSecurity, AWS WAF, or Cloudflare) inspect the *syntax* and *structure* of HTTP requests—searching for known exploit signatures like SQL injection apostrophes, script tags, or anomalous payload sizes.
>
> BOLA, by contrast, is a purely *semantic authorization flaw*. An attacker performing BOLA sends a syntactically valid JSON payload, with a legitimate JWT bearer token issued by the identity provider, using standard HTTP GET or POST methods. To the WAF, the request is indistinguishable from a normal user action.
>
> Furthermore, API Gateways enforce *coarse-grained authentication* (e.g., verifying token signature and expiration), but they do not possess domain-specific object ownership logic. Object-level ownership is buried in the database or ORM layer, which is why BOLA breaches slip past gateways with an HTTP 200 OK."

---

### **Q2: "What is the exact mathematical intuition behind the Tenant Isolation Failure Index (TIFI)?"**
**Answer:**
> "TIFI models both the *volume* and *dispersion* of cross-tenant data leakage.
> If an attacker compromises 100 records belonging solely to Tenant B, that represents a targeted breach. But if an attacker compromises 10 records across 10 different customer tenants, tenant isolation has broken down systemically.
>
> To capture this, TIFI multiplies the Cross-Tenant Exfiltration Ratio ($\mathcal{R}_{\text{cross}} = \sum_{i \neq j} \mathbf{E}_{i \to j} / \sum \mathbf{E}$) by the normalized Shannon directional spillover entropy:
> $$\mathcal{H}_{\text{spill}} = - \sum_{j \neq i} p_{i \to j} \log_2(p_{i \to j})$$
>
> If all leaked data goes to one victim tenant, entropy is zero, keeping TIFI low. If exfiltrated records are uniformly dispersed across all $N$ tenants, entropy reaches $\log_2(N)$, pushing TIFI to its maximum value of $1.0$. This provides CISOs with an empirical, normalized metric of organizational boundary damage."

---

### **Q3: "How do you achieve 100% faithfulness and 0.00% hallucination in your AI reporting module?"**
**Answer:**
> "We achieve this through a *dual-engine constrained architecture*. We do not allow the Large Language Model to act as the primary database or factual record.
>
> 1. The deterministic engine first computes all mathematical facts: exact record counts, victim tenant names, caller IPs, and leaked schema attributes from SQLite telemetry.
> 2. The prompt supplied to the LLM injects these verified facts as strict system context constraints.
> 3. After the LLM generates the narrative report, our post-generation verification parser extracts all named entities, IP addresses, timestamps, and numbers using regex and AST analysis.
> 4. It performs a set intersection: $\mathcal{S}_{\text{faithful}} = \frac{|\mathcal{T}_{\text{AI}} \cap \mathcal{T}_{\text{ground\_truth}}|}{|\mathcal{T}_{\text{AI}}|}$. If any entity is present in the LLM text that is absent from the ground-truth database, it is flagged as a hallucination, rejected, and regenerated.
>
> This guarantees that the final statutory report contains zero fabricated forensic data."

---

### **Q4: "Why use a SHA-256 Merkle hash chain rather than a standard relational database with updated_at timestamps?"**
**Answer:**
> "In judicial proceedings and regulatory investigations under the DPDP Act or GDPR, relational database timestamps have low evidentiary weight because any database administrator or compromised service account with write permissions can execute an `UPDATE` query to alter timestamps or scrub payload fields without leaving an audit trail.
>
> In ExposureLens, each block $B_k$ is cryptographically linked to the previous block's hash:
> $$H_k = \text{SHA-256}(k \;\|\; \tau_k \;\|\; H_{k-1} \;\|\; \text{SHA-256}(\mathcal{P}_{\text{raw}}) \;\|\; t_{\text{caller}} \;\|\; t_{\text{victim}})$$
>
> If an adversary or insider alters a single character of the payload or changes a timestamp in the database, recomputing the hash cascade causes an immediate Merkle root mismatch at block $k+1$. This gives our Proof-of-Exposure certificates mathematical non-repudiation."

---

### **Q5: "How does ExposureLens help organizations comply with the India DPDP Act 2023 and CERT-In directions?"**
**Answer:**
> "Under Section 8(5) of the Digital Personal Data Protection Act 2023, data fiduciaries are legally required to report personal data breaches to the Data Protection Board of India and affected data principals. Fines can reach ₹250 Crores for failure to take reasonable security measures.
>
> Simultaneously, CERT-In directions mandate that cybersecurity incidents—specifically unauthorized access to IT systems—must be reported within a tight **6-hour window**.
>
> Manual incident triage takes an average of 48 to 72 hours just to determine what data leaked. ExposureLens completes deterministic reconstruction in under **6.2 milliseconds**. It automatically generates statutory notification notices with exact counts of affected individuals, leaked property classifications (e.g., SSN, financial data), and forensic hashes, enabling organizations to report within the 6-hour statutory CERT-In window."

---

### **Q6: "What is the difference between BOLA and BOPLA, and how does ExposureLens address both?"**
**Answer:**
> "BOLA (OWASP API1:2023) is *Broken Object Level Authorization*, where an unauthorized user accesses an entire object belonging to another user or tenant.
>
> BOPLA (OWASP API3:2023) is *Broken Object Property-Level Authorization*, where the caller is authorized to view certain properties of an object (e.g., public profile name), but the API serialization layer inadvertently exposes sensitive private fields (e.g., SSN, salary bracket, hashed password).
>
> ExposureLens solves both through our **Semantic Property Delta** formula:
> $$\Delta_{\text{leak}} = \mathcal{P}_{\text{delivered}} \setminus \mathcal{P}_{\text{authorized}}$$
> We validate every returned JSON property against the authorized OpenAPI schema definition, isolating internal properties leaked even when object-level access is nominally permitted."

---

### **Q7: "Why use Open Policy Agent (OPA) for virtual patching rather than modifying the backend Python/Flask source code?"**
**Answer:**
> "In enterprise microservice architectures, updating application source code requires:
> 1. Writing code patches across dozens of services.
> 2. Running regression test suites.
> 3. Security code reviews and approval gates.
> 4. Container rebuilds, staging deployment, and production rollouts.
>
> The Mean Time to Remediate (MTTR) for code-level patches is typically 15 to 30 days. During this window, the vulnerability remains actively exploitable.
>
> By contrast, Open Policy Agent (OPA) operates as an out-of-process authorization engine at the API Gateway or Envoy service mesh layer. ExposureLens automatically generates a declarative Rego policy rule directly from the reconstructed incident. This rule is pushed to OPA at runtime, blocking unauthorized tenant cross-traversals immediately with **zero service restarts and zero downtime**."

---

### **Q8: "What are the practical limitations of ExposureLens, and how will you resolve them?"**
**Answer:**
> "We identify two primary limitations:
> 1. **Data Format Scope:** ExposureLens is currently optimized for RESTful APIs utilizing JSON schemas. In GraphQL APIs, where queries can be arbitrarily nested and aliased, determining property authorization requires abstract syntax tree (AST) parsing. We are currently implementing a GraphQL AST visitor module.
> 2. **Telemetry Ingestion Point:** ExposureLens currently requires access to HTTP access logs, proxy middleware, or application hooks. In environments where teams do not have access to gateway telemetry, passive monitoring is challenging.
>
> To resolve this, our future roadmap includes developing an **eBPF (Extended Berkeley Packet Filter)** kernel module. eBPF hooks directly into Linux kernel socket buffers (`sock_ops` and `tc`), allowing ExposureLens to intercept and reconstruct API traffic out-of-band at line rate with zero application modifications."

---

## 📋 Checklist for Presentation Day

1. **Presentation Files:**
   - [x] Editable PowerPoint: `presentation/ExposureLens_Major_Project.pptx`
   - [x] High-Quality Vector PDF: `presentation/ExposureLens_Major_Project.pdf`
   - [x] Speaker Notes & Defense Guide: `presentation/SPEAKER_NOTES_AND_SCRIPT.md`
2. **Live System Demonstrations:**
   - [x] Live Cloud Web Application: `https://exposurelens.onrender.com`
   - [x] GitHub Repository: `https://github.com/saikatmondal-cy/ExposureLens`
   - [x] Local Dashboard: `streamlit run dashboard/app.py`
3. **Presenter Timing:**
   - Practice with a stopwatch aiming for **9 minutes 30 seconds**.
   - Speak with measured cadence (~130 words per minute).
   - Advance slides exactly at the target cumulative time markers in the table above.
