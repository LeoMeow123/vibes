"""CLI for SLEAP to ROI YAML conversion."""

import argparse
from pathlib import Path

from vibing.sleap_convert.slp_to_yaml import (
    TEMPLATES,
    convert_batch,
    slp_to_roi_yaml,
)


def main():
    parser = argparse.ArgumentParser(
        description="Convert SLEAP predictions to ROI YAML format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert a single SLP file
  vibing-slp-to-yaml predictions.slp -o output.yml

  # Batch convert all SLP files in a directory
  vibing-slp-to-yaml /path/to/slps --batch -o /path/to/yamls

  # Use a specific template
  vibing-slp-to-yaml predictions.slp -o output.yml --template tmaze_horizontal

  # List available templates
  vibing-slp-to-yaml --list-templates
        """,
    )

    parser.add_argument(
        "input",
        type=Path,
        nargs="?",
        help="Path to SLP file or directory (with --batch)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output YAML file or directory (with --batch)",
    )
    parser.add_argument(
        "--batch",
        action="store_true",
        help="Process all SLP files in directory",
    )
    parser.add_argument(
        "--template",
        type=str,
        default="tmaze_horizontal",
        choices=list(TEMPLATES.keys()),
        help="ROI template to use (default: tmaze_horizontal)",
    )
    parser.add_argument(
        "--pattern",
        type=str,
        action="append",
        dest="patterns",
        help="Glob pattern for SLP files (can be repeated, default: *.slp)",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing YAML files",
    )
    parser.add_argument(
        "--frame",
        type=int,
        default=0,
        help="Frame index to extract (default: 0)",
    )
    parser.add_argument(
        "--instance",
        type=int,
        default=0,
        help="Instance index within frame (default: 0)",
    )
    parser.add_argument(
        "--list-templates",
        action="store_true",
        help="List available templates and exit",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Suppress verbose output",
    )

    args = parser.parse_args()

    # List templates
    if args.list_templates:
        print("Available ROI templates:")
        for name, template in TEMPLATES.items():
            print(f"  {name}: {template.description}")
            print(f"    Polygons: {[p.name for p in template.polygons]}")
            print(f"    Required keypoints: {len(template.required_keypoints)}")
            print()
        return

    # Validate input
    if args.input is None:
        parser.error("input is required (unless using --list-templates)")

    verbose = not args.quiet

    if args.batch:
        if not args.input.is_dir():
            parser.error(f"Not a directory: {args.input}")

        output_dir = args.output or args.input / "yml"
        patterns = args.patterns or ["*.slp"]

        if verbose:
            print(f"Converting SLP files in: {args.input}")
            print(f"Output directory: {output_dir}")
            print(f"Template: {args.template}")
            print()

        results = convert_batch(
            args.input,
            output_dir,
            template=args.template,
            patterns=patterns,
            overwrite=args.overwrite,
        )

        # Print results
        n_ok = n_skip = n_error = 0
        for name, result in results.items():
            status = result["status"]
            if status == "ok":
                n_ok += 1
                if verbose:
                    print(f"OK      {name} -> {result['roi_count']} ROIs")
            elif status == "skip":
                n_skip += 1
                if verbose:
                    print(f"SKIP    {name} ({result['message']})")
            else:
                n_error += 1
                if verbose:
                    print(f"ERROR   {name} ({result['message']})")

        if verbose:
            print()
            print(f"Summary: {n_ok} converted, {n_skip} skipped, {n_error} errors")

    else:
        if not args.input.exists():
            parser.error(f"File not found: {args.input}")

        output_path = args.output or args.input.with_suffix(".yml")

        if verbose:
            print(f"Converting: {args.input}")
            print(f"Template: {args.template}")

        try:
            info = slp_to_roi_yaml(
                args.input,
                output_path,
                template=args.template,
                frame=args.frame,
                instance=args.instance,
            )

            if verbose:
                print(f"Output: {output_path}")
                print(f"Keypoints: {info['keypoint_count']}")
                print(f"ROIs: {info['roi_count']}")
                print(f"Image size: {info['image_size']}")

        except Exception as e:
            print(f"Error: {e}")
            exit(1)


if __name__ == "__main__":
    main()
