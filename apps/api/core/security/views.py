"""DRF views for Projeto 2 security lab: Crypto, Steganography, Attacks, Big Data, AI, and Dashboard."""

import base64
import json
import time

from django.db.models import Count, Q
from django.db.models.functions import TruncHour
from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models.security_events import AnomalyAlert, AttackExperiment, SecurityEvent
from core.security.anomaly_detector import (
    detect_anomalies,
    generate_experimental_events,
    record_security_event,
)
from core.security.attacks import (
    evaluate_security_suite,
    run_brute_force_attack,
    run_differential_attack,
    run_statistical_attack,
)
from core.security.cipher import decrypt_data, encrypt_data
from core.security.steganography import (
    create_cover_png,
    embed_payload_in_png,
    extract_payload_from_png,
)


def _client_ip(request: Request) -> str | None:
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


class SecurityEncryptView(APIView):
    """POST /api/security/encrypt/"""

    def post(self, request: Request) -> Response:
        plaintext = request.data.get("plaintext", "")
        secret = request.data.get("secret", "")
        algorithm = request.data.get("algorithm", "spn")
        rounds = int(request.data.get("rounds", 8))

        if not plaintext or not secret:
            return Response(
                {"mensagem": "Campos 'plaintext' e 'secret' sao obrigatorios."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        start = time.perf_counter()
        try:
            result = encrypt_data(plaintext, secret=secret, algorithm=algorithm, rounds=rounds)
        except ValueError as exc:
            return Response({"mensagem": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        latency = round((time.perf_counter() - start) * 1000, 2)

        record_security_event(
            SecurityEvent.EventType.CRYPTO_ENCRYPT,
            user=request.user,
            ip_address=_client_ip(request),
            algorithm=algorithm,
            success=True,
            latency_ms=latency,
            payload_size=len(plaintext.encode("utf-8")),
            sha256_hash=result["ciphertext_sha256"],
        )
        return Response(result, status=status.HTTP_200_OK)


class SecurityDecryptView(APIView):
    """POST /api/security/decrypt/"""

    def post(self, request: Request) -> Response:
        payload = request.data.get("payload")
        secret = request.data.get("secret", "")
        if not isinstance(payload, dict) or not secret:
            return Response(
                {"mensagem": "Campos 'payload' (dict) e 'secret' sao obrigatorios."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        start = time.perf_counter()
        try:
            plaintext = decrypt_data(payload, secret=secret).decode("utf-8")
        except Exception as exc:
            latency = round((time.perf_counter() - start) * 1000, 2)
            record_security_event(
                SecurityEvent.EventType.DECRYPT_FAILURE,
                user=request.user,
                ip_address=_client_ip(request),
                algorithm=str(payload.get("algorithm", "")),
                success=False,
                latency_ms=latency,
                metadata={"error": str(exc)},
            )
            return Response(
                {"mensagem": f"Falha na descriptografia: {exc}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        latency = round((time.perf_counter() - start) * 1000, 2)
        record_security_event(
            SecurityEvent.EventType.CRYPTO_DECRYPT,
            user=request.user,
            ip_address=_client_ip(request),
            algorithm=str(payload.get("algorithm", "")),
            success=True,
            latency_ms=latency,
            payload_size=len(plaintext.encode("utf-8")),
        )
        return Response({"plaintext": plaintext, "integrity_verified": True}, status=status.HTTP_200_OK)


class SecurityStegoEmbedView(APIView):
    """POST /api/security/steganography/embed/"""

    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request: Request) -> Response:
        raw_payload = request.data.get("payload", "")
        if not raw_payload:
            return Response(
                {"mensagem": "Campo 'payload' e obrigatorio."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        payload_bytes = (
            json.dumps(raw_payload).encode("utf-8")
            if isinstance(raw_payload, dict)
            else str(raw_payload).encode("utf-8")
        )

        uploaded = request.FILES.get("image")
        image_bytes = uploaded.read() if uploaded is not None else create_cover_png(320, 320)

        start = time.perf_counter()
        try:
            result = embed_payload_in_png(image_bytes, payload_bytes)
        except Exception as exc:
            return Response({"mensagem": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        latency = round((time.perf_counter() - start) * 1000, 2)

        stego_b64 = base64.b64encode(result["stego_png_bytes"]).decode("ascii")
        record_security_event(
            SecurityEvent.EventType.STEGANO_EMBED,
            user=request.user,
            ip_address=_client_ip(request),
            algorithm="lsb-png",
            success=True,
            latency_ms=latency,
            payload_size=result["payload_size_bytes"],
            sha256_hash=result["stego_sha256"],
        )
        return Response(
            {
                "stego_image_b64": stego_b64,
                "stego_sha256": result["stego_sha256"],
                "payload_sha256": result["payload_sha256"],
                "payload_size_bytes": result["payload_size_bytes"],
                "capacity_used_pct": result["capacity_used_pct"],
                "image_dimensions": result["image_dimensions"],
            },
            status=status.HTTP_200_OK,
        )


class SecurityStegoExtractView(APIView):
    """POST /api/security/steganography/extract/"""

    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request: Request) -> Response:
        uploaded = request.FILES.get("image")
        image_b64 = request.data.get("stego_image_b64")

        if uploaded is not None:
            image_bytes = uploaded.read()
        elif image_b64:
            image_bytes = base64.b64decode(image_b64)
        else:
            return Response(
                {"mensagem": "Envie 'image' (arquivo) ou 'stego_image_b64'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        start = time.perf_counter()
        try:
            extracted = extract_payload_from_png(image_bytes)
        except Exception as exc:
            latency = round((time.perf_counter() - start) * 1000, 2)
            record_security_event(
                SecurityEvent.EventType.FILE_TAMPERED,
                user=request.user,
                ip_address=_client_ip(request),
                algorithm="lsb-png",
                success=False,
                latency_ms=latency,
                metadata={"error": str(exc)},
            )
            return Response({"mensagem": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        latency = round((time.perf_counter() - start) * 1000, 2)
        payload_text = extracted["payload"].decode("utf-8", errors="replace")
        record_security_event(
            SecurityEvent.EventType.STEGANO_EXTRACT,
            user=request.user,
            ip_address=_client_ip(request),
            algorithm="lsb-png",
            success=True,
            latency_ms=latency,
            payload_size=extracted["payload_size_bytes"],
            sha256_hash=extracted["payload_sha256"],
        )
        return Response(
            {
                "extracted_payload": payload_text,
                "payload_sha256": extracted["payload_sha256"],
                "payload_size_bytes": extracted["payload_size_bytes"],
                "integrity_verified": True,
            },
            status=status.HTTP_200_OK,
        )


class SecurityAttackRunView(APIView):
    """POST /api/security/attacks/run/"""

    def post(self, request: Request) -> Response:
        attack_type = request.data.get("attack_type", "suite")
        plaintext = request.data.get("plaintext", "Dados sigilosos do processo TCU-2026 para analise criptografica.")
        secret = request.data.get("secret", "ChaveSecretaDinamica#2026")
        algorithm = request.data.get("algorithm", "spn")

        if attack_type == "brute_force":
            result = run_brute_force_attack(plaintext, secret, algorithm=algorithm)
            summary = result["summary"]
        elif attack_type == "differential":
            result = run_differential_attack(plaintext, secret, algorithm=algorithm)
            summary = result["summary"]
        elif attack_type == "statistical":
            result = run_statistical_attack(plaintext, secret, algorithm=algorithm)
            summary = result["summary"]
        elif attack_type == "suite":
            result = evaluate_security_suite(plaintext, secret, algorithm=algorithm)
            summary = result["verdict"]["justification"]
        else:
            return Response(
                {"mensagem": f"Tipo de ataque invalido: {attack_type}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        AttackExperiment.objects.create(
            attack_type=attack_type,
            algorithm=algorithm,
            metrics=result,
            verdict_summary=summary,
        )
        record_security_event(
            SecurityEvent.EventType.ATTACK_SIMULATION,
            user=request.user,
            ip_address=_client_ip(request),
            algorithm=algorithm,
            success=True,
            metadata={"attack_type": attack_type},
        )
        return Response(result, status=status.HTTP_200_OK)


class SecurityBigDataSimulateView(APIView):
    """POST /api/security/bigdata/simulate/"""

    def post(self, request: Request) -> Response:
        total_events = int(request.data.get("total_events", 2000))
        inject_anomalies = bool(request.data.get("inject_anomalies", True))
        archive_to_minio = bool(request.data.get("archive_to_minio", True))

        result = generate_experimental_events(
            total_events=total_events,
            inject_anomalies=inject_anomalies,
            archive_to_minio=archive_to_minio,
        )
        return Response(result, status=status.HTTP_201_CREATED)


class SecurityAIDetectView(APIView):
    """POST /api/security/ai/detect-anomalies/"""

    def post(self, request: Request) -> Response:
        result = detect_anomalies()
        return Response(result, status=status.HTTP_200_OK)


class SecurityDashboardView(APIView):
    """GET /api/security/dashboard/"""

    def get(self, request: Request) -> Response:
        total_events = SecurityEvent.objects.count()
        failed_events = SecurityEvent.objects.filter(success=False).count()
        auth_failures = SecurityEvent.objects.filter(event_type=SecurityEvent.EventType.AUTH_FAILURE).count()
        decrypt_failures = SecurityEvent.objects.filter(event_type=SecurityEvent.EventType.DECRYPT_FAILURE).count()
        tampered_count = SecurityEvent.objects.filter(event_type=SecurityEvent.EventType.FILE_TAMPERED).count()
        total_anomalies = AnomalyAlert.objects.count()

        by_type = list(
            SecurityEvent.objects.values("event_type")
            .annotate(count=Count("id"))
            .order_by("-count")
        )

        timeline = list(
            SecurityEvent.objects.annotate(hour=TruncHour("created_at"))
            .values("hour")
            .annotate(
                total=Count("id"),
                failures=Count("id", filter=Q(success=False)),
            )
            .order_by("hour")[:24]
        )
        timeline_serialized = [
            {
                "hour": item["hour"].isoformat() if item["hour"] else "",
                "total": item["total"],
                "failures": item["failures"],
            }
            for item in timeline
        ]

        recent_alerts = [
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
            for a in AnomalyAlert.objects.all()[:15]
        ]

        recent_attacks = [
            {
                "id": exp.id,
                "attack_type": exp.attack_type,
                "algorithm": exp.algorithm,
                "verdict_summary": exp.verdict_summary,
                "metrics": exp.metrics,
                "created_at": exp.created_at.isoformat(),
            }
            for exp in AttackExperiment.objects.all()[:10]
        ]

        return Response(
            {
                "kpis": {
                    "total_events": total_events,
                    "failed_events": failed_events,
                    "failure_rate_pct": round((failed_events / max(total_events, 1)) * 100, 2),
                    "auth_failures": auth_failures,
                    "decrypt_failures": decrypt_failures,
                    "tampered_files": tampered_count,
                    "total_anomalies": total_anomalies,
                },
                "events_by_type": by_type,
                "timeline": timeline_serialized,
                "recent_alerts": recent_alerts,
                "recent_attacks": recent_attacks,
            },
            status=status.HTTP_200_OK,
        )
