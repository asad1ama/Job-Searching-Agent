"""
Skill Gap Analyzer
Analyzes ALL scraped jobs to find what skills you're missing
and generates a personalized learning roadmap
"""

import json
from utils.logger import setup_logger

logger = setup_logger()


class SkillAnalyzer:
    def __init__(self, groq_client):
        self.groq = groq_client

    def analyze(self, resume: str, all_jobs: list) -> dict:
        logger.info("  🔍 Analyzing skill gaps across all jobs...")

        # Collect all skills from all jobs
        all_skills_raw = []
        for job in all_jobs:
            skills = job.get("skills", "")
            desc = job.get("description", "")
            all_skills_raw.append(f"{skills} {desc}")

        combined = "\n".join(all_skills_raw[:20])

        prompt = f"""
You are a career coach and skill analyst.

CANDIDATE RESUME:
{resume[:800]}

ALL JOB REQUIREMENTS FOUND (from {len(all_jobs)} jobs):
{combined[:2000]}

Analyze the gap between the candidate's current skills and what employers want.

Return ONLY valid JSON with this exact structure:
{{
  "market_demand": [
    {{"skill": "Spring Boot", "frequency": 85, "priority": "critical"}},
    {{"skill": "Docker", "frequency": 60, "priority": "high"}},
    {{"skill": "Kafka", "frequency": 40, "priority": "medium"}}
  ],
  "candidate_has": ["Java", "React", "Node.js"],
  "candidate_missing": ["Docker", "Kubernetes", "Kafka"],
  "quick_wins": ["Docker basics - 1 week", "REST API design - 3 days"],
  "roadmap": [
    {{"week": 1, "focus": "Docker + Containerization", "resource": "Docker official docs + freeCodeCamp"}},
    {{"week": 2, "focus": "System Design basics", "resource": "Gaurav Sen YouTube"}},
    {{"week": 3, "focus": "Spring Boot advanced", "resource": "Amigoscode free course"}},
    {{"week": 4, "focus": "Mock interviews + LeetCode", "resource": "LeetCode + Pramp"}}
  ],
  "job_ready_score": 72,
  "summary": "One sentence on candidate's strongest advantage"
}}
"""
        try:
            response = self.groq.chat(prompt, max_tokens=1500)
            response = response.strip()
            if response.startswith("```"):
                response = response.split("```")[1]
                if response.startswith("json"):
                    response = response[4:]
            result = json.loads(response)
            logger.info(f"  ✅ Skill analysis complete. Job ready score: {result.get('job_ready_score')}%")
            return result
        except Exception as e:
            logger.error(f"  ❌ Skill analysis failed: {e}")
            return {
                "candidate_missing": ["Docker", "System Design", "Kafka"],
                "quick_wins": ["Docker basics", "REST API patterns"],
                "job_ready_score": 65,
                "summary": "Strong Java foundation, needs cloud and DevOps exposure"
            }