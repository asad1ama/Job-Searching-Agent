import time
from utils.logger import setup_logger

logger = setup_logger()

class GlassdoorScraper:
    def __init__(self, config: dict):
        self.config = config
        self.base_url = "https://www.glassdoor.com"

    def scrape(self) -> list:
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            return self._get_sample_jobs()

        jobs = []
        role = self.config["target_role"].replace(" ", "-").lower()
        url = f"{self.base_url}/Job/{role}-jobs-SRCH_KO0,{len(role)}.htm"
        logger.info(f"  🌐 URL: {url}")

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True,args=["--ignore-certificate-errors"])
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    viewport={"width": 1280, "height": 800},
                )
                page = context.new_page()
                page.goto(url, timeout=30000, wait_until="domcontentloaded")
                time.sleep(4)

                selectors = [
                    "[data-test='jobListing']",
                    ".JobsList_jobListItem__JBBUV",
                    "[class*='JobsList_jobListItem']",
                    "li[class*='JobsList']",
                ]

                job_cards = []
                for sel in selectors:
                    job_cards = page.query_selector_all(sel)
                    if job_cards:
                        logger.info(f"  ✅ Matched: {sel}")
                        break

                logger.info(f"  📦 Found {len(job_cards)} job cards")

                for card in job_cards[:self.config.get("max_jobs_per_run", 10)]:
                    try:
                        job = self._parse_card(card)
                        if job:
                            jobs.append(job)
                    except Exception as e:
                        logger.debug(f"  ⚠️ Parse error: {e}")

                browser.close()

        except Exception as e:
            logger.error(f"  ❌ Glassdoor error: {e}")
            return self._get_sample_jobs()

        if not jobs:
            logger.warning("  ⚠️ No Glassdoor jobs parsed. Using sample data.")
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
            "[data-test='job-title']",
            ".JobCard_jobTitle__GLyJ1",
            "[class*='jobTitle']",
            "a[class*='JobCard']",
            "h3", "h2"
        )
        company = safe_text(
            "[data-test='employer-name']",
            ".EmployerProfile_compactEmployerName__9MGcV",
            "[class*='EmployerProfile']",
            "[class*='employer']"
        )
        location = safe_text(
            "[data-test='emp-location']",
            ".JobCard_location__Ds1fM",
            "[class*='location']"
        )
        salary = safe_text(
            "[data-test='detailSalary']",
            "[class*='salary']"
        )
        url = safe_attr("a[data-test='job-title']", "href") or safe_attr("a", "href")
        if url and not url.startswith("http"):
            url = self.base_url + url

        if not title:
            return None

        return {
            "platform": "glassdoor",
            "title": title,
            "company": company or "Unknown",
            "location": location or "Global / Remote",
            "salary": salary,
            "experience": "0-2 years",
            "skills": self.config["target_role"],
            "description": f"{title} at {company}. Location: {location}. Salary: {salary}",
            "url": url or self.base_url,
        }

    def _get_sample_jobs(self) -> list:
        return [
            {
                "platform": "glassdoor",
                "title": "Java Backend Engineer",
                "company": "Google",
                "location": "Remote / Global",
                "salary": "$80,000 - $120,000",
                "experience": "0-2 years",
                "skills": "Java, Spring Boot, Distributed Systems, GCP",
                "description": "Java backend engineer at Google. Build scalable distributed systems.",
                "url": "https://www.glassdoor.com",
            },
            {
                "platform": "glassdoor",
                "title": "Software Engineer - Backend",
                "company": "Microsoft",
                "location": "Hyderabad, India / Remote",
                "salary": "₹20,00,000 - ₹35,00,000",
                "experience": "Fresher - 2 years",
                "skills": "Java, C#, Azure, REST APIs, SQL",
                "description": "Backend software engineer at Microsoft India. Work on Azure cloud services.",
                "url": "https://www.glassdoor.com",
            },
        ]