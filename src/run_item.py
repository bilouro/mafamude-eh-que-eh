"""
run_item.py
Processa UM item do backlog por execução.

Usage:
    python src/run_item.py --item 5
    python src/run_item.py --next        # primeiro pendente
    python src/run_item.py --list
"""
import argparse
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from git_helper import commit_and_push, pull
from openai_client import ask, load_config

REPO_DIR = Path(__file__).parent.parent
SOBRE_DIR = REPO_DIR / "sobre_mafamude"


def parse_backlog() -> list:
    """
    Lê backlog.md e devolve lista plana de itens com metadados de categoria.
    """
    content = (SOBRE_DIR / "backlog.md").read_text(encoding="utf-8")
    items = []
    current_cat = None
    current_file = None
    current_key = None
    q_idx = 0

    for line in content.splitlines():
        m = re.match(r'^## (.+?) →\s*\[([^\]]+)\]\([^\)]+\)', line)
        if m:
            current_cat = m.group(1).strip()
            current_file = m.group(2).strip()
            current_key = re.sub(r'\.md$', '', current_file)
            q_idx = 0
            continue

        m = re.match(r'^- \[([ x])\] (.+)', line)
        if m and current_cat:
            done = m.group(1) == 'x'
            question = m.group(2).strip()
            items.append({
                'cat_key': current_key,
                'cat_title': current_cat,
                'cat_file': current_file,
                'q_idx': q_idx,
                'question': question,
                'done': done,
            })
            q_idx += 1

    return items


def format_section(question: str, result: dict) -> str:
    conclusion = result.get("conclusion", {})
    reasoning = result.get("reasoning", {})
    answer = conclusion.get("answer", "_(sem resposta)_")
    confidence = conclusion.get("confidence", "")
    unconfirmed = conclusion.get("unconfirmed_points", [])
    sources = reasoning.get("sources_used", [])

    lines = [f"## {question}", "", answer, ""]
    if confidence:
        lines.append(f"**Confiança:** {confidence}  ")
    if sources:
        names = [s.get("title") or s.get("author_or_institution", "") for s in sources]
        names = [n for n in names if n]
        if names:
            lines.append(f"**Fontes:** {'; '.join(names)}  ")
    if unconfirmed:
        lines.append(f"**Pontos não confirmados:** {'; '.join(unconfirmed)}  ")
    lines += ["", "---", ""]
    return "\n".join(lines)


def md_header(item: dict) -> str:
    today = date.today().isoformat()
    return (
        f"# {item['cat_title']} — Mafamude\n"
        f"> Gerado automaticamente via historiador IA.  \n"
        f"> Verificar e complementar com fontes primárias antes de usar na letra/cenografia.  \n"
        f"> Data: {today}\n\n---\n\n"
    )


def mark_backlog(question: str):
    path = SOBRE_DIR / "backlog.md"
    content = path.read_text(encoding="utf-8")
    escaped = re.escape(question)
    new = re.sub(rf"- \[ \] ({escaped})", r"- [x] \1", content, count=1)
    path.write_text(new, encoding="utf-8")


def process_item(item: dict, n: int, total: int, config) -> bool:
    """
    Executa um item: pesquisa → guarda → marca backlog → commit+push.
    """
    out_path = SOBRE_DIR / item["cat_file"]
    question = item["question"]

    if not out_path.exists():
        out_path.write_text(md_header(item), encoding="utf-8")

    payload = {
        "question": question,
        "language": "pt-PT",
        "location_focus": ["Mafamude", "Vila Nova de Gaia"],
        "require_sources": True,
        "max_sources": 6,
    }
    result = ask(payload, config)

    if result.get("error"):
        section = f"## {question}\n\n_(Erro na pesquisa)_\n\n---\n\n"
    else:
        section = format_section(question, result)

    with open(out_path, "a", encoding="utf-8") as f:
        f.write(section)

    mark_backlog(question)

    commit_msg = (
        f"research({item['cat_key']}): {question[:70]}\n\n"
        f"Item {n}/{total} — {item['cat_title']}\n\n"
        f"Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
    )
    commit_and_push(str(REPO_DIR), commit_msg, [str(out_path), str(SOBRE_DIR / "backlog.md")])

    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--item", type=int, help="Número do item a processar (1-based)")
    parser.add_argument("--next", action="store_true", help="Processar o primeiro item pendente")
    parser.add_argument("--list", action="store_true", help="Listar todos os itens")
    parser.add_argument("--config", default=str(REPO_DIR / "config.ini"))
    args = parser.parse_args()

    pull(str(REPO_DIR))
    items = parse_backlog()
    total = len(items)

    if args.list:
        for i, it in enumerate(items, 1):
            status = "x" if it["done"] else " "
            print(f"{i:3d}/{total} [{status}] [{it['cat_title']}] {it['question']}")
        return

    if args.next:
        for i, it in enumerate(items, 1):
            if not it["done"]:
                n = i
                break
        else:
            print("Sem itens pendentes.")
            sys.exit(0)
    elif args.item:
        n = args.item
    else:
        parser.print_help()
        sys.exit(1)

    if n < 1 or n > total:
        print(f"Item {n} inválido. Range: 1–{total}")
        sys.exit(1)

    item = items[n - 1]
    if item["done"]:
        print(f"[SKIP] Item {n}/{total} já concluído.")
        sys.exit(0)

    config = load_config(args.config)
    process_item(item, n, total, config)
    print(f"✓ Item {n}/{total} concluído — [{item['cat_title']}] {item['question'][:70]}")


if __name__ == "__main__":
    main()
