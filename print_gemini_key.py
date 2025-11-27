from pathlib import Path
import sys


def read_gemini_key(secrets_path=None):
    if secrets_path is None:
        path = Path.cwd() / ".streamlit" / "secrets.toml"
    else:
        p = Path(secrets_path)
        if p.is_dir():
            path = p / ".streamlit" / "secrets.toml"
        else:
            path = p

    if not path.exists():
        print(f"Secrets file not found: {path}", file=sys.stderr)
        return 1

    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line_strip = line.strip()
            if line_strip.startswith("GEMINI_API_KEY"):
                parts = line_strip.split("=", 1)
                if len(parts) < 2:
                    continue
                val = parts[1].strip()
                if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                    val = val[1:-1]
                print(val)
                return 0

    print("GEMINI_API_KEY not found in secrets file", file=sys.stderr)
    return 2


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Print GEMINI_API_KEY from .streamlit/secrets.toml")
    parser.add_argument("--path", "-p", help="Path to secrets.toml file or project root", default=None)
    args = parser.parse_args()

    exit(read_gemini_key(args.path))
