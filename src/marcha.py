"""
marcha.py
Gera marchas populares para Mafamude usando o prompt compositor OpenAI.

Fluxo (ideias de ideias.md):
  1. pull
  2. lê ideias pendentes de ideias.md (- [ ])
  3. para cada pendente (respeitando --limit):
     a. lê categorias dos .md
     b. lê marchas já criadas (marchas_criadas.md / marchas/)
     c. envia ao prompt compositor
     d. guarda em marchas/marchaN.md
     e. actualiza marchas_criadas.md (índice)
     f. marca [x] na ideia em ideias.md
     g. commit + push

Fluxo (--ideia manual):
  - gera a marcha a partir da ideia passada
  - guarda em marchas/marchaN.md + actualiza índice
  - não toca em ideias.md

Usage:
    python src/marcha.py                        # todas as pendentes
    python src/marcha.py --limit 2              # só as próximas 2 pendentes
    python src/marcha.py --ideia "texto livre"  # ideia manual
"""
import argparse
import json
import re
import sys
from configparser import ConfigParser
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from git_helper import commit_and_push, pull
from openai import OpenAI

REPO_DIR = Path(__file__).parent.parent
SOBRE_DIR = REPO_DIR / "sobre_mafamude"
MARCHAS_DIR = REPO_DIR / "marchas"
MARCHAS_INDEX = REPO_DIR / "marchas_criadas.md"
IDEIAS_FILE = REPO_DIR / "ideias.md"


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

def load_config(config_path: str = None) -> ConfigParser:
    config = ConfigParser()
    config.read(config_path or str(REPO_DIR / "config.ini"), encoding="utf-8")
    return config


# ---------------------------------------------------------------------------
# Parsear categorias (formato marcha: confianca text, pontos_nao_confirmados)
# ---------------------------------------------------------------------------

def parse_category_file(filepath: Path, category_title: str) -> dict:
    content = filepath.read_text(encoding="utf-8")
    itens = []

    blocks = re.split(r'\n---+\n', content)

    for block in blocks:
        block = block.strip()
        if not block:
            continue

        m = re.match(r'^## (.+?)$', block, re.MULTILINE)
        if not m:
            continue

        question = m.group(1).strip()
        after_question = block[m.end():].strip()

        # Confiança — manter capitalização original (High/Medium/Low)
        confidence = "Medium"
        conf_m = re.search(r'\*\*Confiança:\*\*\s*(.+?)(?:\s{2,}|\n|$)', after_question)
        if conf_m:
            confidence = conf_m.group(1).strip()

        # Pontos não confirmados
        pontos_nao_confirmados = []
        pontos_m = re.search(r'\*\*Pontos não confirmados:\*\*\s*(.+?)(?:\s{2,}|\n|$)', after_question)
        if pontos_m:
            raw = pontos_m.group(1).strip()
            pontos_nao_confirmados = [
                p.strip().rstrip('.')
                for p in re.split(r'[;|]', raw)
                if p.strip() and p.strip() != '.'
            ]

        # Resposta
        answer_lines = []
        for line in after_question.splitlines():
            if line.startswith("**"):
                break
            answer_lines.append(line)
        answer = "\n".join(answer_lines).strip()

        if not answer:
            continue

        itens.append({
            "pergunta": question,
            "resposta": answer,
            "confianca": confidence,
            "pontos_nao_confirmados": pontos_nao_confirmados,
        })

    return {"categoria": category_title, "itens": itens}


def parse_all_categories() -> list:
    backlog_content = (SOBRE_DIR / "backlog.md").read_text(encoding="utf-8")
    categories = []
    seen = set()

    for line in backlog_content.splitlines():
        m = re.match(r'^## (.+?) →\s*\[([^\]]+)\]\([^\)]+\)', line)
        if m:
            title = m.group(1).strip()
            filename = m.group(2).strip()
            filepath = SOBRE_DIR / filename
            if filename in seen or not filepath.exists():
                continue
            seen.add(filename)
            cat = parse_category_file(filepath, title)
            if cat["itens"]:
                categories.append(cat)

    return categories


# ---------------------------------------------------------------------------
# Parsear ideias pendentes de ideias.md
# ---------------------------------------------------------------------------

