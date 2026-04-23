from utils.logger import setup_logger
import time

logger = setup_logger()

class AgentScorer:
    def __init__(self):
        self.start_time = time.time()

    def calculate_score(self, all_jobs: list, ranked_jobs: list, results: list) -> int:
        # Component 1: Jobs Found (max 2000)
        jobs_score = min(len(all_jobs), 10) * 200

        # Component 2: Ranking Quality (max 3000)
        match_scores = [j.get("match_score", 0) for j in ranked_jobs if "match_score" in j]
        if match_scores:
            avg_match = sum(match_scores) / len(match_scores)
            ranking_score = int((avg_match / 100) * 3000)
        else:
            ranking_score = 1500

        # Component 3: Resume Tailoring (max 3000)
        tailored_count = sum(1 for r in results if r.get("tailored_resume") and len(r["tailored_resume"]) > 100)
        tailoring_score = int((tailored_count / max(len(results), 1)) * 3000)

        # Component 4: Speed Bonus (max 1000)
        elapsed = time.time() - self.start_time
        if elapsed < 60:
            speed_score = 1000
        elif elapsed < 120:
            speed_score = 500
        else:
            speed_score = 200

        # Component 5: Platform Diversity (max 1000)
        platforms = set(j.get("platform") for j in all_jobs)
        diversity_score = min(len(platforms) * 500, 1000)

        total = jobs_score + ranking_score + tailoring_score + speed_score + diversity_score
        total = max(1, min(total, 10000))

        logger.info(f"\n  SCORE BREAKDOWN:")
        logger.info(f"  Jobs Found:       {jobs_score}/2000")
        logger.info(f"  Ranking Quality:  {ranking_score}/3000")
        logger.info(f"  Resume Tailoring: {tailoring_score}/3000")
        logger.info(f"  Speed:            {speed_score}/1000")
        logger.info(f"  Platforms:        {diversity_score}/1000")
        logger.info(f"  ─────────────────────────")
        logger.info(f"  TOTAL:            {total}/10,000")

        return total