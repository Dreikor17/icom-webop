#!/usr/bin/env python3
"""Launch the Icom WebOp server. Usage: python run.py [--host H] [--port P]"""
import argparse
import os
import sys
import webbrowser

# make the app importable and paths stable regardless of where we're launched
_HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(_HERE)
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import uvicorn


def main() -> None:
    ap = argparse.ArgumentParser(description="Icom WebOp server")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8700)
    ap.add_argument("--no-browser", action="store_true")
    ap.add_argument("--reload", action="store_true")
    args = ap.parse_args()

    url = f"http://{args.host if args.host != '0.0.0.0' else 'localhost'}:{args.port}"
    if not args.no_browser and not args.reload:
        try:
            webbrowser.open(url)
        except Exception:
            pass
    print(f"Icom WebOp -> {url}")
    uvicorn.run("backend.server:app", host=args.host, port=args.port,
                reload=args.reload, log_level="info")


if __name__ == "__main__":
    main()
