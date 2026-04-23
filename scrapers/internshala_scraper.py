import time
from utils.logger import setup_logger

logger = setup_logger()

class IntershalaScraper:
    def __init__(self, config: dict):
        self.config = config
        self.base_url = "https://internshala.com"

    def scrape(self) -> list:
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            logger.error("❌ Playwright not installed.")
            return self._get_sample_jobs()

        jobs = []
        role_slug = self.config["target_role"].lower().replace(" ", "-")
        url = f"{self.base_url}/jobs/{role_slug}-jobs"
        logger.info(f"  🌐 URL: {url}")

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True, args=["--ignore-certificate-errors"])
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                )
                page = context.new_page()
                page.goto(url, timeout=30000)
                time.sleep(3)

                cards = page.query_selector_all(".job-internship-card")
                if not cards:
                    cards = page.query_selector_all("[class*='internship_meta']")

                logger.info(f"  📦 Found {len(cards)} listings")

                for card in cards[:self.config.get("max_jobs_per_run", 10)]:
                    try:
                        job = self._parse_card(card)
                        if job:
                            jobs.append(job)
                    except Exception as e:
                        logger.debug(f"  ⚠️ Parse error: {e}")
                        continue

                browser.close()

        except Exception as e:
            logger.error(f"  ❌ Internshala error: {e}")
            return self._get_sample_jobs()

        if not jobs:
            logger.warning("  ⚠️ No jobs parsed. Using sample data.")
            return self._get_sample_jobs()

        return jobs

    def _parse_card(self, card) -> dict:
        def safe_text(sel):
            el = card.query_selector(sel)
            return el.inner_text().strip() if el else ""

        title = safe_text(".job-internship-name") or safe_text("h3")
        company = safe_text(".company-name") or safe_text("[class*='company']")
        location = safe_text(".location-names") or safe_text("[class*='location']")
        stipend = safe_text(".stipend") or safe_text("[class*='stipend']")

        link_el = card.query_selector("a")
        url = link_el.get_attribute("href") if link_el else ""
        if url and not url.startswith("http"):
            url = self.base_url + url

        if not title:
            return None

        return {
            "platform": "internshala",
            "title": title,
            "company": company or "Unknown",
            "location": location or "Remote",
            "experience": "0 years (fresher)",
            "stipend": stipend,
            "skills": self.config["target_role"],
            "description": f"{title} at {company}. Location: {location}. Stipend: {stipend}",
            "url": url or self.base_url,
        }

    def _get_sample_jobs(self) -> list:
        return [
            {
                "platform": "internshala",
                "title": "Java Developer Intern",
                "company": "InnovateTech",
                "location": "Work from Home",
                "experience": "0 years",
                "stipend": "₹15,000/month",
                "skills": "Java, Spring Boot, Git",
                "description": "Java developer intern needed. Learn and build real backend services using Spring Boot.",
                "url": "https://internshala.com/sample",
            },
            {
                "platform": "internshala",
                "title": "Full Stack Web Developer",
                "company": "Digital Agency Co",
                "location": "Delhi",
                "experience": "0-6 months",
                "stipend": "₹10,000/month",
                "skills": "HTML, CSS, JavaScript, React, Node.js",
                "description": "Build full stack web apps. React frontend, Node.js backend.",
                "url": "https://internshala.com/sample2",
            },
        ]