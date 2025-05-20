#path to kicad-cli is => /mnt/c/Program\ Files/KiCad/9.0/bin/kicad-cli.exe --version

import os
import sys
import platform
import subprocess

class DocGeneratorKiCLI:
    def __init__(self, project_name=None, project_path=None):
        self.projectName = project_name
        self.projectPath = project_path

        # Decide which kicad-cli to call based on our OS
        os_type = DocGeneratorKiCLI.current_os()
        if os_type == "windows":
            self.kicad_cli = r"C:\Program Files\KiCad\9.0\bin\kicad-cli.exe"
        elif os_type == "wsl":
            # if you want to call the Windows exe from WSL
            self.kicad_cli = "/mnt/c/Program Files/KiCad/9.0/bin/kicad-cli.exe"
        else:
            # assume it's on your $PATH (Linux/macOS install)
            self.kicad_cli = "kicad-cli"

    # ─── Platform Detection ─────────────────────────────────────────
    @staticmethod
    def is_windows() -> bool:
        return os.name == 'nt' or platform.system() == 'Windows'

    @staticmethod
    def is_mac() -> bool:
        return platform.system() == 'Darwin'

    @staticmethod
    def is_wsl() -> bool:
        if platform.system() != 'Linux':
            return False
        return 'microsoft' in platform.uname().release.lower()

    @staticmethod
    def is_linux() -> bool:
        return platform.system() == 'Linux' and not DocGeneratorKiCLI.is_wsl()

    @staticmethod
    def current_os() -> str:
        if DocGeneratorKiCLI.is_wsl():
            return 'wsl'
        if DocGeneratorKiCLI.is_windows():
            return 'windows'
        if DocGeneratorKiCLI.is_mac():
            return 'mac'
        if DocGeneratorKiCLI.is_linux():
            return 'linux'
        return 'unknown'

    # ─── Path Conversion ────────────────────────────────────────────
    @staticmethod
    def wsl_to_windows_path(wsl_path: str) -> str:
        if wsl_path.startswith("/mnt/"):
            parts = wsl_path.split("/")
            drive = parts[2].upper() + ":"
            return os.path.join(drive, *parts[3:])
        return wsl_path

    # ─── Tests ─────────────────────────────────────────────────────
    def test_cli(self):
        """Prints kicad-cli version to confirm we can call it."""
        print(f"Detected OS: {self.current_os()} → using `{self.kicad_cli}`")
        try:
            result = subprocess.run(
                [self.kicad_cli, "--version"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            print("KiCad CLI Version:", result.stdout.strip())
        except subprocess.CalledProcessError as e:
            print("Error running KiCad CLI:", e.stderr)

    # ─── Example: Generate Schematic PDF ────────────────────────────
    def generate_sch_pdf(self, schematic_path: str, output_pdf: str):
        """
        Exports schematic to PDF.

        schematic_path: WSL- or Windows-style path to .kicad_sch
        output_pdf: path to write the PDF (relative or absolute)
        """
        # If we're in WSL and calling the Windows exe, convert paths
        if self.current_os() == "wsl" and self.kicad_cli.lower().endswith(".exe"):
            # schematic_path = self.wsl_to_windows_path(schematic_path)
            # output_pdf = self.wsl_to_windows_path(os.path.abspath(output_pdf))
            schematic_path = schematic_path
            output_pdf = output_pdf

        print("Calling KiCad CLI:", self.kicad_cli)
        print("Schematic:", schematic_path)
        print("Output PDF:", output_pdf)

        result = subprocess.run([
            self.kicad_cli,
            "sch", "export", "pdf",
            "-o", output_pdf,
            schematic_path
        ], capture_output=True, text=True)

        if result.returncode != 0:
            print("❌ Error generating schematic PDF:")
            print(result.stderr)
        else:
            print(f"✅ PDF generated successfully at: {output_pdf}")

# ─── Example Usage ────────────────────────────────────────────────
if __name__ == "__main__":
    # You could replace these with values from a QFileDialog in your GUI
    wsl_sch = "/mnt/c/Users/user/Documents/kicad6/fish_alert/fish_alert/src/fish_alert.kicad_sch"
    win_sch = r"C:\Users\user\Documents\kicad6\fish_alert\fish_alert\src\fish_alert.kicad_sch"

    # Pick the right one based on the environment
    sch = wsl_sch if DocGeneratorKiCLI.is_wsl() else win_sch
    out = "./fish_alert.pdf"

    gen = DocGeneratorKiCLI()
    gen.test_cli()
    #gen.generate_sch_pdf(sch, out)
