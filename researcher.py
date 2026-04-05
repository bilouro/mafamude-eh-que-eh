"""
researcher.py
Orquestrador de pesquisa automática por categoria.
Lê categorias e perguntas directamente do backlog.md (não depende de research_questions.py).
Processa cada pergunta individualmente, com commit+push após cada uma.

Usage:
    python researcher.py --all
    python researcher.py --category gastronomia
    python researcher.py --category lendas_historias --force
    python researcher.py --list
"""
import argparse
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

from openai_client import ask, load_config

REPO_DIR = Path(__file__).parent


def parse_backlog() -> tuple:
    """
    Lê backlog.md e devolve (categories_dict, order_list).
    Formato esperado:
        ## Título da Categoria → [ficheiro.md](ficheiro.md)
        - [ ] Pergunta pendente
        - [x] Pergunta concluída
    """
    content = (REPO_DIR / "backlog.md").read_text(encoding="utf-8")
    categories = {}
    order = []
    current_key = None

    for line in content.splitlines():
        m = re.match(r'^## (.+?) →\s*\[([^\]]+)\]\([^\)]+\)', line)
        if m:
            title = m.group(1).strip()
            file_ = m.group(2).strip()
            current_key = re.sub(r'\.md$', '', file_)
            if current_key not in categories:
                categories[current_key] = {
                    'title': title,
                    'file': file_,
                    'questions': [],
                }
                order.append(current_key)
            continue

        m = re.match(r'^- \[([ x])\] (.+)', line)
        if m and current_key:
            done = m.group(1) == 'x'
            categories[current_key]['questions'].append({
                'text': m.group(2).strip(),
                'done': done,
            })

    return categories, order


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
        source_names = [s.get("title") or s.get("author_or_institution", "") for s in sources]
        source_names = [s for s in source_names if s]
        if source_names:
            lines.append(f"**Fontes:** {'; '.join(source_names)}  ")

    if unconfirmed:
        lines.append(f"**Pontos não confirmados:** {'; '.join(unconfirmed)}  ")

    lines += ["", "---", ""]
    return "\n".join(lines)


def md_header(cat: dict) -> str:
    today = date.today().isoformat()
    return (
        f"# {cat['title']} — Mafamude\n"
        f"> Gerado automaticamente via historiador IA.  \n"
        f"> Verificar e complementar com fontes primárias antes de usar na letra/cenografia.  \n"
        f"> Data: {today}\n\n---\n\n"
    )


def mark_backlog_question(question: str):
    path = REPO_DIR / "backlog.md"
    content = path.read_text(encoding="utf-8")
    escaped = re.escape(question)
    new_content = re.sub(
        rf"- \[ \] ({escaped})",
        r"- [x] \1",
        content,
        count=1,
    )
    path.write_text(new_content, encoding="utf-8")


def git_commit_push(files: list, message: str):
    subprocess.run(["git", "add"] + files, cwd=REPO_DIR, check=True)
    subprocess.run(["git", "commit", "-m", message], cwd=REPO_DIR, check=True)
    subprocess.run(["git", "push", "origin", "main"], cwd=REPO_DIR, check=True)


def main():
    parser = argparse.ArgumentParser(description="Researcher — catalogação de Mafamude")
    parser.add_argument("--category", "-c", help="Chave de categoria a pesquisar (ex: gastronomia)")
    parser.add_argument("--all", "-a", action="store_true", help="Pesquisar todas as categorias")
    parser.add_argument("--force", "-f", action="store_true", help="Re-pesquisar mesmo que já marcado")
    parser.add_argument("--config", default="config.ini")
    parser.add_argument("--list", "-l", action="store_true", help="Listar categorias disponíveis")
    args = parser.parse_args()

    categories, order = parse_backlog()

    if args.list:
        for key in order:
            cat = categories[key]
            total_q = len(cat['questions'])
            done_q = sum(1 for q in cat['questions'] if q['done'])
            print(f"  {key:35s} → {cat['file']}  ({done_q}/{total_q} feitas)")
        return

    config = load_config(args.config)

    if args.all:
        keys = order
    elif args.category:
        if args.category not in categories:
            print(f"Categoria '{args.category}' não encontrada. Use --list para ver as disponíveis.")
            sys.exit(1)
        keys = [args.category]
    else:
        parser.print_help()
        sys.exit(1)

    # Construir lista plana de items a processar
    items = []
    for key in keys:
        cat = categories[key]
        for q_idx, q in enumerate(cat['questions']):
            items.append((key, q_idx, q['text'], q['done']))

    total = len(items)

    for idx, (cat_key, q_idx, question, already_done) in enumerate(items, 1):
        cat = categories[cat_key]
        out_path = REPO_DIR / cat["file"]

        if already_done and not args.force:
            print(f"Item {idx}/{total} — [SKIP já feito] {cat['title']} — {question[:60]}...")
            continue

        print(f"Item {idx}/{total} — {cat['title']} — {question[:70]}...")

        if not out_path.exists():
            out_path.write_text(md_header(cat), encoding="utf-8")

        try:
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

            mark_backlog_question(question)

            commit_msg = f"research: {cat['title']} — {question[:60]}"
            git_commit_push([str(out_path.name), "backlog.md"], commit_msg)

            print(f"  ✓ commit ok")

        except Exception as e:
            print(f"  ✗ ERRO: {e}")

    print(f"\nConcluído: {total} itens processados.")


if __name__ == "__main__":
    main()
