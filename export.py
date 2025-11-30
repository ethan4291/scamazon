"""Export non-dynamic GET routes from the Flask app into a `docs/` folder.

Usage: python export.py

This will recreate `docs/`, render each non-parameterized GET route using
Flask's test client, write the HTML to the corresponding path under `docs/`,
and copy the `static/` folder to `docs/static/` so GitHub Pages can serve it.
"""
from pathlib import Path
import shutil
import sys

try:
    # Import the Flask app instance from app.py
    from app import app
except Exception as e:
    print("Failed to import Flask app from app.py:", e)
    sys.exit(1)


DOCS_DIR = Path("docs")


def _relative_static_prefix(out_path: Path) -> str:
        """Return a relative path prefix from out_path to the docs/ root.

        Examples:
            docs/index.html -> ''
            docs/foo/index.html -> '../'
            docs/foo/bar/index.html -> '../../'
        """
        parent = out_path.parent
        if parent == DOCS_DIR:
                return ''
        rel = parent.relative_to(DOCS_DIR)
        depth = len(rel.parts)
        return '../' * depth


def target_path_for_rule(rule):
    # Map a Flask rule like '/' or '/about' to a file under docs/
    if rule == "/":
        return DOCS_DIR / "index.html"
    # strip leading slash
    p = rule.lstrip("/")
    # Place each route in its own folder with an index.html so links work cleanly
    return DOCS_DIR / p / "index.html"


def main():
    # Recreate docs/
    if DOCS_DIR.exists():
        shutil.rmtree(DOCS_DIR)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    client = app.test_client()

    exported = []
    skipped = []

    # First handle simple, non-parameterized routes as before
    for rule in sorted(app.url_map.iter_rules(), key=lambda r: r.rule):
        # Only export GET routes and skip Flask static endpoint
        if 'GET' not in rule.methods:
            continue
        if rule.rule.startswith('/static') or rule.endpoint == 'static':
            skipped.append((rule.rule, 'static'))
            continue

        # If the rule has no arguments, render it directly
        if not rule.arguments:
            path = rule.rule
            resp = client.get(path)
            if resp.status_code != 200:
                skipped.append((path, f'status:{resp.status_code}'))
                continue

            out_path = target_path_for_rule(path)
            out_path.parent.mkdir(parents=True, exist_ok=True)

            html = resp.get_data(as_text=True)
            # Replace absolute /static/... references with relative paths that work
            rel_static_prefix = _relative_static_prefix(out_path)
            html = html.replace('/static/', rel_static_prefix + 'static/')

            out_path.write_text(html, encoding='utf-8')
            exported.append(str(out_path))
        else:
            # Dynamic routes: attempt a best-effort export for known targets
            # Example: export product pages if the app exposes a PRODUCTS list
            if rule.rule.startswith('/product'):
                # attempt to read PRODUCTS from the app module
                products = getattr(app, 'PRODUCTS', None)
                if products is None:
                    # try importing PRODUCTS from the app module namespace
                    try:
                        from app import PRODUCTS as PRODUCTS_CONST
                        products = PRODUCTS_CONST
                    except Exception:
                        products = None

                if products:
                    for p in products:
                        pid = p.get('id')
                        if not pid:
                            continue
                        path = f'/product/{pid}'
                        resp = client.get(path)
                        if resp.status_code != 200:
                            skipped.append((path, f'status:{resp.status_code}'))
                            continue
                        out_path = target_path_for_rule(path)
                        out_path.parent.mkdir(parents=True, exist_ok=True)
                        html = resp.get_data(as_text=True)
                        rel_static_prefix = _relative_static_prefix(out_path)
                        html = html.replace('/static/', rel_static_prefix + 'static/')
                        out_path.write_text(html, encoding='utf-8')
                        exported.append(str(out_path))
                else:
                    skipped.append((rule.rule, 'dynamic'))
            else:
                skipped.append((rule.rule, 'dynamic'))

    # Copy static/ into docs/static/
    static_src = Path('static')
    if static_src.exists() and static_src.is_dir():
        shutil.copytree(static_src, DOCS_DIR / 'static')

    print('\nExport complete.')
    print('Exported files:')
    for p in exported:
        print('  -', p)
    if skipped:
        print('\nSkipped routes:')
        for r, reason in skipped:
            print('  -', r, '(', reason, ')')


if __name__ == '__main__':
    main()
