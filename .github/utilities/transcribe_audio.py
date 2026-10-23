"""Guarded audio entry point: no service, model, SDK, or data transfer is selected."""

from __future__ import annotations

import argparse
from typing import NoReturn

from artifact_io import ArtifactInputError, PathInput
from extract_source import _print_error


def transcribe_audio(
    source: PathInput, *, service: str | None = None, model: str | None = None,
    data_scope: str | None = None, operation: str | None = None,
    output: PathInput | None = None, authorized: bool = False,
) -> NoReturn:
    """Always refuse until a separately approved concrete adapter exists.

    Supplied strings or an authorized flag cannot install or select an adapter.
    This entry point never opens the audio or output, reads secrets, or discovers providers.
    """
    missing = [name for name, value in (
        ("source", source), ("service", service), ("model", model),
        ("data_scope", data_scope), ("operation", operation), ("output", output),
    ) if value is None or isinstance(value, str) and not value.strip()]
    if authorized is not True:
        raise ArtifactInputError(
            "AUDIO_AUTHORIZATION_REQUIRED", "audio", 1,
            "Separate input/service/model/data_scope/operation/output authorization is required. "
            "Missing inputs: " + (", ".join(missing) if missing else "none; authorization remains required"),
        )
    if missing:
        raise ArtifactInputError("AUDIO_INPUT_REQUIRED", "audio", 1, "Supply explicitly approved " + ", ".join(missing))
    if operation != "transcribe":
        raise ArtifactInputError("AUDIO_INPUT_REQUIRED", "audio", 1, "The only represented operation is transcribe")
    raise ArtifactInputError(
        "SOURCE_ADAPTER_UNAVAILABLE", "audio", 1,
        "No audio service/model/SDK adapter has been selected or approved. Nothing was read, sent or transcribed. "
        "Obtain separate adapter/version, input/data-transfer and new-output authorization first.",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True)
    parser.add_argument("--service")
    parser.add_argument("--model")
    parser.add_argument("--data-scope")
    parser.add_argument("--operation")
    parser.add_argument("--output")
    parser.add_argument("--authorized", action="store_true")
    args = parser.parse_args()
    try:
        transcribe_audio(
            args.source, service=args.service, model=args.model, data_scope=args.data_scope,
            operation=args.operation, output=args.output, authorized=args.authorized,
        )
    except ArtifactInputError as error:
        return _print_error(error)


if __name__ == "__main__":
    raise SystemExit(main())
