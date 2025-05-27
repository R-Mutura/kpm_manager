
import sys
import os
import platform
import subprocess
from utils import get_app_settings

class ProductionFilesGeneratorKICLI:
    def __init__(self, project_name=None, project_path=None):
        # self.kicad_cli = kicad_cli_path
        self.projectName = project_name
        self.projectPath = project_path
        kicad_bom_script_name = "bom_csv_grouped_by_value.py"

        kicad_executable = get_app_settings()

        self.kicad_cli = kicad_executable.value("kicad_cli_exec", "")
        self.kicad_bom_script = os.path.join(os.path.dirname(self.kicad_cli), "scripting", "plugins", kicad_bom_script_name)
        self.custom_bom_py = self.kicad_bom_script
        #print(f"production_file: {self.kicad_cli}")


         


        
        # Decide which kicad-cli to call based on our OS
        # os_type = ProductionFilesGeneratorKICLI.current_os()
        # if os_type == "windows":
        #     self.kicad_cli = r"C:\Program Files\KiCad\9.0\bin\kicad-cli.exe"
        #     bom_script_path = r"C:\Program Files\KiCad\9.0\bin\scripting\plugins\bom_csv_grouped_by_value.py"
        #     self.custom_bom_py = r"C:\Program Files\KiCad\9.0\bin\scripting\plugins/bom_csv_grouped_by_value.py"
        # elif os_type == "wsl":
        #     # if you want to call the Windows exe from WSL
        #     self.kicad_cli = "/mnt/c/Program Files/KiCad/9.0/bin/kicad-cli.exe"
        # else:
        #     # assume it's on your $PATH (Linux/macOS install)
        #     self.kicad_cli = "kicad-cli"
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
        return platform.system() == 'Linux' and not ProductionFilesGeneratorKICLI.is_wsl()

    @staticmethod
    def current_os() -> str:
        if ProductionFilesGeneratorKICLI.is_wsl():
            return 'wsl'
        if ProductionFilesGeneratorKICLI.is_windows():
            return 'windows'
        if ProductionFilesGeneratorKICLI.is_mac():
            return 'mac'
        if ProductionFilesGeneratorKICLI.is_linux():
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

    def generate_bom_legacy(self, sch_path: str, output_dir: str):
        # output_path = os.path.join(output_dir, "bom.csv")
        result = subprocess.run([
            self.kicad_cli, "sch", "export", "python-bom",
            "--output", output_dir,
            sch_path
        ], capture_output=True, text=True)
        if result.returncode != 0:
            error_msg = f"KiCad CLI failed: {result.stderr}"
            print("❌ Error:", error_msg)
            raise RuntimeError(error_msg)
        else:
            print(f"✅ PDF generated successfully at: {output_dir}")


    def generate_bom(self, sch_path: str, output_dir: str):
        # output_path = os.path.join(output_dir, "bom.csv")
        #path to custom plug in generator => C:\Program Files\KiCad\9.0\bin\scripting\plugins/bom_csv_grouped_by_value.py
        # Build command
        try:
            cmd = [
                "python3 ",
                self.custom_bom_py,
                sch_path,
                output_dir
            ]
            # Execute subprocess
            result = subprocess.run(cmd, capture_output=True, text=True)
            # Check for errors
            if result.returncode != 0:
                print(f"❌ BOM generation failed (code {result.returncode}):", file=sys.stderr)
                print(result.stderr, file=sys.stderr)
                return False

            print(f"✅ BOM generated successfully at: {output_dir}")
            return True

        except Exception as e:
            print(f"❌ Exception during BOM generation: {e}", file=sys.stderr)
            return False

        # Run the command
        result = subprocess.run([
            "python",  # or "python3" depending on your environment
            self.custom_bom_py,
            sch_path,
            output_dir
        ], capture_output=True, text=True)

        # Handle result
        if result.returncode != 0:
            print("❌ Error generating BOM:")
            print(result.stderr)
        else:
            print("✅ BOM generated successfully at:", output_dir)

    def generate_gerber(self, pcb_path, output_dir):
        # TODO: ! ADD A FEATURE THAT ONLY EXPORTS ACTIVE
        #! WORKS WELL ENOUGH AS IS FOR NOW
        result = subprocess.run([
            self.kicad_cli, "pcb", "export", "gerbers",
            "--output", output_dir,
            pcb_path
        ], capture_output=True, text=True)
        if result.returncode != 0:
            error_msg = f"KiCad CLI failed: {result.stderr}"
            print("❌ Error:", error_msg)
            raise RuntimeError(error_msg)
        else:
            print(f"✅ PDF generated successfully at: {output_dir}")

    def generate_placement(self, pcb_path, output_dir):
        result = subprocess.run([
            self.kicad_cli, "pcb", 
            "export", "pos",
            "--units", "mm",
            "--format", "csv",
            "--exclude-dnp",
            "--output", output_dir,
            pcb_path
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            error_msg = f"KiCad CLI failed: {result.stderr}"
            print("❌ Error:", error_msg)
            raise RuntimeError(error_msg)
        else:
            print(f"✅ PDF generated successfully at: {output_dir}")

    def generate_stackup(self, pcb_path, output_dir):
        output_path = os.path.join(output_dir, "stackup.html")
        result = subprocess.run([
            self.kicad_cli, "pcb", "export", "stackup",
            "--output", output_path,
            pcb_path
        ], capture_output=True, text=True)
        if result.returncode != 0:
            error_msg = f"KiCad CLI failed: {result.stderr}"
            print("❌ Error:", error_msg)
            raise RuntimeError(error_msg)
        else:
            print(f"✅ PDF generated successfully at: {output_dir}")

    def generate_drill(self, pcb_path, output_dir):
        result = subprocess.run([
            self.kicad_cli, "pcb", "export", "drill",
            "--output", output_dir,
            pcb_path
        ], capture_output=True, text=True)
        if result.returncode != 0:
            error_msg = f"KiCad CLI failed: {result.stderr}"
            print("❌ Error:", error_msg)
            raise RuntimeError(error_msg)
        else:
            print(f"✅ PDF generated successfully at: {output_dir}")

    def generate_dxf(self, pcb_path, output_dir):
        result = subprocess.run([
            self.kicad_cli, "pcb", "export", "dxf",
            "--output", output_dir,
            pcb_path
        ], capture_output=True, text=True)
        if result.returncode != 0:
            error_msg = f"KiCad CLI failed: {result.stderr}"
            print("❌ Error:", error_msg)
            raise RuntimeError(error_msg)
        else:
            print(f"✅ PDF generated successfully at: {output_dir}")

if __name__ == "__main__":
    import argparse

    gen = ProductionFilesGeneratorKICLI() 

    sch = r"C:\Users\user\Documents\KiCad\KPM_PROJECTS\ONE\SRC\ONE\ONE.xml"
    output = r"C:\Users\user\Documents\KiCad\KPM_PROJECTS\ONE\Project_Files\BOM\one.csv"
    success = gen.generate_bom(sch, output)
    sys.exit(0 if success else 1)