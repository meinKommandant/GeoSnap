"""
Build script for GeoSnap executable.
Verifies dependencies, cleans previous builds, and creates portable .exe
"""
import subprocess
import sys
import shutil
from pathlib import Path


def check_dependencies() -> bool:
    """Verify all required packages are installed."""
    required = {
        'PIL': 'Pillow',
        'pillow_heif': 'pillow-heif',
        'ttkbootstrap': 'ttkbootstrap',
        'simplekml': 'simplekml',
        'openpyxl': 'openpyxl',
        'docx': 'python-docx',
    }
    optional = {
        'tkinterdnd2': 'tkinterdnd2',
        'geomag': 'geomag',
    }
    
    missing = []
    for pkg, name in required.items():
        try:
            __import__(pkg)
            print(f"  [OK] {name}")
        except ImportError:
            print(f"  [X]  {name} (REQUIRED)")
            missing.append(name)
    
    for pkg, name in optional.items():
        try:
            __import__(pkg)
            print(f"  [OK] {name} (optional)")
        except ImportError:
            print(f"  [!]  {name} (optional - not installed)")
    
    if missing:
        print(f"\n[ERROR] Missing required packages: {missing}")
        print("   Install with: pip install " + " ".join(missing))
        return False
    
    print("\n[OK] All required dependencies found")
    return True


def clean_build() -> None:
    """Remove previous build artifacts."""
    print("\n[CLEAN] Cleaning previous builds...")
    for folder in ['build', 'dist']:
        path = Path(folder)
        if path.exists():
            shutil.rmtree(path)
            print(f"   Removed {folder}/")


def build_exe() -> bool:
    """Run PyInstaller with the spec file."""
    print("\n[BUILD] Building executable...")
    print("   This may take a few minutes...\n")
    
    result = subprocess.run(
        [sys.executable, '-m', 'PyInstaller', 'GeoSnap.spec', '--noconfirm'],
        cwd=Path(__file__).parent
    )
    return result.returncode == 0


def verify_build() -> bool:
    """Check the exe was created successfully."""
    exe_path = Path('dist/GeoSnap.exe')
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"\n[SUCCESS] Build successful!")
        print(f"   Output: {exe_path.absolute()}")
        print(f"   Size: {size_mb:.1f} MB")
        return True
    
    print("\n[ERROR] Build failed: GeoSnap.exe not found in dist/")
    return False


def main():
    print("=" * 60)
    print("GeoSnap Build Script")
    print("=" * 60)
    
    print("\n[CHECK] Checking dependencies...")
    if not check_dependencies():
        sys.exit(1)
    
    clean_build()
    
    if not build_exe():
        print("\n[ERROR] PyInstaller failed. Check the output above for errors.")
        sys.exit(1)
    
    if not verify_build():
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("[DONE] Build complete! You can find GeoSnap.exe in the dist/ folder")
    print("=" * 60)


if __name__ == '__main__':
    main()
