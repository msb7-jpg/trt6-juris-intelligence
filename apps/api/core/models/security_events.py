"""Models for Big Data security events, AI anomaly alerts, and cryptographic attack experiments."""

from django.conf import settings
from django.db import models
from django.utils import timezone


class SecurityEvent(models.Model):
    """High-volume event log for crypto, auth, steganography, and file integrity operations."""

    class EventType(models.TextChoices):
        CRYPTO_ENCRYPT = "CRYPTO_ENCRYPT", "Cifragem"
        CRYPTO_DECRYPT = "CRYPTO_DECRYPT", "Decifragem"
        DECRYPT_FAILURE = "DECRYPT_FAILURE", "Falha de Descriptografia"
        AUTH_SUCCESS = "AUTH_SUCCESS", "Autenticacao Sucesso"
        AUTH_FAILURE = "AUTH_FAILURE", "Falha de Autenticacao"
        STEGANO_EMBED = "STEGANO_EMBED", "Esteganografia Embed"
        STEGANO_EXTRACT = "STEGANO_EXTRACT", "Esteganografia Extract"
        FILE_INTEGRITY_CHECK = "FILE_INTEGRITY_CHECK", "Verificacao de Integridade"
        FILE_TAMPERED = "FILE_TAMPERED", "Alteracao Inesperada de Arquivo"
        ATTACK_SIMULATION = "ATTACK_SIMULATION", "Simulacao de Ataque"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="security_events",
    )
    actor_label = models.CharField(max_length=150, blank=True, default="anonymous", db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True, db_index=True)
    event_type = models.CharField(max_length=32, choices=EventType.choices, db_index=True)
    algorithm = models.CharField(max_length=32, blank=True, default="")
    success = models.BooleanField(default=True, db_index=True)
    latency_ms = models.FloatField(default=0.0)
    payload_size = models.IntegerField(default=0)
    sha256_hash = models.CharField(max_length=64, blank=True, default="")
    is_synthetic = models.BooleanField(default=False, db_index=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["event_type", "created_at"]),
            models.Index(fields=["actor_label", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"[{self.event_type}] {self.actor_label} ({'ok' if self.success else 'fail'})"


class AnomalyAlert(models.Model):
    """Anomalies detected by the AI model (IsolationForest / statistical fallback)."""

    class AnomalyType(models.TextChoices):
        AUTH_BRUTE_FORCE = "AUTH_BRUTE_FORCE", "Tentativas Incomuns de Autenticacao"
        HIGH_DECRYPT_FAIL_RATE = "HIGH_DECRYPT_FAIL_RATE", "Frequencia Elevada de Falhas de Descriptografia"
        FILE_ALTERATION = "FILE_ALTERATION", "Alteracao Inesperada em Arquivo"
        ATYPICAL_ACCESS_PATTERN = "ATYPICAL_ACCESS_PATTERN", "Padrao Atipico de Acesso"
        EVENT_BURST = "EVENT_BURST", "Comportamento Incomum na Geracao de Eventos"

    class Severity(models.TextChoices):
        LOW = "LOW", "Baixa"
        MEDIUM = "MEDIUM", "Media"
        HIGH = "HIGH", "Alta"
        CRITICAL = "CRITICAL", "Critica"

    anomaly_type = models.CharField(max_length=40, choices=AnomalyType.choices, db_index=True)
    severity = models.CharField(max_length=16, choices=Severity.choices, default=Severity.MEDIUM)
    actor_label = models.CharField(max_length=150, blank=True, default="system")
    score = models.FloatField(help_text="Anomaly score from IsolationForest / Z-score")
    event_count = models.IntegerField(default=0)
    summary = models.TextField()
    details = models.JSONField(default=dict, blank=True)
    detected_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        ordering = ["-detected_at"]

    def __str__(self) -> str:
        return f"[{self.severity}] {self.anomaly_type} ({self.actor_label})"


class AttackExperiment(models.Model):
    """Persisted results of controlled attack simulations (Brute Force, Differential, Statistical)."""

    attack_type = models.CharField(max_length=32, db_index=True)
    algorithm = models.CharField(max_length=32)
    metrics = models.JSONField(default=dict)
    verdict_summary = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.attack_type} ({self.algorithm}) @ {self.created_at:%Y-%m-%d %H:%M}"
