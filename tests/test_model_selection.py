"""Model-family aliases for unattended Claude jobs."""

import unittest

from runner.config import JobSpec, load_job


class ModelSelectionTest(unittest.TestCase):
    def test_jobs_use_family_aliases_instead_of_release_pins(self):
        self.assertEqual(load_job("morning_brief").model, "opus")
        for name in ("granola_notion_sync", "notion_todoist_sync", "hello"):
            with self.subTest(job=name):
                self.assertEqual(load_job(name).model, "sonnet")

    def test_precheck_uses_haiku_family_alias(self):
        self.assertEqual(
            JobSpec(name="example", description="example").precheck_model, "haiku"
        )


if __name__ == "__main__":
    unittest.main()
