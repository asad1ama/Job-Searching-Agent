import time
from utils.logger import setup_logger

logger = setup_logger()

class WellfoundScraper:
    def __init__(self, config: dict):
        self.config = config
        self.base_url = "https://wellfound.com"

    def scrape(self) -> list:
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            return self._get_sample_jobs()

        jobs = []
        role = self.config["target_role"].replace(" ", "-").lower()
        url = f"{self.base_url}/role/{role}"
        logger.info(f"  🌐 URL: {url}")

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True, args=["--ignore-certificate-errors"])
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    viewport={"width": 1280, "height": 800},
                )
                page = context.new_page()
                page.goto(url, timeout=30000, wait_until="domcontentloaded")
                time.sleep(4)

                page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
                time.sleep(2)

                selectors = [
                    "[class*='JobListing']",
                    "[data-test='StartupResult']",
                    ".styles_component__ucLFM",
                    "[class*='styles_jobResult']",
                ]

                job_cards = []
                for sel in selectors:
                    job_cards = page.query_selector_all(sel)
                    if job_cards:
                        logger.info(f"  ✅ Matched: {sel}")
                        break

                logger.info(f"  📦 Found {len(job_cards)} cards")

                for card in job_cards[:self.config.get("max_jobs_per_run", 10)]:
                    try:
                        job = self._parse_card(card)
                        if job:
                            jobs.append(job)
                    except Exception as e:
                        logger.debug(f"  ⚠️ Parse error: {e}")

                browser.close()

        except Exception as e:
            logger.error(f"  ❌ Wellfound error: {e}")
            return self._get_sample_jobs()

        if not jobs:
            logger.warning("  ⚠️ No Wellfound jobs. Using sample data.")
            return self._get_sample_jobs()

        return jobs

    def _parse_card(self, card) -> dict:
        def safe_text(*selectors):
            for sel in selectors:
                el = card.query_selector(sel)
                if el:
                    text = el.inner_text().strip()
                    if text:
                        return text
            return ""

        def safe_attr(selector, attr):
            el = card.query_selector(selector)
            return el.get_attribute(attr) if el else ""

        title = safe_text(
            "[class*='title']", "[class*='jobTitle']",
            "h2", "h3", "a"
        )
        company = safe_text(
            "[class*='startupName']", "[class*='company']",
            "[class*='startup']"
        )
        location = safe_text(
            "[class*='location']", "[class*='remote']"
        )
        compensation = safe_text(
            "[class*='compensation']", "[class*='salary']"
        )
        url = safe_attr("a", "href")
        if url and not url.startswith("http"):
            url = self.base_url + url

        if not title:
            return None

        return {
            "platform": "wellfound",
            "title": title,
            "company": company or "Startup",
            "location": location or "Remote / Global",
            "salary": compensation,
            "experience": "0-3 years",
            "skills": self.config["target_role"],
            "description": f"{title} at {company} startup. {location}. Compensation: {compensation}",
            "url": url or self.base_url,
        }

    def _get_sample_jobs(self) -> list:
        return [
            {
                "platform": "wellfound",
                "title": "Backend Engineer",
                "company": "FinTech Startup",
                "location": "Remote / Worldwide",
                "salary": "$60,000 - $90,000",
                "experience": "0-2 years",
                "skills": "Java, Node.js, PostgreSQL, Docker, AWS",
                "description": "Backend engineer at fast-growing fintech startup. Full remote, equity offered.",
                "url": "https://wellfound.com",
            },
            {
                "platform": "wellfound",
                "title": "Full Stack Developer",
                "company": "AI SaaS Startup",
                "location": "Remote / Asia preferred",
                "salary": "$40,000 - $70,000",
                "experience": "Fresher welcome",
                "skills": "React, Node.js, Python, MongoDB, REST APIs",
                "description": "Full stack developer at AI SaaS startup. Remote-first, fast growth.",
                "url": "https://wellfound.com",
            },
        ]