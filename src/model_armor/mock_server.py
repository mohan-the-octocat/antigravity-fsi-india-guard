"""High-Fidelity Model Armor Mock Simulator for Offline Development and Testing."""

import re
from typing import Any, Dict, List


def simulate_model_armor_sanitization(prompt: str, template_name: str = "fsi-india-compliance-template") -> Dict[str, Any]:
    """Simulates Google Cloud Model Armor sanitization engine.

    Inspects prompt against prompt injection, responsible AI, malicious URIs, and CSAM.
    Returns a valid Model Armor API response dictionary.
    """
    filter_results: Dict[str, Any] = {}
    match_found = False
    lower_prompt = prompt.lower()

    # 1. Prompt Injection & Jailbreak Heuristic Matcher
    pi_jb_patterns = [
        r"ignore\s+(?:all\s+)?previous\s+instructions",
        r"disregard\s+(?:all\s+)?prior\s+(?:rules|prompts|instructions)",
        r"you\s+are\s+now\s+in\s+developer\s+mode",
        r"dan\s+mode\s+enabled",
        r"bypass\s+all\s+(?:safety|security|content)\s+filters",
        r"reveal\s+(?:your\s+)?system\s+prompt",
        r"output\s+initial\s+instructions",
        r"roleplay\s+as\s+(?:an\s+)?unfiltered\s+ai",
        r"sudo\s+mode\s+activated",
        r"system\s+override\s+code\s*[:=]",
        r"jailbreak\s+prompt",
    ]

    is_pi_jb = any(re.search(pat, lower_prompt) for pat in pi_jb_patterns)
    if is_pi_jb:
        match_found = True
        filter_results["pi_and_jailbreak"] = {
            "pi_and_jailbreak_filter_result": {
                "match_state": "MATCH_FOUND",
                "confidence_level": "HIGH",
                "score": 0.94,
                "detected_techniques": ["DIRECT_PROMPT_INJECTION", "JAILBREAK_ATTEMPT", "SYSTEM_PROMPT_EXTRACTION"]
            }
        }
    else:
        filter_results["pi_and_jailbreak"] = {
            "pi_and_jailbreak_filter_result": {
                "match_state": "NO_MATCH_FOUND",
                "confidence_level": "LOW",
                "score": 0.05
            }
        }

    # 2. Responsible AI (RAI) Heuristic Matcher
    rai_hate_patterns = [r"(?:kill\s+all|exterminate|hate\s+all\s+members\s+of)"]
    rai_danger_patterns = [r"(?:how\s+to\s+build\s+a\s+bomb|make\s+explosive|manufacture\s+ricin|synthesize\s+sarin)"]
    rai_harass_patterns = [r"(?:doxx\s+this\s+person|harass\s+them\s+online|swat\s+their\s+address)"]

    is_hate = any(re.search(p, lower_prompt) for p in rai_hate_patterns)
    is_danger = any(re.search(p, lower_prompt) for p in rai_danger_patterns)
    is_harass = any(re.search(p, lower_prompt) for p in rai_harass_patterns)

    if is_hate or is_danger or is_harass:
        match_found = True
        filter_results["rai"] = {
            "rai_filter_result": {
                "match_state": "MATCH_FOUND",
                "rai_filter_type_results": {
                    "HATE_SPEECH": {"confidence_level": "HIGH" if is_hate else "LOW"},
                    "DANGEROUS_CONTENT": {"confidence_level": "HIGH" if is_danger else "LOW"},
                    "HARASSMENT": {"confidence_level": "HIGH" if is_harass else "LOW"},
                    "SEXUALLY_EXPLICIT": {"confidence_level": "LOW"}
                }
            }
        }
    else:
        filter_results["rai"] = {
            "rai_filter_result": {
                "match_state": "NO_MATCH_FOUND",
                "rai_filter_type_results": {
                    "HATE_SPEECH": {"confidence_level": "LOW"},
                    "DANGEROUS_CONTENT": {"confidence_level": "LOW"},
                    "HARASSMENT": {"confidence_level": "LOW"},
                    "SEXUALLY_EXPLICIT": {"confidence_level": "LOW"}
                }
            }
        }

    # 3. Malicious URI Matcher
    malicious_domains = ["malicious-phishing.com", "evil-banking-login.in", "free-gift-cards-claim.xyz", "credential-stealer.net"]
    has_bad_uri = any(dom in lower_prompt for dom in malicious_domains)
    if has_bad_uri:
        match_found = True
        filter_results["malicious_uris"] = {
            "malicious_uri_filter_result": {
                "match_state": "MATCH_FOUND",
                "matched_uris": [dom for dom in malicious_domains if dom in lower_prompt]
            }
        }
    else:
        filter_results["malicious_uris"] = {
            "malicious_uri_filter_result": {
                "match_state": "NO_MATCH_FOUND"
            }
        }

    # 4. CSAM Matcher
    csam_keywords = ["csam_test_trigger_payload"]
    has_csam = any(k in lower_prompt for k in csam_keywords)
    if has_csam:
        match_found = True
        filter_results["csam"] = {
            "csam_filter_filter_result": {
                "match_state": "MATCH_FOUND"
            }
        }
    else:
        filter_results["csam"] = {
            "csam_filter_filter_result": {
                "match_state": "NO_MATCH_FOUND"
            }
        }

    filter_match_state = "MATCH_FOUND" if match_found else "NO_MATCH_FOUND"

    return {
        "sanitization_result": {
            "filter_match_state": filter_match_state,
            "filter_results": filter_results,
            "invocation_result": "SUCCESS",
            "sanitization_metadata": {
                "error_code": 0,
                "error_message": "",
                "ignore_partial_invocation_failures": False
            }
        }
    }


class MockModelArmorServer:
    """Mock server harness for testing Model Armor integrations."""

    def __init__(self):
        self.invocations: List[Dict[str, Any]] = []

    def sanitize(self, prompt: str, template: str) -> Dict[str, Any]:
        resp = simulate_model_armor_sanitization(prompt, template)
        self.invocations.append({"prompt": prompt, "template": template, "response": resp})
        return resp
