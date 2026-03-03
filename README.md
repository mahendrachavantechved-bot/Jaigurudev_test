# Loan Processing Demo – Retail + SME (End-to-End)

> **Bengaluru Dev Setup** | March 2026  
> Combined Retail (personal / home / auto / gold / education) + SME / Corporate Trade Finance demo

---

## Project Structure

```
loan-processing-demo-final/
│
├── main.py                      ← Combined Flet UI (Retail + SME tabs)
├── retail_pipeline.py           ← 10-agent Retail pipeline (FOIR, LTV, credit scoring)
├── sme_pipeline.py              ← 10-agent SME pipeline (DSCR, collateral, underwriting)
├── gauges.py                    ← DSCR gauge + LTV gauge (matplotlib → base64 PNG)
├── sarvam_utils.py              ← Sarvam STT (Saaras v3) + Mayura Translation wrappers
├── synthetic_data_generator.py  ← Generates 10,000 Retail + 10,000 SME applicants
│
├── retail_applicants.json       ← 10,000 synthetic retail records (auto-generated)
├── retail_applicants.csv        ← Same data in CSV format
├── sme_applicants.json          ← 10,000 synthetic SME records (auto-generated)
├── sme_applicants.csv           ← Same data in CSV format
│
├── requirements.txt
├── README.md
└── assets/
    ├── bank.ico                 ← App icon for .exe packaging
    └── logo.png                 ← Optional branding logo
```

---

## Quick Start

### Step 1 – Clone / unzip

```bash
git clone https://github.com/your-org/loan-processing-demo-final.git
cd loan-processing-demo-final
```

### Step 2 – Create virtual environment (recommended)

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### Step 3 – Install dependencies

```bash
pip install -r requirements.txt
```

> **Note:** `sarvamai` requires your Sarvam API subscription key. If you don't have one,
> the app still runs with mock STT / translation responses.

### Step 4 – Generate synthetic data (10,000 customers each)

```bash
python synthetic_data_generator.py
```

This creates:
- `retail_applicants.json` (10,000 records, all unique names)
- `sme_applicants.json`    (10,000 records, all unique business names)
- `retail_applicants.csv`
- `sme_applicants.csv`

> **~44% of applicants are from Bengaluru** (weighted for local demos).

### Step 5 – Run the app

```bash
flet run main.py
```

---

## Configuration

### Sarvam API Key

Edit `sarvam_utils.py` and replace:

```python
SARVAM_KEY = "YOUR_REAL_SARVAM_SUBSCRIPTION_KEY_HERE"
```

### Change number of synthetic records

Edit `synthetic_data_generator.py`, last line:

```python
generate_and_save(10000)   # change to 5000, 50000, etc.
```

---

## Pipeline Architecture

### Retail Pipeline (10 Agents)

| # | Agent | Key Logic |
|---|-------|-----------|
| 1 | Intake & Lead Scoring | Pre-approval check, lead score |
| 2 | KYC & Identity | Liveness check, PAN/Aadhaar match |
| 3 | Income & FOIR | Net income, EMI calc, FOIR % vs threshold |
| 4 | Credit Bureau | CIBIL band (A/B/C/D), fraud score |
| 5 | Property Appraisal | Market value, LTV ratio (home loan only) |
| 6 | Credit Decisioning | Weighted scorecard, hard reject rules |
| 7 | Sanction | Offer letter generation |
| 8 | Documentation | e-Sign, NACH UMRN mock |
| 9 | Disbursement | IMPS / NEFT, loan account number |
| 10 | Monitoring | DPD, NPA risk score |

**FOIR Thresholds:**
- Income < ₹25,000 → max 45%
- Income ₹25,000–₹1,00,000 → max 50%
- Income > ₹1,00,000 → max 60%

**Hard Reject Rules:**
- CIBIL < 650
- FOIR > 65%
- Fraud score > 80
- LTV > max allowed + 5%
- KYC failure

### SME Pipeline (10 Agents)

