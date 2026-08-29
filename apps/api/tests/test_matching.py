import unittest
from unittest.mock import AsyncMock, MagicMock
import uuid

from app.models.job import Job
from app.services.matching.scorer import (
    WEIGHTS,
    _location_match,
    _skill_overlap,
    _generate_reasoning,
)


class TestMatchingEngine(unittest.IsolatedAsyncioTestCase):
    def test_weights_sum_to_one(self):
        """Verify the matching scoring weights sum up to 1.0 (100%)."""
        total = sum(WEIGHTS.values())
        self.assertAlmostEqual(total, 1.0, places=5)

    def test_location_match_scoring(self):
        """Verify remote, specified location, and unspecified location scores."""
        remote_job = Job(id=uuid.uuid4(), user_id=uuid.uuid4(), title="Dev", company="Acme", remote=True)
        self.assertEqual(_location_match(remote_job), 100.0)

        onsite_job = Job(id=uuid.uuid4(), user_id=uuid.uuid4(), title="Dev", company="Acme", remote=False, location="New York, NY")
        self.assertEqual(_location_match(onsite_job), 60.0)

        unknown_job = Job(id=uuid.uuid4(), user_id=uuid.uuid4(), title="Dev", company="Acme", remote=False, location=None)
        self.assertEqual(_location_match(unknown_job), 50.0)

    async def test_skill_overlap_calculation(self):
        """Verify skill overlap calculation when user matches a subset of job skills."""
        job_id = uuid.uuid4()
        user_id = uuid.uuid4()

        mock_db = AsyncMock()

        # Mock job skills: ["python", "fastapi", "docker"]
        mock_job_skills_result = MagicMock()
        mock_job_skills_result.fetchall.return_value = [("python",), ("fastapi",), ("docker",)]

        # Mock user skills: ["python", "fastapi", "react"]
        mock_user_skills_result = MagicMock()
        mock_user_skills_result.fetchall.return_value = [("python",), ("fastapi",), ("react",)]

        mock_db.execute.side_effect = [mock_job_skills_result, mock_user_skills_result]

        score, matched, missing = await _skill_overlap(job_id, user_id, mock_db)

        # 2 out of 3 matched -> 66.67%
        self.assertAlmostEqual(score, (2 / 3) * 100, places=1)
        self.assertEqual(matched, ["fastapi", "python"])
        self.assertEqual(missing, ["docker"])

    async def test_generate_reasoning_fallback_without_client(self):
        """Verify fallback reasoning when OpenAI client is not initialized."""
        job = Job(id=uuid.uuid4(), user_id=uuid.uuid4(), title="Backend Engineer", company="Stripe")
        reasoning = await _generate_reasoning(
            job=job,
            score=85.0,
            strong_points=["Python", "FastAPI"],
            skill_gaps=["Kubernetes"],
            component_scores={"skill_overlap": 80, "semantic_similarity": 90},
        )
        self.assertIn("Match score: 85/100", reasoning)
        self.assertIn("Matching skills: Python, FastAPI", reasoning)


if __name__ == "__main__":
    unittest.main()
