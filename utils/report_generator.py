"""
HTML Report Generator
Generates a beautiful visual report including skill gap analysis
"""

import os
from datetime import datetime
from utils.logger import setup_logger

logger = setup_logger()


class ReportGenerator:
    def generate(self, all_jobs: list, results: list, score: int, skill_data: dict = None):
        os.makedirs("output", exist_ok=True)
        path = "output/report.html"

        platform_counts = {}
        for job in all_jobs:
            p = job.get("platform", "unknown")
            platform_counts[p] = platform_counts.get(p, 0) + 1

        colors = {
            "naukri": "#4A90D9",
            "internshala": "#E84393",
            "linkedin": "#0A66C2",
            "indeed": "#2164F3",
            "glassdoor": "#0CAA41",
            "wellfound": "#FB5B00",
            "remoteok": "#27AE60",
        }

        platform_badges = ""
        for platform, count in platform_counts.items():
            color = colors.get(platform, "#888")
            platform_badges += f'<span class="badge" style="background:{color}">{platform.capitalize()} ({count})</span>'

        # Job cards
        cards_html = ""
        for i, r in enumerate(results):
            match_score = r.get("match_score", 50)
            match_reason = r.get("match_reason", "")
            platform = r.get("platform", "")
            color = colors.get(platform, "#888")
            score_pct = int(match_score) if str(match_score).isdigit() else 50

            cards_html += f"""
            <div class="card">
                <div class="card-header">
                    <div>
                        <span class="badge" style="background:{color}">{platform.capitalize()}</span>
                        <h3>{r.get('title', 'N/A')}</h3>
                        <p class="company">🏢 {r.get('company', 'N/A')}</p>
                        <p class="location">📍 {r.get('location', 'N/A')}</p>
                    </div>
                    <div class="score-circle">{match_score}</div>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width:{score_pct}%;background:{color}"></div>
                </div>
                <p class="reason">🤖 {match_reason}</p>
                <div class="files">
                    <span>📄 resume_{i+1}.txt</span>
                    <span>✉️ cover_letter_{i+1}.txt</span>
                </div>
                <a href="{r.get('url', '#')}" target="_blank" class="apply-btn">View Job →</a>
            </div>"""

        # Skill gap section
        skill_html = ""
        if skill_data:
            missing = skill_data.get("candidate_missing", [])
            quick_wins = skill_data.get("quick_wins", [])
            roadmap = skill_data.get("roadmap", [])
            job_ready = skill_data.get("job_ready_score", 0)
            summary = skill_data.get("summary", "")
            market = skill_data.get("market_demand", [])

            missing_tags = "".join([f'<span class="gap-tag missing">{s}</span>' for s in missing])
            wins_tags = "".join([f'<span class="gap-tag win">⚡ {s}</span>' for s in quick_wins])

            market_bars = ""
            for item in market[:6]:
                freq = item.get("frequency", 50)
                priority = item.get("priority", "medium")
                p_color = {"critical": "#ef4444", "high": "#f97316", "medium": "#eab308"}.get(priority, "#888")
                market_bars += f"""
                <div class="market-item">
                    <div class="market-label">
                        <span>{item.get('skill')}</span>
                        <span style="color:{p_color};font-size:0.75rem">{priority.upper()}</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width:{freq}%;background:{p_color}"></div>
                    </div>
                </div>"""

            roadmap_html = ""
            for step in roadmap:
                roadmap_html += f"""
                <div class="roadmap-step">
                    <div class="week-badge">Week {step.get('week')}</div>
                    <div class="step-content">
                        <strong>{step.get('focus')}</strong>
                        <p>📚 {step.get('resource')}</p>
                    </div>
                </div>"""

            skill_html = f"""
            <div class="skill-section">
                <h2 class="section-title">🧠 AI Skill Gap Analysis</h2>
                <p class="skill-summary">"{summary}"</p>

                <div class="skill-grid">
                    <div class="skill-box">
                        <h4>📈 Market Demand</h4>
                        {market_bars}
                    </div>
                    <div class="skill-box">
                        <div class="ready-score">
                            <div class="ready-num">{job_ready}%</div>
                            <div class="ready-label">Job Ready Score</div>
                        </div>
                        <h4 style="margin:16px 0 8px">❌ Skills to Learn</h4>
                        <div class="gap-tags">{missing_tags}</div>
                        <h4 style="margin:16px 0 8px">⚡ Quick Wins (This Week)</h4>
                        <div class="gap-tags">{wins_tags}</div>
                    </div>
                </div>

                <h3 style="color:#fff;margin:32px 0 16px;text-align:center">📅 4-Week Learning Roadmap</h3>
                <div class="roadmap">{roadmap_html}</div>
            </div>"""

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Job Agent Report</title>
    <style>
        * {{ margin:0; padding:0; box-sizing:border-box; }}
        body {{ font-family:'Segoe UI',sans-serif; background:#0f0f1a; color:#e0e0e0; }}

        .header {{ background:linear-gradient(135deg,#1a1a2e,#16213e); padding:40px; text-align:center; border-bottom:1px solid #2a2a4a; }}
        .header h1 {{ font-size:2.5rem; color:#fff; margin-bottom:8px; }}
        .header p {{ color:#888; }}

        .stats {{ display:flex; justify-content:center; gap:24px; padding:32px 40px; flex-wrap:wrap; }}
        .stat-box {{ background:#1a1a2e; border:1px solid #2a2a4a; border-radius:12px; padding:24px 36px; text-align:center; min-width:160px; }}
        .stat-box .num {{ font-size:2.5rem; font-weight:700; color:#7c6af7; }}
        .stat-box .label {{ color:#888; font-size:0.85rem; margin-top:4px; }}

        .section-title {{ text-align:center; font-size:1.4rem; color:#fff; margin:8px 0 24px; }}
        .platforms {{ text-align:center; margin-bottom:32px; }}
        .badge {{ display:inline-block; padding:6px 16px; border-radius:20px; color:white; font-size:0.85rem; margin:4px; font-weight:600; }}

        .cards {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(340px,1fr)); gap:24px; padding:0 40px 40px; max-width:1200px; margin:0 auto; }}
        .card {{ background:#1a1a2e; border:1px solid #2a2a4a; border-radius:16px; padding:24px; transition:transform 0.2s; }}
        .card:hover {{ transform:translateY(-4px); border-color:#7c6af7; }}
        .card-header {{ display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:16px; }}
        .card h3 {{ font-size:1.1rem; color:#fff; margin:6px 0 4px; }}
        .card .company {{ color:#aaa; font-size:0.9rem; }}
        .card .location {{ color:#888; font-size:0.85rem; margin-top:2px; }}
        .score-circle {{ width:56px; height:56px; border-radius:50%; background:linear-gradient(135deg,#7c6af7,#a78bfa); display:flex; align-items:center; justify-content:center; font-weight:700; font-size:1rem; color:white; flex-shrink:0; margin-left:12px; }}
        .progress-bar {{ background:#2a2a4a; border-radius:4px; height:6px; margin:12px 0; }}
        .progress-fill {{ height:100%; border-radius:4px; }}
        .reason {{ color:#aaa; font-size:0.85rem; margin:8px 0 12px; line-height:1.4; }}
        .files {{ display:flex; gap:12px; margin:12px 0; flex-wrap:wrap; }}
        .files span {{ background:#0f0f1a; border:1px solid #2a2a4a; border-radius:6px; padding:4px 10px; font-size:0.8rem; color:#888; }}
        .apply-btn {{ display:inline-block; margin-top:8px; padding:8px 20px; background:linear-gradient(135deg,#7c6af7,#a78bfa); color:white; border-radius:8px; text-decoration:none; font-size:0.9rem; font-weight:600; }}

        .skill-section {{ max-width:1200px; margin:0 auto 40px; padding:0 40px; }}
        .skill-summary {{ text-align:center; color:#aaa; font-style:italic; margin-bottom:32px; font-size:1.05rem; }}
        .skill-grid {{ display:grid; grid-template-columns:1fr 1fr; gap:24px; }}
        .skill-box {{ background:#1a1a2e; border:1px solid #2a2a4a; border-radius:16px; padding:24px; }}
        .skill-box h4 {{ color:#fff; margin-bottom:16px; }}
        .market-item {{ margin-bottom:12px; }}
        .market-label {{ display:flex; justify-content:space-between; margin-bottom:4px; font-size:0.9rem; }}
        .ready-score {{ text-align:center; padding:24px; background:#0f0f1a; border-radius:12px; margin-bottom:8px; }}
        .ready-num {{ font-size:3rem; font-weight:700; color:#22c55e; }}
        .ready-label {{ color:#888; font-size:0.85rem; }}
        .gap-tags {{ display:flex; flex-wrap:wrap; gap:8px; }}
        .gap-tag {{ padding:6px 12px; border-radius:20px; font-size:0.8rem; font-weight:600; }}
        .gap-tag.missing {{ background:#ef444422; color:#ef4444; border:1px solid #ef444444; }}
        .gap-tag.win {{ background:#22c55e22; color:#22c55e; border:1px solid #22c55e44; }}

        .roadmap {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(240px,1fr)); gap:16px; }}
        .roadmap-step {{ background:#1a1a2e; border:1px solid #2a2a4a; border-radius:12px; padding:20px; }}
        .week-badge {{ background:linear-gradient(135deg,#7c6af7,#a78bfa); color:white; display:inline-block; padding:4px 12px; border-radius:20px; font-size:0.8rem; font-weight:700; margin-bottom:12px; }}
        .step-content strong {{ color:#fff; display:block; margin-bottom:6px; }}
        .step-content p {{ color:#888; font-size:0.85rem; }}

        .footer {{ text-align:center; padding:24px; color:#444; font-size:0.85rem; border-top:1px solid #2a2a4a; }}

        @media(max-width:768px) {{ .skill-grid {{ grid-template-columns:1fr; }} .cards {{ padding:0 16px 24px; }} }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 Job Agent Report</h1>
        <p>Generated on {datetime.now().strftime("%B %d, %Y at %I:%M %p")} &nbsp;|&nbsp; AI-Powered Job Matching</p>
    </div>

    <div class="stats">
        <div class="stat-box"><div class="num">{len(all_jobs)}</div><div class="label">Jobs Found</div></div>
        <div class="stat-box"><div class="num">{len(results)}</div><div class="label">Resumes Tailored</div></div>
        <div class="stat-box"><div class="num">{len(platform_counts)}</div><div class="label">Platforms Scraped</div></div>
        <div class="stat-box"><div class="num" style="color:#22c55e">{score}</div><div class="label">Agent Score / 10,000</div></div>
    </div>

    <div class="platforms">
        <h2 class="section-title">Platforms Scraped</h2>
        {platform_badges}
    </div>

    <h2 class="section-title">Top Matched Jobs</h2>
    <div class="cards">{cards_html}</div>

    {skill_html}

    <div class="footer">
        Built with Python · Groq llama-3.3-70b · Playwright · 4 Platforms · Job Application Automation Agent
    </div>
</body>
</html>"""

        with open(path, "w", encoding="utf-8") as f:
            f.write(html)

        logger.info(f"  ✅ HTML report saved to {path}")
        return path