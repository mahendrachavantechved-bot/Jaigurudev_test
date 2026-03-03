"""
synthetic_data_generator.py
============================
Generates 10,000 unique Retail + 10,000 unique SME applicants.
All names are guaranteed unique using a combination pool strategy.

Fixes applied:
  1. Removed unused `uuid` import
  2. Fixed GSTIN to use full 10-char PAN → correct 15-char GSTIN
  3. INDUSTRY_WEIGHTS now sums to 100
  4. date_of_birth now covers days 1–31 safely (no month-end bias)
  5. loan_amt in SME capped/floored more robustly to avoid silent overrides
  6. Added PAN 4th-char convention (P for individual, C for company)
  7. Middle-initial fallback counter fixed (only increments on success)

Usage:
    python synthetic_data_generator.py

Outputs:
    retail_applicants.json   (10,000 records)
    sme_applicants.json      (10,000 records)
    retail_applicants.csv    (10,000 records)
    sme_applicants.csv       (10,000 records)
"""

import json
import csv
import random
import calendar
from datetime import datetime, timedelta

random.seed(2026)  # reproducible for demos

# ─────────────────────────────────────────────────────────────────────────────
# Name pools
# ─────────────────────────────────────────────────────────────────────────────
FIRST_NAMES = [
    "Aarav","Aditya","Akash","Akshay","Amith","Anand","Anil","Anjali","Ankit","Anush",
    "Arjun","Aruna","Ashish","Ashok","Ashwini","Bharath","Bhavana","Chandra","Chetan","Deepa",
    "Deepak","Dhruv","Divya","Geetha","Girish","Gopal","Govind","Harish","Harsha","Hemanth",
    "Indira","Jagadish","Jaya","Jayesh","Kalpana","Karthik","Kiran","Krishnan","Kumar","Lakshmi",
    "Lavanya","Lekha","Madhav","Madhuri","Mahesh","Mamatha","Manoj","Meena","Meghna","Mohan",
    "Mrinal","Murali","Nagesh","Nandini","Naresh","Naveen","Neha","Nikhil","Nilesh","Nisha",
    "Pallavi","Pavan","Pooja","Pradeep","Prasad","Prasanna","Preethi","Priya","Priyanshi","Rahul",
    "Rajesh","Rakesh","Ramesh","Ranjith","Ravi","Rekha","Reshma","Rohit","Roopa","Rupesh",
    "Sachin","Sahana","Samir","Sandeep","Sangeetha","Sanjay","Santhosh","Sarath","Saritha","Satish",
    "Savitha","Shashi","Shiva","Shruti","Smitha","Sneha","Sowmya","Sridhar","Srikanth","Srini",
    "Srinivas","Subash","Sudhir","Sumanth","Sumitra","Sunil","Sunita","Suresh","Sushma","Swati",
    "Tejaswi","Thejesh","Uday","Usha","Vaishnavi","Varun","Vasanth","Veena","Venkat","Vidya",
    "Vijay","Vikas","Vikram","Vinay","Vishnu","Vishal","Yamuna","Yogesh","Yashwanth","Zara",
    "Aarohi","Aayush","Abhijit","Abhilasha","Abhimanyu","Abhishek","Aishwarya","Akanksha","Alok","Amarjeet",
    "Amisha","Amrita","Anchita","Angad","Ankita","Anshika","Anshul","Antara","Anurag","Aparna",
    "Archana","Arpit","Astha","Avni","Ayesha","Bhavesh","Bhumi","Chanchal","Chirag","Deepika",
    "Devika","Dheeraj","Disha","Esha","Fatima","Gaurav","Gauri","Gunjan","Gurpreet","Harsh",
    "Himanshu","Ishaan","Ishika","Jatin","Juhi","Kabir","Kajal","Kapil","Kavita","Khushi",
    "Komal","Kritika","Kunal","Latika","Manish","Manisha","Manjeet","Meghana","Mili",
    "Mitali","Mohit","Muskan","Namita","Nandita","Namrata","Naomi","Natasha","Nidhi","Nikita",
    "Nimisha","Nupur","Pallak","Pankaj","Parth","Payal","Pinky","Prachi","Pramod",
    "Pranav","Pranita","Pranjal","Prashanth","Preeti","Puja","Rachna","Radhika","Rajan","Rajni",
    "Rashi","Raunak","Riya","Rohini","Ruhi","Saanvi","Sabina","Saloni","Sanchi",
    "Seema","Shaily","Shikha","Shivani","Simran","Sonam","Sonia","Srishti","Stuti","Swara",
    "Tanisha","Tanvi","Tarun","Trisha","Tushita","Urvashi","Utkarsh","Vaibhav","Vandana","Vanshika",
    "Varsha","Vedant","Vibha","Vivek","Vrinda","Yash","Yashika","Zeenat","Zubaida","Zubair",
    "Aabha","Aachal","Aadhira","Aadhvik","Aagam","Aahan","Aaira","Aaliya","Aamani",
    "Aanal","Aanya","Aarchi","Aaryan","Aashna","Aatmaj","Aatrey","Aavya","Aayat","Aazeen",
    "Abeer","Abha","Abhaya","Abhi","Abhirup","Abirami","Achal","Achintya","Adesh",
    "Adhavan","Adheera","Adhiraj","Adhira","Adhiti","Aditi","Adithi","Advaita","Advaith","Advika",
]