def parse_pending_ideias() -> list:
    """Devolve lista de textos de ideias pendentes (- [ ])."""
    if not IDEIAS_FILE.exists():
        return []

    content = IDEIAS_FILE.read_text(encoding="utf-8")
    pending = []

    pattern = re.compile(r'- \[ \]\s*\n```text\n(.*?)```', re.DOTALL)
    for m in pattern.finditer(content):
        text = m.group(1).strip()
        if text:
            pending.append(text)

    return pending


def mark_ideia_done(ideia_text: str):
    """Marca a primeira ocorrência pendente da ideia como [x] em ideias.md."""
    if not IDEIAS_FILE.exists():
        return

    content = IDEIAS_FILE.read_text(encoding="utf-8")
    escaped = re.escape(ideia_text)
    new_content = re.sub(
        rf'- \[ \]\n(```text\n{escaped}\n```)',
        r'- [x]\n\1',
        content,
        count=1,
        flags=re.DOTALL,
    )
    IDEIAS_FILE.write_text(new_content, encoding="utf-8")


# ---------------------------------------------------------------------------
# Parsear marchas já criadas (para marchas_ja_feitas)
# ---------------------------------------------------------------------------

def parse_marchas_criadas() -> list:
    """
    Lê cada marchas/marchaN.md e extrai o JSON de metadata do comentário HTML.
    Devolve lista no formato marchas_ja_feitas.
    """
    if not MARCHAS_DIR.exists():
        return []

    marchas = []
    for filepath in sorted(MARCHAS_DIR.glob("marcha*.md")):
        content = filepath.read_text(encoding="utf-8")
        m = re.search(r'<!--\s*METADATA\s*\n(\{.*?\})\s*-->', content, re.DOTALL)
        if m:
            try:
                data = json.loads(m.group(1))
                marchas.append(data)
            except json.JSONDecodeError:
                pass

    return marchas


def next_marcha_number() -> int:
    """Determina o próximo número sequencial para marchaN.md."""
    if not MARCHAS_DIR.exists():
        return 1
    existing = list(MARCHAS_DIR.glob("marcha*.md"))
    if not existing:
        return 1
    nums = []
    for f in existing:
        m = re.match(r'marcha(\d+)\.md', f.name)
        if m:
            nums.append(int(m.group(1)))
    return max(nums) + 1 if nums else 1


# ---------------------------------------------------------------------------
# Extrair letra como texto plano
# ---------------------------------------------------------------------------

def letra_to_text(letra: dict) -> str:
    parts = []
    section_labels = {
        "estrofe_1": "Estrofe 1",
        "estrofe_2": "Estrofe 2",
        "estrofe_3": "Estrofe 3",
        "refrao": "Refrão",
        "final": "Final",
    }
    for key, label in section_labels.items():
        versos = letra.get(key, [])
        if versos:
            parts.append(label + ":")
            for v in versos:
                parts.append(v.get("texto", ""))
            parts.append("")
    return "\n".join(parts).strip()


# ---------------------------------------------------------------------------
# Guardar marcha em marchas/marchaN.md
# ---------------------------------------------------------------------------

