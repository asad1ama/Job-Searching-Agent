import time
from utils.logger import setup_logger

logger = setup_logger()

class LinkedInScraper:
    def __init__(self, config: dict):
        self.config = config
        self.base_url = "https://www.linkedin.com"

    def scrape(self) -> list:
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            return self._get_sample_jobs()

        jobs = []
        role = self.config["target_role"].replace(" ", "%20")
        location = self.config["target_location"].replace(" ", "%20")
        url = f"https://www.linkedin.com/jobs/search/?keywords={role}&location={location}&f_E=1%2C2&sortBy=DD"
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

                # Scroll to load more jobs
                page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
                time.sleep(2)

                selectors = [
                    ".jobs-search__results-list li",
                    ".job-search-card",
                    "[class*='job-search-card']",
                    ".base-card",
                ]

                job_cards = []
                for sel in selectors:
                    job_cards = page.query_selector_all(sel)
                    if job_cards:
                        logger.info(f"  ✅ Matched selector: {sel}")
                        break

                logger.info(f"  📦 Found {len(job_cards)} job cards")

                for card in job_cards[:self.config.get("max_jobs_per_run", 10)]:
                    try:
                        job = self._parse_card(card)
                        if job:
                            jobs.append(job)
                    except Exception as e:
                        logger.debug(f"  ⚠️ Parse error: {e}")
                        continue

                browser.close()

        except Exception as e:
            logger.error(f"  ❌ LinkedIn scraping error: {e}")
            return self._get_sample_jobs()

        if not jobs:
            logger.warning("  ⚠️ No LinkedIn jobs parsed. Using sample data.")
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
            ".base-search-card__title",
            "h3.base-search-card__title",
            "[class*='job-title']",
            "h3", "h4"
        )
        company = safe_text(
            ".base-search-card__subtitle",
            "h4.base-search-card__subtitle",
            "[class*='company-name']"
        )
        location = safe_text(
            ".job-search-card__location",
            "[class*='job-search-card__location']",
            ".base-search-card__metadata"
        )
        url = safe_attr("a.base-card__full-link", "href") or safe_attr("a", "href")

        if not title:
            return None

        return {
            "platform": "linkedin",
            "title": title,
            "company": company or "Unknown Company",
            "location": location or self.config["target_location"],
            "experience": "0-2 years",
            "skills": self.config["target_role"],
            "description": f"{title} at {company}. Location: {location}.",
            "url": url or self.base_url,
        }

    def _get_sample_jobs(self) -> list:
        return [
            {
                "platform": "linkedin",
                "title": "Java Backend Developer",
                "company": "Infosys",
                "location": "Bangalore, India",
                "experience": "0-1 years",
                "skills": "Java, Spring Boot, Microservices, REST API",
                "description": "Entry level Java backend developer at Infosys. Work on enterprise microservices.",
                "url": "https://www.linkedin.com/jobs",
            },
            {
                "platform": "linkedin",
                "title": "Software Engineer - Full Stack",
                "company": "Wipro",
                "location": "Hyderabad, India",
                "experience": "Fresher",
                "skills": "Java, React, SQL, Spring Boot",
                "description": "Full stack software engineer role at Wipro for freshers with Java and React skills.",
                "url": "https://www.linkedin.com/jobs",
            },
        ]