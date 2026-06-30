import os
import re
import json
import sqlite3
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, jsonify, send_from_directory

try:
    import PyPDF2
except Exception:
    PyPDF2 = None

try:
    from docx import Document
except Exception:
    Document = None


app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
DB_PATH = os.path.join(BASE_DIR, "memoryverse.db")

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024

ALLOWED_EXTENSIONS = {"pdf", "docx", "txt", "png", "jpg", "jpeg", "webp"}


SKILL_LIBRARY = {
    "Python": ["python"],
    "Java": ["java"],
    "C": [" c programming", " c language", "programming in c"],
    "C++": ["c++"],
    "HTML": ["html"],
    "CSS": ["css"],
    "JavaScript": ["javascript", "js"],
    "React": ["react", "reactjs"],
    "Node.js": ["node", "node.js", "nodejs"],
    "Express.js": ["express", "express.js"],
    "Flask": ["flask"],
    "Django": ["django"],
    "SQLite": ["sqlite"],
    "MySQL": ["mysql"],
    "MongoDB": ["mongodb"],
    "GitHub": ["github"],
    "Git": [" git ", "git version"],
    "AI": [" ai ", "artificial intelligence"],
    "Machine Learning": ["machine learning", " ml "],
    "Data Science": ["data science"],
    "NLP": ["nlp", "natural language processing"],
    "RAG": ["rag", "retrieval augmented generation"],
    "Embeddings": ["embedding", "embeddings"],
    "Semantic Search": ["semantic search"],
    "Full Stack": ["full stack", "fullstack"],
    "Frontend": ["frontend", "front end", "ui", "ux"],
    "Backend": ["backend", "back end", "server"],
    "Database": ["database", "dbms"],
    "Portfolio": ["portfolio"],
    "Resume Building": ["resume", "cv"],
    "Document Intelligence": ["document", "identity", "knowledge repository", "digital journey", "retrieval"],
    "Communication": ["communication"],
    "Leadership": ["leader", "leadership", "club lead"],
    "Problem Solving": ["problem solving", "logic", "algorithm"],
}


CATEGORY_KEYWORDS = {
    "Resume": ["resume", "cv", "curriculum vitae"],
    "Certification": ["certificate", "certification", "certified", "course completion"],
    "Internship": ["internship", "intern", "offer letter", "joining letter", "company", "training"],
    "Project": ["project", "repository", "system", "website", "application", "app", "report"],
    "Achievement": ["achievement", "award", "winner", "prize", "rank", "badge", "selected", "participation"],
    "Academics": ["marksheet", "degree", "college", "university", "semester", "academic", "bsc", "mca"],
    "Portfolio": ["portfolio", "linkedin", "github", "github profile", "personal website"],
}


