# Antigravity FSI India Guard Plugin

[![Compliance: RBI IT Governance 2023](https://img.shields.io/badge/Compliance-RBI%20IT%20Governance%202023-blue)](docs/RBI_COMPLIANCE.md)
[![Compliance: SEBI CSCRF 2024](https://img.shields.io/badge/Compliance-SEBI%20CSCRF%202024-green)](docs/SEBI_COMPLIANCE.md)
[![Compliance: DPDP Act 2023](https://img.shields.io/badge/Compliance-DPDP%20Act%202023-orange)](docs/RBI_COMPLIANCE.md)
[![Security: Google Cloud Model Armor](https://img.shields.io/badge/Security-Google%20Cloud%20Model%20Armor-red)](docs/MODEL_ARMOR_SETUP.md)
[![Test Suite: 100% Pass](https://img.shields.io/badge/Tests-25%2F25%20Passing-brightgreen)](tests/run_all_tests.py)

Enterprise-grade Governance, Risk, and Compliance (GRC) Antigravity Plugin providing real-time **Indian PII Regex/Checksum Protection** and **Google Cloud Model Armor Safety Filtering** for Financial Services Institutions (Banks, NBFCs, Stock Brokers, AMCs, FinTechs) in India.

---

## Key Features

1. **Deterministic Indian PII Guard Hook (`PreInvocation` & `PreToolUse`)**:
   - **UIDAI Aadhaar**: 12-digit number validated via **Verhoeff Dihedral Group D5** algorithm.
   - **Income Tax PAN**: 10-character alphanumeric with entity character classification (`P`, `C`, `H`, `F`, `A`, `T`, `B`, `L`, `J`, `G`).
   - **Payment Cards**: 16-digit RuPay, Visa, Mastercard with **Luhn Mod-10** verification.
   - **GSTIN**: 15-character identifier with state prefix and **Mod 36** checksum.
   - **Banking Data**: Core Banking Account numbers, IFSC codes, MICR codes.
   - **NPCI UPI VPA**: Real-time validation of bank handles (`@okaxis`, `@okhdfcbank`, `@oksbi`, `@paytm`, etc.).
   - **Identity & Contact**: Indian Driving Licences (Sarathi format), Passports, Voter ID (EPIC), PIN codes, CIN, Phone numbers.

2. **Google Cloud Model Armor Safety Hook (`PreInvocation` & `PreToolUse`)**:
   - **Prompt Injection & Jailbreak (PI/JB)**: Intercepts direct/indirect instruction overrides, developer mode exploits, and system prompt leakage attacks.
   - **Responsible AI (RAI)**: Filters hate speech, harassment, dangerous content, and toxicity.
   - **Malicious URIs & Phishing**: Intercepts unapproved external links and malware distribution vectors.
   - **Multi-Lingual Support**: Native detection across English and Indian languages (Hindi, Tamil, Telugu, Bengali, Marathi, Gujarati, Kannada).
   - **Fail-Closed Security**: High-availability resilience defaulting to deny on security anomalies.

3. **Tamper-Resistant Cryptographic Audit Trail**:
   - Every prompt evaluation and hook decision is recorded with a **SHA-256 cryptographic hash chain**.
   - Dual UTC & IST timestamps formatted for 7-year regulatory retention under RBI and SEBI rules.

4. **Complete Regulatory Rules & Skills**:
   - Workspace rules (`rules/rbi_governance.md`, `rules/sebi_governance.md`, `rules/pii_handling.md`).
   - Interactive diagnostic skills (`fsi-compliance-audit`, `model-armor-diagnostics`).
   - Administrative CLI tool (`src/cli/grc_admin.py`).

---

## Quickstart

### 1. Provision Server-Side Model Armor & Infrastructure via Terraform
```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform apply
```

### 2. Run Automated Test Suite
```bash
python3 tests/run_all_tests.py
```

### 3. Test a Prompt with the Admin CLI
```bash
python3 src/cli/grc_admin.py test-prompt "Check KYC: PAN ABCPE1234F, Aadhaar 2345 6789 0124"
```

### 4. Verify Compliance Matrix
```bash
python3 src/cli/grc_admin.py verify-compliance --framework ALL
```

### 5. Inspect Cryptographic Audit Trail
```bash
python3 src/cli/grc_admin.py show-audit --tail 10
```

---

## Documentation Links

* [System Architecture & SDD](docs/ARCHITECTURE.md)
* [Terraform Infrastructure Automation](terraform/README.md)
* [RBI Master Direction Compliance Mapping](docs/RBI_COMPLIANCE.md)
* [SEBI CSCRF Framework Compliance Mapping](docs/SEBI_COMPLIANCE.md)
* [Google Cloud Model Armor Deployment Guide](docs/MODEL_ARMOR_SETUP.md)
* [Operator & Developer User Guide](docs/USER_GUIDE.md)

---

## License
Apache-2.0. Developed for Google Cloud Financial Services Customers.
