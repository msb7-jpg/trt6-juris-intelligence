from shared.llm_constants import SYSTEM_PROMPT
from shared.schemas.resumo_ia import ProcessoAnalise


def test_processo_analise_schema_matches_expected_contract():
    expected_properties = {
        "numero_processo",
        "resumo",
        "tipo_ato_principal",
        "decisao",
        "palavras_chave",
        "status",
        "desfecho",
        "resultado_reclamante",
        "valor_causa",
        "custas_valor_total",
    }

    assert set(ProcessoAnalise.SCHEMA["properties"].keys()) == expected_properties
    assert ProcessoAnalise.SCHEMA["additionalProperties"] is False
    assert ProcessoAnalise.SCHEMA["properties"]["palavras_chave"]["minItems"] == 10


def test_system_prompt_uses_api_field_names_only():
    expected_fields = [
        "numero_processo",
        "resumo",
        "tipo_ato_principal",
        "decisao",
        "palavras_chave",
        "status",
        "desfecho",
        "resultado_reclamante",
        "valor_causa",
        "custas_valor_total",
    ]
    legacy_fields = [
        "tribunal",
        "classe_nome",
        "orgao_julgador_nome",
        "data_ajuizamento",
        "tempo_tramitacao",
        "status_processo",
        "decisao_resumo",
        "palavras_chave_processo",
        "palavras_chave_desfecho",
    ]

    for field in expected_fields:
        assert f"- {field}:" in SYSTEM_PROMPT

    for field in legacy_fields:
        assert field not in SYSTEM_PROMPT
