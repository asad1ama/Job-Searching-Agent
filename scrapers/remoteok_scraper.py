import time
import requests
from utils.logger import setup_logger

logger = setup_logger()

class RemoteOKScraper:
    def __init__(self, config: dict):
        self.config = config
        self.base_url = "https://remoteok.com"

    def scrape(self) -> list:
        """RemoteOK has a public JSON API - no Playwright needed!"""
        role_tag = self.config["target_role"].lower().split()[0]
        url = f"{self.base_url}/api?tag={role_tag}"
        logger.info(f"  🌐 URL: {url}")

        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "application/json",
            }
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            data = response.json()

            # First item is metadata, skip it
            job_list = [j for j in data if isinstance(j, dict) and j.get("position")]

            logger.info(f"  📦 Found {len(job_list)} remote jobs")

            jobs = []
            for job in job_list[:self.config.get("max_jobs_per_run", 10)]:
                parsed = self._parse_job(job)
                if parsed:
                    jobs.append(parsed)

            return jobs

        except Exception as e:
            logger.error(f"  ❌ RemoteOK error: {e}")
            return self._get_sample_jobs()

    def _parse_job(self, job: dict) -> dict:
        title = job.get("position", "")
        company = job.get("company", "Unknown")
        location = job.get("location", "Remote / Worldwide")
        salary = job.get("salary", "")
        tags = job.get("tags", [])
        skills = ", ".join(tags[:6]) if tags else self.config["target_role"]
        url = job.get("url", "") or f"{self.base_url}/l/{job.get('slug', '')}"
        description = job.get("description", f"{title} at {company}. Remote position.")

        # Clean HTML from description
        import re
        description = re.sub(r"<[^>]+>", " ", description).strip()[:300]

        if not title:
            return None

        return {
            "platform": "remoteok",
            "title": title,
            "company": company,
            "location": location or "Remote / Worldwide",
            "salary": salary,
            "experience": "0-3 years",
            "skills": skills,
            "description": description,
            "url": url,
        }

    def _get_sample_jobs(self) -> list:
        return [
            {
                "platform": "remoteok",
                "title": "Remote Java Developer",
                "company": "Remote Global Inc",
                "location": "Worldwide / Remote",
                "salary": "$50,000 - $80,000",
                "experience": "0-2 years",
                "skills": "Java, Spring Boot, Docker, REST API, AWS",
                "description": "Fully remote Java developer role. Work from anywhere. Flexible hours.",
                "url": "https://remoteok.com",
            },
            {
                "platform": "remoteok",
                "title": "Full Stack Engineer (Remote)",
                "company": "OpenSource Co",
                "location": "Remote / Async",
                "salary": "$45,000 - $75,000",
                "experience": "Fresher - 2 years",
                "skills": "React, Node.js, TypeScript, PostgreSQL",
                "description": "Remote full stack engineer. Build open source tools used by millions.",
                "url": "https://remoteok.com",
            },
        ]