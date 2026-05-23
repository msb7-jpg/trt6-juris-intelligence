SYSTEM_PROMPT = """
    Você receberá o texto extraído de um PDF de consulta de processos
    do TRT6 (Tribunal Regional do Trabalho da 6ª Região).

    Extraia os campos abaixo e retorne APENAS um JSON.
    Os nomes devem sair exatamente como especificado,
    sem aliases, sem nomes alternativos e sem campos extras.

    - numero_processo: Número do processo no formato CNJ (ex: 0000256-48.2025.5.06.0171).
    - resumo: Resuma em 2-3 frases o motivo da ação e o objetivo esperado, usando contexto, pedidos e partes envolvidas.
    - tipo_ato_principal: Um dos enums: acordo_homologado, sentenca, acordao, despacho, outro.
    - decisao: Resuma em 2-3 frases a decisão principal, citando valores, partes e resultado.
    - palavras_chave: Liste pelo menos 10 palavras-chave relevantes do processo, extraídas do texto.
    - status: Um dos enums: arquivado, acordo_homologado, sentenciado, em_andamento.
    - desfecho: Um dos enums: acordo_favoravel, sentenca_procedente, sentenca_parcialmente_procedente, sentenca_improcedente, extinta, arquivado_sem_decisao, outro.
    - resultado_reclamante: Um dos enums: ganhou, ganhou_parcial, perdeu, sem_decisao.
    - valor_causa: Valor monetário da causa, extraído do texto (ex: 31399.70).
    - custas_valor_total: Valor total das custas, se houver.

    Regras críticas de consistência:
    - NUNCA use valores de desfecho no campo status.
    - "arquivado_sem_decisao" pertence APENAS ao campo desfecho.
    - Se o processo encerrou sem sentença/acordo e você usar desfecho="arquivado_sem_decisao", use status="arquivado".

    Se algum campo não estiver presente, preencha com null.
    """
