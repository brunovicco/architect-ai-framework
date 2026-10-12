"""Bilingual (pt-BR / en) UI strings for the Streamlit app.

This module only affects presentation. The decision engine (`engine.py`)
always computes and returns English strings so its behavior and tests stay
language-independent; `translate_items`/`translate_pattern`/`translate_criterion`
map that fixed set of English strings to Portuguese for display only.
"""

LANGS = ("pt-BR", "en")
DEFAULT_LANG = "pt-BR"

# Single source of truth for the method's 9 steps (letter + name), in order.
# The sidebar list and every tab subheader are built from this so the two
# can never drift apart (e.g. "Trust" vs "Trust & Controls"). Each language
# spells its own real word: ARQUITETO in Portuguese, ARCHITECT (its literal
# English translation) in English — not a letter-by-letter transliteration.
STEPS = {
    "pt-BR": [
        ("A", "Alvo"),
        ("R", "Requisitos"),
        ("Q", "Quem faz o quê"),
        ("U", "Uso arquitetural"),
        ("I", "Integração & Informação"),
        ("T", "Trust & Controls"),
        ("E", "Evaluation"),
        ("T", "Trade-offs"),
        ("O", "Operação"),
    ],
    "en": [
        ("A", "Aim"),
        ("R", "Requirements"),
        ("C", "Composition"),
        ("H", "Harness"),
        ("I", "Integration & Information"),
        ("T", "Trust & Controls"),
        ("E", "Evaluation"),
        ("C", "Comparison"),
        ("T", "Telemetry"),
    ],
}

BRAND = {"pt-BR": "ARQUITETO", "en": "ARCHITECT"}

# Which STEPS indexes (0-based, in method order) each tab's subheader covers.
_TAB_STEP_INDEXES = {
    "t1_subheader": (0, 1),  # A, R
    "t2_subheader": (2, 3),  # who-does-what, usage pattern
    "t3_subheader": (4,),  # I
    "t4_subheader": (5, 6, 8),  # Trust & Controls, Evaluation, Operations
    "t5_subheader": (7,),  # Trade-offs
}

