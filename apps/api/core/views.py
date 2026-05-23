# Endpoints necessarios ate agr

# Deduplicate Processes
# Recebe vários processos e retorna os processos ainda não presentes no banco, baseado no numero do processo e na última data de atualização

"""Endpoints necessarios ate agr.

Deduplicate Processes
Recebe vários processos e retorna os processos ainda não presentes no banco,
baseado no numero do processo e na última data de atualização.

Endpoint: POST /processos/deduplicar

Adicionar Analise
Recebe o numero do proesso e os campos provenientes da analise e adiciona ao
processo correspondente.

Endpoint: POST /processos/adicionar-analise
"""

# Endpoint: POST /processos/deduplicar

# Adicionar Analise
# Recebe o numero do proesso e os campos provenientes da analise e adiciona ao processo correspondente

# Endpoint: POST /processos/adicionar-analise

from django.db import IntegrityError, transaction
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response

from core.serializers.processo_serializer import (
    ProcessoAdicionarAnaliseEntradaSerializer,
    ProcessoDeduplicarEntradaSerializer,
    ProcessoResumoSerializer,
    ProcessoSemPdfResumoSerializer,
    ProcessoSerializer,
)
from core.services import (
    ProcessoNotFoundError,
    ProcessoSemPdfLookupError,
    adicionar_analise_ao_processo,
    filtrar_processos_faltantes,
    listar_processos_nao_possuem_analise,
    listar_processos_nao_possuem_pdf,
)


class ProcessoViewset(viewsets.ViewSet):


    @action(detail=False, methods=['post'])
    def deduplicar(self, request: Request):
        input_serializer = ProcessoDeduplicarEntradaSerializer(data=request.data, many=True)
        input_serializer.is_valid(raise_exception=True)

        processos_filtrados = filtrar_processos_faltantes(input_serializer.validated_data)

        try:
            with transaction.atomic():
                created_items = [ProcessoSerializer().create(item) for item in processos_filtrados]
        except IntegrityError as exc:
            raise ValidationError(
                {
                    "mensagem": "Falha ao persistir lote de processos. Nenhum processo foi criado.",
                    "detalhes": str(exc),
                }
            ) from exc

        output_serializer = ProcessoResumoSerializer(created_items, many=True)

        return Response(output_serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def nao_possuem_pdf(self, request: Request):
        try:
            processos = listar_processos_nao_possuem_pdf()
        except ProcessoSemPdfLookupError as exc:
            return Response(
                {
                    "mensagem": "Falha ao consultar pendencias de PDF.",
                    "detalhes": str(exc),
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        output_serializer = ProcessoSemPdfResumoSerializer(processos, many=True)
        return Response(output_serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def nao_possuem_analise(self, request: Request):
        processos = listar_processos_nao_possuem_analise()
        output_serializer = ProcessoSemPdfResumoSerializer(processos, many=True)
        return Response(output_serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def adicionar_analise(self, request: Request):
        input_serializer = ProcessoAdicionarAnaliseEntradaSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        payload = input_serializer.validated_data
        try:
            processo = adicionar_analise_ao_processo(
                numero_processo=payload["numero_processo"],
                grau=payload["grau"],
                analise_data=dict(payload["analise"]),
            )
        except ProcessoNotFoundError as exc:
            return Response(
                {
                    "mensagem": "Processo nao encontrado.",
                    "detalhes": str(exc),
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        output_serializer = ProcessoResumoSerializer(processo)
        return Response(output_serializer.data, status=status.HTTP_200_OK)

