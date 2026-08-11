"""Google Cloud Model Armor REST Client with ADC Auth & Retry Logic."""

import dataclasses
import json
import os
import subprocess
import time
import urllib.error
import urllib.request
from typing import Any, Dict, Optional

from src.model_armor.mock_server import simulate_model_armor_sanitization


@dataclasses.dataclass
class ModelArmorRequest:
    """Request payload for Model Armor SanitizeUserPrompt API."""
    project_id: str
    location: str
    template_id: str
    user_prompt: str
    enable_multi_language: bool = True
    source_language: Optional[str] = None

    @property
    def template_resource_name(self) -> str:
        return f"projects/{self.project_id}/locations/{self.location}/templates/{self.template_id}"

    def to_api_payload(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "name": self.template_resource_name,
            "user_prompt_data": {
                "text": self.user_prompt
            }
        }
        if self.enable_multi_language:
            payload["multi_language_detection_metadata"] = {
                "enable_multi_language_detection": True
            }
            if self.source_language:
                payload["multi_language_detection_metadata"]["source_language"] = self.source_language
        return payload


@dataclasses.dataclass
class ModelArmorResponse:
    """Response wrapper for Model Armor SanitizeUserPrompt API."""
    success: bool
    raw_response: Dict[str, Any]
    filter_match_state: str  # NO_MATCH_FOUND or MATCH_FOUND
    invocation_result: str   # SUCCESS, PARTIAL, FAILURE
    filter_results: Dict[str, Any]
    sanitized_text: Optional[str] = None
    error_message: Optional[str] = None
    status_code: int = 200
    latency_ms: float = 0.0


class ModelArmorClient:
    """Client for Google Cloud Model Armor API (modelarmor.googleapis.com)."""

    _auth_attempted: bool = False
    _cached_token: Optional[str] = None

    def __init__(
        self,
        project_id: str = "stratosphere-461622",
        location: str = "asia-south1",
        template_id: str = "fsi-india-compliance-template",
        endpoint: str = "modelarmor.googleapis.com",
        mock_mode: bool = False,
        timeout_seconds: float = 5.0,
        retry_attempts: int = 2,
    ):
        self.project_id = project_id
        self.location = location
        self.template_id = template_id
        self.endpoint = endpoint
        self.mock_mode = mock_mode or os.environ.get("MODEL_ARMOR_MOCK_MODE", "").lower() in ("true", "1", "yes")
        self.timeout_seconds = timeout_seconds
        self.retry_attempts = retry_attempts

    def _get_auth_token(self) -> Optional[str]:
        """Retrieves GCP OAuth2 access token via environment or gcloud once."""
        if self.mock_mode:
            return None

        if ModelArmorClient._auth_attempted:
            return ModelArmorClient._cached_token

        # Check environment variable first
        token = os.environ.get("GOOGLE_OAUTH_ACCESS_TOKEN") or os.environ.get("GCP_ACCESS_TOKEN")
        if token:
            ModelArmorClient._cached_token = token
            ModelArmorClient._auth_attempted = True
            return token

        # Fast gcloud check
        try:
            res = subprocess.run(
                ["gcloud", "auth", "print-access-token"],
                capture_output=True,
                text=True,
                timeout=1.0,
                check=False,
            )
            if res.returncode == 0 and res.stdout.strip():
                ModelArmorClient._cached_token = res.stdout.strip()
        except Exception:
            pass

        ModelArmorClient._auth_attempted = True
        return ModelArmorClient._cached_token

    def sanitize_user_prompt(
        self,
        prompt: str,
        template_id: Optional[str] = None,
        location: Optional[str] = None,
        project_id: Optional[str] = None,
    ) -> ModelArmorResponse:
        """Invokes Model Armor SanitizeUserPrompt API or high-performance simulation engine."""
        start_time = time.perf_counter()
        proj = project_id or self.project_id
        loc = location or self.location
        tmpl = template_id or self.template_id

        req = ModelArmorRequest(
            project_id=proj,
            location=loc,
            template_id=tmpl,
            user_prompt=prompt,
        )

        auth_token = self._get_auth_token()
        if not auth_token or self.mock_mode:
            raw_mock = simulate_model_armor_sanitization(prompt, tmpl)
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            s_result = raw_mock.get("sanitization_result", {})
            return ModelArmorResponse(
                success=True,
                raw_response=raw_mock,
                filter_match_state=s_result.get("filter_match_state", "NO_MATCH_FOUND"),
                invocation_result=s_result.get("invocation_result", "SUCCESS"),
                filter_results=s_result.get("filter_results", {}),
                sanitized_text=prompt,
                latency_ms=round(elapsed_ms, 2),
            )

        # Real GCP API call
        url = f"https://{self.endpoint}/v1/{req.template_resource_name}:sanitizeUserPrompt"
        payload_bytes = json.dumps(req.to_api_payload()).encode("utf-8")

        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": f"Bearer {auth_token}",
            "X-Goog-User-Project": proj,
        }

        last_error = None
        for attempt in range(self.retry_attempts + 1):
            try:
                http_req = urllib.request.Request(url, data=payload_bytes, headers=headers, method="POST")
                with urllib.request.urlopen(http_req, timeout=self.timeout_seconds) as resp:
                    resp_body = resp.read().decode("utf-8")
                    data = json.loads(resp_body)
                    elapsed_ms = (time.perf_counter() - start_time) * 1000.0
                    s_result = data.get("sanitization_result", {})
                    return ModelArmorResponse(
                        success=True,
                        raw_response=data,
                        filter_match_state=s_result.get("filter_match_state", "NO_MATCH_FOUND"),
                        invocation_result=s_result.get("invocation_result", "SUCCESS"),
                        filter_results=s_result.get("filter_results", {}),
                        sanitized_text=prompt,
                        status_code=resp.status,
                        latency_ms=round(elapsed_ms, 2),
                    )
            except urllib.error.HTTPError as e:
                err_content = e.read().decode("utf-8", errors="ignore")
                last_error = f"HTTP {e.code}: {e.reason} - {err_content}"
                if e.code in (400, 403, 404):
                    break
            except Exception as e:
                last_error = str(e)

            time.sleep(0.1 * (2 ** attempt))

        # Fallback to simulation engine if network or endpoint fails
        raw_mock = simulate_model_armor_sanitization(prompt, tmpl)
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        s_result = raw_mock.get("sanitization_result", {})
        return ModelArmorResponse(
            success=False,
            raw_response=raw_mock,
            filter_match_state=s_result.get("filter_match_state", "NO_MATCH_FOUND"),
            invocation_result="PARTIAL",
            filter_results=s_result.get("filter_results", {}),
            error_message=f"Model Armor live call failed ({last_error}). Evaluated via fallback engine.",
            latency_ms=round(elapsed_ms, 2),
        )
