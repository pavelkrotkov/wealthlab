"""Local commands reuse the exact UI household engine.

JSON stdout is an explicit local report and can contain private financial values.
Selected-file output uses the same guarded exclusive writer as the UI. Errors
omit scenario values and private input paths rather than echoing a validation dump.
"""

import argparse
import sys
from pathlib import Path

from pydantic import ValidationError

from wealthlab import country_report
from wealthlab.household import report
from wealthlab.local_files import write_new
from wealthlab.local_launch import serve
from wealthlab.optimization import report as policy_report


def parser():
    cli = argparse.ArgumentParser(prog="python -m wealthlab")
    commands = cli.add_subparsers(dest="command", required=True)
    launch = commands.add_parser("serve", help="Launch the local browser UI on loopback")
    launch.add_argument("--port", type=int, default=8501)
    project = commands.add_parser("project", help="Project an explicitly selected household JSON")
    project.add_argument("scenario", type=Path)
    compare = commands.add_parser(
        "compare", help="Compare selected household scenarios on aligned dates"
    )
    compare.add_argument("baseline", type=Path)
    compare.add_argument("candidate", type=Path)
    optimize = commands.add_parser(
        "optimize", help="Evaluate an explicitly bounded policy-search JSON"
    )
    optimize.add_argument("scenario", type=Path)
    for command in (project, compare, optimize):
        command.add_argument("--output-directory", type=Path)
        command.add_argument("--filename")
    return cli


def main(argv=None):
    options = parser().parse_args(argv)
    try:
        if options.command == "serve":
            return serve(options.port)
        if options.filename is not None and options.output_directory is None:
            raise ValueError("Select an output directory for a named report.")
        result = calculate(options)
        emit(report.encode(result), options)
        return 0
    except KeyboardInterrupt:
        return 130
    except ValidationError:
        print(
            "Invalid scenario. Review field diagnostics in the local UI; no report was written.",
            file=sys.stderr,
        )
    except (ValueError, OSError):
        print(
            "Cannot complete this local action. Check input, dates and private output path. "
            "Existing files are never overwritten.",
            file=sys.stderr,
        )
    return 2


def emit(text, options):
    if options.output_directory is None:
        sys.stdout.write(text)
        return
    filename = (
        options.filename
        or {
            "project": "projection.json",
            "compare": "comparison.json",
            "optimize": "policy-search.json",
        }[options.command]
    )
    write_new(text, options.output_directory, filename)
    print("Saved a new report in the explicitly selected private directory.")


def calculate(options):
    if options.command == "project":
        return country_report.run(options.scenario)
    if options.command == "compare":
        return country_report.compare(options.baseline, options.candidate)
    return policy_report.run(options.scenario)
