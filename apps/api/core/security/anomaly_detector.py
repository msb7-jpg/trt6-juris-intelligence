"""Big Data event ingestion, MinIO analytical archiving, and AI anomaly detection (IsolationForest)."""

import io
import json
import random
from datetime import timedelta

import numpy as np
from django.db.models import Avg, Count, Q
from django.utils import timezone
from sklearn.ensemble import IsolationForest

from core.models.security_events import AnomalyAlert, SecurityEvent
from shared.logger import get_logger

logger = get_logger("core.security.anomaly_detector")

SECURITY_BUCKET = "security-bigdata"


def record_security_event(
    event_type: str,
    *,
    user=None,
    actor_label: str | None = None,
    ip_address: str | None = None,
    algorithm: str = "",
    success: bool = True,
    latency_ms: float = 0.0,
    payload_size: int = 0,
    sha256_hash: str = "",
    metadata: dict | None = None,
) -> SecurityEvent:
    """Persist a single operational security event."""
    label = actor_label or (user.username if user and getattr(user, "is_authenticated", False) else "anonymous")
    return SecurityEvent.objects.create(
        user=user if user and getattr(user, "is_authenticated", False) else None,
        actor_label=label,
        ip_address=ip_address,
        event_type=event_type,
        algorithm=algorithm,
        success=success,
        latency_ms=latency_ms,
        payload_size=payload_size,
        sha256_hash=sha256_hash,
        metadata=metadata or {},
    )


def _archive_snapshot_to_minio(summary: dict) -> str | None:
    """Best-effort upload of Big Data analytical snapshot to MinIO S3."""
    try:
        from shared.s3_client import get_s3_client

        client = get_s3_client()
        if not client.bucket_exists(SECURITY_BUCKET):
            client.make_bucket(SECURITY_BUCKET)
        key = f"snapshots/bigdata-{timezone.now():%Y%m%d-%H%M%S}.json"
        raw = json.dumps(summary, ensure_ascii=False).encode("utf-8")
        client.put_object(
            SECURITY_BUCKET,
            key,
            io.BytesIO(raw),
            length=len(raw),
            content_type="application/json",
        )
        return f"{SECURITY_BUCKET}/{key}"
    except Exception as exc:  # pragma: no cover - MinIO optional in unit tests
        logger.warning(f"MinIO snapshot skipped: {exc}")
        return None


