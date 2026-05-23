
from collections.abc import Mapping, Sequence

from django.db.models import Q
from shared.logger import get_logger
from shared.s3_client import get_s3_client

from core.models.analise import Analise
from core.models.palavra_chave import PalavraChave
from core.models.processo import Processo

logger = get_logger("core.services")

PDF_BUCKET_NAME = "pje-documents"


class ProcessoSemPdfLookupError(Exception):
    """Raised when pending PDF lookup cannot be completed."""


class ProcessoNotFoundError(Exception):
    """Raised when process cannot be found for requested keys."""


def _normalize_grau(grau: str) -> str:
    raw = (grau or "").strip().upper()
    if raw.startswith("G") and len(raw) > 1:
        return raw[1:]
    return raw


def _s3_object_key(numero_processo: str, grau: str) -> str:
    return f"{numero_processo}_{_normalize_grau(grau)}.pdf"


def _s3_object_exists(client, bucket_name: str, object_name: str) -> bool:
    objects = client.list_objects(bucket_name, prefix=object_name, recursive=True)
    return any(getattr(item, "object_name", "") == object_name for item in objects)


def filtrar_processos_faltantes(
    dados_entrada: Sequence[dict],
) -> list[dict]:
    # Deduplica o lote por chave unica do modelo para evitar conflitos no mesmo request.
    # Em caso de repeticao da mesma chave, mantem o item mais recente.
    deduplicado_por_chave: dict[tuple[str, str, str], dict] = {}
    for item in dados_entrada:
        chave = (
            item.get("numero_processo", ""),
            item.get("tribunal", ""),
            item.get("grau", ""),
        )

        existente = deduplicado_por_chave.get(chave)
        if existente is None:
            deduplicado_por_chave[chave] = item
            continue

        data_nova = item.get("data_hora_ultima_atualizacao")
        data_existente = existente.get("data_hora_ultima_atualizacao")
        if data_nova and (data_existente is None or data_nova > data_existente):
            deduplicado_por_chave[chave] = item

    itens_deduplicados = list(deduplicado_por_chave.values())

    numeros_entrada: list[str] = [item["numero_processo"] for item in itens_deduplicados]

    if not numeros_entrada:
        return []

    processos_no_banco = Processo.objects.filter(numero_processo__in=numeros_entrada).values(
        "numero_processo",
        "tribunal",
        "grau",
    )

    chaves_banco: Mapping[tuple[str, str, str], bool] = {
        (item["numero_processo"], item["tribunal"], item["grau"]): True
        for item in processos_no_banco
    }

    def precisa_de_processamento(item: dict) -> bool:
        chave = (
            item.get("numero_processo", ""),
            item.get("tribunal", ""),
            item.get("grau", ""),
        )
        return chave not in chaves_banco

    return [item for item in itens_deduplicados if precisa_de_processamento(item)]


def listar_processos_nao_possuem_pdf() -> list[Processo]:
    client = get_s3_client()
    candidatos = Processo.objects.filter(Q(pdf_url__isnull=True) | Q(pdf_url="")).only(
        "numero_processo",
        "grau",
        "pdf_url",
    )

    pendentes: list[Processo] = []
    for processo in candidatos:
        object_name = _s3_object_key(processo.numero_processo, processo.grau)
        try:
            exists = _s3_object_exists(client, PDF_BUCKET_NAME, object_name)
        except Exception as exc:
            raise ProcessoSemPdfLookupError("Falha ao consultar objetos PDF no S3.") from exc

        if not exists:
            pendentes.append(processo)

    return pendentes


def listar_processos_com_analise() -> list[Processo]:
    return list(
        Processo.objects.filter(analise__isnull=False).only(
            "numero_processo",
            "grau",
            "analise",
        )
    )


def listar_processos_nao_possuem_analise() -> list[Processo]:
    return list(
        Processo.objects.filter(analise__isnull=True).only(
            "numero_processo",
            "grau",
            "analise",
        )
    )


def _normalize_grau_for_query(grau: str) -> set[str]:
    normalized = _normalize_grau(grau)
    if not normalized:
        return {""}
    return {normalized, f"G{normalized}"}


def _sanitize_palavras_chave(values: list[str]) -> list[str]:
    output: list[str] = []
    for raw in values:
        normalized = (raw or "").strip()
        if normalized:
            output.append(normalized)
    return output