def save_marcha_file(result: dict, n: int, ideia_origem: str) -> Path:
    MARCHAS_DIR.mkdir(exist_ok=True)
    filepath = MARCHAS_DIR / f"marcha{n:02d}.md"
    today = date.today().isoformat()

    titulo = result.get("titulo", f"Marcha {n}")
    conceito = result.get("conceito_central", "")
    angulo = result.get("angulo_criativo", "")
    letra = result.get("letra", {})
    elementos = result.get("elementos_de_mafamude_usados", [])
    validacao = result.get("validacao", {})
    fontes = result.get("fontes_online_consultadas", [])
    ideia_utilizada = result.get("ideia_utilizada", {})

    # Texto completo da letra para metadata
    letra_text = letra_to_text(letra)

    # Metadata JSON para parsing futuro (marchas_ja_feitas)
    metadata = {
        "titulo": titulo,
        "ano": 2026,
        "origem": "Mafamude",
        "tema": conceito,
        "letra": letra_text,
        "observacoes": angulo,
    }

    lines = [
        f"# {titulo}",
        "",
        f"> Data: {today}  ",
        f"> Evento: Marchas de São João de Vila Nova de Gaia 2026  ",
        f"> Ficheiro: marcha{n:02d}.md  ",
        "",
        "---",
        "",
        "## Conceito",
        "",
        f"**Conceito central:** {conceito}",
        "",
        f"**Ângulo criativo:** {angulo}",
        "",
    ]

    # Ideia utilizada
    if ideia_utilizada:
        lines += [
            "**Ideia de origem:**",
            f"> {ideia_utilizada.get('ideia_recebida', '_(livre)_')[:300]}",
            "",
            f"**Modo de aproveitamento:** {ideia_utilizada.get('modo_de_aproveitamento', '')}",
            "",
            f"**Conceito final adoptado:** {ideia_utilizada.get('conceito_final_adoptado', '')}",
            "",
        ]

    lines += ["---", "", "## Letra", ""]

    section_labels = [
        ("estrofe_1", "Estrofe 1"),
        ("estrofe_2", "Estrofe 2"),
        ("estrofe_3", "Estrofe 3"),
        ("refrao", "Refrão"),
        ("final", "Final"),
    ]
    for key, label in section_labels:
        versos = letra.get(key, [])
        if versos:
            lines.append(f"### {label}")
            lines.append("")
            for v in versos:
                obs = v.get("observacao_metrica", "")
                lines.append(f"{v.get('texto', '')}  ")
                if obs:
                    lines.append(f"*({obs})*  ")
            lines.append("")

    lines += ["---", "", "## Elementos de Mafamude utilizados", ""]
    for el in elementos:
        elem = el.get("elemento", "")
        modo = el.get("modo_de_uso_na_letra", "")
        lines.append(f"- **{elem}** — {modo}")
    lines.append("")

    if fontes:
        lines += ["---", "", "## Fontes consultadas", ""]
        for f in fontes:
            url = f.get("url", "")
            title = f.get("titulo", "")
            tipo = f.get("tipo", "")
            lines.append(f"- [{title}]({url}) _{tipo}_")
        lines.append("")

    if validacao:
        lines += ["---", "", "## Validação", ""]
        lines.append(f"- Foco em Mafamude: {validacao.get('foco_em_mafamude', '')}  ")
        lines.append(f"- Refrão colectivo: {validacao.get('refrao_colectivo_e_memoravel', '')}  ")
        lines.append(f"- Risco de semelhança: {validacao.get('risco_de_semelhanca_com_marchas_anteriores', '')}  ")
        lines.append("")

    # Metadata embebida para parsing futuro
    lines += [
        "---",
        "",
        f"<!-- METADATA",
        json.dumps(metadata, ensure_ascii=False),
        "-->",
        "",
    ]

    filepath.write_text("\n".join(lines), encoding="utf-8")
    return filepath


# ---------------------------------------------------------------------------
# Actualizar índice marchas_criadas.md
# ---------------------------------------------------------------------------

def update_index(result: dict, n: int):
    titulo = result.get("titulo", f"Marcha {n}")
    conceito = result.get("conceito_central", "")[:80]
    link = f"marchas/marcha{n:02d}.md"

    if not MARCHAS_INDEX.exists():
        header = (
            "# Marchas Criadas — Mafamude\n\n"
            "> Marchas geradas via prompt compositor OpenAI para o concurso "
            "**Marchas de São João de Vila Nova de Gaia 2026**.\n\n"
            "---\n\n"
            "| # | Título | Conceito central |\n"
            "|---|--------|------------------|\n"
        )
        MARCHAS_INDEX.write_text(header, encoding="utf-8")

    row = f"| {n} | [{titulo}]({link}) | {conceito} |\n"
    with open(MARCHAS_INDEX, "a", encoding="utf-8") as f:
        f.write(row)


# ---------------------------------------------------------------------------
# Construir payload para o prompt compositor
# ---------------------------------------------------------------------------

def build_payload(ideia: str, categories: list, marchas_ja_feitas: list) -> dict:
    return {
        "ideia": ideia,
        "metadata": {
            "tema_principal": "Mafamude",
            "evento": "Marchas de São João de Vila Nova de Gaia 2026",
            "idioma": "pt-PT",
        },
        "parametros_criativos": {
            "tom": ["popular", "festivo", "identitario", "emocional"],
            "obrigacoes": [
                "foco sempre em Mafamude",
                "versos em 8 tempos",
                "refrão fácil de gravar e cantar",
                "evitar semelhança com marchas anteriores",
            ],
            "preferencias": {
                "usar_historia": True,
                "usar_imagens_populares": True,
                "equilibrar_passado_e_presente": True,
                "dar_forca_ao_refrao": True,
            },
        },
        "categorias": categories,
        "marchas_ja_feitas": marchas_ja_feitas,
    }