def connect_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            year TEXT,
            category TEXT,
            description TEXT,
            skills TEXT,
            career_path TEXT,
            summary TEXT,
            file_name TEXT,
            original_name TEXT,
            link TEXT,
            upload_date TEXT
        )
    """)

    conn.commit()
    conn.close()

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
init_db()


def allowed_file(filename):
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in ALLOWED_EXTENSIONS


def clean_text(text):
    if not text:
        return ""
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_text_from_file(file_path):
    if not file_path:
        return ""

    ext = file_path.rsplit(".", 1)[-1].lower()

    try:
        if ext == "txt":
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return clean_text(f.read())

        if ext == "pdf" and PyPDF2:
            text = ""
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    page_text = page.extract_text() or ""
                    text += " " + page_text
            return clean_text(text)

        if ext == "docx" and Document:
            doc = Document(file_path)
            text = " ".join([p.text for p in doc.paragraphs])
            return clean_text(text)

    except Exception:
        return ""

    return ""


def detect_category(text, manual_type="Auto Detect"):
    text_lower = f" {text.lower()} "
    scores = {}

    for category, keywords in CATEGORY_KEYWORDS.items():
        score = 0
        for keyword in keywords:
            if keyword in text_lower:
                score += 2
        scores[category] = score

    if manual_type and manual_type != "Auto Detect":
        scores[manual_type] = scores.get(manual_type, 0) + 1

    best_category = max(scores, key=scores.get)

    if scores[best_category] == 0:
        return "Academics"

    return best_category


def extract_skills(text):
    text_lower = f" {text.lower()} "
    found = []

    for skill, keywords in SKILL_LIBRARY.items():
        for keyword in keywords:
            if keyword.lower() in text_lower:
                found.append(skill)
                break

    unique_skills = []
    for skill in found:
        if skill not in unique_skills:
            unique_skills.append(skill)

    return unique_skills


def generate_career_path(skills, category):
    skills_set = set(skills)

    if {"HTML", "CSS", "JavaScript"} & skills_set and {"Flask", "React", "Node.js", "SQLite", "MySQL"} & skills_set:
        return "Full Stack Developer"

    if {"HTML", "CSS", "JavaScript", "Frontend"} & skills_set:
        return "Frontend Developer"

    if {"Python", "Flask", "Django", "Backend", "Database"} & skills_set:
        return "Backend Developer"

    if {"AI", "Machine Learning", "Data Science", "NLP", "RAG", "Embeddings", "Semantic Search"} & skills_set:
        return "AI/ML Developer"

    if {"Python", "Java", "C", "C++", "Problem Solving"} & skills_set:
        return "Software Developer"

    if category == "Internship":
        return "Professional Experience"

    if category == "Certification":
        return "Skill Development"

    if category == "Academics":
        return "Academic Growth"

    if category == "Achievement":
        return "Career Showcase"

    return "Student Digital Identity"


def generate_summary(title, category, skills, description):
    skills_text = ", ".join(skills[:6]) if skills else "general academic and professional skills"

    if category == "Project":
        return f"{title} is a project record connected with {skills_text}."
    if category == "Certification":
        return f"{title} is a certification that supports skills like {skills_text}."
    if category == "Internship":
        return f"{title} represents internship or professional experience connected with {skills_text}."
    if category == "Resume":
        return f"{title} is a resume document representing career profile and skills."
    if category == "Portfolio":
        return f"{title} is a portfolio or profile link showcasing work and achievements."
    if category == "Achievement":
        return f"{title} is an achievement record connected with {skills_text}."
    if category == "Academics":
        return f"{title} represents academic progress and learning journey."

    short_desc = description[:120] + "..." if description and len(description) > 120 else description
    return short_desc or f"{title} is part of the student's digital identity journey."


def row_to_dict(row):
    data = dict(row)

    try:
        data["skills"] = json.loads(data.get("skills") or "[]")
    except Exception:
        data["skills"] = []

    if data.get("file_name"):
        data["file_url"] = f"/uploads/{data['file_name']}"
    else:
        data["file_url"] = ""

    return data


def get_all_documents():
    conn = connect_db()
    rows = conn.execute("SELECT * FROM documents ORDER BY id DESC").fetchall()
    conn.close()
    return [row_to_dict(row) for row in rows]


def build_relationships(docs):
    relationships = []

    for doc in docs:
        title = doc["title"]
        category = doc["category"]
        skills = doc["skills"]
        career = doc["career_path"]

        for skill in skills[:5]:
            if category == "Certification":
                relationships.append({
                    "from": title,
                    "to": f"{skill} Skill",
                    "type": "Certification → Skill"
                })

            if category == "Project":
                relationships.append({
                    "from": f"{skill} Skill",
                    "to": title,
                    "type": "Skill → Project"
                })

            if category == "Internship":
                relationships.append({
                    "from": title,
                    "to": f"{skill} Skill",
                    "type": "Internship → Skill"
                })

            if category == "Portfolio":
                relationships.append({
                    "from": f"{skill} Skill",
                    "to": title,
                    "type": "Skill → Portfolio"
                })

        if category == "Project":
            relationships.append({
                "from": title,
                "to": career,
                "type": "Project → Career Path"
            })

        if category == "Internship":
            relationships.append({
                "from": title,
                "to": career,
                "type": "Internship → Career Path"
            })

        if category == "Achievement":
            relationships.append({
                "from": title,
                "to": career,
                "type": "Achievement → Career Showcase"
            })

    projects = [d for d in docs if d["category"] == "Project"]
    internships = [d for d in docs if d["category"] == "Internship"]
    certifications = [d for d in docs if d["category"] == "Certification"]

    for cert in certifications:
        cert_skills = set(cert["skills"])
        for project in projects:
            project_skills = set(project["skills"])
            if cert_skills & project_skills:
                relationships.append({
                    "from": cert["title"],
                    "to": project["title"],
                    "type": "Certification → Project"
                })

    for project in projects:
        project_skills = set(project["skills"])
        for internship in internships:
            internship_skills = set(internship["skills"])
            if project_skills & internship_skills:
                relationships.append({
                    "from": project["title"],
                    "to": internship["title"],
                    "type": "Project → Internship"
                })

    unique = []
    seen = set()

    for rel in relationships:
        key = (rel["from"], rel["to"], rel["type"])
        if key not in seen:
            seen.add(key)
            unique.append(rel)

    return unique[:50]


def score_document_for_query(doc, query):
    q = query.lower()
    score = 0

    text = " ".join([
        doc.get("title") or "",
        doc.get("category") or "",
        doc.get("description") or "",
        " ".join(doc.get("skills") or []),
        doc.get("career_path") or "",
        doc.get("summary") or "",
        doc.get("link") or "",
        doc.get("year") or "",
    ]).lower()

    query_tokens = re.findall(r"[a-zA-Z0-9+#.]+", q)

    for token in query_tokens:
        if token in text:
            score += 2

    if q in text:
        score += 5

    category_aliases = {
        "certificate": "Certification",
        "certificates": "Certification",
        "certification": "Certification",
        "internship": "Internship",
        "internships": "Internship",
        "resume": "Resume",
        "cv": "Resume",
        "project": "Project",
        "projects": "Project",
        "achievement": "Achievement",
        "achievements": "Achievement",
        "academics": "Academics",
        "academic": "Academics",
        "portfolio": "Portfolio",
    }

    for word, category in category_aliases.items():
        if word in q and doc.get("category") == category:
            score += 10

    if "github" in q:
        if doc.get("category") in ["Portfolio", "Project"]:
            score += 10
        if "GitHub" in doc.get("skills", []):
            score += 8

    if "latest" in q or "recent" in q:
        score += 1

    if "full stack" in q or "fullstack" in q:
        if "Full Stack" in doc.get("skills", []) or doc.get("career_path") == "Full Stack Developer":
            score += 12
        if {"HTML", "CSS", "JavaScript"} & set(doc.get("skills", [])):
            score += 5

    if "ai" in q or "machine learning" in q or "ml" in q:
        if {"AI", "Machine Learning", "NLP", "RAG", "Embeddings", "Semantic Search"} & set(doc.get("skills", [])):
            score += 12

    if "journey" in q or "growth" in q:
        score += 2

    return score


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


@app.route("/api/dashboard")
def dashboard():
    docs = get_all_documents()

    total_docs = len(docs)
    total_projects = len([d for d in docs if d["category"] == "Project"])
    total_certifications = len([d for d in docs if d["category"] == "Certification"])
    total_internships = len([d for d in docs if d["category"] == "Internship"])
    total_resumes = len([d for d in docs if d["category"] == "Resume"])

    all_skills = set()
    for doc in docs:
        for skill in doc["skills"]:
            all_skills.add(skill)

    return jsonify({
        "total_docs": total_docs,
        "total_projects": total_projects,
        "total_certifications": total_certifications,
        "total_internships": total_internships,
        "total_resumes": total_resumes,
        "total_skills": len(all_skills),
    })


@app.route("/api/documents")
def documents():
    return jsonify(get_all_documents())


@app.route("/api/upload", methods=["POST"])
def upload_document():
    title = request.form.get("title", "").strip()
    year = request.form.get("year", "").strip()
    manual_type = request.form.get("doc_type", "Auto Detect").strip()
    description = request.form.get("description", "").strip()
    link = request.form.get("link", "").strip()

    if not title:
        return jsonify({"success": False, "message": "Title is required."}), 400

    file = request.files.get("document_file")
    file_name = ""
    original_name = ""
    extracted_text = ""

    if file and file.filename:
        if not allowed_file(file.filename):
            return jsonify({"success": False, "message": "File type not supported."}), 400

        original_name = file.filename
        safe_name = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        file_name = f"{timestamp}_{safe_name}"
        save_path = os.path.join(app.config["UPLOAD_FOLDER"], file_name)
        file.save(save_path)

        extracted_text = extract_text_from_file(save_path)

    combined_text = " ".join([
        title,
        description,
        original_name,
        link,
        extracted_text
    ])

    category = detect_category(combined_text, manual_type)
    skills = extract_skills(combined_text)
    career_path = generate_career_path(skills, category)
    summary = generate_summary(title, category, skills, description)

    conn = connect_db()
    conn.execute("""
        INSERT INTO documents
        (title, year, category, description, skills, career_path, summary, file_name, original_name, link, upload_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        title,
        year,
        category,
        description,
        json.dumps(skills),
        career_path,
        summary,
        file_name,
        original_name,
        link,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": "Document uploaded and analyzed successfully.",
        "category": category,
        "skills": skills,
        "career_path": career_path
    })