LAST_NAMES = [
    "Rao","Reddy","Nair","Iyer","Iyengar","Pillai","Menon","Krishnamurthy","Venkataraman","Subramaniam",
    "Gowda","Hegde","Shetty","Kamath","Bhat","Naik","Prabhu","Pai","Kulkarni","Joshi",
    "Patil","Desai","Naidu","Chetty","Mudaliar","Aiyar","Bhatt","Sharma","Verma","Gupta",
    "Singh","Kumar","Patel","Shah","Mehta","Chopra","Malhotra","Khanna","Kapoor","Arora",
    "Murthy","Rajan","Krishnan","Sundaram","Subramanian","Balakrishnan","Annamalai","Thiruvengadam",
    "Ramaswamy","Venkatesan","Gopalakrishnan","Natarajan","Chandrasekaran","Ramachandran","Sivaramakrishnan",
    "Banerjee","Chatterjee","Mukherjee","Ghosh","Das","Bose","Roy","Sen","Dey","Chakraborty",
    "Ganguly","Sarkar","Mandal","Biswas","Paul","Nandi","Mondal","Chaudhury","Bhattacharya","Datta",
    "Jain","Agrawal","Bajaj","Birla","Maheshwari","Mittal","Khandelwal","Singhania","Oswal","Lodha",
    "Doshi","Zaveri","Sanghvi","Parekh","Modi","Trivedi","Pandya","Bhavsar","Raval","Thakkar",
    "Yadav","Mishra","Pandey","Tiwari","Dubey","Shukla","Srivastava","Dwivedi","Tripathi","Chaturvedi",
    "Awasthi","Bajpai","Upadhyay","Chauhan","Rajput","Rathore","Shekhawat","Bhati","Tanwar","Sisodia",
    "Ahlawat","Dagar","Hooda","Khatri","Saini","Dhull","Sangwan","Beniwal","Phogat","Godara",
    "Gill","Grewal","Sandhu","Sidhu","Dhaliwal","Dhillon","Brar","Mann","Sekhon","Virk",
    "Randhawa","Sohal","Toor","Kang","Thind","Nijjar","Bains","Hayer","Pannu","Deol",
    "Shinde","Jadhav","Pawar","More","Bhosale","Thorat","Kale","Deshpande","Phadke","Gokhale",
    "Apte","Limaye","Marathe","Ranade","Savarkar","Tilak","Dalvi","Gawde","Salunkhe","Waghmare",
    "Kamble","Mane","Bhalerao","Kshirsagar","Jog","Vedak","Datar","Chitale","Gupte",
    "Arunachalam","Duraisamy","Govindasamy","Karuppusamy","Muthusamy","Palaniswamy","Ramasamy","Shanmugam",
    "Thirumeni","Veerasamy","Arumugam","Chidambaram","Devarajan","Ganesan","Hariharan",
    "Abraham","George","Thomas","Philip","Mathew","Joseph","John","James","Peter","Paul",
    "Xavier","Fernandes","D'Souza","Pereira","Noronha","Pinto","Monteiro","Sequeira","Rodrigues","Gomes",
]