UI = {
    "lang_label": {"pt-BR": "Idioma", "en": "Language"},
    "load_example_button": {
        "pt-BR": "📂 Carregar exemplo: Investment Assistant",
        "en": "📂 Load example: Investment Assistant",
    },
    "clear_form_button": {"pt-BR": "🧹 Limpar formulário", "en": "🧹 Clear form"},
    "app_title": {"pt-BR": "🏛️ ARQUITETO", "en": "🏛️ ARCHITECT"},
    "app_caption": {
        "pt-BR": "Decisões de arquitetura de IA / LLM neutras em relação a fornecedor — do problema de negócio ao plano operacional.",
        "en": "Vendor-neutral AI / LLM architecture decisions — from business problem to operating plan. (English rendition of the ARQUITETO method.)",
    },
    "sidebar_header": {"pt-BR": "Framework", "en": "Framework"},
    "sidebar_rule": {
        "pt-BR": "Regra: prefira a arquitetura mais simples que satisfaça os requisitos obrigatórios e mantenha a aplicação crítica fora do comportamento probabilístico do modelo.",
        "en": "Rule: prefer the simplest architecture that satisfies hard requirements and keep critical enforcement outside probabilistic model behavior.",
    },
    "tab_1": {"pt-BR": "1 · A/R", "en": "1 · A/R"},
    "tab_2": {"pt-BR": "2 · Q/U", "en": "2 · C/H"},
    "tab_3": {"pt-BR": "3 · I", "en": "3 · I"},
    "tab_4": {"pt-BR": "4 · T/E/O", "en": "4 · T/E/T"},
    "tab_5": {"pt-BR": "5 · Trade-offs", "en": "5 · Comparison"},
    "tab_6": {"pt-BR": "6 · Plano", "en": "6 · Plan"},
    "case_name_label": {"pt-BR": "Nome do caso", "en": "Case name"},
    "case_name_default": {"pt-BR": "Caso de Arquitetura de IA", "en": "AI Architecture Case"},
    "business_problem_label": {"pt-BR": "Problema de negócio", "en": "Business problem"},
    "business_problem_placeholder": {
        "pt-BR": "O que precisa mudar para o negócio/usuário?",
        "en": "What needs to change for the business/user?",
    },
    "desired_outcome_label": {"pt-BR": "Resultado desejado", "en": "Desired outcome"},
    "desired_outcome_placeholder": {
        "pt-BR": "Qual resultado mensurável define sucesso?",
        "en": "What measurable result defines success?",
    },
    "users_label": {"pt-BR": "Usuários / público", "en": "Users / audience"},
    "users_placeholder": {
        "pt-BR": "Quem usa ou é afetado pelo sistema?",
        "en": "Who uses or is affected by the system?",
    },
    "quality_target_label": {"pt-BR": "Meta de qualidade", "en": "Quality target"},
    "quality_target_placeholder": {
        "pt-BR": "ex.: sucesso da tarefa >= 95% na coorte crítica",
        "en": "e.g. task success >= 95% on critical cohort",
    },
    "latency_target_label": {"pt-BR": "Meta de latência", "en": "Latency target"},
    "latency_target_placeholder": {
        "pt-BR": "ex.: p95 < 2s para consultas simples",
        "en": "e.g. p95 < 2s for simple queries",
    },
    "cost_constraint_label": {"pt-BR": "Restrição de custo", "en": "Cost constraint"},
    "cost_constraint_placeholder": {
        "pt-BR": "ex.: custo-alvo por tarefa bem-sucedida",
        "en": "e.g. target cost per successful task",
    },
    "regulatory_constraints_label": {
        "pt-BR": "Restrições regulatórias / de política",
        "en": "Regulatory / policy constraints",
    },
    "regulatory_constraints_placeholder": {
        "pt-BR": "ex.: aprovação humana, evidência de auditoria, residência de dados",
        "en": "e.g. human approval, audit evidence, data residency",
    },
    "t2_intro": {
        "pt-BR": "Descreva as características de execução; o motor recomenda o menor padrão adequado.",
        "en": "Describe execution characteristics; the engine recommends the smallest fitting pattern.",
    },
    "path_known_label": {
        "pt-BR": "O caminho de execução é conhecido com antecedência",
        "en": "Execution path is known in advance",
    },
    "dynamic_next_steps_label": {
        "pt-BR": "Os próximos passos são descobertos durante a execução",
        "en": "Next steps are discovered during execution",
    },
    "dynamic_tool_choice_label": {
        "pt-BR": "O modelo precisa escolher ferramentas/ações dinamicamente",
        "en": "The model must dynamically choose tools/actions",
    },
    "independent_autonomous_domains_label": {
        "pt-BR": "Existem domínios autônomos separados com responsabilidade/contratos claros",
        "en": "There are separate autonomous domains with clear ownership/contracts",
    },
    "strict_auditability_label": {
        "pt-BR": "Auditabilidade / reprodutibilidade estrita é exigida",
        "en": "Strict auditability / reproducibility is required",
    },
    "structured_output_label": {
        "pt-BR": "Sistemas downstream exigem saída estruturada/schema",
        "en": "Downstream systems require structured output/schema",
    },
    "needs_document_knowledge_label": {
        "pt-BR": "Precisa de conhecimento corporativo/documental (candidato a RAG)",
        "en": "Needs enterprise/document knowledge (RAG candidate)",
    },
    "needs_dynamic_data_label": {
        "pt-BR": "Precisa de dados operacionais dinâmicos/em tempo real",
        "en": "Needs live/dynamic operational data",
    },
    "long_running_context_label": {
        "pt-BR": "Sessões longas / crescimento de contexto",
        "en": "Long-running sessions / context growth",
    },
    "existing_api_label": {
        "pt-BR": "Já existe uma API/serviço maduro",
        "en": "A mature API/service already exists",
    },
    "many_external_capabilities_label": {
        "pt-BR": "Muitas ferramentas/capacidades voltadas ao modelo precisam de descoberta/protocolos padronizados",
        "en": "Many model-facing tools/capabilities need standardized discovery/protocols",
    },
    "remote_autonomous_service_label": {
        "pt-BR": "Um agente/serviço remoto autônomo executa tarefas complexas",
        "en": "A remote autonomous agent/service performs complex tasks",
    },
    "sensitive_data_label": {"pt-BR": "Dados sensíveis / restritos", "en": "Sensitive / restricted data"},
    "high_impact_actions_label": {
        "pt-BR": "Pode disparar efeitos colaterais de alto impacto",
        "en": "Can trigger high-impact side effects",
    },
    "irreversible_actions_label": {
        "pt-BR": "Pode disparar ações irreversíveis",
        "en": "Can trigger irreversible actions",
    },
    "human_approval_required_label": {
        "pt-BR": "Aprovação humana é exigida por política/risco",
        "en": "Human approval is required by policy/risk",
    },
    "subjective_quality_label": {
        "pt-BR": "A qualidade tem dimensões subjetivas",
        "en": "Quality has subjective dimensions",
    },
    "critical_cohorts_label": {
        "pt-BR": "Coortes/casos de uso críticos devem ser avaliados separadamente",
        "en": "Critical cohorts/use cases must be evaluated separately",
    },
    "ops_note": {
        "pt-BR": "Recomendações operacionais são geradas automaticamente para tracing, retries/fallbacks, idempotência e loops de feedback.",
        "en": "Operational recommendations are generated automatically for tracing, retries/fallbacks, idempotency and feedback loops.",
    },
    "t5_intro": {
        "pt-BR": "Pontue cada opção de 1 (ruim) a 5 (excelente). Restrições obrigatórias ainda sobrepõem a pontuação total.",
        "en": "Score each option from 1 (poor) to 5 (excellent). Hard constraints still override total score.",
    },
    "option_a_label": {"pt-BR": "Opção A", "en": "Option A"},
    "option_b_label": {"pt-BR": "Opção B", "en": "Option B"},
    "option_c_label": {"pt-BR": "Opção C", "en": "Option C"},
    "option_a_default": {"pt-BR": "Padrão recomendado", "en": "Recommended pattern"},
    "option_b_default": {"pt-BR": "Alternativa 1", "en": "Alternative 1"},
    "option_c_default": {"pt-BR": "Alternativa 2", "en": "Alternative 2"},
    "weight_word": {"pt-BR": "peso", "en": "weight"},
    "highest_score_label": {"pt-BR": "Maior pontuação ponderada", "en": "Highest weighted score"},
    "selected_option_label": {"pt-BR": "Opção selecionada", "en": "Selected option"},
    "tradeoff_notes_label": {"pt-BR": "Justificativa do trade-off", "en": "Trade-off rationale"},
    "tradeoff_notes_placeholder": {
        "pt-BR": "Por que essa opção, o que ganhamos, o que aceitamos, quando revisitaríamos essa decisão?",
        "en": "Why this option, what do we gain, what do we accept, when would we revisit it?",
    },
    "t6_subheader": {"pt-BR": "Plano de Decisão de Arquitetura", "en": "Architecture Decision Plan"},
    "architecture_metric_label": {"pt-BR": "Arquitetura", "en": "Architecture"},
    "integration_metric_label": {"pt-BR": "Integração", "en": "Integration"},
    "rationale_heading": {"pt-BR": "### Justificativa", "en": "### Rationale"},
    "information_heading": {"pt-BR": "### Estratégia de informação", "en": "### Information strategy"},
    "model_strategy_heading": {
        "pt-BR": "### Estratégia de modelo / fornecedor",
        "en": "### Model / provider strategy",
    },
    "controls_heading": {"pt-BR": "### Trust & controles", "en": "### Trust & controls"},
    "evaluation_heading": {"pt-BR": "### Evaluation", "en": "### Evaluation"},
    "operations_heading": {"pt-BR": "### Operação", "en": "### Operations"},
    "export_heading": {"pt-BR": "### Exportar", "en": "### Export"},
    "download_markdown_label": {"pt-BR": "Baixar Markdown", "en": "Download Markdown"},
    "download_docx_label": {"pt-BR": "Baixar DOCX", "en": "Download DOCX"},
    "download_json_label": {"pt-BR": "Baixar JSON", "en": "Download JSON"},
    "preview_expander_label": {"pt-BR": "Pré-visualizar Markdown gerado", "en": "Preview generated Markdown"},
    "download_pdf_label": {"pt-BR": "Baixar PDF", "en": "Download PDF"},
    "download_adr_label": {"pt-BR": "Baixar ADR", "en": "Download ADR"},

    "tab_7": {"pt-BR": "7 · Modelos", "en": "7 · Models"},
    "models_intro": {
        "pt-BR": "Adicione candidatos de modelo/fornecedor e preencha notas por critério. Isto é só estrutura de comparação — o framework não recomenda qual fornecedor escolher.",
        "en": "Add model/provider candidates and fill in notes per criterion. This is just comparison structure — the framework doesn't recommend which vendor to pick.",
    },
    "model_candidate_a_label": {"pt-BR": "Candidato A", "en": "Candidate A"},
    "model_candidate_b_label": {"pt-BR": "Candidato B", "en": "Candidate B"},
    "model_candidate_c_label": {"pt-BR": "Candidato C", "en": "Candidate C"},
    "model_candidate_a_default": {"pt-BR": "Fornecedor 1", "en": "Provider 1"},
    "model_candidate_b_default": {"pt-BR": "Fornecedor 2", "en": "Provider 2"},
    "model_candidate_c_default": {"pt-BR": "Fornecedor 3", "en": "Provider 3"},
    "model_criterion_task_quality_label": {
        "pt-BR": "Aderência de qualidade à tarefa",
        "en": "Task quality fit",
    },
    "model_criterion_latency_label": {"pt-BR": "Classe de latência", "en": "Latency class"},
    "model_criterion_cost_label": {"pt-BR": "Classe de custo", "en": "Cost class"},
    "model_criterion_context_window_label": {"pt-BR": "Janela de contexto", "en": "Context window"},
    "model_criterion_structured_output_label": {
        "pt-BR": "Suporte a saída estruturada",
        "en": "Structured output support",
    },
    "model_criterion_privacy_label": {
        "pt-BR": "Aderência de privacidade / residência",
        "en": "Privacy / residency fit",
    },
    "model_criterion_rate_limits_label": {
        "pt-BR": "Limites de taxa / disponibilidade",
        "en": "Rate limits / availability",
    },
    "model_criterion_portability_label": {
        "pt-BR": "Portabilidade / risco de lock-in",
        "en": "Portability / lock-in risk",
    },

    "saved_cases_header": {"pt-BR": "Casos salvos (sessão)", "en": "Saved cases (session)"},
    "saved_case_name_placeholder": {"pt-BR": "Nome do caso para salvar", "en": "Name to save as"},
    "save_case_button": {"pt-BR": "💾 Salvar caso atual", "en": "💾 Save current case"},
    "load_saved_case_label": {"pt-BR": "Carregar caso salvo", "en": "Load a saved case"},
    "load_saved_case_button": {"pt-BR": "📂 Carregar", "en": "📂 Load"},
    "delete_saved_case_button": {"pt-BR": "🗑️ Excluir", "en": "🗑️ Delete"},
    "saved_cases_note": {
        "pt-BR": "Mantidos só nesta sessão do navegador — nunca gravados no servidor.",
        "en": "Kept only in this browser session — never written server-side.",
    },
    "no_saved_cases": {"pt-BR": "Nenhum caso salvo ainda.", "en": "No saved cases yet."},
    "case_saved_toast": {"pt-BR": "Caso salvo.", "en": "Case saved."},

    "import_json_label": {"pt-BR": "Importar plano (.json)", "en": "Import plan (.json)"},
    "import_json_error": {
        "pt-BR": "Não foi possível importar este arquivo: {error}",
        "en": "Could not import this file: {error}",
    },
    "import_json_success": {"pt-BR": "Plano importado.", "en": "Plan imported."},

    "ai_review_expander_label": {"pt-BR": "🤖 Revisão por IA (opcional)", "en": "🤖 AI Review (optional)"},
    "ai_review_intro": {
        "pt-BR": "Opcional e neutro em fornecedor: conecte qualquer endpoint compatível com a API de chat da OpenAI (OpenAI, Ollama, vLLM, gateways...) para obter uma crítica deste plano. Sua chave fica só nesta sessão — nunca é salva nem enviada para mais nenhum lugar.",
        "en": "Optional and vendor-neutral: connect any OpenAI-chat-completions-compatible endpoint (OpenAI, Ollama, vLLM, gateways...) to get a critique of this plan. Your key stays in this session only — never saved, never sent anywhere else.",
    },
    "ai_review_base_url_label": {"pt-BR": "Base URL (https://...)", "en": "Base URL (https://...)"},
    "ai_review_api_key_label": {"pt-BR": "Chave de API", "en": "API key"},
    "ai_review_model_label": {"pt-BR": "Nome do modelo", "en": "Model name"},
    "ai_review_button": {"pt-BR": "Obter revisão por IA", "en": "Get AI review"},
    "ai_review_disclaimer": {
        "pt-BR": "⚠️ Conteúdo gerado por IA — não verificado. Revise antes de confiar.",
        "en": "⚠️ AI-generated content — unverified. Review before relying on it.",
    },
    "ai_review_error": {"pt-BR": "Falha ao obter revisão: {error}", "en": "Failed to get a review: {error}"},
    "ai_review_system_prompt": {
        "pt-BR": "Você é um revisor sênior de arquitetura de IA/LLM. Analise criticamente o plano de decisão de arquitetura a seguir e aponte riscos, lacunas ou suposições questionáveis. Seja direto e específico. Responda em português.",
        "en": "You are a senior AI/LLM architecture reviewer. Critically analyze the following architecture decision plan and point out risks, gaps, or questionable assumptions. Be direct and specific. Respond in English.",
    },
}

