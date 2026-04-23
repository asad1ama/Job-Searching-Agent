import json
import os
from utils.logger import setup_logger
from utils.groq_client import GroqClient
from scrapers.naukri_scraper import NaukriScraper
from scrapers.internshala_scraper import IntershalaScraper
from scrapers.linkedin_scraper import LinkedInScraper
from scrapers.indeed_scraper import IndeedScraper
from scrapers.glassdoor_scraper import GlassdoorScraper
from scrapers.wellfound_scraper import WellfoundScraper
from scrapers.remoteok_scraper import RemoteOKScraper
from utils.resume_tailor import ResumeTailor
from utils.scorer import AgentScorer
from utils.report_generator import ReportGenerator
from utils.skill_analyzer import SkillAnalyzer

logger = setup_logger()


class JobAgent:
    def __init__(self, config: dict, groq_api_key: str):
        self.config = config
        self.groq = GroqClient(groq_api_key)
        self.tailor = ResumeTailor(self.groq)
        self.scorer = AgentScorer()
        self.reporter = ReportGenerator()
        self.skill_analyzer = SkillAnalyzer(self.groq)
        self.resume = self._load_resume(config["resume_path"])

        # Telegram (optional)
        tg_token = os.getenv("TELEGRAM_BOT_TOKEN")
        tg_chat = os.getenv("TELEGRAM_CHAT_ID")
        self.telegram = None
        if tg_token and tg_chat:
            from utils.telegram_bot import TelegramBot
            self.telegram = TelegramBot(tg_token, tg_chat)
            logger.info("📱 Telegram notifications enabled")

        self.scrapers = {
            "naukri": NaukriScraper,
            "internshala": IntershalaScraper,
            "linkedin": LinkedInScraper,
            "indeed": IndeedScraper,
            "glassdoor": GlassdoorScraper,
            "wellfound": WellfoundScraper,
            "remoteok": RemoteOKScraper,
        }

    def _load_resume(self, path: str) -> str:
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            logger.warning(f"⚠️ Resume not found at {path}.")
            return "Fresher with skills in Java, Spring Boot, React, Node.js, SQL."

    def run(self):
        logger.info("=" * 60)
        logger.info("🚀 Agent Pipeline Starting")
        logger.info("=" * 60)

        all_jobs = []

        # Step 1: Scrape all platforms
        for platform in self.config["platforms"]:
            platform = platform.strip()
            if platform not in self.scrapers:
                logger.warning(f"⚠️ Unknown platform: {platform}")
                continue
            logger.info(f"\n📡 Scraping {platform.upper()}...")
            scraper = self.scrapers[platform](self.config)
            try:
                jobs = scraper.scrape()
                logger.info(f"✅ Found {len(jobs)} jobs on {platform}")
                all_jobs.extend(jobs)
            except Exception as e:
                logger.error(f"❌ Scraping failed for {platform}: {e}")

        if not all_jobs:
            logger.warning("⚠️ No jobs found.")
            return

        # Remove duplicates
        seen = set()
        unique_jobs = []
        for job in all_jobs:
            key = f"{job.get('title','').lower()}_{job.get('company','').lower()}"
            if key not in seen:
                seen.add(key)
                unique_jobs.append(job)
        all_jobs = unique_jobs
        logger.info(f"\n📊 Total unique jobs: {len(all_jobs)}")

        # Step 2: AI Rank
        logger.info("\n🧠 Ranking jobs with AI...")
        ranked_jobs = self._rank_jobs(all_jobs)

        # Step 3: Tailor top 5
        logger.info(f"\n✍️ Tailoring resumes for top 5 jobs...")
        results = []
        for i, job in enumerate(ranked_jobs[:5]):
            logger.info(f"\n[{i+1}] {job['title']} at {job['company']}")
            tailored = self.tailor.tailor_resume(self.resume, job)
            cover_letter = self.tailor.generate_cover_letter(self.resume, job)
            result = {
                **job,
                "tailored_resume": tailored,
                "cover_letter": cover_letter,
                "status": "ready_to_apply"
            }
            results.append(result)
            self._save_output(result, i + 1)

        # Step 4: Skill Gap Analysis
        logger.info("\n🧠 Running skill gap analysis...")
        skill_data = self.skill_analyzer.analyze(self.resume, all_jobs)

        # Step 5: Save JSON
        self._save_json(results, skill_data)

        # Step 6: Score + HTML Report
        logger.info("\n📊 Generating HTML report...")
        score = self.scorer.calculate_score(all_jobs, ranked_jobs, results)
        report_path = self.reporter.generate(all_jobs, results, score, skill_data)
        logger.info(f"🌐 Report: {report_path}")

        # Step 7: Telegram notification
        if self.telegram:
            logger.info("\n📱 Sending Telegram notification...")
            self.telegram.send_job_summary(all_jobs, results, score, skill_data)

        logger.info(f"\n{'='*60}")
        logger.info(f"🏆 Agent Performance Score: {score}/10,000")
        logger.info(f"{'='*60}")
        logger.info("\n✅ Done! Open output/report.html to see results.")

    def _rank_jobs(self, jobs: list) -> list:
        # Only send top 10 to avoid token overflow
        jobs_to_rank = jobs[:10]

        # Clean jobs to remove long descriptions before sending
        clean_jobs = []
        for j in jobs_to_rank:
            clean_jobs.append({
                "title": j.get("title", ""),
                "company": j.get("company", ""),
                "location": j.get("location", ""),
                "platform": j.get("platform", ""),
                "skills": j.get("skills", "")[:100],
                "description": j.get("description", "")[:150],
            })

        prompt = f"""Rank these jobs for this candidate.

CANDIDATE: {self.config['target_role']}, {self.config['experience_level']}
SKILLS: {self.resume[:300]}

JOBS:
{json.dumps(clean_jobs, indent=2)}

Return ONLY a valid JSON array. Add match_score (0-100) and match_reason (max 10 words) to each job. No extra text, no markdown."""

        try:
            response = self.groq.chat(prompt, max_tokens=1500)
            response = response.strip()
            if "```" in response:
                response = response.split("```")[1]
                if response.startswith("json"):
                    response = response[4:]
            response = response.strip()
            ranked_small = json.loads(response)

            # Merge match scores back into full job objects
            score_map = {}
            for r in ranked_small:
                key = f"{r.get('title','').lower()}_{r.get('company','').lower()}"
                score_map[key] = {
                    "match_score": r.get("match_score", 50),
                    "match_reason": r.get("match_reason", ""),
                }

            for job in jobs:
                key = f"{job.get('title','').lower()}_{job.get('company','').lower()}"
                if key in score_map:
                    job["match_score"] = score_map[key]["match_score"]
                    job["match_reason"] = score_map[key]["match_reason"]
                else:
                    job["match_score"] = 40
                    job["match_reason"] = "Not in top ranked set"

            # Sort all jobs by match_score
            jobs.sort(key=lambda x: x.get("match_score", 0), reverse=True)
            return jobs

        except Exception as e:
            logger.error(f"❌ AI ranking failed: {e}. Using original order.")
            return jobs

    def _save_output(self, result: dict, index: int):
        os.makedirs("output", exist_ok=True)
        safe_company = result["company"].replace(" ", "_").replace("/", "_")
        base = f"output/{index}_{safe_company}"
        with open(f"{base}_resume.txt", "w", encoding="utf-8") as f:
            f.write(result["tailored_resume"])
        with open(f"{base}_cover_letter.txt", "w", encoding="utf-8") as f:
            f.write(result["cover_letter"])
        logger.info(f"💾 Saved: {base}")

    def _save_json(self, results: list, skill_data: dict = None):
        os.makedirs("output", exist_ok=True)
        summary = []
        for r in results:
            summary.append({
                "title": r.get("title"),
                "company": r.get("company"),
                "location": r.get("location"),
                "url": r.get("url"),
                "match_score": r.get("match_score"),
                "match_reason": r.get("match_reason"),
                "status": r.get("status"),
            })
        output = {"jobs": summary, "skill_analysis": skill_data}
        with open("output/jobs_results.json", "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2)
        logger.info("💾 Results saved to output/jobs_results.json")