BIZ_PREFIXES = [
    "Aarav","Aditya","Akshara","Amrit","Anand","Apex","Arjun","Arunodaya","Arya","Ashoka",
    "Atharva","Avanti","Ayush","Bharat","Bright","Celestial","Chandra","Chetan","Crest","Crown",
    "Crystal","Dakshin","Deep","Delta","Devi","Dharma","Dhruv","Disha","Dynamic","Eagle",
    "Eastern","Elite","Emerald","Empire","Excel","First","Fortune","Galaxy","Ganesh","Garuda",
    "Global","Gold","Golden","Gopala","Green","Guru","Harmony","Himalaya","Horizon","Indra",
    "Indus","Infinity","Innova","Inspire","Integrated","Jain","Jayalakshmi","Jyoti","Kailash","Kalpa",
    "Kamala","Karthikeya","Kaveri","Keystone","Konkan","Krishna","Lakshmi","Landmark","Legend","Link",
    "Lotus","Madhav","Mahindra","Majestic","Malabar","Maruthi","Matrix","Maxim","Mega","Metro",
    "Modern","Mukunda","Nandana","National","Nature","Navadurga","Naveen","Next","Noble","Omega",
    "Omni","One","Pacific","Padmavathi","Peak","Pioneer","Prabhu","Pragati","Prakash","Premier",
    "Pride","Prime","Pro","Progressive","Pushpa","Quality","Radha","Raj","Raja","Rajendra",
    "Rajguru","Rajlakshmi","Ranjit","Ravi","Reliance","Rich","Riddhi","Rising","Royal","Sagar",
    "Sahyadri","Samrudhi","Saraswati","Sarvam","Satyam","Savita","Shakti","Shankar","Shiva","Shree",
    "Shri","Siddhi","Silicon","Sky","Smart","Sri","Standard","Star","Sterling","Summit",
    "Sunrise","Superior","Supreme","Supriya","Surya","Swift","Synergy","Tech","Techno","Triumph",
    "Tulasi","Uma","United","Universal","Usha","Vaishnavi","Vajra","Vega","Venkat","Vidya",
    "Vijay","Vikas","Vishnu","Vista","Vivek","Western","White","Wisdom","World","Yashoda",
    "Zenith","Zest","Alpha","Beta","Gamma","Sigma","Titan","Turbo","Ultra","Venture",
]

BIZ_SUFFIXES = [
    "Solutions","Enterprises","Industries","Exports","Manufacturing","Traders","Foods",
    "Fashions","Technologies","Systems","Services","Logistics","Infrastructure","Projects",
    "Constructions","International","Chemicals","Pharmaceuticals","Textiles","Agro",
    "Motors","Electronics","Electricals","Engineering","Consultancy","Finance","Realty",
    "Builders","Developers","Healthcare","Hospital","Diagnostics","Labs","Research",
    "Packaging","Plastics","Polymers","Metals","Steel","Alloys","Castings","Forgings",
    "Auto Components","Spares","Accessories","Garments","Apparels","Yarns","Fabrics",
    "Paper","Print","Media","Studios","Events","Advertising","Marketing","Digital",
    "Software","Infotech","Telecom","Networks","Security","Automation","Robotics","Power",
]

BIZ_TYPES = ["Pvt Ltd", "LLP", "& Co", "Associates", "Group", "Co-op", "OPC Pvt Ltd", "Pvt Ltd"]

