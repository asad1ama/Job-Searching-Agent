import time
from utils.logger import setup_logger

logger = setup_logger()

class NaukriScraper:
    def __init__(self, config: dict):
        self.config = config
        self.base_url = "https://www.naukri.com"

    def scrape(self) -> list:
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            logger.error("❌ Playwright not installed.")
            return self._get_sample_jobs()

        jobs = []
        role = self.config["target_role"].lower().replace(" ", "-")
        location = self.config["target_location"].lower().replace(" ", "-")
        url = f"{self.base_url}/{role}-jobs-in-{location}"
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

                with open("output/naukri_debug.html", "w", encoding="utf-8") as f:
                    f.write(page.content())
                logger.info("  📄 Saved debug HTML to output/naukri_debug.html")

                # Try multiple selectors
                selectors = [
                    "article.jobTuple",
                    ".jobTupleHeader",
                    "[class*='jobTuple']",
                    ".job-post",
                    "[class*='srp-jobtuple']",
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
                        job = self._parse_card(card, page)
                        if job:
                            jobs.append(job)
                    except Exception as e:
                        logger.debug(f"  ⚠️ Card parse error: {e}")
                        continue

                browser.close()

        except Exception as e:
            logger.error(f"  ❌ Naukri scraping error: {e}")
            return self._get_sample_jobs()

        if not jobs:
            logger.warning("  ⚠️ No jobs parsed. Using sample data.")
            return self._get_sample_jobs()

        return jobs

    def _parse_card(self, card, page) -> dict:
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
            ".title", ".jobTitle", "[class*='title']",
            "a.title", "h2", "h3"
        )
        company = safe_text(
            ".subTitle", ".companyName", "[class*='company']",
            "[class*='comp-name']"
        )
        location = safe_text(
            ".location", ".loc", "[class*='location']",
            "[class*='loc-link']"
        )
        experience = safe_text(
            ".experience", ".exp", "[class*='experience']"
        )
        salary = safe_text(
            ".salary", ".sal", "[class*='salary']"
        )
        skills_els = card.query_selector_all(".tag, [class*='tag'], .skill")
        skills = ", ".join([s.inner_text().strip() for s in skills_els if s.inner_text().strip()])

        url = safe_attr("a.title", "href") or safe_attr("a", "href")
        if url and not url.startswith("http"):
            url = self.base_url + url

        if not title:
            return None

        return {
            "platform": "naukri",
            "title": title,
            "company": company or "Unknown Company",
            "location": location or self.config["target_location"],
            "experience": experience,
            "salary": salary,
            "skills": skills,
            "description": f"{title} at {company}. Location: {location}. Experience: {experience}. Skills: {skills}",
            "url": url or self.base_url,
        }

    def _get_sample_jobs(self) -> list:
        return [
            {
                "platform": "naukri",
                "title": "Java Backend Developer",
                "company": "TechCorp India",
                "location": "Bangalore",
                "experience": "0-1 years",
                "skills": "Java, Spring Boot, REST API, MySQL",
                "description": "Looking for a fresher Java backend developer with Spring Boot and MySQL skills.",
                "url": "https://www.naukri.com",
            },
            {
                "platform": "naukri",
                "title": "Full Stack Developer Intern",
                "company": "StartupXYZ",
                "location": "Remote",
                "experience": "0 years",
                "skills": "React, Node.js, MongoDB, Git",
                "description": "Full stack intern needed. React, Node.js, MongoDB. Build real products from day 1.",
                "url": "https://www.naukri.com",
            },
        ]