## fasta_nibbler

`fasta_nibbler` extracts the first and/or last N base pairs from each record in a FASTA file and writes the result to a new FASTA file.
It supports either a single input FASTA file or batch processing of all FASTA files in a directory (optionally recursive).

The main code logic and documentation have been updated with the assistance of GPT 5.2 with reasoning.

## Installation

- Requires Python 3.9+ (recommended: Python 3.11+).
- No external dependencies.

## Usage

**Command**
- `python fasta_nibbler.py -t {1,2,3,4} -i INPUT [-o OUTPUT] [-bp N] [--extensions ...] [-r] [--wrap N] [-v]`

**Output types (`-t`, `--type`, required)**
- `1`: Full sequence (same as input).
- `2`: 5' ends only.
- `3`: 3' ends only.
- `4`: Both 5' and 3' ends (two records per input record).

**Examples**
- Single file (auto-named output):  
  `python fasta_nibbler.py -t 2 -i example.fasta -bp 300`
- Single file (explicit output):  
  `python fasta_nibbler.py -t 4 -i example.fasta -o example.ends.fasta -bp 200`
- Directory batch mode (writes one output per FASTA):  
  `python fasta_nibbler.py -t 3 -i ./fastas/ -bp 100`
- Directory recursive + custom output directory:  
  `python fasta_nibbler.py -t 2 -i ./fastas/ -r -o ./processed_fastas/`

## Arguments

- `-i, --input` (required): Path to an input FASTA file **or** a directory containing FASTA files.
- `-o, --output` (optional):  
  - If `--input` is a file: output FASTA filepath.
  - If `--input` is a directory: output directory.
  - If omitted: a default output name/location is derived from the input.
- `-bp, --basepairs` (optional, default: `300`): Number of base pairs to take from each end (must be a positive integer).
- `--extensions` (optional): File extensions to include when `--input` is a directory (default includes common FASTA extensions such as `.fa`, `.fasta`, `.fna`, etc.).
- `-r, --recursive` (optional): When `--input` is a directory, search recursively for FASTA files.
- `--wrap` (optional, default: `60`): Wrap output FASTA sequences to this line width.
- `-v, --verbose` (optional): Enable more detailed logging.

## Output naming

- If `--input` is a file and `--output` is not provided, output defaults to:  
  `INPUT_STEM.{full|5prime|3prime|5and3prime}.fasta` 
- If `--input` is a directory and `--output` is not provided, outputs are written under a default output folder within the input directory (one output file per input file).

If you found this useful for your project, please cite this as:  
 
[![DOI](https://zenodo.org/badge/975677185.svg)](https://doi.org/10.5281/zenodo.15312728)