# ─────────────────────────────────────────────────────────────────────────────
# Geography & reference data
# ─────────────────────────────────────────────────────────────────────────────
CITY_DATA = [
    ("Bengaluru", 45, "29"), ("Mumbai", 10, "27"), ("Delhi", 9, "07"),
    ("Hyderabad", 7, "36"), ("Chennai", 6, "33"), ("Pune", 5, "27"),
    ("Ahmedabad", 4, "24"), ("Kolkata", 3, "19"), ("Coimbatore", 2, "33"),
    ("Indore", 2, "23"), ("Surat", 2, "24"), ("Nagpur", 1, "27"),
    ("Jaipur", 1, "08"), ("Lucknow", 1, "09"), ("Bhopal", 1, "23"),
    ("Kochi", 1, "32"),
]
CITIES_LIST  = [c[0] for c in CITY_DATA]
CITY_WEIGHTS = [c[1] for c in CITY_DATA]
STATE_CODES  = {c[0]: c[2] for c in CITY_DATA}

INDUSTRIES = [
    "IT / Software Services","Manufacturing","Retail Trade","Textiles & Garments",
    "Food Processing","Pharmaceuticals","Construction","Automobile Components",
    "Logistics","Agriculture","Healthcare","E-commerce","Education",
    "Chemicals","Steel & Metals","Printing & Packaging","Real Estate","Hospitality",
]
# FIX 3: weights now sum exactly to 100
INDUSTRY_WEIGHTS = [20, 15, 13, 10, 8, 7, 6, 5, 4, 3, 2, 2, 1, 1, 1, 1, 1, 0]
# Hospitality gets 0 but we keep it in list; drop it to be safe:
INDUSTRIES       = INDUSTRIES[:-1]
INDUSTRY_WEIGHTS = [20, 15, 13, 10, 8, 7, 6, 5, 4, 3, 2, 2, 1, 1, 1, 1, 1]  # sum=100

LOAN_PURPOSES_RETAIL = [
    "Home renovation","Vehicle purchase","Personal expenses","Wedding",
    "Medical emergency","Education","Debt consolidation","Travel","Business expansion",
    "Consumer durables","Home appliances","Solar panel installation",
]
LOAN_PURPOSES_SME = [
    "Business expansion","Machinery purchase","Working capital","Invoice financing",
    "Shop renovation","Inventory purchase","New branch setup","Technology upgrade",
    "Export financing","Project finance","Capacity expansion","Trade finance",
]
EMPLOYMENT_TYPES = ["salaried","self_employed_professional","self_employed_non_professional"]
GENDERS          = ["M","F","O"]
EMAIL_DOMAINS    = ["gmail.com","outlook.com","yahoo.co.in","rediffmail.com","hotmail.com"]

RETAIL_LOAN_TYPES = ["personal_loan","home_loan","auto_loan","gold_loan","education_loan"]
SME_LOAN_TYPES    = ["term_loan","working_capital","equipment_finance","invoice_discounting","project_finance"]

# ─────────────────────────────────────────────────────────────────────────────
# Helper generators
# ─────────────────────────────────────────────────────────────────────────────

def fake_pan(entity_type: str = "individual") -> str:
    """
    PAN format: AAAAA9999A
    4th char convention:
      P = individual person
      C = company / firm
    """
    letters   = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    fourth    = "P" if entity_type == "individual" else "C"
    return (
        "".join(random.choices(letters, k=3)) +
        fourth +
        random.choice(letters) +
        str(random.randint(1000, 9999)) +
        random.choice(letters)
    )


def fake_mobile() -> str:
    return f"9{random.randint(100000000, 999999999)}"


def fake_email(name_part: str, idx: int) -> str:
    clean = name_part.lower().replace(" ", ".").replace("'", "")
    return f"{clean}{idx}@{random.choice(EMAIL_DOMAINS)}"