MODEL_CRITERIA = [
    "model_criterion_task_quality_label",
    "model_criterion_latency_label",
    "model_criterion_cost_label",
    "model_criterion_context_window_label",
    "model_criterion_structured_output_label",
    "model_criterion_privacy_label",
    "model_criterion_rate_limits_label",
    "model_criterion_portability_label",
]

# Sidebar step list and tab subheaders are derived from STEPS so the letter
# names can never go out of sync between the sidebar and the tabs.
UI["sidebar_steps"] = {
    lang: "  \n".join(f"**{letter}** {name}" for letter, name in STEPS[lang]) for lang in LANGS
}
for _key, _indexes in _TAB_STEP_INDEXES.items():
    UI[_key] = {
        lang: " / ".join(f"{STEPS[lang][i][0]} — {STEPS[lang][i][1]}" for i in _indexes) for lang in LANGS
    }


def t(lang: str, key: str) -> str:
    return UI[key][lang]


# Portuguese translations for the fixed set of English strings the
# deterministic engine returns (rationale, warnings, information strategy,
# model strategy, controls, evaluations, operations). The engine itself stays
# English-only/provider-neutral; unknown strings fall back to the original.
ENGINE_PT = {
    "Separate autonomous domains plus dynamic execution can justify multiple agents, "
    "but each boundary should have a clear ownership and contract.": (
        "Domínios autônomos separados somados a execução dinâmica podem justificar múltiplos agentes, "
        "mas cada fronteira deve ter responsabilidade e contrato claros."
    ),
    "The system must discover or choose next steps during execution, which favors bounded agentic behavior.": (
        "O sistema precisa descobrir ou escolher os próximos passos durante a execução, "
        "o que favorece um comportamento de agente limitado (bounded)."
    ),
    "The execution path is known in advance, so a workflow offers greater predictability and auditability.": (
        "O caminho de execução é conhecido com antecedência, então um workflow oferece maior previsibilidade e auditabilidade."
    ),
    "No orchestration requirement was identified; start with the smallest useful augmented-model pattern.": (
        "Nenhuma necessidade de orquestração foi identificada; comece com o padrão de modelo aumentado mais simples possível."
    ),
    "A remote capability has its own autonomy and execution lifecycle, favoring agent-to-agent coordination.": (
        "Uma capacidade remota tem seu próprio ciclo de vida e autonomia de execução, favorecendo a coordenação agente-a-agente."
    ),
    "Multiple model-facing capabilities benefit from standardized discovery and contracts; "
    "a tool protocol such as MCP can be a candidate interface.": (
        "Múltiplas capacidades voltadas ao modelo se beneficiam de descoberta e contratos padronizados; "
        "um protocolo de ferramentas como o MCP pode ser uma interface candidata."
    ),
    "Existing operational sources should remain the source of truth and be exposed as tools/APIs.": (
        "As fontes operacionais existentes devem permanecer como fonte da verdade e ser expostas como ferramentas/APIs."
    ),
    "Validate that multi-agent autonomy is necessary. "
    "Prefer workflow + tools when it provides the same outcome with less complexity.": (
        "Valide se a autonomia multi-agente é realmente necessária. "
        "Prefira workflow + ferramentas quando isso entregar o mesmo resultado com menos complexidade."
    ),
    "Strict auditability is in tension with open-ended agentic execution. "
    "Bound autonomy, persist state/decisions and consider workflow for regulated steps.": (
        "Auditabilidade estrita está em tensão com execução agente aberta. "
        "Limite a autonomia, persista estado/decisões e considere workflow para etapas regulatórias."
    ),
    "Use RAG for enterprise/document knowledge; evaluate chunking, indexing, retrieval quality and citations.": (
        "Use RAG para conhecimento corporativo/documental; avalie chunking, indexação, qualidade de recuperação e citações."
    ),
    "Use a live operational source/API as source of truth for dynamic data; "
    "do not rely on model memory or stale RAG snapshots.": (
        "Use uma fonte/API operacional em tempo real como fonte da verdade para dados dinâmicos; "
        "não dependa da memória do modelo ou de snapshots de RAG desatualizados."
    ),
    "Use progressive context loading and preserve critical state separately from disposable conversation history.": (
        "Use carregamento progressivo de contexto e preserve estado crítico separadamente do histórico de conversa descartável."
    ),
    "Keep context minimal; add retrieval or state only when the use case requires it.": (
        "Mantenha o contexto mínimo; adicione recuperação ou estado apenas quando o caso de uso exigir."
    ),
    "Evaluate model/runtime candidates only after hard requirements are clear.": (
        "Avalie candidatos a modelo/runtime somente depois que os requisitos obrigatórios estiverem claros."
    ),
    "Compare task quality, latency/throughput and total cost per successful task on representative evals.": (
        "Compare qualidade da tarefa, latência/throughput e custo total por tarefa bem-sucedida em avaliações representativas."
    ),
    "Validate context, structured-output and tool-use capabilities required by the architecture.": (
        "Valide as capacidades de contexto, saída estruturada e uso de ferramentas exigidas pela arquitetura."
    ),
    "Treat privacy, data residency, retention and compliance requirements as hard constraints when applicable.": (
        "Trate privacidade, residência de dados, retenção e requisitos de compliance como restrições obrigatórias quando aplicável."
    ),
    "Assess rate limits, availability, observability, operational support and portability/vendor lock-in before selection.": (
        "Avalie limites de taxa, disponibilidade, observabilidade, suporte operacional e portabilidade/lock-in de fornecedor antes da seleção."
    ),
    "Apply least privilege to tools, data and capabilities.": (
        "Aplique privilégio mínimo a ferramentas, dados e capacidades."
    ),
    "Propagate real user/service identity to authorization checks at execution time.": (
        "Propague a identidade real do usuário/serviço para as verificações de autorização em tempo de execução."
    ),
    "Enforce data isolation and access policy outside the model prompt; log access evidence where appropriate.": (
        "Aplique isolamento de dados e política de acesso fora do prompt do modelo; registre evidência de acesso quando apropriado."
    ),
    "Enforce high-impact action policy in the execution layer; do not depend on prompt compliance.": (
        "Aplique a política de ações de alto impacto na camada de execução; não dependa da conformidade do prompt."
    ),
    "Use fail-closed behavior when authorization or policy evidence is unavailable.": (
        "Use comportamento fail-closed quando a autorização ou evidência de política não estiver disponível."
    ),
    "Place human approval immediately before the governed side effect, with the final action details visible to the reviewer.": (
        "Posicione a aprovação humana imediatamente antes do efeito colateral governado, "
        "com os detalhes finais da ação visíveis ao revisor."
    ),
    "Use progressive capability discovery/exposure so the model sees only relevant tools at each stage.": (
        "Use descoberta/exposição progressiva de capacidades para que o modelo veja apenas as ferramentas relevantes em cada etapa."
    ),
    "Create a representative evaluation dataset before production promotion.": (
        "Crie um conjunto de avaliação representativo antes da promoção para produção."
    ),
    "Track quality/task success, latency, cost and relevant safety/security metrics.": (
        "Acompanhe sucesso da tarefa/qualidade, latência, custo e métricas relevantes de segurança."
    ),
    "Use deterministic/code-based checks for schema, required fields and other objective constraints.": (
        "Use verificações determinísticas/baseadas em código para schema, campos obrigatórios e outras restrições objetivas."
    ),
    "Use calibrated LLM-as-a-judge and/or human evaluation for subjective quality dimensions.": (
        "Use um avaliador LLM calibrado (LLM-as-a-judge) e/ou avaliação humana para dimensões subjetivas de qualidade."
    ),
    "Segment evaluation by critical cohorts/use cases so aggregate metrics do not hide failure modes.": (
        "Segmente a avaliação por coortes/casos de uso críticos para que métricas agregadas não escondam modos de falha."
    ),
    "Add adversarial and policy-bypass cases focused on unauthorized or unsafe actions.": (
        "Adicione casos adversariais e de bypass de política focados em ações não autorizadas ou inseguras."
    ),
    "Trace model calls, retrieval, tool calls, latency, errors and final outcomes with a shared correlation/trace ID.": (
        "Rastreie chamadas de modelo, recuperação, chamadas de ferramenta, latência, erros e resultados finais "
        "com um ID de correlação/trace compartilhado."
    ),
    "Define timeout, retry and fallback policies per dependency; avoid unsafe retries for non-idempotent side effects.": (
        "Defina políticas de timeout, retry e fallback por dependência; evite retries inseguros para efeitos colaterais não idempotentes."
    ),
    "Use feedback and production failure modes to drive the next evaluation and architecture iteration.": (
        "Use feedback e modos de falha em produção para orientar a próxima iteração de avaliação e arquitetura."
    ),
    "Require idempotency/deduplication for retried side effects and provide a kill-switch/feature flag for risky capabilities.": (
        "Exija idempotência/deduplicação para efeitos colaterais reexecutados e forneça um kill-switch/feature flag "
        "para capacidades de risco."
    ),
}

