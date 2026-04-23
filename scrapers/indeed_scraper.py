import time
from utils.logger import setup_logger

logger = setup_logger()

class IndeedScraper:
    def __init__(self, config: dict):
        self.config = config
        self.base_url = "https://in.indeed.com"

    def scrape(self) -> list:
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            return self._get_sample_jobs()

        jobs = []
        role = self.config["target_role"].replace(" ", "+")
        location = self.config["target_location"].replace(" ", "+")
        url = f"{self.base_url}/jobs?q={role}&l={location}&fromage=7"
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

                selectors = [
                    ".job_seen_beacon",
                    ".jobsearch-ResultsList li",
                    "[class*='job_seen_beacon']",
                    ".tapItem",
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
            logger.error(f"  ❌ Indeed scraping error: {e}")
            return self._get_sample_jobs()

        if not jobs:
            logger.warning("  ⚠️ No Indeed jobs parsed. Using sample data.")
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
            ".jobTitle span",
            "h2.jobTitle",
            "[class*='jobTitle']",
            "h2", "h3"
        )
        company = safe_text(
            "[data-testid='company-name']",
            ".companyName",
            "[class*='companyName']"
        )
        location = safe_text(
            "[data-testid='text-location']",
            ".companyLocation",
            "[class*='location']"
        )
        salary = safe_text(
            "[data-testid='attribute_snippet_testid']",
            ".salary-snippet",
            "[class*='salary']"
        )

        link = card.query_selector("h2.jobTitle a") or card.query_selector("a")
        job_id = link.get_attribute("data-jk") if link else ""
        url = f"{self.base_url}/viewjob?jk={job_id}" if job_id else self.base_url

        if not title:
            return None

        return {
            "platform": "indeed",
            "title": title,
            "company": company or "Unknown Company",
            "location": location or self.config["target_location"],
            "salary": salary,
            "experience": "0-2 years",
            "skills": self.config["target_role"],
            "description": f"{title} at {company}. Location: {location}. Salary: {salary}",
            "url": url,
        }

    def _get_sample_jobs(self) -> list:
        return [
            {
                "platform": "indeed",
                "title": "Java Developer Fresher",
                "company": "HCL Technologies",
                "location": "Noida, India",
                "experience": "0-1 years",
                "skills": "Java, Spring, Hibernate, SQL",
                "description": "Java developer fresher role at HCL. Work on enterprise Java applications.",
                "url": "https://in.indeed.com",
            },
            {
                "platform": "indeed",
                "title": "Backend Engineer",
                "company": "Tech Mahindra",
                "location": "Pune, India",
                "experience": "Fresher",
                "skills": "Java, REST API, MySQL, Git",
                "description": "Backend engineer at Tech Mahindra for freshers with Java skills.",
                "url": "https://in.indeed.com",
            },
        ]