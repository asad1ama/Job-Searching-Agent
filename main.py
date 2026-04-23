"""
Job Application Automation Agent
Entry point - run this to start the agent
"""

import os
from dotenv import load_dotenv
load_dotenv()

from agent.job_agent import JobAgent
from utils.logger import setup_logger

logger = setup_logger()

def main():
    logger.info("🤖 Job Application Agent Starting...")

    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError("❌ GROQ_API_KEY not found. Check your .env file.")

    config = {
        "target_role": os.getenv("TARGET_ROLE", "Java Backend Developer"),
        "target_location": os.getenv("TARGET_LOCATION", "India"),
        "experience_level": os.getenv("EXPERIENCE_LEVEL", "fresher"),
        "resume_path": os.getenv("RESUME_PATH", "config/resume.txt"),
        "max_jobs_per_run": int(os.getenv("MAX_JOBS_PER_RUN", "10")),
        "platforms": os.getenv("PLATFORMS", "naukri,internshala").split(","),
    }

    logger.info(f"🎯 Target Role: {config['target_role']}")
    logger.info(f"📍 Location: {config['target_location']}")
    logger.info(f"🔍 Platforms: {config['platforms']}")

    agent = JobAgent(config, groq_api_key)
    agent.run()

if __name__ == "__main__":
    main()