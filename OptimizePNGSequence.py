# Makes PNG Sequence G+A (from RGBA) to save space

#!/usr/bin/env python3

import re
import sys
from pathlib import Path
from PIL import Image


def main():
    if len(sys.argv) != 2:
        print('Usage: python3 <this script> "<path to first image>"')
        sys.exit(1)

    first = Path(sys.argv[1]).expanduser().resolve()

    if not first.is_file():
        sys.exit(f"Error: File not found: {first}")

    # Identify the first frame number in the filename
    match = re.fullmatch(r"(.*?)(\d+)(\.[^.]+)", first.name)

    if not match:
        sys.exit(
            "Error: The filename must end with a frame number! before its extension, (e.g. frame-001.png)"
        )

    prefix, number, extension = match.groups()
    start_number = int(number)
    padding = len(number)

    # find all files with the same prefix and extension
    pattern = re.compile(
        rf"{re.escape(prefix)}(\d{{{padding}}}){re.escape(extension)}"
    )

    frames = {}

    for path in first.parent.iterdir():
        found = pattern.fullmatch(path.name)
        if found and path.is_file():
            frames[int(found.group(1))] = path

    if start_number not in frames:
        sys.exit("Error: The specified starting frame was not found.")

    # Use the selected frame as the beginning of the sequence
    frame_numbers = sorted(n for n in frames if n >= start_number)

    if not frame_numbers:
        sys.exit("Error: No frames found.")

    expected = list(range(frame_numbers[0], frame_numbers[-1] + 1))
    missing = sorted(set(expected) - set(frame_numbers))

    if missing:
        sys.exit(f"Error: Missing frame numbers: {missing}")

    output_dir = first.parent / "gray-alpha"
    output_dir.mkdir(exist_ok=True)

    print(f"Input:  {first.parent}")
    print(f"Frames: {len(frame_numbers)}")
    print(f"Range:  {frame_numbers[0]}–{frame_numbers[-1]}")
    print(f"Output: {output_dir}")

    for i, frame_number in enumerate(frame_numbers, 1):
        path = frames[frame_number]
        output_path = output_dir / path.name

        with Image.open(path) as image:
            rgba = image.convert("RGBA")
            alpha = rgba.getchannel("A")

            # grayscale (white) + og alpha.
            gray = Image.new("L", rgba.size, 255)
            gray_alpha = Image.merge("LA", (gray, alpha))

            gray_alpha.save(output_path, format="PNG")

        print(f"\rConverted {i}/{len(frame_numbers)}", end="", flush=True)

    print("\n...done!")


if __name__ == "__main__":
    main()
