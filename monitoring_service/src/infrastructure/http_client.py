from __future__ import annotations
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict
from typing import Iterable, List, Optional
from urllib import request, error as urlerror
import ssl

from monitoring_service.src.domain.entities import Endpoint, CheckResult

logger = logging.getLogger(__name__)


def _http_request(method: str, url: str, timeout: float) -> tuple[int, Optional[bytes]]:
    data = None
    payload = None
    req = request.Request(url=url, data=payload, method=method.upper())
    context = ssl.create_default_context()
    with request.urlopen(req, timeout=timeout, context=context) as resp:
        status = getattr(resp, "status", None) or resp.getcode()
        try:
            data = resp.read()
        except Exception:
            data = None
        return status, data


class ParallelHTTPChecker:
    def __init__(self, timeout_seconds: float = 5.0, max_workers: int = 8) -> None:
        self.timeout_seconds = timeout_seconds
        self.max_workers = max_workers

    def _check_one(self, ep: Endpoint) -> CheckResult:
        start_ns = time.perf_counter_ns()
        try:
            status, _ = _http_request(ep.method, ep.url, timeout=self.timeout_seconds)
            elapsed_ms = int((time.perf_counter_ns() - start_ns) / 1_000_000)
            status_ok = status == ep.expected_status
            rt_ok = elapsed_ms < 2000
            if status_ok and rt_ok:
                return CheckResult(
                    name=ep.name,
                    url=ep.url,
                    method=ep.method,
                    expected_status=ep.expected_status,
                    actual_status=status,
                    response_time_ms=elapsed_ms,
                    status="ok",
                )
            else:
                err_msg = None
                if not status_ok:
                    err_msg = f"Expected status {ep.expected_status}, got {status}"
                elif not rt_ok:
                    err_msg = f"Slow response: {elapsed_ms}ms"
                return CheckResult(
                    name=ep.name,
                    url=ep.url,
                    method=ep.method,
                    expected_status=ep.expected_status,
                    actual_status=status,
                    response_time_ms=elapsed_ms,
                    status="failed",
                    error=err_msg,
                )
        except urlerror.HTTPError as he:
            elapsed_ms = int((time.perf_counter_ns() - start_ns) / 1_000_000)
            return CheckResult(
                name=ep.name,
                url=ep.url,
                method=ep.method,
                expected_status=ep.expected_status,
                actual_status=he.code,
                response_time_ms=elapsed_ms,
                status="failed",
                error=f"HTTPError: {he.reason}",
            )
        except urlerror.URLError as ue:
            elapsed_ms = int((time.perf_counter_ns() - start_ns) / 1_000_000)
            return CheckResult(
                name=ep.name,
                url=ep.url,
                method=ep.method,
                expected_status=ep.expected_status,
                actual_status=None,
                response_time_ms=elapsed_ms,
                status="failed",
                error=f"Connection error: {ue.reason}",
            )
        except Exception as e:
            elapsed_ms = int((time.perf_counter_ns() - start_ns) / 1_000_000)
            return CheckResult(
                name=ep.name,
                url=ep.url,
                method=ep.method,
                expected_status=ep.expected_status,
                actual_status=None,
                response_time_ms=elapsed_ms,
                status="failed",
                error=f"Exception: {e}",
            )

    def check_many(self, endpoints: Iterable[Endpoint]) -> List[CheckResult]:
        eps = list(endpoints)
        results: List[CheckResult] = []
        if not eps:
            return results
        with ThreadPoolExecutor(max_workers=min(self.max_workers, len(eps))) as pool:
            future_to_ep = {pool.submit(self._check_one, ep): ep for ep in eps}
            for fut in as_completed(future_to_ep):
                try:
                    result = fut.result()
                    results.append(result)
                except Exception as e:
                    ep = future_to_ep[fut]
                    logger.exception("Unexpected error while checking %s: %s", ep.url, e)
                    results.append(
                        CheckResult(
                            name=ep.name,
                            url=ep.url,
                            method=ep.method,
                            expected_status=ep.expected_status,
                            actual_status=None,
                            response_time_ms=None,
                            status="failed",
                            error=f"Worker exception: {e}",
                        )
                    )
        return results

