"""
researcher.py
Loop sobre todos os itens pendentes do backlog, item a item.
Pull inicial, depois executa cada pendente com commit+push entre cada um.

Usage:
    python researcher.py                          # todos os pendentes
    python researcher.py --category gastronomia   # só uma categoria
    python researcher.py --list                   # listar categorias e progresso
"""
import argparse
import sys

from git_helper import pull
from openai_client import load_config
from run_item import REPO_DIR, parse_backlog, process_item


def main():
    parser = argparse.ArgumentParser(description="Researcher — sweep do backlog de Mafamude")
    parser.add_argument("--category", "-c", help="Filtrar por categoria (cat_key, ex: gastronomia)")
    parser.add_argument("--count", "-n", type=int, help="Número máximo de itens a processar")
    parser.add_argument("--list", "-l", action="store_true", help="Listar categorias e progresso")
    parser.add_argument("--config", default="config.ini")
    args = parser.parse_args()

    pull(str(REPO_DIR))
    items = parse_backlog()

    if args.list:
        # Agrupar por categoria para mostrar progresso
        cats = {}
        for it in items:
            key = it["cat_key"]
            if key not in cats:
                cats[key] = {"title": it["cat_title"], "total": 0, "done": 0}
            cats[key]["total"] += 1
            if it["done"]:
                cats[key]["done"] += 1
        for key, c in cats.items():
            print(f"  {key:35s} {c['done']:2d}/{c['total']:2d}  {c['title']}")
        return

    # Filtrar por categoria se pedido
    if args.category:
        pending = [it for it in items if not it["done"] and it["cat_key"] == args.category]
        if not pending:
            print(f"Sem itens pendentes na categoria '{args.category}'.")
            sys.exit(0)
    else:
        pending = [it for it in items if not it["done"]]

    if args.count:
        pending = pending[:args.count]

    total_all = len(items)
    total_pending = len(pending)

    if not total_pending:
        print("Sem itens pendentes. Backlog completo.")
        sys.exit(0)

    print(f"Itens pendentes: {total_pending}")
    config = load_config(args.config)

    for idx, item in enumerate(pending, 1):
        # Calcular posição global no backlog
        n_global = next(i + 1 for i, it in enumerate(items) if it is item)
        print(f"\n[{idx}/{total_pending}] [{item['cat_title']}] {item['question'][:80]}")
        try:
            process_item(item, n_global, total_all, config)
            print(f"  ✓ commit ok")
        except Exception as e:
            print(f"  ✗ ERRO: {e}")

    print(f"\nSweep concluído: {total_pending} itens processados.")


if __name__ == "__main__":
    main()
