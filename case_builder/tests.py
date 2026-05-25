from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse

from .services import evaluate_chain, generate_vba, parse_chain


class CaseBuilderTests(TestCase):
    def test_chain_evaluates_function_of_function(self):
        result = evaluate_chain(4, ["sqrt", "inv", "exp"])

        self.assertTrue(result.ok)
        self.assertAlmostEqual(result.value, 1.648721, places=5)

    def test_domain_error_is_reported(self):
        result = evaluate_chain(-1, ["sqrt"])

        self.assertFalse(result.ok)
        self.assertEqual(result.step, 1)

    def test_vba_generation_contains_domain_checks(self):
        code = generate_vba(["sqrt", "inv"])

        self.assertIn("Function CalculateModel", code)
        self.assertIn("If value < 0 Then GoTo DomainError", code)
        self.assertIn("If value = 0 Then GoTo DomainError", code)

    def test_designer_page_renders_generated_code(self):
        response = self.client.post(reverse("case_builder:designer"), {"x_value": "4", "chain": ["sqrt", "inv"]})

        self.assertContains(response, "VBA-код")
        self.assertContains(response, "CalculateModel")

    @override_settings()
    def test_parse_chain_rejects_unknown_function(self):
        with self.assertRaises(ValueError):
            parse_chain("sqrt nope")

    def test_telegram_command_dry_run_requires_token(self):
        with patch.dict("os.environ", {}, clear=True), self.assertRaises(Exception):
            call_command("telegram_bot", "--dry-run")
