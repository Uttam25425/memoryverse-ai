# MemoryVerse AI – Intelligent Digital Identity System

MemoryVerse AI is an AI-powered digital identity system for students. It helps students upload resumes, certificates, internship letters, project reports, portfolio links, GitHub repositories, achievements, and academic records in one place.

The system automatically organizes uploaded information into categories such as Projects, Certifications, Internships, Achievements, Academics, Resume, and Portfolio. It also extracts skills, builds relationships between documents, creates a digital journey timeline, and allows users to retrieve information using natural language search.

## Problem Statement

Students collect many important documents during their academic and professional journey, but these files are usually scattered across folders, emails, cloud drives, and devices. Traditional storage platforms can store files, but they do not understand a student’s growth, skills, achievements, and career journey.

MemoryVerse AI solves this problem by converting scattered documents into a structured, searchable, and intelligent digital identity repository.

## Key Features

* Upload resumes, certificates, internship letters, project reports, portfolio links, and academic documents
* Automatic document categorization
* Skill extraction from title, description, and document text
* Relationship engine connecting certificates, skills, projects, internships, and career paths
* Digital journey timeline
* Smart natural language search
* Original file access in the same format
* Dashboard with total documents, projects, certifications, internships, resumes, and skills
* SQLite database for local storage

## Modules Covered

### Module 1: AI Data Ingestion

Users can upload academic and professional documents or add portfolio/GitHub links.

### Module 2: Intelligent Categorization

The system automatically classifies uploaded information into meaningful categories.

### Module 3: Relationship Engine

The system connects related information such as:

Certification → Skill
Skill → Project
Project → Internship
Internship → Career Path

### Module 4: Digital Journey Timeline

The system generates a timeline that represents the student’s growth and achievements.

### Module 5: Smart Retrieval System

Users can search naturally, such as:

* Show all my certificates
* Show my AI projects
* Show internship documents
* Show my latest resume
* Show my full stack journey

## Tech Stack

Frontend: HTML, CSS, JavaScript
Backend: Python Flask
Database: SQLite
File Storage: Local uploads folder
AI/NLP Logic: Keyword extraction, rule-based categorization, relationship mapping, and semantic-style search scoring

## AI/ML Approach

This prototype uses NLP-inspired keyword extraction, intelligent categorization, semantic-style search scoring, and relationship mapping. The system is designed in a way that can be extended with embeddings, vector databases, and RAG-based retrieval in the future.

## How to Run

1. Clone the repository or download the project folder.

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the Flask app:

```bash
python app.py
```

4. Open in browser:

```text
http://127.0.0.1:5000
```

5. Click on “Load Demo Data” to test the project.

## Demo Search Examples

```text
Show all my certificates
Show my AI projects
Show internship documents
Show my latest resume
Show my full stack journey
```

## Project Goal

The goal of MemoryVerse AI is to make students say:

“I never have to search through folders again.”

## Future Improvements

* Add real embeddings for better semantic search
* Add vector database support using FAISS or ChromaDB
* Add OCR for image-based certificates
* Add RAG-based AI answering
* Add graph-based relationship visualization
* Add user login and cloud storage