def montar_texto_indexacao(processo: Processo) -> str:
    """Consolida os campos do processo e sua análise em uma string canônica formatada."""
    classe_nome = processo.classe.nome if processo.classe else ""
    orgao_julgador_nome = processo.orgao_julgador.nome if processo.orgao_julgador else ""

    # Concatena assuntos com ponto e vírgula
    assuntos_list = [assunto.nome for assunto in processo.assuntos.all() if assunto.nome]
    assuntos_str = "; ".join(assuntos_list)

    analise = processo.analise
    if not analise:
        return ""

    resumo = analise.resumo or ""
    decisao = analise.decisao or ""

    # Concatena palavras-chave com ponto e vírgula
    palavras_list = [pc.nome for pc in analise.palavras_chave.all() if pc.nome]
    palavras_str = "; ".join(palavras_list)

    desfecho = analise.desfecho or ""
    resultado_reclamante = analise.resultado_reclamante or ""

    texto_canonico = (
        f"classe: {classe_nome}\n"
        f"orgao_julgador: {orgao_julgador_nome}\n"
        f"assuntos: {assuntos_str}\n"
        f"resumo: {resumo}\n"
        f"decisao: {decisao}\n"
        f"palavras_chave: {palavras_str}\n"
        f"desfecho: {desfecho}\n"
        f"resultado_reclamante: {resultado_reclamante}"
    )
    return texto_canonico


def adicionar_analise_ao_processo(numero_processo: str, grau: str, analise_data: dict) -> Processo:
    graus = _normalize_grau_for_query(grau)
    processo = Processo.objects.filter(
        numero_processo=numero_processo,
    ).filter(
        Q(grau__in=graus)
    ).first()

    if processo is None:
        raise ProcessoNotFoundError("Processo nao encontrado para numero e grau informados.")

    palavras_chave = _sanitize_palavras_chave(analise_data.pop("palavras_chave", []))

    if processo.analise is None:
        processo.analise = Analise.objects.create(**analise_data)
    else:
        for attr, value in analise_data.items():
            setattr(processo.analise, attr, value)
        processo.analise.save()

    processo.analise.palavras_chave.clear()
    for palavra in palavras_chave:
        palavra_obj, _ = PalavraChave.objects.get_or_create(nome=palavra)
        processo.analise.palavras_chave.add(palavra_obj)

    processo.save(update_fields=["analise"])

    # Pipeline Síncrona de Geração de Embeddings
    try:
        from shared.embeddings import embed_text
        texto = montar_texto_indexacao(processo)
        if texto:
            logger.info(f"Gerando embedding síncrono para processo_id={processo.id}...")
            embedding = embed_text(texto)
            processo.analise.embedding = embedding
            processo.analise.save(update_fields=["embedding"])
            logger.info(f"Embedding síncrono salvo com sucesso para processo_id={processo.id}.")
    except Exception as exc:
        logger.exception(f"Erro ao gerar ou salvar embedding para o processo {processo.id}: {exc}")

    return processo


def buscar_processos_semanticos(consulta: str, top_k: int = 5) -> list[Processo]:
    """Realiza a busca vetorial por similaridade de cosseno direto no banco de dados."""
    from pgvector.django import CosineDistance
    from shared.embeddings import embed_text

    logger.info(f"Iniciando busca semântica para consulta: '{consulta}' | top_k={top_k}")
    query_embedding = embed_text(consulta)

    processos = Processo.objects.filter(analise__embedding__isnull=False) \
        .select_related("classe", "orgao_julgador", "analise") \
        .prefetch_related("assuntos", "analise__palavras_chave") \
        .annotate(similaridade=1 - CosineDistance("analise__embedding", query_embedding)) \
        .order_by("-similaridade")[:top_k]

    return list(processos)


def reindexar_processos_sem_embedding() -> int:
    """Calcula e persiste o embedding para todos os processos que possuem análise mas não possuem embedding calculado."""
    # Filtra processos que possuem análise, mas cujo embedding na análise é nulo
    processos = Processo.objects.filter(
        analise__isnull=False,
        analise__embedding__isnull=True
    ).select_related("classe", "orgao_julgador", "analise").prefetch_related("assuntos")

    total = processos.count()
    if total == 0:
        logger.info("Nenhum processo pendente de indexação vetorial.")
        return 0

    logger.info(f"Encontrados {total} processos pendentes de indexação vetorial. Iniciando processamento...")

    from shared.embeddings import embed_text

    count = 0
    for processo in processos:
        try:
            texto = montar_texto_indexacao(processo)
            if texto:
                embedding = embed_text(texto)
                processo.analise.embedding = embedding
                processo.analise.save(update_fields=["embedding"])
                count += 1
                if count % 10 == 0 or count == total:
                    logger.info(f"Progresso: {count}/{total} processos indexados.")
        except Exception as exc:
            logger.exception(f"Falha ao gerar embedding para processo_id={processo.id}: {exc}")

    return count