def fake_gstin(city: str, pan: str) -> str:
    """
    GSTIN format (15 chars):
      2-char state code + 10-char PAN + 1-digit entity number + 1-char Z + 1-char checksum
    FIX 2: was only using pan[:5]; now uses full 10-char PAN
    """
    state      = STATE_CODES.get(city, "29")
    letters    = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    entity_num = random.randint(1, 9)
    checksum   = random.choice(letters)
    return f"{state}{pan}{entity_num}Z{checksum}"  # 2+10+1+1+1 = 15 ✓


def fake_date_of_birth(age: int) -> str:
    """
    FIX 4: Use calendar.monthrange to get correct max day per month,
    eliminating the day-28 cap bias.
    """
    year  = datetime.now().year - age
    month = random.randint(1, 12)
    _, max_day = calendar.monthrange(year, month)
    day   = random.randint(1, max_day)
    return f"{year:04d}-{month:02d}-{day:02d}"


def random_date_in_past(days_back: int = 730) -> str:
    d = datetime.now() - timedelta(days=random.randint(0, days_back))
    return d.strftime("%Y-%m-%d")


# ─────────────────────────────────────────────────────────────────────────────
# Unique name generators
# ─────────────────────────────────────────────────────────────────────────────

def build_unique_retail_names(count: int) -> list:
    """
    Generate `count` unique full names.
    FIX 7: counter `i` increments only on successful unique insertion.
    """
    used  = set()
    names = []
    pool_size = len(FIRST_NAMES) * len(LAST_NAMES)

    while len(names) < count:
        first = random.choice(FIRST_NAMES)
        last  = random.choice(LAST_NAMES)
        # use middle initial once we've used more than 60% of the plain pool
        if len(names) > pool_size * 0.6:
            mid   = random.choice("ABCDEFGHJKLMNPRSTV") + "."
            full  = f"{first} {mid} {last}"
        else:
            full  = f"{first} {last}"
        if full not in used:
            used.add(full)
            names.append(full)

    return names


def build_unique_sme_names(count: int) -> list:
    """Generate `count` unique business names."""
    used  = set()
    names = []
    pool_size = len(BIZ_PREFIXES) * len(BIZ_SUFFIXES)

    while len(names) < count:
        prefix = random.choice(BIZ_PREFIXES)
        suffix = random.choice(BIZ_SUFFIXES)
        btype  = random.choice(BIZ_TYPES)
        if len(names) > pool_size * 0.5:
            qualifier = random.choice(["India","Global","Group","International","National"])
            full = f"{prefix} {suffix} {qualifier} {btype}".strip()
        else:
            full = f"{prefix} {suffix} {btype}".strip()
        if full not in used:
            used.add(full)
            names.append(full)

    return names


# ─────────────────────────────────────────────────────────────────────────────
# Record generators
# ─────────────────────────────────────────────────────────────────────────────

