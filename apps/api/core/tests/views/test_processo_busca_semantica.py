import os
from unittest.mock import patch

import pytest
from rest_framework import status
from rest_framework.test import APIClient

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api.settings")

import django

django.setup()

from core.models.analise import Analise
from core.models.processo import Processo
from core.tests.constants import DATA_BASE, TRIBUNAL_TRT6
from core.tests.helpers import DataSetup

BUSCA_SEMANTICA_ENDPOINT = "/api/processos/busca_semantica/"

pytestmark = pytest.mark.django_db


class TestProcessoViewsetBuscaSemantica:
    @patch("shared.embeddings.embed_text")
    def test_given_valid_query_when_post_busca_semantica_then_return_results_ordered_by_similarity(self, mock_embed):
        # Configura o mock do embedding da busca: Vetor unitário apontando na dimensão 0
        vector_query = [1.0] + [0.0] * 383
        mock_embed.return_value = vector_query

        # Cria Processo 1 com embedding idêntico (similaridade = 1.0)
        p1 = DataSetup.create_processo_existente(
            numero_processo="00000012026506000001",
            data_hora_ultima_atualizacao=DATA_BASE,
            tribunal=TRIBUNAL_TRT6,
            grau="G1",
        )
        analise1 = Analise.objects.create(
            resumo="Processo cobrando horas extras decorrentes de jornada excessiva.",
            embedding=[1.0] + [0.0] * 383,
        )
        p1.analise = analise1
        p1.save()

        # Cria Processo 2 com embedding ortogonal (similaridade = 0.0)
        p2 = DataSetup.create_processo_existente(
            numero_processo="00000022026506000002",
            data_hora_ultima_atualizacao=DATA_BASE,
            tribunal=TRIBUNAL_TRT6,
            grau="G1",
        )
        analise2 = Analise.objects.create(
            resumo="Processo solicitando indenização por suposto dano moral.",
            embedding=[0.0, 1.0] + [0.0] * 382,
        )
        p2.analise = analise2
        p2.save()

        # Cria Processo 3 sem embedding (não deve ser retornado)
        p3 = DataSetup.create_processo_existente(
            numero_processo="00000032026506000003",
            data_hora_ultima_atualizacao=DATA_BASE,
            tribunal=TRIBUNAL_TRT6,
            grau="G1",
        )

        api_client = APIClient()
        payload = {
            "consulta": "horas extras por jornada extra",
            "top_k": 5,
        }

        response = api_client.post(BUSCA_SEMANTICA_ENDPOINT, payload, format="json")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        items = data["items"]

        # Processo sem embedding (p3) não deve constar na busca
        assert len(items) == 2

        # Primeiro item deve ser o p1 (similaridade máxima de 1.0)
        assert items[0]["numero_processo"] == "00000012026506000001"
        assert items[0]["similaridade"] == 1.0
        assert items[0]["analise"]["resumo"] == "Processo cobrando horas extras decorrentes de jornada excessiva."

        # Segundo item deve ser o p2 (similaridade de 0.0)
        assert items[1]["numero_processo"] == "00000022026506000002"
        assert items[1]["similaridade"] == 0.0

    def test_given_missing_consulta_when_post_busca_semantica_then_return_400(self):
        api_client = APIClient()
        payload = {
            "top_k": 3,
        }
        response = api_client.post(BUSCA_SEMANTICA_ENDPOINT, payload, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
