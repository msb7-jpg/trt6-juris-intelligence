
import json
import os
import tempfile
from pathlib import Path
from typing import Any

import opendataloader_pdf
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from shared.schemas.resumo_ia import ProcessoAnalise

DEFAULT_INPUT_PATH = "output/mock.md"


def build_system_prompt() -> str:
    return """
    Você receberá o texto extraído de um PDF de consulta de processos do TRT6 (Tribunal Regional do Trabalho da 6ª Região).

    Extraia os seguintes campos e retorne APENAS um JSON com a estrutura abaixo. Siga as regras para cada campo:

    - numero_processo: Extraia o número do processo no formato CNJ (ex: 0000256-48.2025.5.06.0171).
    - tribunal: Sempre "TRT6".
    - classe_nome: Extraia o nome da classe processual (ex: "Ação Trabalhista - Rito Sumaríssimo").
    - orgao_julgador_nome: Nome da vara ou órgão julgador (ex: "1ª Vara do Trabalho do Cabo").
    - data_ajuizamento: Data em que o processo foi ajuizado, formato YYYY-MM-DD (ex: 2025-04-15).
    - tempo_tramitacao: Tempo total de tramitação do processo, calculado a partir da data de ajuizamento até a data da última decisão, em dias.
    - resumo: Resuma em 2-3 frases qual foi motivo de abertura da ação, e objetivo esperado a ser alcançado, usando informações do texto, incluindo pedidos, contexto e partes envolvidas.
    - tipo_ato_principal: Classifique como um dos enums: acordo_homologado, sentenca, acordao, despacho, outro. Use palavras-chave como "ACORDO HOMOLOGADO", "SENTENÇA", "DESPACHO".
    - decisao: Resuma em 2-3 frases a decisão principal, citando valores, partes e resultado.
    - palavras_chave: Liste pelo menos 5 palavras-chave relevantes do processo, extraídas do texto que consigam classificar o processo e encontrar outros similares e liste mais 5 palavras chaves relacionadas ao desfecho.
    - status: Classifique como um dos enums: arquivado, acordo_homologado, sentenciado, em_andamento. Use regras: "arquivem-se" => arquivado; "acordo homologado" => acordo_homologado; "sentença" sem arquivamento => sentenciado; senão em_andamento.
    - desfecho: Classifique como um dos enums: acordo_favoravel, sentenca_procedente, sentenca_parcialmente_procedente, sentenca_improcedente, extinta, arquivado_sem_decisao, outro. Use palavras-chave e contexto.
    - resultado_reclamante: Classifique como um dos enums: ganhou, ganhou_parcial, perdeu, sem_decisao. Use o desfecho para inferir.
    - valor_causa: Valor monetário da causa, extraído do texto (ex: 31399.70).
    - custas_valor_total: Valor total das custas, se houver.

    Se algum campo não estiver presente, preencha com null.
    """


def _build_llm() -> ChatOpenAI:
    return ChatOpenAI(
        base_url=os.getenv("WORKER_LLM_BASE_URL", "http://172.26.192.1:1234/v1"),
        api_key=os.getenv("WORKER_LLM_API_KEY", "lm-studio"),
        model_name=os.getenv("WORKER_LLM_MODEL", "google/gemma-3-4b"),
    )


def _markdown_from_pdf(pdf_path: Path) -> str:
    with tempfile.TemporaryDirectory() as tmpdir:
        opendataloader_pdf.convert(
            input_path=[str(pdf_path)],
            output_dir=tmpdir,
            image_output="off",
            format="markdown",
        )
        generated = sorted(Path(tmpdir).glob("*.md"))
        if not generated:
            raise RuntimeError("Nao foi possivel extrair markdown do PDF.")
        return generated[0].read_text(encoding="utf-8")


def extract_text_from_document(path: str) -> str:
    input_path = Path(path)
    if input_path.suffix.lower() == ".pdf":
        return _markdown_from_pdf(input_path)
    return input_path.read_text(encoding="utf-8")


def analyze_text(pdf_text: str) -> ProcessoAnalise:
    agent = create_agent(
        model=_build_llm(),
        response_format=ProcessoAnalise,
    )
    response = agent.invoke(
        {
            "messages": [
                {"role": "system", "content": build_system_prompt()},
                {"role": "user", "content": f"Texto extraído do PDF:\n{pdf_text}"},
            ]
        }
    )

    if "structured_response" not in response:
        raise RuntimeError("LLM nao retornou structured_response.")
    return response["structured_response"]


def analyze_file(file_path: str) -> ProcessoAnalise:
    return analyze_text(extract_text_from_document(file_path))


def save_response(result: Any, path: str = "result.json"):
    with open(path, "w", encoding="utf-8") as f:
        if hasattr(result, "model_dump"):
            json.dump(result.model_dump(mode="json"), f, ensure_ascii=False, indent=2)
        elif isinstance(result, dict):
            json.dump(result, f, ensure_ascii=False, indent=2)
        else:
            f.write(str(result))


def main():
    input_path = os.getenv("WORKER_LLM_INPUT_PATH", DEFAULT_INPUT_PATH)
    response = analyze_file(input_path)
    save_response(response)


if __name__ == "__main__":
    main()
