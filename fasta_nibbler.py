from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Iterable, Iterator, Sequence, Tuple

LOGGER = logging.getLogger(__name__)


def positive_int(value: str) -> int:
    """Argparse type: require a strictly positive integer."""
    try:
        ivalue = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"{value!r} is not an integer") from exc

    if ivalue <= 0:
        raise argparse.ArgumentTypeError(f"{ivalue} is not a positive integer")
    return ivalue


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="first_last_fasta",
        description=(
            "Extract the first and/or last N base pairs from each FASTA record "
            "and write to a new FASTA file."
        ),
    )

    parser.add_argument(
        "-t",
        "--type",
        required=True,
        type=int,
        choices=(1, 2, 3, 4),
        help=(
            "Output type: 1=full sequence, 2=5' ends, 3=3' ends, 4=5' and 3' ends."
        ),
    )
    parser.add_argument(
        "-i",
        "--input",
        required=True,
        type=Path,
        help="Input FASTA file, or a directory containing FASTA files.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help=(
            "If --input is a file: output FASTA filepath. "
            "If --input is a directory: output directory. "
            "Default is derived from input."
        ),
    )
    parser.add_argument(
        "-bp",
        "--basepairs",
        type=positive_int,
        default=300,
        help="Number of base pairs to extract from each end (default: 300).",
    )
    parser.add_argument(
        "--extensions",
        nargs="+",
        default=[".fa", ".fasta", ".fna", ".ffn", ".faa", ".frn"],
        help=(
            "File extensions to consider when --input is a directory "
            "(default: common FASTA extensions)."
        ),
    )
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="When --input is a directory, search recursively.",
    )
    parser.add_argument(
        "--wrap",
        type=positive_int,
        default=60,
        help="Wrap FASTA sequence lines to this width (default: 60).",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable INFO-level logging.",
    )

    return parser.parse_args(argv)


def iter_fasta_records(path: Path) -> Iterator[Tuple[str, str]]:
    """
    Stream FASTA records from a file.

    Yields:
        (header_without_>, sequence_without_whitespace)
    """
    header: str | None = None
    chunks: list[str] = []

    with path.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line:
                continue
            if line.startswith(">"):
                if header is not None:
                    yield header, "".join(chunks)
                header = line[1:].strip()
                chunks = []
            else:
                chunks.append(line)

    if header is not None:
        yield header, "".join(chunks)


def wrap_sequence(seq: str, width: int) -> str:
    """Return sequence wrapped to fixed width with a trailing newline."""
    if width <= 0:
        return seq + "\n"
    return "\n".join(seq[i : i + width] for i in range(0, len(seq), width)) + "\n"


def ends(seq: str, bp: int) -> Tuple[str, str]:
    """Return (5prime, 3prime); if seq shorter than bp, both are full seq."""
    if len(seq) <= bp:
        return seq, seq
    return seq[:bp], seq[-bp:]


def type_label(type_id: int) -> str:
    return {
        1: "full",
        2: "5prime",
        3: "3prime",
        4: "5and3prime",
    }[type_id]


def default_output_for_file(input_file: Path, type_id: int) -> Path:
    label = type_label(type_id)
    return input_file.with_name(f"{input_file.stem}.{label}.fasta")


def collect_input_files(
    input_path: Path, extensions: Iterable[str], recursive: bool
) -> list[Path]:
    if input_path.is_file():
        return [input_path]

    if not input_path.is_dir():
        raise FileNotFoundError(f"Input path does not exist: {input_path}")

    exts = {e.lower() if e.startswith(".") else f".{e.lower()}" for e in extensions}
    globber = input_path.rglob("*") if recursive else input_path.glob("*")
    files = sorted(p for p in globber if p.is_file() and p.suffix.lower() in exts)
    return files


def process_one_file(
    input_file: Path,
    output_file: Path,
    type_id: int,
    bp: int,
    wrap_width: int,
) -> None:
    records = iter_fasta_records(input_file)

    output_file.parent.mkdir(parents=True, exist_ok=True)
    with output_file.open("w", encoding="utf-8") as out:
        for header, seq in records:
            five_p, three_p = ends(seq, bp)

            if type_id == 1:
                out.write(f">fullseq_{header}\n")
                out.write(wrap_sequence(seq, wrap_width))
            elif type_id == 2:
                out.write(f">5_prime_{header}\n")
                out.write(wrap_sequence(five_p, wrap_width))
            elif type_id == 3:
                out.write(f">3_prime_{header}\n")
                out.write(wrap_sequence(three_p, wrap_width))
            elif type_id == 4:
                out.write(f">5_prime_{header}\n")
                out.write(wrap_sequence(five_p, wrap_width))
                out.write(f">3_prime_{header}\n")
                out.write(wrap_sequence(three_p, wrap_width))
            else:
                raise ValueError(f"Unexpected type: {type_id}")


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)

    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(levelname)s: %(message)s",
    )

    input_path: Path = args.input
    input_files = collect_input_files(input_path, args.extensions, args.recursive)

    if not input_files:
        LOGGER.warning("No input FASTA files found under: %s", input_path)
        return 2

    # Output handling:
    # - input is a file: --output is a file (optional)
    # - input is a dir : --output is a dir (optional)
    if input_path.is_file():
        output_file = args.output if args.output is not None else default_output_for_file(input_path, args.type)
        process_one_file(input_path, output_file, args.type, args.basepairs, args.wrap)
        LOGGER.info("Wrote: %s", output_file)
        return 0

    output_dir = args.output if args.output is not None else (input_path / "first_last_out")
    output_dir.mkdir(parents=True, exist_ok=True)

    for f in input_files:
        out_path = output_dir / default_output_for_file(f.name if isinstance(f.name, Path) else f, args.type).name  # safe name
        # The above line is overly defensive; simplest is:
        out_path = output_dir / f"{f.stem}.{type_label(args.type)}.fasta"
        process_one_file(f, out_path, args.type, args.basepairs, args.wrap)
        LOGGER.info("Wrote: %s", out_path)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
