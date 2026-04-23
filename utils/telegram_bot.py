"""
Telegram Notification Bot
Sends job results directly to your phone
"""

import requests
from utils.logger import setup_logger

logger = setup_logger()


class TelegramBot:
    def __init__(self, token: str, chat_id: str):
        self.token = token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{token}"

    def send(self, message: str):
        try:
            url = f"{self.base_url}/sendMessage"
            payload = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "Markdown",
            }
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            logger.info("  ✅ Telegram notification sent")
        except Exception as e:
            logger.warning(f"  ⚠️ Telegram failed: {e}")

    def send_job_summary(self, all_jobs: list, results: list, score: int, skill_data: dict):
        """Send a rich summary of the agent run to Telegram"""

        # Header
        header = f"""
🤖 *Job Agent Report*
━━━━━━━━━━━━━━━━━━━━
📊 *Run Summary*
- Jobs Found: {len(all_jobs)}
- Resumes Tailored: {len(results)}
- Agent Score: *{score}/10,000*
"""

        # Top 3 jobs
        jobs_section = "\n🏆 *Top Matched Jobs*\n"
        for i, r in enumerate(results[:3]):
            match = r.get("match_score", "N/A")
            jobs_section += f"""
*{i+1}. {r.get('title')}*
🏢 {r.get('company')}
📍 {r.get('location')}
🎯 Match: {match}/100
🔗 {r.get('url', 'N/A')[:50]}
"""

        # Skill gap
        skill_section = ""
        if skill_data:
            missing = skill_data.get("candidate_missing", [])[:3]
            quick_wins = skill_data.get("quick_wins", [])[:2]
            job_score = skill_data.get("job_ready_score", "N/A")
            skill_section = f"""
━━━━━━━━━━━━━━━━━━━━
🧠 *Skill Gap Analysis*
- Job Ready Score: *{job_score}%*
- Missing: {', '.join(missing)}
- Quick Wins: {', '.join(quick_wins)}
"""

        footer = "\n━━━━━━━━━━━━━━━━━━━━\n✅ Check output/report.html for full details"

        full_message = header + jobs_section + skill_section + footer
        self.send(full_message)