def generate_retail_applicant(idx: int, name: str) -> dict:
    city   = random.choices(CITIES_LIST, weights=CITY_WEIGHTS, k=1)[0]
    lt     = random.choices(RETAIL_LOAN_TYPES, weights=[35, 30, 20, 10, 5], k=1)[0]
    emp    = random.choice(EMPLOYMENT_TYPES)
    age    = random.randint(22, 60)
    gender = random.choice(GENDERS)
    pan    = fake_pan("individual")  # FIX 6: pass entity type

    income_band = random.choices([1, 2, 3], weights=[45, 38, 17], k=1)[0]
    if income_band == 1:
        income = random.randint(22000, 65000)
    elif income_band == 2:
        income = random.randint(65001, 150000)
    else:
        income = random.randint(150001, 400000)

    if lt == "home_loan":
        loan_amt = random.randint(10, 80) * 100_000
        tenure   = random.choice([120, 180, 240, 300])
    elif lt == "auto_loan":
        loan_amt = random.randint(3, 20) * 100_000
        tenure   = random.choice([36, 48, 60, 72])
    elif lt == "gold_loan":
        loan_amt = random.randint(5, 25) * 10_000
        tenure   = random.choice([6, 12, 18, 24])
    elif lt == "education_loan":
        loan_amt = random.randint(5, 30) * 100_000
        tenure   = random.choice([60, 84, 120])
    else:
        loan_amt = random.randint(1, 25) * 100_000
        tenure   = random.choice([12, 24, 36, 48, 60])

    cibil = random.choices(
        list(range(550, 900)),
        weights=[1 if s < 650 else 3 if s < 700 else 5 if s < 750 else 8 if s < 800 else 6
                 for s in range(550, 900)],
        k=1
    )[0]
    existing_emi = random.randint(0, income // 3)
    rate         = round(random.uniform(9.5, 18.5), 2)

    return {
        "id":                    f"RET-{idx:06d}",
        "application_id":        f"RET-{idx:06d}",
        "name":                  name,
        "full_name":             name,
        "pan":                   pan,
        "mobile":                fake_mobile(),
        "email":                 fake_email(name.split()[0], idx),
        "gender":                gender,
        "age":                   age,
        "date_of_birth":         fake_date_of_birth(age),   # FIX 4
        "cibil":                 cibil,
        "cibil_score":           cibil,
        "monthly_income":        income,
        "loan_amt":              loan_amt,
        "loan_amount_requested": loan_amt,
        "tenure_months":         tenure,
        "existing_emi":          existing_emi,
        "type":                  lt,
        "loan_type":             lt,
        "city":                  city,
        "employment_type":       emp,
        "loan_purpose":          random.choice(LOAN_PURPOSES_RETAIL),
        "indicative_rate":       rate,
        "property_type":         random.choice(["ready_to_move","under_construction"]) if lt == "home_loan" else None,
        "created":               random_date_in_past(730),
    }


def generate_sme_applicant(idx: int, name: str) -> dict:
    city  = random.choices(CITIES_LIST, weights=CITY_WEIGHTS, k=1)[0]
    lt    = random.choices(SME_LOAN_TYPES, weights=[35, 30, 15, 12, 8], k=1)[0]
    pan   = fake_pan("company")   # FIX 6: company PAN (4th char = C)
    gstin = fake_gstin(city, pan)  # FIX 2: full 10-char PAN passed

    turnover_band = random.choices([1, 2, 3], weights=[42, 40, 18], k=1)[0]
    if turnover_band == 1:
        turnover = random.randint(15, 55) * 100_000
    elif turnover_band == 2:
        turnover = random.randint(55, 220) * 100_000
    else:
        turnover = random.randint(220, 950) * 100_000

    # FIX 5: robust loan amount — min 5L, max lesser of 60% turnover or 5 Cr
    max_loan = max(500_000, min(int(turnover * 0.6), 50_000_000))
    loan_amt = random.randint(500_000, max_loan)
    loan_amt = round(loan_amt / 100_000) * 100_000  # round to nearest lakh

    vintage = random.randint(2, 22)
    cibil   = random.choices(
        list(range(550, 900)),
        weights=[1 if s < 620 else 2 if s < 650 else 4 if s < 700 else 7 if s < 750 else 9 if s < 800 else 5
                 for s in range(550, 900)],
        k=1
    )[0]

    collateral = (
        0 if lt in ["working_capital", "invoice_discounting"]
        else round(turnover * random.uniform(0.4, 1.5), -4)
    )
    industry = random.choices(INDUSTRIES, weights=INDUSTRY_WEIGHTS, k=1)[0]

    promoter_name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"

    return {
        "id":                     f"SME-{idx:06d}",
        "application_id":         f"SME-{idx:06d}",
        "name":                   name,
        "business_name":          name,
        "pan":                    pan,
        "gstin":                  gstin,
        "mobile":                 fake_mobile(),
        "email":                  fake_email(name.split()[0].lower(), idx),
        "promoter_name":          promoter_name,
        "promoter_cibil_score":   cibil,
        "cibil":                  cibil,
        "annual_turnover":        turnover,
        "turnover":               turnover,
        "loan_amt":               loan_amt,
        "loan_amount_requested":  loan_amt,
        "business_vintage_years": vintage,
        "vintage":                vintage,
        "type":                   lt,
        "loan_type":              lt,
        "collateral":             collateral,
        "collateral_value":       collateral,
        "city":                   city,
        "industry":               industry,
        "loan_purpose":           random.choice(LOAN_PURPOSES_SME),
        "created":                random_date_in_past(730),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def generate_and_save(count: int = 10000):
    print(f"Generating {count:,} Retail applicants with unique names ...")
    retail_names = build_unique_retail_names(count)
    retail_list  = [generate_retail_applicant(i + 1, retail_names[i]) for i in range(count)]

    print(f"Generating {count:,} SME applicants with unique business names ...")
    sme_names = build_unique_sme_names(count)
    sme_list  = [generate_sme_applicant(i + 1, sme_names[i]) for i in range(count)]

    # ── JSON ────────────────────────────────────────────────────────────────
    with open("retail_applicants.json", "w", encoding="utf-8") as f:
        json.dump(retail_list, f, indent=2, ensure_ascii=False)
    with open("sme_applicants.json", "w", encoding="utf-8") as f:
        json.dump(sme_list, f, indent=2, ensure_ascii=False)

    # ── CSV ─────────────────────────────────────────────────────────────────
    retail_fields = [
        "id","application_id","name","full_name","pan","mobile","email","gender",
        "age","date_of_birth","cibil","cibil_score","monthly_income","loan_amt",
        "loan_amount_requested","tenure_months","existing_emi","type","loan_type",
        "city","employment_type","loan_purpose","indicative_rate","property_type","created",
    ]
    with open("retail_applicants.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=retail_fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(retail_list)

    sme_fields = [
        "id","application_id","name","business_name","pan","gstin","mobile","email",
        "promoter_name","promoter_cibil_score","cibil","annual_turnover","turnover",
        "loan_amt","loan_amount_requested","business_vintage_years","vintage",
        "type","loan_type","collateral","collateral_value","city","industry",
        "loan_purpose","created",
    ]
    with open("sme_applicants.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=sme_fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(sme_list)

    # ── Validation checks ───────────────────────────────────────────────────
    gstin_lengths = [len(r["gstin"]) for r in sme_list]
    assert all(l == 15 for l in gstin_lengths), "GSTIN length error!"

    pan_lengths_r = [len(r["pan"]) for r in retail_list]
    pan_lengths_s = [len(r["pan"]) for r in sme_list]
    assert all(l == 10 for l in pan_lengths_r + pan_lengths_s), "PAN length error!"

    retail_names_set = {r["name"] for r in retail_list}
    sme_names_set    = {r["name"] for r in sme_list}
    assert len(retail_names_set) == count, "Duplicate retail names found!"
    assert len(sme_names_set)    == count, "Duplicate SME names found!"

    # ── Summary ─────────────────────────────────────────────────────────────
    bengaluru_r = sum(1 for a in retail_list if a["city"] == "Bengaluru")
    bengaluru_s = sum(1 for a in sme_list   if a["city"] == "Bengaluru")

    print(f"\nDone!")
    print(f"  Retail : {len(retail_list):,} records  ({bengaluru_r:,} Bengaluru = {bengaluru_r*100//count}%)")
    print(f"  SME    : {len(sme_list):,} records  ({bengaluru_s:,} Bengaluru = {bengaluru_s*100//count}%)")
    print(f"\n  Files written:")
    print(f"    retail_applicants.json  ({len(retail_list):,} rows)")
    print(f"    sme_applicants.json     ({len(sme_list):,} rows)")
    print(f"    retail_applicants.csv   ({len(retail_list):,} rows)")
    print(f"    sme_applicants.csv      ({len(sme_list):,} rows)")
    print(f"\n  Validations passed:")
    print(f"    All PANs   = 10 chars  OK")
    print(f"    All GSTINs = 15 chars  OK")
    print(f"    All names unique       OK")


if __name__ == "__main__":
    generate_and_save(10000)
