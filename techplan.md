# Plano Técnico — Investigação e Catalogação de Mafamude

## Objectivo
Orquestrar a pesquisa automática de 15 categorias sobre Mafamude usando o historiador IA (OpenAI stored prompt), gerando um ficheiro `.md` por categoria e marcando o progresso no `projectplan.md`.

---

## Ficheiros a criar

- [ ] `research_questions.py` — dicionário com todas as categorias, ficheiros de destino e perguntas
- [ ] `researcher.py` — orquestrador principal

---

## Especificações técnicas

### `research_questions.py`

- Dicionário `CATEGORIES` com uma entrada por categoria
- Cada entrada contém:
  - `file` — nome do ficheiro `.md` de destino (ex: `gastronomia.md`)
  - `projectplan_label` — texto exacto que aparece no `projectplan.md` para marcar o `[x]`
  - `questions` — lista de 4 a 8 perguntas em português focadas em Mafamude / Vila Nova de Gaia

**Categorias e número de perguntas indicativo:**

| Categoria | Ficheiro | Perguntas |
|-----------|----------|-----------|
| Identidade e Território | `identidade_territorio.md` | 5 |
| História | `historia.md` | 8 |
| Pessoas Notáveis | `pessoas_notaveis.md` | 6 |
| Lugares e Património | `lugares_patrimonio.md` | 7 |
| Gastronomia | `gastronomia.md` | 5 |
| Festas e Tradições | `festas_tradicoes.md` | 6 |
| Associações e Colectividades | `associacoes_colectividades.md` | 5 |
| Arte e Cultura | `arte_cultura.md` | 5 |
| Lendas e Histórias Populares | `lendas_historias.md` | 5 |
| Arquitectura e Urbanismo | `arquitetura_urbanismo.md` | 5 |
| Economia e Trabalho | `economia_trabalho.md` | 5 |
| Religião e Espiritualidade | `religiao.md` | 6 |
| Desporto | `desporto.md` | 4 |
| Marchas e São João | `marchas_sao_joao.md` | 6 |
| Relação com Vila Nova de Gaia | `relacao_gaia.md` | 4 |

---

### `researcher.py`

#### Argumentos CLI
- `--category <nome>` — pesquisar uma categoria específica (ex: `gastronomia`)
- `--all` — pesquisar todas as categorias sequencialmente
- `--force` — forçar re-pesquisa mesmo que o ficheiro `.md` já exista
- `--config <path>` — caminho para `config.ini` (default: `config.ini`)

#### Fluxo de execução
1. Carregar `config.ini` via `load_config()` de `openai_client.py`
2. Seleccionar categorias a processar (`--category` ou `--all`)
3. Para cada categoria:
   - [ ] Verificar se o ficheiro `.md` já existe → saltar se existir (a menos que `--force`)
   - [ ] Para cada pergunta da lista:
     - Chamar `ask()` de `openai_client.py` com `location_focus=["Mafamude", "Vila Nova de Gaia"]`
     - Mostrar progresso: `[2/6] A pesquisar: tascas históricas...`
     - Formatar resposta como secção Markdown (ver formato abaixo)
   - [ ] Agregar todas as secções e escrever ficheiro `.md`
   - [ ] Marcar checkbox em `projectplan.md`: `- [ ] [Label](file.md)` → `- [x] [Label](file.md)`
   - [ ] Confirmar no terminal: `✓ gastronomia.md escrito (5 perguntas)`

#### Importações
- `from openai_client import ask, load_config` — reutilizar directamente, sem subprocess
- Sem dependências externas além do que já existe no projecto

#### Idempotência
- Se `.md` existe e `--force` não está activo → imprimir aviso e saltar
- A marcação do `[x]` no `projectplan.md` só acontece após o ficheiro `.md` ser escrito com sucesso

---

### Formato do ficheiro `.md` gerado

```markdown
# <Nome da Categoria> — Mafamude
> Gerado automaticamente via historiador IA.  
> Verificar e complementar com fontes primárias antes de usar na letra/cenografia.  
> Data: YYYY-MM-DD

---

## <Pergunta 1>

<resposta>

**Confiança:** High / Medium / Low  
**Fontes:** Autor 1, Autor 2  
**Pontos não confirmados:** item 1; item 2  

---

## <Pergunta 2>
...
```

---

### Marcação do checkbox em `projectplan.md`
- Usar `re.sub` para substituir `- [ ] [Label]` por `- [x] [Label]` na linha correspondente
- Só substituir a primeira ocorrência exacta do label para evitar colisões

---

## Fluxo de uso

```bash
# Pesquisar uma categoria
python researcher.py --category gastronomia

# Pesquisar todas (sequencial)
python researcher.py --all

# Forçar re-pesquisa
python researcher.py --category lendas_historias --force
```

---

## Decisões técnicas

| Decisão | Escolha | Porquê |
|---------|---------|--------|
| Chamar OpenAI | `import ask()` directo | Mais limpo que subprocess |
| Perguntas | Dicionário em ficheiro separado | Fácil editar sem tocar no runner |
| Idempotência | Verifica se `.md` existe | Não repete chamadas pagas |
| Marcar `[x]` | `re.sub` no `projectplan.md` | Cirúrgico, não afecta outras linhas |
| `--all` | Sequencial, não paralelo | Rate limits da API; fácil acompanhar |
| Encoding | `utf-8` em todos os ficheiros | Caracteres portugueses |

---

## Estado

- [ ] `research_questions.py` criado
- [ ] `researcher.py` criado
- [ ] Testado com `--category gastronomia`
- [ ] Testado com `--all`
- [ ] Todos os 15 ficheiros `.md` gerados
- [ ] Todos os checkboxes marcados em `projectplan.md`