@app.route("/api/delete/<int:doc_id>", methods=["DELETE"])
def delete_document(doc_id):
    conn = connect_db()
    row = conn.execute("SELECT * FROM documents WHERE id = ?", (doc_id,)).fetchone()

    if not row:
        conn.close()
        return jsonify({"success": False, "message": "Document not found."}), 404

    file_name = row["file_name"]

    conn.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
    conn.commit()
    conn.close()

    if file_name:
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], file_name)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass

    return jsonify({"success": True, "message": "Document deleted."})


@app.route("/api/timeline")
def timeline():
    docs = get_all_documents()

    timeline_items = []
    for doc in docs:
        timeline_items.append({
            "year": doc["year"] or "Unknown",
            "title": doc["title"],
            "category": doc["category"],
            "summary": doc["summary"],
            "skills": doc["skills"]
        })

    timeline_items.sort(key=lambda x: x["year"], reverse=True)
    return jsonify(timeline_items)


@app.route("/api/relationships")
def relationships():
    docs = get_all_documents()
    return jsonify(build_relationships(docs))


@app.route("/api/search")
def smart_search():
    query = request.args.get("q", "").strip()

    if not query:
        return jsonify({
            "answer": "Type something like: show my certificates, show my AI projects, show latest resume, show GitHub records, or show my full stack journey.",
            "results": []
        })

    docs = get_all_documents()

    scored_docs = []
    for doc in docs:
        score = score_document_for_query(doc, query)
        if score > 0:
            scored_docs.append((score, doc))

    scored_docs.sort(key=lambda x: x[0], reverse=True)
    results = [doc for score, doc in scored_docs[:8]]

    q = query.lower()

    if not results:
        answer = "I could not find an exact match. Try uploading more documents or search with words like certificate, internship, project, resume, AI, GitHub, or full stack."
    elif "full stack" in q or "fullstack" in q:
        skills = set()
        for doc in results:
            for skill in doc["skills"]:
                skills.add(skill)
        answer = f"Your full stack journey includes {len(results)} connected record(s). Key skills found: {', '.join(list(skills)[:8])}."
    elif "latest" in q and ("resume" in q or "cv" in q):
        resume_docs = [d for d in results if d["category"] == "Resume"]
        if resume_docs:
            results = resume_docs[:3]
            answer = f"I found your latest resume-related document: {resume_docs[0]['title']}."
        else:
            answer = "I found related records, but no resume document is uploaded yet."
    elif "certificate" in q or "certification" in q:
        answer = f"I found {len(results)} certificate-related record(s)."
    elif "internship" in q:
        answer = f"I found {len(results)} internship-related record(s)."
    elif "project" in q:
        answer = f"I found {len(results)} project-related record(s)."
    elif "github" in q:
        answer = f"I found {len(results)} GitHub or portfolio-related record(s)."
    elif "ai" in q or "ml" in q or "machine learning" in q:
        answer = f"I found {len(results)} AI/ML-related record(s)."
    else:
        answer = f"I found {len(results)} relevant record(s) from your digital identity repository."

    return jsonify({
        "answer": answer,
        "results": results
    })