PATTERN_PT = {
    "Augmented LLM": "LLM Aumentado",
    "Workflow": "Workflow",
    "Agent": "Agente",
    "Multi-agent": "Multiagente",
    "API / Tool": "API / Ferramenta",
    "Tool Protocol / MCP": "Protocolo de Ferramentas / MCP",
    "Agent-to-Agent": "Agente-a-Agente",
    "None": "Nenhuma",
}

CRITERIA_PT = {
    "Quality / task success": "Qualidade / sucesso da tarefa",
    "Latency": "Latência",
    "Cost": "Custo",
    "Risk / control": "Risco / controle",
    "Auditability / predictability": "Auditabilidade / previsibilidade",
    "Maintainability": "Manutenibilidade",
    "Observability / debugging": "Observabilidade / depuração",
    "Privacy / residency / compliance": "Privacidade / residência / compliance",
    "Portability / lock-in": "Portabilidade / lock-in",
    "Fit with hard constraints": "Aderência às restrições obrigatórias",
}


def translate_items(lang: str, items: list[str]) -> list[str]:
    if lang == "en":
        return items
    return [ENGINE_PT.get(item, item) for item in items]


def translate_pattern(lang: str, pattern: str) -> str:
    if lang == "en":
        return pattern
    return PATTERN_PT.get(pattern, pattern)


