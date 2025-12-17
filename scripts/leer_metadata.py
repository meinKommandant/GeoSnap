#!/usr/bin/env python3
"""
Read EXIF metadata from photo files.

CLI tool to inspect EXIF data including GPS coordinates, orientation,
and compass direction from geotagged photos.

Usage:
    python scripts/leer_metadata.py --file "photo.jpg"
    python scripts/leer_metadata.py --dir "./photos" --file "photo.jpg"
"""

import argparse
import os
import sys
from pathlib import Path
from PIL import Image, ExifTags


def get_metadata(file_path: Path) -> None:
    """Extract and display EXIF metadata from an image file.

    Args:
        file_path: Path to the image file to analyze.
    """
    print(f"\n--- Processing file: {file_path} ---")

    try:
        img = Image.open(file_path)
        exif_data = img._getexif()

        if not exif_data:
            print("❌ Image opened, but has NO EXIF metadata.")
            return

        print("✅ Metadata found. Looking for orientation and GPS data...\n")

        found_gps = False

        for tag_id in exif_data:
            tag = ExifTags.TAGS.get(tag_id, tag_id)
            data = exif_data.get(tag_id)

            # 1. Image Orientation (Rotation)
            if tag == "Orientation":
                print(f"📷 Orientation (Rotation): {data} (1=Normal)")

            # 2. GPS Data
            if tag == "GPSInfo":
                found_gps = True
                print("\n🌍 --- GPS DATA ---")

                gps_tags = {}
                for key in data.keys():
                    decode_name = ExifTags.GPSTAGS.get(key, key)
                    gps_tags[decode_name] = data[key]

                # Compass Direction (Azimuth)
                img_direction = gps_tags.get("GPSImgDirection")
                img_ref = gps_tags.get("GPSImgDirectionRef")

                if img_direction:
                    print(f"🧭 Camera Direction (Azimuth): {img_direction} degrees")
                    print(f"   Reference: {img_ref} (M=Magnetic, T=True/Geographic)")
                else:
                    print("⚠️ GPS coordinates exist, but no direction (compass) was recorded.")

                # Coordinates (Latitude/Longitude)
                lat = gps_tags.get("GPSLatitude")
                lon = gps_tags.get("GPSLongitude")
                print(f"📍 Latitude (raw): {lat}")
                print(f"📍 Longitude (raw): {lon}")

        if not found_gps:
            print("\n❌ No GPS data found in this image.")

    except FileNotFoundError:
        print("\n❌ ERROR: File not found.")
        print("👉 Verify the filename is correct and the file exists in the specified directory.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


def main() -> None:
    """Main entry point for the CLI tool."""
    parser = argparse.ArgumentParser(
        description="Read EXIF metadata from photo files including GPS and orientation data.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/leer_metadata.py --file "photo.jpg"
  python scripts/leer_metadata.py --dir "./photos" --file "photo.jpg"
  python scripts/leer_metadata.py --file "DSC_0001.JPG" --dir "C:\\Photos\\Trip"
        """,
    )

    parser.add_argument(
        "--dir",
        type=str,
        default="./input",
        help="Input directory containing the photo (default: ./input)",
    )
    parser.add_argument(
        "--file",
        type=str,
        required=True,
        help="Filename of the photo to analyze (required)",
    )

    args = parser.parse_args()

    # Resolve the full path
    input_dir = Path(args.dir)
    file_path = input_dir / args.file

    print(f"📂 Search directory: {input_dir.resolve()}")
    print(f"📄 Target file: {args.file}")

    if not input_dir.exists():
        print(f"\n❌ ERROR: Directory does not exist: {input_dir}")
        sys.exit(1)

    if not file_path.exists():
        print(f"\n❌ ERROR: File not found: {file_path}")
        print("👉 Check the filename and ensure it exists in the specified directory.")
        sys.exit(1)

    get_metadata(file_path)


if __name__ == "__main__":
    main()