@app.route("/api/demo-data", methods=["POST"])
def demo_data():
    samples = [
        {
            "title": "Latest Student Resume",
            "year": "2026",
            "category": "Resume",
            "description": "A latest resume containing education, technical skills, project experience, certifications, GitHub profile, and career objective.",
            "skills": ["Python", "Java", "HTML", "CSS", "JavaScript", "GitHub", "Resume Building"],
            "career_path": "Software Developer",
            "summary": "Latest resume representing the student's academic profile, technical skills, and career journey.",
            "link": ""
        },
        {
            "title": "Python Programming Certificate",
            "year": "2023",
            "category": "Certification",
            "description": "A certificate for completing Python programming with logic building, problem solving, loops, functions, and basic software development.",
            "skills": ["Python", "Problem Solving"],
            "career_path": "Software Developer",
            "summary": "Python certification connected with programming, logic building, and problem-solving skills.",
            "link": ""
        },
        {
            "title": "Full Stack Web Development Certificate",
            "year": "2024",
            "category": "Certification",
            "description": "A certificate showing learning records in HTML, CSS, JavaScript, frontend design, backend basics, and database concepts.",
            "skills": ["HTML", "CSS", "JavaScript", "Frontend", "Backend", "Database", "Full Stack"],
            "career_path": "Full Stack Developer",
            "summary": "Full stack certification connected with frontend, backend, and web development skills.",
            "link": ""
        },
        {
            "title": "Student Digital Portfolio",
            "year": "2025",
            "category": "Portfolio",
            "description": "A personal portfolio that showcases academic details, skills, certificates, project links, achievements, and GitHub repositories.",
            "skills": ["HTML", "CSS", "JavaScript", "Portfolio", "GitHub", "Frontend"],
            "career_path": "Frontend Developer",
            "summary": "Portfolio record that represents the student's digital identity and project showcase.",
            "link": "https://github.com/"
        },
        {
            "title": "Smart Career Path Recommendation Project",
            "year": "2026",
            "category": "Project",
            "description": "An AI-based project report that analyzes student skills, certifications, achievements, and projects to suggest suitable career paths.",
            "skills": ["AI", "Machine Learning", "NLP", "Python", "Semantic Search", "Data Science"],
            "career_path": "AI/ML Developer",
            "summary": "AI project connected with student skill analysis, career recommendation, and intelligent knowledge retrieval.",
            "link": "https://github.com/"
        },
        {
            "title": "Web Development Internship Letter",
            "year": "2026",
            "category": "Internship",
            "description": "An internship letter showing practical experience in frontend development, backend concepts, teamwork, GitHub workflow, and project documentation.",
            "skills": ["Full Stack", "Frontend", "Backend", "HTML", "CSS", "JavaScript", "GitHub", "Communication"],
            "career_path": "Professional Experience",
            "summary": "Internship record showing practical web development and professional learning experience.",
            "link": ""
        },
        {
            "title": "MCA Semester Academic Record",
            "year": "2026",
            "category": "Academics",
            "description": "Academic record containing MCA semester subjects, marks, learning progress, and university performance details.",
            "skills": ["Database", "Java", "Problem Solving", "Communication"],
            "career_path": "Student Digital Identity",
            "summary": "Academic record representing the student's educational progress and learning journey.",
            "link": ""
        },
        {
            "title": "Hackathon Participation Achievement",
            "year": "2026",
            "category": "Achievement",
            "description": "Achievement record for participating in a technology hackathon and building a working prototype with documentation and demo video.",
            "skills": ["Problem Solving", "Frontend", "GitHub", "Communication", "Leadership"],
            "career_path": "Software Developer",
            "summary": "Hackathon achievement connected with project building, problem solving, and technical presentation skills.",
            "link": ""
        },
        {
            "title": "GitHub Learning Repository",
            "year": "2026",
            "category": "Portfolio",
            "description": "GitHub repository containing learning projects, source code, README files, project documentation, and technical progress records.",
            "skills": ["GitHub", "Git", "Python", "JavaScript", "Portfolio", "Problem Solving"],
            "career_path": "Software Developer",
            "summary": "GitHub repository that preserves source code, learning records, and project growth.",
            "link": "https://github.com/"
        },
        {
            "title": "MemoryVerse AI System Report",
            "year": "2026",
            "category": "Project",
            "description": "Project report for an AI-powered digital identity system using document ingestion, intelligent categorization, skill extraction, relationship mapping, timeline generation, and smart retrieval.",
            "skills": ["AI", "NLP", "RAG", "Embeddings", "Semantic Search", "Python", "Flask", "SQLite"],
            "career_path": "AI/ML Developer",
            "summary": "MemoryVerse AI project report explaining how scattered student documents become a structured and searchable digital identity.",
            "link": "https://github.com/"
        }
    ]

    conn = connect_db()

    inserted = 0
    for sample in samples:
        existing = conn.execute(
            "SELECT id FROM documents WHERE title = ?",
            (sample["title"],)
        ).fetchone()

        if existing:
            continue

        conn.execute("""
            INSERT INTO documents
            (title, year, category, description, skills, career_path, summary, file_name, original_name, link, upload_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            sample["title"],
            sample["year"],
            sample["category"],
            sample["description"],
            json.dumps(sample["skills"]),
            sample["career_path"],
            sample["summary"],
            "",
            "",
            sample["link"],
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        inserted += 1

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": f"{inserted} student journey demo records added successfully."
    })


if __name__ == "__main__":
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)