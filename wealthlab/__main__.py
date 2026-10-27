"""Configure repository-local runtime paths before importing numerical engines."""

from wealthlab.runtime import configure

configure()

from wealthlab.cli import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
