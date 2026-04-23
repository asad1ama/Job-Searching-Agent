from utils.logger import setup_logger

logger = setup_logger()

class ResumeTailor:
    def __init__(self, groq_client):
        self.groq = groq_client

    def tailor_resume(self, resume: str, job: dict) -> str:
        prompt = f"""
You are an expert resume writer. Tailor the candidate's resume for this specific job.

JOB DETAILS:
- Title: {job.get('title', 'N/A')}
- Company: {job.get('company', 'N/A')}
- Description: {job.get('description', 'N/A')[:800]}
- Skills Required: {job.get('skills', 'N/A')}

ORIGINAL RESUME:
{resume}

INSTRUCTIONS:
1. Reorder and emphasize skills that match the job requirements
2. Use keywords from the job description naturally
3. Keep it honest - don't add fake experience
4. Keep the format clean and ATS-friendly
5. Make the summary line match the role specifically

Return ONLY the tailored resume text, no extra explanation.
"""
        try:
            tailored = self.groq.chat(prompt, max_tokens=1500)
            logger.info(f"  ✅ Resume tailored for {job.get('company')}")
            return tailored
        except Exception as e:
            logger.error(f"  ❌ Resume tailoring failed: {e}")
            return resume

    def generate_cover_letter(self, resume: str, job: dict) -> str:
        prompt = f"""
Write a compelling, concise cover letter for this job application.

JOB DETAILS:
- Title: {job.get('title', 'N/A')}
- Company: {job.get('company', 'N/A')}
- Description: {job.get('description', 'N/A')[:600]}

CANDIDATE PROFILE:
{resume[:600]}

INSTRUCTIONS:
1. Keep it under 250 words
2. Opening: Show genuine interest in THIS company specifically
3. Middle: Connect 2-3 skills to job requirements
4. Closing: Clear call to action
5. Tone: Professional but enthusiastic

Return ONLY the cover letter text.
"""
        try:
            letter = self.groq.chat(prompt, max_tokens=600)
            logger.info(f"  ✅ Cover letter generated for {job.get('company')}")
            return letter
        except Exception as e:
            logger.error(f"  ❌ Cover letter generation failed: {e}")
            return f"Dear Hiring Team at {job.get('company', 'your company')},\n\nI am excited to apply...\n\nBest regards"