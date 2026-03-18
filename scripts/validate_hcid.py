import json
import sys


def validate_hcid_json(schema_file, json_file):
    from jsonschema import validate, exceptions

    with open(json_file, "r") as f:
        data = json.load(f)

    with open(schema_file, "r") as f:
        schema = json.load(f)

    try:
        validate(instance=data, schema=schema)
        print("HCID JSON is valid.")
    except exceptions.ValidationError as e:
        print("HCID JSON is invalid:", e)
        sys.exit(1)


def fasta_validate(json_file, fasta_file):
    from Bio import SeqIO
    import gzip

    failure = False

    with open(json_file, "r") as f:
        data = json.load(f)

    with gzip.open(fasta_file, "rt") as f:
        seqs = list(SeqIO.parse(f, "fasta"))
        seq_ids = set(seq.id for seq in seqs)

    for entry in data:
        required_refs = set(entry["required_refs"])
        additional_refs = set(entry.get("additional_refs", []))

        missing_refs = required_refs - seq_ids
        if missing_refs:
            print(f"Entry {entry['id']} is missing required references: {missing_refs}")
            failure = True

        missing_additional_refs = additional_refs - seq_ids
        if missing_additional_refs:
            print(
                f"Entry {entry['id']} is missing additional references: {missing_additional_refs}"
            )
            failure = True

    if failure:
        print("FASTA validation failed due to missing reference sequences.")
        sys.exit(1)

    print(
        "FASTA validation passed. All required and additional references are present."
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Validate HCID JSON and FASTA files.")
    parser.add_argument(
        "--schema", required=True, help="Path to the HCID JSON schema file."
    )
    parser.add_argument(
        "--json", required=True, help="Path to the HCID JSON file to validate."
    )
    parser.add_argument(
        "--fasta",
        required=True,
        help="Path to the gzipped FASTA file containing reference sequences.",
    )
    args = parser.parse_args()

    validate_hcid_json(args.schema, args.json)
    fasta_validate(args.json, args.fasta)