| # | Agent | Key Logic |
|---|-------|-----------|
| 1 | Lead Intake | Vintage ≥ 3 yrs, turnover ≥ ₹15L, loan/turnover ratio |
| 2 | KYC | GST verification, face match |
| 3 | Financial Analysis | DSCR, current ratio, D/E, gross margin |
| 4 | Credit Bureau | Promoter CIBIL score → A/B/C/D grade |
| 5 | Collateral | LTV matrix by asset type |
| 6 | Underwriting | Scorecard → AUTO_APPROVE / APPROVE_WITH_CONDITIONS / REFER / REJECT |
| 7 | Sanction | Conditions, moratorium, validity 90 days |
| 8 | Documentation | e-Sign, NACH UMRN |
| 9 | Disbursement | RTGS / NEFT |
| 10 | Monitoring | DPD, NPA risk, loan health score |

**DSCR Benchmark:** ≥ 1.25 (minimum), ≥ 1.5 (preferred)

**LTV Matrix:**
| Asset Type | Max LTV |
|------------|---------|
| Residential property | 75% |
| Commercial property | 65% |
| Plant & machinery | 50% |
| Book debts / invoices | 75–80% |
| Stock | 65% |

---

## Package as .exe (Windows)

```bash
pip install pyinstaller flet

flet pack main.py \
  --name "LoanDemo-Final" \
  --icon assets/bank.ico \
  --add-data "assets;assets" \
  --add-data "retail_applicants.json;." \
  --add-data "sme_applicants.json;." \
  --hidden-import matplotlib \
  --hidden-import sarvamai \
  --hidden-import numpy
```

---

## Data Schema

### retail_applicants.json (each record)

```json
{
  "id": "RET-000001",
  "application_id": "RET-000001",
  "name": "Pallavi Khandelwal",
  "full_name": "Pallavi Khandelwal",
  "pan": "ABCDE1234F",
  "mobile": "9876543210",
  "email": "pallavi.1@gmail.com",
  "gender": "F",
  "age": 34,
  "date_of_birth": "1991-06-15",
  "cibil": 755,
  "cibil_score": 755,
  "monthly_income": 82000,
  "loan_amt": 1200000,
  "loan_amount_requested": 1200000,
  "tenure_months": 60,
  "existing_emi": 15000,
  "type": "personal_loan",
  "loan_type": "personal_loan",
  "city": "Bengaluru",
  "employment_type": "salaried",
  "loan_purpose": "Home renovation",
  "indicative_rate": 12.5,
  "property_type": null,
  "created": "2025-08-14"
}
```

### sme_applicants.json (each record)

```json
{
  "id": "SME-000001",
  "application_id": "SME-000001",
  "name": "Lakshmi Exports Associates",
  "business_name": "Lakshmi Exports Associates",
  "pan": "ABCDE1234F",
  "gstin": "29ABCDE1234FZ1",
  "mobile": "9876543210",
  "email": "lakshmi.1@gmail.com",
  "promoter_name": "Kiran Reddy",
  "promoter_cibil_score": 742,
  "cibil": 742,
  "annual_turnover": 4100000,
  "turnover": 4100000,
  "loan_amt": 1500000,
  "loan_amount_requested": 1500000,
  "business_vintage_years": 7,
  "vintage": 7,
  "type": "working_capital",
  "loan_type": "working_capital",
  "collateral": 2200000,
  "collateral_value": 2200000,
  "city": "Bengaluru",
  "industry": "Textiles & Garments",
  "loan_purpose": "Working capital",
  "created": "2025-04-22"
}
```

---

## GitHub Repository Setup

```bash
# Init repo
git init
git add .
git commit -m "Initial commit: Loan Processing Demo v1.0"

# Add remote and push
git remote add origin https://github.com/your-org/loan-processing-demo-final.git
git push -u origin main
```

### Recommended `.gitignore`

```
.venv/
__pycache__/
*.pyc
dist/
build/
*.spec
.env
```

> **Tip:** Commit the `.json` / `.csv` data files to the repo so teammates can run
> immediately without generating. For very large counts (100k+), add them to `.gitignore`
> and run the generator locally.

---

## Team / Client Notes

- Window opens at **1400 × 860** dark theme
- Search is **instant** (client-side filter, no network call)
- Selecting any applicant opens a **side panel** with full details
- Results show visual **DSCR gauge** (SME) and **LTV gauge** (Retail home loans)
- Translate button sends result text to **Sarvam Mayura** for Hindi output
- All pipeline computations are **synchronous mock** (no external API except Sarvam)
- Replace `SARVAM_KEY` to enable real STT/translation

---

*Generated: March 2026 | Bengaluru Dev Setup*
