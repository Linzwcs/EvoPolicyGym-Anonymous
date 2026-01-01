# Review artifact

This snapshot provides the v0.3.0 kernel, independent Benchmark distributions,
packaged baseline policies, example runners, tests, and local documentation.
The Python package and command names in this artifact are `evopolicygym` and
`evopolicygym-session`. Install the local source and its locked dependencies;
do not install a similarly named package from a public package index.

## Reproduce the checks

Use Python 3.12 and uv 0.11.16 from the repository root:

```console
uv sync --locked --extra dev
uv run ruff check src tests
uv run mypy
uv run python -m unittest discover -s tests
uv run evopolicygym --version
uv run evopolicygym-session --version
uv build
uv sync --project environments/gymnasium/classic_control/cartpole --locked --extra dev
uv run --project environments/gymnasium/classic_control/cartpole python -m unittest discover -s environments/gymnasium/classic_control/cartpole/tests
```

The [quickstart](docs/getting-started.md) evaluates a bundled baseline without
an API key. Agent optimization additionally requires a supported coding-agent
CLI and the reviewer's own credentials. `ProcessExecution.unsafe()` does not
isolate untrusted code; run only trusted policies and agents.

## Reproducibility scope

The original package names, seed domains, content-digest domains, benchmark
logic, and test fixtures are retained. Anonymization does not change their
computational behavior. This is a current implementation snapshot, not the
historical paper release; historical leaderboard results and unavailable run
artifacts are not supplied here.

## Contents and attribution

Author contact details, publication identifiers, original project links,
public-site assets, and previous Git history are omitted. Third-party
licenses, upstream provenance, and required environment assets are retained.
The initial commit uses an anonymous identity. The static website uses local
assets and has no analytics, remote fonts, or third-party scripts.

The site entry point is [index.html](index.html). It can be served with:

```console
python3 -m http.server 8000 --bind 127.0.0.1
```

The local [documentation](docs/index.md) is also available independently of
the website and the hosting service.

To rebuild the website from the local documentation:

```console
uv run scripts/build_review_site.py
```

The script pins its Markdown renderer and generates the landing page and
HTML documentation. Serve the repository root, with `index.html` as the
website entry point. The project name is intentionally retained; the source
and site remove direct author identification, not discoverability through
deliberate searches for the public project name or code.
