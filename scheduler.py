"""
Agent Scheduler
Runs the job agent automatically every morning at 8am
No human input needed - true autonomous agent
"""

import os
import time
import schedule
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from agent.job_agent import JobAgent
from utils.logger import setup_logger

logger = setup_logger()


def run_agent():
    logger.info(f"\n⏰ Scheduled run started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        logger.error("❌ GROQ_API_KEY not found.")
        return

    config = {
        "target_role": os.getenv("TARGET_ROLE", "Java Backend Developer"),
        "target_location": os.getenv("TARGET_LOCATION", "India"),
        "experience_level": os.getenv("EXPERIENCE_LEVEL", "fresher"),
        "resume_path": os.getenv("RESUME_PATH", "config/resume.txt"),
        "max_jobs_per_run": int(os.getenv("MAX_JOBS_PER_RUN", "10")),
        "platforms": os.getenv("PLATFORMS", "naukri,internshala,linkedin,indeed").split(","),
    }

    try:
        agent = JobAgent(config, groq_api_key)
        agent.run()
        logger.info("✅ Scheduled run completed successfully")
    except Exception as e:
        logger.error(f"❌ Scheduled run failed: {e}")


def main():
    run_time = os.getenv("SCHEDULE_TIME", "08:00")

    logger.info(f"⏰ Scheduler started - Agent will run daily at {run_time}")
    logger.info("Press Ctrl+C to stop\n")

    # Schedule daily run
    schedule.every().day.at(run_time).do(run_agent)

    # Also run immediately on start
    logger.info("🚀 Running agent now for immediate results...")
    run_agent()

    # Keep running
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    main()