def generate_experimental_events(
    total_events: int = 2000,
    inject_anomalies: bool = True,
    archive_to_minio: bool = True,
) -> dict:
    """Generate a synthetic Big Data security event dataset in bulk."""
    total_events = max(100, min(total_events, 50_000))
    rng = random.Random(42)  # noqa: S311 - deterministic experimental dataset
    now = timezone.now()

    normal_actors = [f"analista_{i:02d}@tcu.gov.br" for i in range(1, 21)]
    normal_types = [
        (SecurityEvent.EventType.CRYPTO_ENCRYPT, True),
        (SecurityEvent.EventType.CRYPTO_DECRYPT, True),
        (SecurityEvent.EventType.AUTH_SUCCESS, True),
        (SecurityEvent.EventType.STEGANO_EMBED, True),
        (SecurityEvent.EventType.FILE_INTEGRITY_CHECK, True),
    ]

    anomaly_quota = min(max(int(total_events * 0.08), 40), 600) if inject_anomalies else 0
    normal_quota = total_events - anomaly_quota

    batch: list[SecurityEvent] = []
    for _ in range(normal_quota):
        ev_type, ok = rng.choice(normal_types)
        actor = rng.choice(normal_actors)
        offset_mins = rng.randint(0, 720)
        batch.append(
            SecurityEvent(
                actor_label=actor,
                ip_address=f"10.0.1.{rng.randint(10, 60)}",
                event_type=ev_type,
                algorithm=rng.choice(["spn", "aes-256-gcm"]),
                success=ok,
                latency_ms=round(rng.uniform(2.0, 28.0), 2),
                payload_size=rng.randint(64, 4096),
                is_synthetic=True,
                created_at=now - timedelta(minutes=offset_mins),
            )
        )

    if inject_anomalies:
        # 1. Auth brute-force actor
        for _ in range(anomaly_quota // 4):
            batch.append(
                SecurityEvent(
                    actor_label="attacker_bruteforce@external",
                    ip_address="198.51.100.77",
                    event_type=SecurityEvent.EventType.AUTH_FAILURE,
                    success=False,
                    latency_ms=round(rng.uniform(1.0, 5.0), 2),
                    is_synthetic=True,
                    created_at=now - timedelta(minutes=rng.randint(0, 10)),
                )
            )
        # 2. High decryption failure rate actor
        for _ in range(anomaly_quota // 4):
            batch.append(
                SecurityEvent(
                    actor_label="suspect_decrypt@external",
                    ip_address="203.0.113.45",
                    event_type=SecurityEvent.EventType.DECRYPT_FAILURE,
                    algorithm="spn",
                    success=False,
                    latency_ms=round(rng.uniform(15.0, 45.0), 2),
                    is_synthetic=True,
                    created_at=now - timedelta(minutes=rng.randint(0, 15)),
                )
            )
        # 3. File tampering + atypical burst actor
        for _ in range(anomaly_quota - 2 * (anomaly_quota // 4)):
            batch.append(
                SecurityEvent(
                    actor_label="insider_tamper@tcu.gov.br",
                    ip_address="172.16.99.250",
                    event_type=rng.choice(
                        [
                            SecurityEvent.EventType.FILE_TAMPERED,
                            SecurityEvent.EventType.CRYPTO_ENCRYPT,
                        ]
                    ),
                    algorithm="aes-256-gcm",
                    success=False,
                    latency_ms=round(rng.uniform(80.0, 220.0), 2),
                    payload_size=rng.randint(10_000, 90_000),
                    is_synthetic=True,
                    created_at=now.replace(hour=3, minute=rng.randint(0, 59)),
                )
            )

    SecurityEvent.objects.bulk_create(batch, batch_size=1000)

    snapshot_path = None
    if archive_to_minio:
        snapshot_path = _archive_snapshot_to_minio(
            {
                "generated_at": now.isoformat(),
                "total_inserted": len(batch),
                "normal_events": normal_quota,
                "injected_anomaly_events": anomaly_quota,
            }
        )

    return {
        "inserted_events": len(batch),
        "normal_events": normal_quota,
        "injected_anomaly_events": anomaly_quota,
        "minio_snapshot": snapshot_path,
    }


def _classify_actor_anomaly(row: dict) -> tuple[str, str, str]:
    """Map behavioral feature counts to a specific PDF anomaly category and severity."""
    auth_fails = row["auth_failures"]
    decrypt_fails = row["decrypt_failures"]
    tampered = row["file_tampered"]
    atypical = row["atypical_hours"]

    if tampered > 0:
        return (
            AnomalyAlert.AnomalyType.FILE_ALTERATION,
            AnomalyAlert.Severity.CRITICAL,
            f"{tampered} alteracoes inesperadas de arquivo/hash detectadas para {row['actor_label']}.",
        )
    if auth_fails >= 10:
        return (
            AnomalyAlert.AnomalyType.AUTH_BRUTE_FORCE,
            AnomalyAlert.Severity.HIGH,
            f"Numero incomum de falhas de autenticacao ({auth_fails}) para {row['actor_label']}.",
        )
    if decrypt_fails >= 8:
        return (
            AnomalyAlert.AnomalyType.HIGH_DECRYPT_FAIL_RATE,
            AnomalyAlert.Severity.HIGH,
            f"Frequencia elevada de falhas de descriptografia ({decrypt_fails}) para {row['actor_label']}.",
        )
    if atypical > 0:
        return (
            AnomalyAlert.AnomalyType.ATYPICAL_ACCESS_PATTERN,
            AnomalyAlert.Severity.MEDIUM,
            f"Padrao atipico de acesso em horario incomum ({atypical} eventos) para {row['actor_label']}.",
        )
    return (
        AnomalyAlert.AnomalyType.EVENT_BURST,
        AnomalyAlert.Severity.MEDIUM,
        f"Comportamento incomum na geracao de eventos ({row['total_events']} eventos) para {row['actor_label']}.",
    )


def detect_anomalies() -> dict:
    """Aggregate SecurityEvents per actor and detect behavioral anomalies with IsolationForest."""
    aggregates = list(
        SecurityEvent.objects.values("actor_label").annotate(
            total_events=Count("id"),
            auth_failures=Count("id", filter=Q(event_type=SecurityEvent.EventType.AUTH_FAILURE)),
            decrypt_failures=Count("id", filter=Q(event_type=SecurityEvent.EventType.DECRYPT_FAILURE)),
            file_tampered=Count("id", filter=Q(event_type=SecurityEvent.EventType.FILE_TAMPERED)),
            atypical_hours=Count("id", filter=Q(created_at__hour__lt=6)),
            avg_latency=Avg("latency_ms"),
        )
    )

    if not aggregates:
        return {"analyzed_actors": 0, "anomalies_detected": 0, "alerts": []}

    features = np.array(
        [
            [
                row["total_events"],
                row["auth_failures"],
                row["decrypt_failures"],
                row["file_tampered"],
                row["atypical_hours"],
                row["avg_latency"] or 0.0,
            ]
            for row in aggregates
        ],
        dtype=float,
    )

    if len(aggregates) >= 5:
        model = IsolationForest(contamination=0.2, random_state=42)
        preds = model.fit_predict(features)
        scores = model.decision_function(features)
        flagged_indices = [i for i, pred in enumerate(preds) if pred == -1]
    else:
        scores = np.zeros(len(aggregates))
        flagged_indices = [
            i
            for i, row in enumerate(aggregates)
            if row["auth_failures"] >= 5 or row["decrypt_failures"] >= 5 or row["file_tampered"] > 0
        ]

    created_alerts: list[AnomalyAlert] = []
    for idx in flagged_indices:
        row = aggregates[idx]
        # Avoid flagging purely normal actors if they have zero failures and zero tampering
        if (
            row["auth_failures"] == 0
            and row["decrypt_failures"] == 0
            and row["file_tampered"] == 0
            and row["atypical_hours"] == 0
            and row["total_events"] < 500
        ):
            continue

        anomaly_type, severity, summary = _classify_actor_anomaly(row)
        alert = AnomalyAlert.objects.create(
            anomaly_type=anomaly_type,
            severity=severity,
            actor_label=row["actor_label"],
            score=round(float(scores[idx]), 4),
            event_count=row["total_events"],
            summary=summary,
            details={
                "auth_failures": row["auth_failures"],
                "decrypt_failures": row["decrypt_failures"],
                "file_tampered": row["file_tampered"],
                "atypical_hours": row["atypical_hours"],
                "avg_latency_ms": round(float(row["avg_latency"] or 0.0), 2),
            },
        )
        created_alerts.append(alert)

    return {
        "analyzed_actors": len(aggregates),
        "anomalies_detected": len(created_alerts),
        "alerts": [
            {
                "id": a.id,
                "anomaly_type": a.anomaly_type,
                "severity": a.severity,
                "actor_label": a.actor_label,
                "score": a.score,
                "event_count": a.event_count,
                "summary": a.summary,
                "details": a.details,
                "detected_at": a.detected_at.isoformat(),
            }
            for a in created_alerts
        ],
    }
