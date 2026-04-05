"""
ideias.py
Gera uma nova ideia de marcha para Mafamude usando o prompt criativo OpenAI.

Usage:
    python src/ideias.py
    python src/ideias.py --ideia "Quero explorar a ligação de Mafamude ao Douro"
"""
import argparse
import json
import re
import sys
from configparser import ConfigParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from git_helper import commit_and_push, pull
from openai import OpenAI

REPO_DIR = Path(__file__).parent.parent
SOBRE_DIR = REPO_DIR / "sobre_mafamude"
IDEIAS_FILE = REPO_DIR / "ideias.md"


def load_config(config_path: str = None) -> ConfigParser:
    config = ConfigParser()
    config.read(config_path or str(REPO_DIR / "config.ini"), encoding="utf-8")
    return config


CONFIDENCE_MAP = {
    "high": "high",
    "medium": "midium",
    "midium": "midium",
    "low": "lown",
    "lown": "lown",
}


def map_confidence(raw: str) -> str:
    return CONFIDENCE_MAP.get(raw.strip().lower(), "midium")


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

        confidence_raw = ""
        pontos_nao_confirmados = []

        conf_m = re.search(r'\*\*Confiança:\*\*\s*(.+?)(?:\s{2,}|\n|$)', after_question)
        if conf_m:
            confidence_raw = conf_m.group(1).strip()

        pontos_m = re.search(r'\*\*Pontos não confirmados:\*\*\s*(.+?)(?:\s{2,}|\n|$)', after_question)
        if pontos_m:
            raw_pontos = pontos_m.group(1).strip()
            pontos_nao_confirmados = [
                p.strip().rstrip('.')
                for p in re.split(r'[;|]', raw_pontos)
                if p.strip() and p.strip() != '.'
            ]

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
            "confianca": map_confidence(confidence_raw) if confidence_raw else "midium",
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


def parse_ideias() -> list:
    if not IDEIAS_FILE.exists():
        return []
    content = IDEIAS_FILE.read_text(encoding="utf-8")
    ideias = []
    pattern = re.compile(r'- \[[ x]\]\s*\n```text\n(.*?)```', re.DOTALL)
    for m in pattern.finditer(content):
        ideia_text = m.group(1).strip()
        if ideia_text:
            ideias.append({"ideia": ideia_text})
    return ideias


def build_payload(ideia_input: str, categories: list, ideias_anteriores: list) -> dict:
    return {
        "ideia": ideia_input,
        "metadata": {
            "tema_principal": "Mafamude",
            "evento": "Marchas de São João de Vila Nova de Gaia 2026",
            "idioma": "pt-PT",
        },
        "parametros_criativos": {
            "tom": ["popular", "festivo", "identitario", "visual"],
            "obrigacoes": [
                "foco sempre em Mafamude",
                "criar uma ideia original",
                "ser útil para o compositor",
                "evitar semelhança com ideias anteriores",
                "evitar semelhança com marchas já feitas",
            ],
            "preferencias": {
                "usar_historia": True,
                "usar_imagens_populares": True,
                "equilibrar_passado_e_presente": True,
                "dar_potencial_ao_refrao": True,
            },
        },
        "categorias": categories,
        "ideias_anteriores": ideias_anteriores,
        "marchas_ja_feitas": [],
    }


def ask_ideas(payload: dict, config: ConfigParser) -> str:
    client = OpenAI(api_key=config["openai"]["token"])
    response = client.responses.create(
        prompt={
            "id": config["openai_ideas"]["prompt_id"],
            "version": config["openai_ideas"]["prompt_version"],
        },
        input=json.dumps(payload, ensure_ascii=False),
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
    result = json.loads(result_text)
    return result["ideia"]


def append_ideia(ideia_text: str):
    entry = f"\n- [ ]\n```text\n{ideia_text}\n```\n"
    if not IDEIAS_FILE.exists():
        header = "# Ideias de Marcha — Mafamude\n\n> Cada ideia gerada pelo prompt criativo OpenAI.\n> Marcar `[x]` quando a marcha correspondente for criada.\n"
        IDEIAS_FILE.write_text(header + entry, encoding="utf-8")
    else:
        with open(IDEIAS_FILE, "a", encoding="utf-8") as f:
            f.write(entry)


def main():
    parser = argparse.ArgumentParser(description="Gerador de ideias de marcha — Mafamude")
    parser.add_argument("--ideia", "-i", default="", help="Direcção criativa opcional")
    parser.add_argument("--config", default=str(REPO_DIR / "config.ini"))
    args = parser.parse_args()

    pull(str(REPO_DIR))

    print("A ler categorias pesquisadas...")
    categories = parse_all_categories()
    print(f"  {len(categories)} categorias carregadas")

    print("A ler ideias anteriores...")
    ideias_anteriores = parse_ideias()
    print(f"  {len(ideias_anteriores)} ideias anteriores encontradas")

    config = load_config(args.config)
    payload = build_payload(args.ideia, categories, ideias_anteriores)

    print("A enviar para o prompt criativo OpenAI...")
    ideia_text = ask_ideas(payload, config)
    print("  Ideia recebida.")

    append_ideia(ideia_text)
    print("  Guardada em ideias.md")

    n_ideias = len(ideias_anteriores) + 1
    commit_msg = (
        f"ideia: conceito #{n_ideias} gerado para marcha de Mafamude\n\n"
        f"Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
    )
    commit_and_push(str(REPO_DIR), commit_msg, [str(IDEIAS_FILE)])
    print("  Commit + push feitos.")
    print(f"\n✓ Ideia #{n_ideias} gerada e guardada em ideias.md")


if __name__ == "__main__":
    main()
