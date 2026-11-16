# Generated for Projeto 2 security models: SecurityEvent, AnomalyAlert, AttackExperiment.

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("core", "0008_buscasalva_last_results"),
    ]

    operations = [
        migrations.CreateModel(
            name="AnomalyAlert",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "anomaly_type",
                    models.CharField(
                        choices=[
                            ("AUTH_BRUTE_FORCE", "Tentativas Incomuns de Autenticacao"),
                            ("HIGH_DECRYPT_FAIL_RATE", "Frequencia Elevada de Falhas de Descriptografia"),
                            ("FILE_ALTERATION", "Alteracao Inesperada em Arquivo"),
                            ("ATYPICAL_ACCESS_PATTERN", "Padrao Atipico de Acesso"),
                            ("EVENT_BURST", "Comportamento Incomum na Geracao de Eventos"),
                        ],
                        db_index=True,
                        max_length=40,
                    ),
                ),
                (
                    "severity",
                    models.CharField(
                        choices=[("LOW", "Baixa"), ("MEDIUM", "Media"), ("HIGH", "Alta"), ("CRITICAL", "Critica")],
                        default="MEDIUM",
                        max_length=16,
                    ),
                ),
                ("actor_label", models.CharField(blank=True, default="system", max_length=150)),
                ("score", models.FloatField(help_text="Anomaly score from IsolationForest / Z-score")),
                ("event_count", models.IntegerField(default=0)),
                ("summary", models.TextField()),
                ("details", models.JSONField(blank=True, default=dict)),
                ("detected_at", models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
            ],
            options={
                "ordering": ["-detected_at"],
            },
        ),
        migrations.CreateModel(
            name="AttackExperiment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("attack_type", models.CharField(db_index=True, max_length=32)),
                ("algorithm", models.CharField(max_length=32)),
                ("metrics", models.JSONField(default=dict)),
                ("verdict_summary", models.TextField(blank=True, default="")),
                ("created_at", models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="SecurityEvent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("actor_label", models.CharField(blank=True, db_index=True, default="anonymous", max_length=150)),
                ("ip_address", models.GenericIPAddressField(blank=True, db_index=True, null=True)),
                (
                    "event_type",
                    models.CharField(
                        choices=[
                            ("CRYPTO_ENCRYPT", "Cifragem"),
                            ("CRYPTO_DECRYPT", "Decifragem"),
                            ("DECRYPT_FAILURE", "Falha de Descriptografia"),
                            ("AUTH_SUCCESS", "Autenticacao Sucesso"),
                            ("AUTH_FAILURE", "Falha de Autenticacao"),
                            ("STEGANO_EMBED", "Esteganografia Embed"),
                            ("STEGANO_EXTRACT", "Esteganografia Extract"),
                            ("FILE_INTEGRITY_CHECK", "Verificacao de Integridade"),
                            ("FILE_TAMPERED", "Alteracao Inesperada de Arquivo"),
                            ("ATTACK_SIMULATION", "Simulacao de Ataque"),
                        ],
                        db_index=True,
                        max_length=32,
                    ),
                ),
                ("algorithm", models.CharField(blank=True, default="", max_length=32)),
                ("success", models.BooleanField(db_index=True, default=True)),
                ("latency_ms", models.FloatField(default=0.0)),
                ("payload_size", models.IntegerField(default=0)),
                ("sha256_hash", models.CharField(blank=True, default="", max_length=64)),
                ("is_synthetic", models.BooleanField(db_index=True, default=False)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="security_events",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
                "indexes": [
                    models.Index(fields=["event_type", "created_at"], name="core_securi_event_t_2e7025_idx"),
                    models.Index(fields=["actor_label", "created_at"], name="core_securi_actor_l_6985f6_idx"),
                ],
            },
        ),
    ]
