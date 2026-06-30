const uploadForm = document.getElementById("uploadForm");
const uploadResult = document.getElementById("uploadResult");
const documentGrid = document.getElementById("documentGrid");
const relationshipGrid = document.getElementById("relationshipGrid");
const timelineList = document.getElementById("timelineList");
const searchInput = document.getElementById("searchInput");
const searchBtn = document.getElementById("searchBtn");
const answerCard = document.getElementById("answerCard");
const searchResults = document.getElementById("searchResults");
const loadDemoBtn = document.getElementById("loadDemoBtn");
const toast = document.getElementById("toast");

function escapeHTML(value) {
    if (!value) return "";
    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

function showToast(message) {
    toast.textContent = message;
    toast.classList.add("show");

    setTimeout(() => {
        toast.classList.remove("show");
    }, 2600);
}

function skillChips(skills) {
    if (!skills || skills.length === 0) {
        return `<span class="skill-chip">No skill detected</span>`;
    }

    return skills
        .map(skill => `<span class="skill-chip">${escapeHTML(skill)}</span>`)
        .join("");
}

async function loadDashboard() {
    const res = await fetch("/api/dashboard");
    const data = await res.json();

    document.getElementById("totalDocs").textContent = data.total_docs;
    document.getElementById("totalProjects").textContent = data.total_projects;
    document.getElementById("totalCertifications").textContent = data.total_certifications;
    document.getElementById("totalInternships").textContent = data.total_internships;
    document.getElementById("totalResumes").textContent = data.total_resumes;
    document.getElementById("totalSkills").textContent = data.total_skills;
}

async function loadDocuments() {
    const res = await fetch("/api/documents");
    const docs = await res.json();

    if (!docs.length) {
        documentGrid.innerHTML = `
            <div class="empty-state">
                No documents uploaded yet. Upload your resume, certificate, project report or click “Load Demo Data”.
            </div>
        `;
        return;
    }

    documentGrid.innerHTML = docs.map(doc => {
        const fileButton = doc.file_url
            ? `<a class="small-btn" href="${escapeHTML(doc.file_url)}" target="_blank">Open File</a>`
            : "";

        const linkButton = doc.link
            ? `<a class="small-btn" href="${escapeHTML(doc.link)}" target="_blank">Open Link</a>`
            : "";

        return `
            <div class="doc-card">
                <div class="doc-top">
                    <span class="category-badge">${escapeHTML(doc.category)}</span>
                    <span class="doc-meta">${escapeHTML(doc.year || "No Year")}</span>
                </div>

                <h3>${escapeHTML(doc.title)}</h3>

                <div class="doc-meta">
                    Career Path: ${escapeHTML(doc.career_path || "Not detected")}
                </div>

                <p class="doc-summary">${escapeHTML(doc.summary || doc.description || "No summary available.")}</p>

                <div class="skill-list">
                    ${skillChips(doc.skills)}
                </div>

                <div class="doc-actions">
                    ${fileButton}
                    ${linkButton}
                    <button class="small-btn danger" onclick="deleteDocument(${doc.id})">Delete</button>
                </div>
            </div>
        `;
    }).join("");
}

async function loadTimeline() {
    const res = await fetch("/api/timeline");
    const items = await res.json();

    if (!items.length) {
        timelineList.innerHTML = `
            <div class="empty-state">
                Timeline will appear after uploading documents.
            </div>
        `;
        return;
    }

    timelineList.innerHTML = items.map(item => `
        <div class="timeline-item">
            <div class="timeline-year">${escapeHTML(item.year)}</div>
            <h3>${escapeHTML(item.title)}</h3>
            <p>${escapeHTML(item.summary)}</p>
            <div class="skill-list">
                <span class="category-badge">${escapeHTML(item.category)}</span>
                ${skillChips(item.skills)}
            </div>
        </div>
    `).join("");
}

async function loadRelationships() {
    const res = await fetch("/api/relationships");
    const rels = await res.json();

    if (!rels.length) {
        relationshipGrid.innerHTML = `
            <div class="empty-state">
                Relationship map will appear after uploading certificates, skills, projects and internships.
            </div>
        `;
        return;
    }

    relationshipGrid.innerHTML = rels.map(rel => `
        <div class="relation-card">
            <div class="relation-type">${escapeHTML(rel.type)}</div>
            <div class="relation-line">
                <span class="relation-node">${escapeHTML(rel.from)}</span>
                <span class="arrow">→</span>
                <span class="relation-node">${escapeHTML(rel.to)}</span>
            </div>
        </div>
    `).join("");
}

async function refreshAll() {
    await loadDashboard();
    await loadDocuments();
    await loadTimeline();
    await loadRelationships();
}

uploadForm.addEventListener("submit", async function (e) {
    e.preventDefault();

    const formData = new FormData(uploadForm);

    uploadResult.classList.add("hidden");
    uploadResult.innerHTML = "";

    try {
        const res = await fetch("/api/upload", {
            method: "POST",
            body: formData
        });

        const data = await res.json();

        if (!data.success) {
            showToast(data.message || "Upload failed.");
            return;
        }

        uploadResult.classList.remove("hidden");
        uploadResult.innerHTML = `
            <strong>${escapeHTML(data.message)}</strong><br>
            Category: ${escapeHTML(data.category)}<br>
            Skills: ${escapeHTML(data.skills.join(", ") || "No skill detected")}<br>
            Career Path: ${escapeHTML(data.career_path)}
        `;

        uploadForm.reset();
        showToast("Document analyzed successfully.");
        await refreshAll();

    } catch (error) {
        showToast("Something went wrong while uploading.");
    }
});

async function deleteDocument(id) {
    const confirmDelete = confirm("Do you want to delete this document?");
    if (!confirmDelete) return;

    const res = await fetch(`/api/delete/${id}`, {
        method: "DELETE"
    });

    const data = await res.json();
    showToast(data.message || "Deleted.");
    await refreshAll();
}

async function runSearch(queryText = "") {
    const query = queryText || searchInput.value.trim();

    if (!query) {
        showToast("Please type something to search.");
        return;
    }

    searchInput.value = query;

    const res = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
    const data = await res.json();

    answerCard.innerHTML = `
        <span>AI Answer</span>
        <p>${escapeHTML(data.answer)}</p>
    `;

    if (!data.results.length) {
        searchResults.innerHTML = `
            <div class="empty-state">
                No matching records found.
            </div>
        `;
        return;
    }

    searchResults.innerHTML = data.results.map(doc => {
        const fileButton = doc.file_url
            ? `<a class="small-btn" href="${escapeHTML(doc.file_url)}" target="_blank">Open File</a>`
            : "";

        const linkButton = doc.link
            ? `<a class="small-btn" href="${escapeHTML(doc.link)}" target="_blank">Open Link</a>`
            : "";

        return `
            <div class="result-card">
                <span class="category-badge">${escapeHTML(doc.category)}</span>
                <h3>${escapeHTML(doc.title)}</h3>
                <p class="doc-summary">${escapeHTML(doc.summary)}</p>
                <div class="skill-list">${skillChips(doc.skills)}</div>
                <div class="doc-actions">
                    ${fileButton}
                    ${linkButton}
                </div>
            </div>
        `;
    }).join("");
}

searchBtn.addEventListener("click", () => runSearch());

searchInput.addEventListener("keydown", function (e) {
    if (e.key === "Enter") {
        runSearch();
    }
});

document.querySelectorAll(".quick-search button").forEach(btn => {
    btn.addEventListener("click", () => {
        runSearch(btn.dataset.query);
    });
});

loadDemoBtn.addEventListener("click", async function () {
    const res = await fetch("/api/demo-data", {
        method: "POST"
    });

    const data = await res.json();
    showToast(data.message || "Demo data loaded.");
    await refreshAll();
});

refreshAll();
const documentFileInput = document.getElementById("documentFile");
const fileNameText = document.getElementById("fileNameText");

if (documentFileInput && fileNameText) {
    documentFileInput.addEventListener("change", function () {
        if (this.files && this.files.length > 0) {
            fileNameText.textContent = "Selected: " + this.files[0].name;
        } else {
            fileNameText.textContent = "PDF, DOCX, TXT, PNG, JPG supported";
        }
    });
}

