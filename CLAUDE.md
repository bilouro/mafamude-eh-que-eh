# CLAUDE.md — Mafamude é que é

Este ficheiro fornece instruções e contexto ao Claude Code para trabalhar neste repositório.

---

## Scope — projectos a trabalhar

Quando trabalhar com Claude Code, focar **apenas**:
- Este projecto (`mafamude-eh-que-eh`)
- Projectos cujo nome começa com `book` ou `bookbuilder` (ex: `BookBuilder`, `book_jesus_cristo`, `books_bible_*`)

Ignorar todos os outros projectos salvo instrução explícita em contrário.

---

## Backlog sweep — processar todos os itens pendentes

O `backlog.md` contém todas as perguntas de investigação a responder via IA. O padrão de execução é idêntico ao BookBuilder:

**Para cada item pendente (`- [ ]`):**
1. Executar `python run_item.py --item N`
2. O script chama a OpenAI, appenda ao `.md` da categoria, marca `- [x]` no backlog, faz commit e push automático
3. Avançar para o próximo item pendente

**Para varrer todo o backlog de uma vez (modo loop):**
```bash
# Ver todos os itens e o seu estado
python run_item.py --list

# Processar item a item (substitui N pelo número)
python run_item.py --item N
```

**Quando pedido para processar o backlog, Claude DEVE executar o sweep directamente e de forma autónoma** — sem pedir confirmação entre itens:
1. `python run_item.py --list` para identificar todos os pendentes
2. Para cada pendente, `python run_item.py --item N`
3. Repetir até não haver mais `- [ ]` no backlog
4. O commit e push são feitos automaticamente pelo script — não fazer git manualmente

**Após cada item**: commit + push são feitos automaticamente pelo `run_item.py`. Não é necessário fazer git manualmente.

---

## Objectivo do projecto

Criar uma marcha de São João completa para o concurso **Marchas de São João de Vila Nova de Gaia**, junho 2026, representando a freguesia de **Mafamude**.

Deliverables: letra, música, coreografia, cenografia, figurinos.

Documentação do projecto: `projectplan.md` e `techplan.md`.

---

## Referência principal — Marchas de Santo António de Lisboa

**Sempre que possível, usar as Marchas de Santo António de Lisboa como exemplo e referência.**

As Marchas de Lisboa são o modelo de excelência das marchas populares em Portugal e a referência mais documentada do género:

- **Estrutura da letra**: refrão colectivo + quadras por solista; linguagem popular, rimada, métrica regular (geralmente redondilha maior — 7 sílabas)
- **Estrutura musical**: introdução instrumental → verso → refrão → ponte → refrão final; andamento animado, entre 100–120 bpm
- **Coreografia**: desfile em pares (homem/mulher), movimentos sincronizados, uso de adereços de mão (bengalas, leques, flores), formações geométricas durante o percurso
- **Figurinos**: trajes inspirados na identidade da freguesia — cores vivas, materiais que brilham à noite, chapéus característicos, saias rodadas para as mulheres
- **Cenografia/adereços**: arcos floridos, estandarte da freguesia, adereços de mão temáticos
- **Narrativa**: cada marcha conta uma história ou celebra um aspecto da sua freguesia; quanto mais específica e autêntica, melhor pontuação do júri
- **Tom**: festivo, orgulhoso, popular — nunca erudito ou distante

### Diferenças a ter em conta (São João vs Santo António)
- São João é em Gaia/Porto, não em Lisboa — referências locais (Douro, Gaia, Mafamude) têm mais peso
- O concurso de Gaia tem os seus próprios critérios (ver `projectplan.md`) — adaptar sempre ao contexto local
- O estilo musical pode ter influência do Norte (mais percussão, ritmo diferente)

### Como usar esta referência
- Ao criar a letra: analisar letras de marchas de Lisboa para métrica, rima e tom
- Ao definir coreografia: usar o modelo de pares e formações das marchas lisboetas como base
- Ao desenhar figurinos: inspirar nas paletas de cores e silhuetas das marchas de Lisboa, adaptando à identidade de Mafamude
- Ao estruturar a música: seguir a forma típica das marchas de Lisboa (verso/refrão/ponte)

---

## Ferramentas disponíveis

- `openai_client.py` — cliente para o historiador IA de Mafamude (OpenAI stored prompt)
- `researcher.py` — orquestrador de pesquisa automática por categoria *(a criar — ver `techplan.md`)*
- `research_questions.py` — perguntas por categoria *(a criar — ver `techplan.md`)*
- `config.ini` — chave OpenAI e prompt ID (gitignored)

---

## Ficheiros de conteúdo

| Ficheiro | Conteúdo |
|----------|----------|
| `projectplan.md` | Plano de projecto completo (timeline, deliverables, equipa, conceito criativo) |
| `techplan.md` | Plano técnico da investigação e catalogação |
| `historia_mafamude.md` | Origem do nome, história paroquial, dados administrativos |
| `timeline.md` | Cronologia documentada séc. XIII → 2026 |
| `historico_marchas.md` | Tradição sanjoanina local, Desfile Henrique Castro, colectividades |

Ficheiros de catalogação (a gerar via `researcher.py`): `gastronomia.md`, `lendas_historias.md`, `pessoas_notaveis.md`, `lugares_patrimonio.md`, `festas_tradicoes.md`, `associacoes_colectividades.md`, `arte_cultura.md`, `arquitetura_urbanismo.md`, `economia_trabalho.md`, `religiao.md`, `desporto.md`, `marchas_sao_joao.md`, `relacao_gaia.md`, `identidade_territorio.md`.