# ---------------------------------------------------------------------------
# Chamada ao prompt OpenAI
# ---------------------------------------------------------------------------

def ask_marcha(payload: dict, config: ConfigParser) -> dict:
    client = OpenAI(api_key=config["openai"]["token"])

    response = client.responses.create(
        prompt={
            "id": config["openai_marcha"]["prompt_id"],
            "version": config["openai_marcha"]["prompt_version"],
        },
        input=json.dumps({**payload, "output": "json"}, ensure_ascii=False),
        tools=[],  # web search incompatível com JSON mode
    )

    result_text = None
    if hasattr(response, "output_text") and response.output_text:
        result_text = response.output_text
    elif hasattr(response, "output"):
        for item in response.output:
            if hasattr(item, "content"):
                for content in item.content:
                    if hasattr(content, "text"):
                        result_text = content.text
                        break
            if result_text:
                break

    if not result_text:
        raise RuntimeError("Resposta OpenAI vazia ou formato inesperado")

    result_text = result_text.strip()
    return json.loads(result_text)


# ---------------------------------------------------------------------------
# Processar uma ideia → gerar marcha
# ---------------------------------------------------------------------------

def process_idea(ideia_text: str, config: ConfigParser, from_ideias_md: bool) -> int:
    """
    Gera uma marcha a partir de ideia_text.
    Se from_ideias_md=True, marca [x] em ideias.md após commit.
    Devolve o número da marcha criada.
    """
    print("  A ler categorias...")
    categories = parse_all_categories()
    print(f"  {len(categories)} categorias")

    print("  A ler marchas já criadas...")
    marchas_ja_feitas = parse_marchas_criadas()
    print(f"  {len(marchas_ja_feitas)} marchas anteriores")

    n = next_marcha_number()
    payload = build_payload(ideia_text, categories, marchas_ja_feitas)

    print(f"  A enviar ao prompt compositor (marcha{n:02d})...")
    result = ask_marcha(payload, config)

    titulo = result.get("titulo", f"Marcha {n}")
    print(f"  Título: {titulo}")

    marcha_path = save_marcha_file(result, n, ideia_text)
    print(f"  Guardada em {marcha_path.relative_to(REPO_DIR)}")

    update_index(result, n)
    print(f"  Índice actualizado em marchas_criadas.md")

    if from_ideias_md:
        mark_ideia_done(ideia_text)
        print(f"  Ideia marcada [x] em ideias.md")

    files = [str(marcha_path), str(MARCHAS_INDEX)]
    if from_ideias_md:
        files.append(str(IDEIAS_FILE))

    commit_msg = (
        f"marcha: {titulo}\n\n"
        f"marcha{n:02d}.md — Marchas de São João de Gaia 2026\n\n"
        f"Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
    )
    commit_and_push(str(REPO_DIR), commit_msg, files)
    print(f"  ✓ Commit + push feitos")

    return n


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Gerador de marchas — Mafamude")
    parser.add_argument("--ideia", "-i", default=None, help="Ideia criativa manual (texto livre)")
    parser.add_argument("--limit", "-n", type=int, default=None, help="Número máximo de ideias a processar")
    parser.add_argument("--config", default=str(REPO_DIR / "config.ini"))
    args = parser.parse_args()

    pull(str(REPO_DIR))
    config = load_config(args.config)

    # Modo manual: --ideia passado por argumento
    if args.ideia:
        print(f"\nModo manual — ideia passada por argumento")
        n = process_idea(args.ideia, config, from_ideias_md=False)
        print(f"\n✓ Marcha #{n} criada em marchas/marcha{n:02d}.md")
        return

    # Modo backlog: processar pendentes de ideias.md
    pending = parse_pending_ideias()
    if not pending:
        print("Sem ideias pendentes em ideias.md.")
        sys.exit(0)

    to_process = pending if args.limit is None else pending[:args.limit]
    total = len(to_process)
    print(f"Ideias pendentes: {len(pending)} | A processar: {total}")

    for idx, ideia_text in enumerate(to_process, 1):
        preview = ideia_text[:80].replace("\n", " ")
        print(f"\n[{idx}/{total}] {preview}...")
        try:
            n = process_idea(ideia_text, config, from_ideias_md=True)
            print(f"  ✓ marcha{n:02d}.md criada")
        except Exception as e:
            print(f"  ✗ ERRO: {e}")

    print(f"\nConcluído: {total} marcha(s) gerada(s).")


if __name__ == "__main__":
    main()
