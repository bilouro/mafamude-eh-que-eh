"""
researcher.py
Orquestrador de pesquisa automática por categoria.
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
from research_questions import CATEGORIES

REPO_DIR = Path(__file__).parent


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


def md_header(category_key: str) -> str:
    cat = CATEGORIES[category_key]
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


def mark_projectplan_category(label: str):
    path = REPO_DIR / "projectplan.md"
    content = path.read_text(encoding="utf-8")
    escaped = re.escape(label)
    new_content = re.sub(
        rf"- \[ \] \[({escaped})\]",
        r"- [x] [\1]",
        content,
        count=1,
    )
    path.write_text(new_content, encoding="utf-8")


def git_commit_push(files: list, message: str):
    subprocess.run(["git", "add"] + files, cwd=REPO_DIR, check=True)
    subprocess.run(["git", "commit", "-m", message], cwd=REPO_DIR, check=True)
    subprocess.run(["git", "push", "origin", "main"], cwd=REPO_DIR, check=True)


def build_item_list(keys: list) -> list:
    """Retorna lista plana de (category_key, question_index, question)."""
    items = []
    for key in keys:
        for i, q in enumerate(CATEGORIES[key]["questions"]):
            items.append((key, i, q))
    return items


def main():
    parser = argparse.ArgumentParser(description="Researcher — catalogação de Mafamude")
    parser.add_argument("--category", "-c", help="Categoria a pesquisar")
    parser.add_argument("--all", "-a", action="store_true", help="Pesquisar todas as categorias")
    parser.add_argument("--force", "-f", action="store_true", help="Re-pesquisar mesmo que pergunta já esteja marcada")
    parser.add_argument("--config", default="config.ini")
    parser.add_argument("--list", "-l", action="store_true", help="Listar categorias")
    args = parser.parse_args()

    if args.list:
        for key, cat in CATEGORIES.items():
            print(f"  {key:35s} → {cat['file']}")
        return

    config = load_config(args.config)

    if args.all:
        keys = list(CATEGORIES.keys())
    elif args.category:
        if args.category not in CATEGORIES:
            print(f"Categoria '{args.category}' não encontrada.")
            sys.exit(1)
        keys = [args.category]
    else:
        parser.print_help()
        sys.exit(1)

    items = build_item_list(keys)
    total = len(items)

    # Ler backlog para saber quais já estão marcados
    backlog_content = (REPO_DIR / "backlog.md").read_text(encoding="utf-8")

    for idx, (cat_key, q_idx, question) in enumerate(items, 1):
        cat = CATEGORIES[cat_key]
        out_path = REPO_DIR / cat["file"]

        # Verificar se já está marcado no backlog
        escaped = re.escape(question)
        already_done = bool(re.search(rf"- \[x\] {escaped}", backlog_content))
        if already_done and not args.force:
            print(f"Item {idx}/{total} — [SKIP já feito] {cat['title']} — {question[:60]}...")
            continue

        print(f"Item {idx}/{total} — {cat['title']} — {question[:70]}...")

        # Inicializar .md com header se não existir
        if not out_path.exists():
            out_path.write_text(md_header(cat_key), encoding="utf-8")

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

            # Append ao ficheiro .md
            with open(out_path, "a", encoding="utf-8") as f:
                f.write(section)

            # Marcar checkbox no backlog
            mark_backlog_question(question)
            # Actualizar backlog_content em memória
            backlog_content = (REPO_DIR / "backlog.md").read_text(encoding="utf-8")

            # Se é a última pergunta da categoria, marcar projectplan
            cat_questions = CATEGORIES[cat_key]["questions"]
            if q_idx == len(cat_questions) - 1:
                mark_projectplan_category(cat["projectplan_label"])

            # Commit + push
            commit_msg = f"research: {cat['title']} — {question[:60]}"
            files_to_commit = [str(out_path.name), "backlog.md"]
            if q_idx == len(cat_questions) - 1:
                files_to_commit.append("projectplan.md")
            git_commit_push(files_to_commit, commit_msg)

            print(f"  ✓ commit ok")

        except Exception as e:
            print(f"  ✗ ERRO: {e}")

    print(f"\nConcluído: {total} itens processados.")


if __name__ == "__main__":
    main()
