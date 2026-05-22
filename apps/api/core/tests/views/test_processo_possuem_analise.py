import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api.settings")

import django
import pytest
from rest_framework import status
from rest_framework.test import APIClient

django.setup()

from core.models.analise import Analise
from core.tests.constants import DATA_BASE, POSSUEM_ANALISE_ENDPOINT, PROCESSO_NUMERO_1, PROCESSO_NUMERO_2
from core.tests.helpers import DataSetup

pytestmark = pytest.mark.django_db


class TestProcessoViewsetPossuemAnalise:
    def test_given_empty_database_when_get_possuem_analise_then_return_empty_list(self):
        api_client = APIClient()

        response = api_client.get(POSSUEM_ANALISE_ENDPOINT)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_given_process_with_analise_when_get_then_return_resumo_with_normalized_grau(self):
        api_client = APIClient()
        analise = Analise.objects.create(resumo="Resumo teste")
        processo = DataSetup.create_processo_existente(
            numero_processo=PROCESSO_NUMERO_1,
            data_hora_ultima_atualizacao=DATA_BASE,
            grau="G1",
            pdf_url="s3://pje-documents/000.pdf",
        )
        processo.analise = analise
        processo.save(update_fields=["analise"])

        response = api_client.get(POSSUEM_ANALISE_ENDPOINT)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == [{"numero_processo": PROCESSO_NUMERO_1, "grau": "1"}]

    def test_given_process_without_analise_when_get_then_do_not_return_process(self):
        api_client = APIClient()
        DataSetup.create_processo_existente(
            numero_processo=PROCESSO_NUMERO_2,
            data_hora_ultima_atualizacao=DATA_BASE,
            grau="G2",
            pdf_url="s3://pje-documents/000.pdf",
        )

        response = api_client.get(POSSUEM_ANALISE_ENDPOINT)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []