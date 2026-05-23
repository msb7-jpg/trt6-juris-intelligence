import os

import pytest
from rest_framework import status
from rest_framework.test import APIClient

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api.settings")

import django

django.setup()

from core.models.processo import Processo
from core.tests.constants import DATA_BASE, PROCESSO_NUMERO_1, TRIBUNAL_TRT6
from core.tests.helpers import DataSetup

ADICIONAR_ANALISE_ENDPOINT = "/api/processos/adicionar_analise/"

pytestmark = pytest.mark.django_db


class TestProcessoViewsetAdicionarAnalise:
    def test_given_existing_processo_when_post_adicionar_analise_then_create_analysis(self):
        api_client = APIClient()
        DataSetup.create_processo_existente(
            numero_processo=PROCESSO_NUMERO_1,
            data_hora_ultima_atualizacao=DATA_BASE,
            tribunal=TRIBUNAL_TRT6,
            grau="G1",
        )

        payload = {
            "numero_processo": PROCESSO_NUMERO_1,
            "grau": "1",
            "analise": {
                "resumo": "Resumo teste",
                "tipo_ato_principal": "sentenca",
                "decisao": "Decisao teste",
                "palavras_chave": ["trabalho", "rescisao"],
                "status": "sentenciado",
                "desfecho": "sentenca_procedente",
                "resultado_reclamante": "ganhou",
                "valor_causa": "1234.56",
                "custas_valor_total": "99.99",
            },
        }

        response = api_client.post(ADICIONAR_ANALISE_ENDPOINT, payload, format="json")

        assert response.status_code == status.HTTP_200_OK
        processo = Processo.objects.get(numero_processo=PROCESSO_NUMERO_1, grau="G1")
        assert processo.analise is not None
        assert processo.analise.resumo == "Resumo teste"
        assert processo.analise.palavras_chave.count() == 2

    def test_given_existing_analysis_when_post_adicionar_analise_then_update_existing(self):
        api_client = APIClient()
        processo = DataSetup.create_processo_existente(
            numero_processo=PROCESSO_NUMERO_1,
            data_hora_ultima_atualizacao=DATA_BASE,
            tribunal=TRIBUNAL_TRT6,
            grau="G1",
        )

        first_payload = {
            "numero_processo": PROCESSO_NUMERO_1,
            "grau": "1",
            "analise": {
                "resumo": "Resumo inicial",
                "palavras_chave": ["inicial"],
                "status": "em_andamento",
            },
        }
        second_payload = {
            "numero_processo": PROCESSO_NUMERO_1,
            "grau": "1",
            "analise": {
                "resumo": "Resumo atualizado",
                "palavras_chave": ["atualizado", "final"],
                "status": "arquivado",
            },
        }

        response_1 = api_client.post(ADICIONAR_ANALISE_ENDPOINT, first_payload, format="json")
        assert response_1.status_code == status.HTTP_200_OK
        analise_id = Processo.objects.get(pk=processo.pk).analise_id

        response_2 = api_client.post(ADICIONAR_ANALISE_ENDPOINT, second_payload, format="json")
        assert response_2.status_code == status.HTTP_200_OK

        processo.refresh_from_db()
        assert processo.analise_id == analise_id
        assert processo.analise.resumo == "Resumo atualizado"
        assert processo.analise.status == "arquivado"
        assert sorted([p.nome for p in processo.analise.palavras_chave.all()]) == ["atualizado", "final"]

    def test_given_missing_processo_when_post_adicionar_analise_then_return_404(self):
        api_client = APIClient()
        payload = {
            "numero_processo": PROCESSO_NUMERO_1,
            "grau": "1",
            "analise": {
                "resumo": "Resumo teste",
                "palavras_chave": ["chave"],
            },
        }

        response = api_client.post(ADICIONAR_ANALISE_ENDPOINT, payload, format="json")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "mensagem" in response.json()

    def test_given_desfecho_value_in_status_when_post_adicionar_analise_then_normalize_and_accept(self):
        api_client = APIClient()
        DataSetup.create_processo_existente(
            numero_processo=PROCESSO_NUMERO_1,
            data_hora_ultima_atualizacao=DATA_BASE,
            tribunal=TRIBUNAL_TRT6,
            grau="G1",
        )

        payload = {
            "numero_processo": PROCESSO_NUMERO_1,
            "grau": "1",
            "analise": {
                "resumo": "Resumo teste",
                "status": "arquivado_sem_decisao",
                "desfecho": "arquivado_sem_decisao",
                "palavras_chave": ["teste"],
            },
        }

        response = api_client.post(ADICIONAR_ANALISE_ENDPOINT, payload, format="json")

        assert response.status_code == status.HTTP_200_OK
        processo = Processo.objects.get(numero_processo=PROCESSO_NUMERO_1, grau="G1")
        assert processo.analise is not None
        assert processo.analise.status == "arquivado"
        assert processo.analise.desfecho == "arquivado_sem_decisao"