def translate_criterion(lang: str, criterion: str) -> str:
    if lang == "en":
        return criterion
    return CRITERIA_PT.get(criterion, criterion)


# Labels specific to the exported Markdown/DOCX document (distinct from the
# UI's "###"-prefixed heading strings in UI, since the document builds its
# own heading levels). Letter prefixes mirror BRAND/STEPS for each language.
EXPORT = {
    "doc_title": {"pt-BR": "Plano de Decisão de Arquitetura", "en": "Architecture Decision Plan"},
    "section_a": {"pt-BR": "A — Alvo", "en": "A — Aim"},
    "business_problem": {"pt-BR": "Problema de negócio", "en": "Business problem"},
    "desired_outcome": {"pt-BR": "Resultado desejado", "en": "Desired outcome"},
    "users": {"pt-BR": "Usuários / público", "en": "Users / audience"},
    "section_r": {"pt-BR": "R — Requisitos", "en": "R — Requirements"},
    "quality_target": {"pt-BR": "Meta de qualidade", "en": "Quality target"},
    "latency_target": {"pt-BR": "Meta de latência", "en": "Latency target"},
    "cost_constraint": {"pt-BR": "Restrição de custo", "en": "Cost constraint"},
    "regulatory_constraints": {"pt-BR": "Restrições regulatórias", "en": "Regulatory constraints"},
    "section_responsibility": {
        "pt-BR": "Q/U — Responsabilidade e arquitetura",
        "en": "C/H — Responsibility and architecture",
    },
    "recommended_pattern": {"pt-BR": "Padrão recomendado", "en": "Recommended pattern"},
    "rationale": {"pt-BR": "Justificativa", "en": "Rationale"},
    "section_i": {"pt-BR": "I — Integração & Informação", "en": "I — Integration & Information"},
    "recommended_integration": {"pt-BR": "Integração recomendada", "en": "Recommended integration"},
    "section_model": {"pt-BR": "Estratégia de Modelo / Fornecedor", "en": "Model / Provider Strategy"},
    "section_t": {"pt-BR": "T — Trust & Controls", "en": "T — Trust & Controls"},
    "section_e": {"pt-BR": "E — Evaluation", "en": "E — Evaluation"},
    "section_tradeoffs": {"pt-BR": "T — Trade-offs", "en": "C — Comparison"},
    "option_matrix": {"pt-BR": "Matriz de opções", "en": "Option matrix"},
    "selected_option": {"pt-BR": "Opção selecionada", "en": "Selected option"},
    "tradeoff_notes": {"pt-BR": "Notas de trade-off", "en": "Trade-off notes"},
    "section_operations": {"pt-BR": "O — Operação", "en": "T — Telemetry"},
    "warnings": {"pt-BR": "Avisos / decisões a validar", "en": "Warnings / decisions to validate"},
    "not_defined": {"pt-BR": "Não definido", "en": "Not defined"},
    "not_selected": {"pt-BR": "Não selecionada", "en": "Not selected"},
    "no_option_matrix": {"pt-BR": "Nenhuma matriz de opções informada", "en": "No option matrix supplied"},
    "footer": {
        "pt-BR": "Gerado com o framework ARQUITETO — um método de decisão de arquitetura de IA neutro em fornecedor.",
        "en": "Generated with the ARCHITECT framework — a vendor-neutral AI architecture decision method.",
    },
    "model_comparison_heading": {
        "pt-BR": "Comparação de Modelos / Fornecedores",
        "en": "Model / Provider Comparison",
    },
    "adr_title_prefix": {"pt-BR": "ADR", "en": "ADR"},
    "adr_status_heading": {"pt-BR": "Status", "en": "Status"},
    "adr_status_value": {"pt-BR": "Proposto", "en": "Proposed"},
    "adr_context_heading": {"pt-BR": "Contexto", "en": "Context"},
    "adr_decision_heading": {"pt-BR": "Decisão", "en": "Decision"},
    "adr_decision_intro": {
        "pt-BR": "Adotaremos **{architecture}** com integração **{integration}**.",
        "en": "We will adopt **{architecture}** with **{integration}** integration.",
    },
    "adr_consequences_heading": {"pt-BR": "Consequências", "en": "Consequences"},
    "adr_alternatives_heading": {
        "pt-BR": "Alternativas consideradas",
        "en": "Alternatives considered",
    },
}


def e(lang: str, key: str) -> str:
    return EXPORT[key][lang]
