"""
openai_client.py
Sends questions to the Mafamude historian OpenAI stored prompt and returns structured JSON.

Usage:
    python openai_client.py --question "Qual é a origem do nome Mafamude?"
    python openai_client.py --input question.json
    python openai_client.py  # interactive mode
"""
import argparse
import json
import sys
from configparser import ConfigParser

from openai import OpenAI


def load_config(config_path: str = "config.ini") -> ConfigParser:
    config = ConfigParser()
    config.read(config_path, encoding="utf-8")
    return config


def build_question(question: str, **kwargs) -> dict:
    """Build the JSON input payload for the historian prompt."""
    payload = {"question": question}
    if "language" in kwargs:
        payload["language"] = kwargs["language"]
    if "location_focus" in kwargs:
        payload["location_focus"] = kwargs["location_focus"]
    if "topic_type" in kwargs:
        payload["topic_type"] = kwargs["topic_type"]
    if "time_scope" in kwargs:
        payload["time_scope"] = kwargs["time_scope"]
    if "require_sources" in kwargs:
        payload["require_sources"] = kwargs["require_sources"]
    if "max_sources" in kwargs:
        payload["max_sources"] = kwargs["max_sources"]
    return payload


def ask(payload: dict, config: ConfigParser) -> dict:
    """Send a question to the stored prompt and return the parsed JSON response."""
    client = OpenAI(api_key=config["openai"]["token"])

    response = client.responses.create(
        prompt={
            "id": config["openai"]["prompt_id"],
            "version": config["openai"]["prompt_version"],
        },
        input=json.dumps({**payload, "output": "json"}, ensure_ascii=False),
        tools=[],  # disable web search (incompatible with JSON output mode)
    )

    # Extract text from response
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


def print_result(result: dict):
    """Pretty-print the historian response."""
    if result.get("error"):
        print("\n[ERRO]")
        print(json.dumps(result["error"], ensure_ascii=False, indent=2))
        return

    conclusion = result.get("conclusion", {})
    reasoning = result.get("reasoning", {})

    print("\n" + "=" * 60)
    print("RESPOSTA")
    print("=" * 60)
    print(conclusion.get("answer", ""))

    confidence = conclusion.get("confidence", "")
    print(f"\nConfiança: {confidence}")

    unconfirmed = conclusion.get("unconfirmed_points", [])
    if unconfirmed:
        print("\nPontos não confirmados:")
        for p in unconfirmed:
            print(f"  - {p}")

    confirmed = reasoning.get("confirmed_facts", [])
    if confirmed:
        print("\nFactos confirmados:")
        for f in confirmed:
            print(f"  ✓ {f}")

    uncertainties = reasoning.get("uncertainties_disputed_points", [])
    if uncertainties:
        print("\nIncertezas / pontos disputados:")
        for u in uncertainties:
            print(f"  ? {u}")

    sources = reasoning.get("sources_used", [])
    if sources:
        print(f"\nFontes ({len(sources)}):")
        for s in sources:
            title = s.get("title", "")
            institution = s.get("author_or_institution", "")
            url = s.get("url", "")
            source_type = s.get("source_type", "")
            line = f"  [{source_type}] {title}"
            if institution:
                line += f" — {institution}"
            if url:
                line += f"\n    {url}"
            print(line)

    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Historiador de Mafamude — cliente OpenAI")
    parser.add_argument("--question", "-q", help="Pergunta em texto livre")
    parser.add_argument("--input", "-i", help="Ficheiro JSON com payload completo")
    parser.add_argument("--config", default="config.ini", help="Caminho para config.ini")
    parser.add_argument("--raw", action="store_true", help="Mostrar JSON raw em vez de formatado")
    parser.add_argument("--language", default="pt-PT")
    parser.add_argument("--topic-type", default=None)
    parser.add_argument("--max-sources", type=int, default=8)
    args = parser.parse_args()

    config = load_config(args.config)

    # Build payload
    if args.input:
        with open(args.input, encoding="utf-8") as f:
            payload = json.load(f)
    elif args.question:
        payload = build_question(
            question=args.question,
            language=args.language,
            location_focus=["Mafamude", "Vila Nova de Gaia"],
            require_sources=True,
            max_sources=args.max_sources,
            **({"topic_type": args.topic_type} if args.topic_type else {}),
        )
    else:
        # Interactive mode
        print("Historiador de Mafamude")
        print("Escreva a sua pergunta (ou 'sair' para terminar):\n")
        while True:
            question = input("> ").strip()
            if question.lower() in ("sair", "exit", "quit"):
                break
            if not question:
                continue
            payload = build_question(
                question=question,
                language="pt-PT",
                location_focus=["Mafamude", "Vila Nova de Gaia"],
                require_sources=True,
                max_sources=8,
            )
            try:
                result = ask(payload, config)
                if args.raw:
                    print(json.dumps(result, ensure_ascii=False, indent=2))
                else:
                    print_result(result)
            except Exception as e:
                print(f"Erro: {e}")
        return

    try:
        result = ask(payload, config)
        if args.raw:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print_result(result)
    except Exception as e:
        print(f"Erro: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
