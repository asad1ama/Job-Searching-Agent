# Quest Submission - FDE / APO Position

**Candidate:** Asad Amanullah  
**Agent:** Job Application Automation Agent  
**GitHub:** https://github.com/asad1ama/Job-Searching-Agent

---

## ✅ Requirement 1 — Build Your Own Agent

Full pipeline agent built in Python:
- Scrapes 7 platforms (Indian + Global)
- AI ranks jobs by resume fit
- Tailors resume per job
- Generates cover letter per company
- Runs skill gap analysis
- Sends Telegram notification
- Tracks in Google Sheets
- Generates HTML dashboard
- Runs on daily schedule

---

## ✅ Requirement 2 — Cursor-Based Setup

`.cursorrules` included in root with:
- Project purpose and architecture
- Tech stack explanation
- Folder structure
- Coding conventions
- Run commands
- How to add new scrapers

Open in Cursor → AI understands full codebase instantly.

---

## ✅ Requirement 3 — Security

- All secrets in `.env` (gitignored)
- `.env.example` has placeholders only
- `config/google_creds.json` gitignored
- `config/resume.txt` gitignored
- `output/` gitignored
- Zero secrets in any source file

Verify: `grep -r "sk-\|AIza" .` returns nothing.

---

## ✅ Requirement 4 — Performance Metrics

**Agent Score: 8,000 / 10,000**

### Scoring Formula
Score = A + B + C + D + E
A = Jobs Found      (max 2,000) = jobs_found × 200 [capped at 10]
B = Ranking Quality (max 3,000) = (avg_match_score / 100) × 3,000
C = Resume Tailoring(max 3,000) = (tailored / total) × 3,000
D = Speed Bonus     (max 1,000) = 1,000 if <60s | 500 if <120s
E = Platform Spread (max 1,000) = 500 × unique_platforms

### Sample Run Calculation

| Component | Value | Score |
|---|---|---|
| Jobs Found | 46 jobs | 2,000/2,000 |
| Ranking Quality | avg 75/100 | 2,250/3,000 |
| Resume Tailoring | 5/5 tailored | 3,000/3,000 |
| Speed | 90 seconds | 500/1,000 |
| Platforms | 7 platforms | 1,000/1,000 |
| **TOTAL** | | **8,000/10,000** |

### Why This Formula

Each component measures a real verifiable output:
- **Jobs Found** — did the scraper actually work?
- **Ranking Quality** — did AI produce useful relevance signals?
- **Tailoring** — did every job get a custom resume?
- **Speed** — is this faster than a human?
- **Diversity** — does it search more than one source?

---

## ✅ Requirement 5 — Benchmark Comparison

### This Agent vs Default Cursor/Claude

| Capability | Default Cursor/Claude | This Agent |
|---|---|---|
| Scrape live jobs | ❌ Cannot access web | ✅ 7 platforms automated |
| Rank jobs by resume fit | ❌ Manual copy-paste | ✅ Groq AI auto-ranks |
| Tailor resume per job | ❌ One at a time manually | ✅ Batch — all top 5 |
| Generate cover letters | ❌ Manually trigger each | ✅ Auto per company |
| Skill gap analysis | ❌ Not possible | ✅ AI powered roadmap |
| Phone notifications | ❌ Not possible | ✅ Telegram bot |
| Daily auto-scheduler | ❌ Not possible | ✅ Runs at 8am daily |
| Track applications | ❌ No memory | ✅ Google Sheets + JSON |
| Indian platforms | ❌ None | ✅ Naukri + Internshala |
| Global platforms | ❌ None | ✅ LinkedIn, Indeed, Glassdoor, Wellfound, RemoteOK |
| Time per job | 15-30 minutes | < 2 minutes |
| **Performance Score** | **0 / 10,000** | **8,000 / 10,000** |

### Concrete Example

**Default Cursor workflow for 10 jobs:**
Human opens Naukri → copies job 1 → pastes into Cursor
→ asks for resume tailoring → copies result → opens resume doc
→ pastes manually → repeats 9 more times
Total time: 3-4 hours. Zero tracking. No cover letters. No skill analysis.

**This Agent workflow for 10 jobs:**
python main.py
→ Scrapes 46 jobs from 7 platforms automatically
→ AI ranks all by resume fit in one Groq call
→ Tailors resume for top 5, generates 5 cover letters
→ Runs skill gap analysis across all 46 jobs
→ Saves HTML report + JSON + txt files
→ Sends results to phone via Telegram
Total time: ~90 seconds. Full tracking. Ready to apply.

---

## ✅ Requirement 6 — Problem Specialization

### Problem: Job Hunting for Freshers is Broken

**What the agent specializes in:**
End-to-end automation of the job application pipeline for freshers
targeting both Indian and global tech job platforms.

### Why I Chose This Problem

I am the target user. As a fresher targeting Full Stack and Java
Backend Developer roles, I was spending 2-3 hours per day on:

1. Manually checking 7 different job sites every morning
2. Sending the same generic resume everywhere → low callback rate
3. Never writing cover letters → too time consuming
4. Losing track of where I applied after 20+ applications
5. No idea which skills employers actually want right now

This is not a hypothetical problem. It is my current #1 blocker
between where I am and getting hired.

### Why This is My #1 Priority

The return on solving this is asymmetric:
- Input: 1 week of building
- Output: Every future job search is 95% automated forever

This is exactly the Priority Definition Ability the hiring post
describes. A talent who identifies the highest-leverage problem
and executes on it fast creates disproportionate value.

I proved this by:
- Building a 7-platform scraper in days
- Adding AI ranking, tailoring, skill gap analysis
- Making it fully autonomous with Telegram + scheduler
- Scoring 8000/10,000 vs 0 for default Cursor

Additionally this problem generalizes — same agent works for
any candidate, any role, any geography by changing one .env file.
That is product thinking, not just engineering.

### Impact Measurement
- Before agent: 2-3 hours/day job hunting manually
- After agent: 90 seconds/day, fully automated
- Time saved: ~95% reduction
- Quality: Every application has tailored resume + cover letter

---

## ✅ Requirement 7 — Documentation

Full documentation in README.md including:
- Problem statement and motivation
- Complete pipeline explanation
- Setup guide (install → configure → run)
- Performance score formula
- Benchmark table
- Folder structure with every file explained
- How to add new platforms
- Security notes
- Design decisions
- Screenshots of terminal, report, output, Telegram

### Design Decisions

| Decision | Reason |
|---|---|
| Groq over OpenAI | Free tier, fast inference |
| Playwright over APIs | Naukri/Internshala have no public API |
| 7 platforms | Cover both Indian + global job markets |
| JSON fallback | Agent runs without Google Sheets setup |
| Sample data fallback | Scraper failures don't kill the whole run |
| Telegram bot | True autonomous agent — zero human input needed |
| Scheduler | Wakes up, finds jobs, notifies — no human trigger |
| Per-platform location | Indian sites search India, global sites worldwide |
| `.cursorrules` | Cursor understands full codebase instantly |

### Usage Examples

**Basic run:**
```bash
python main.py
```

**Change target role:**
TARGET_ROLE=AI Engineer

**Change location:**
TARGET_LOCATION=Singapore

**Run on schedule:**
```bash
python scheduler.py
```

**Output files:**
output/
├── report.html                    ← Visual dashboard
├── jobs_results.json              ← All results + skill analysis
├── 1_CompanyName_resume.txt       ← Tailored resume
└── 1_CompanyName_cover_letter.txt ← Cover letter