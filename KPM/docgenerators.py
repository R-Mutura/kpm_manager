#path to kicad-cli is => /mnt/c/Program\ Files/KiCad/9.0/bin/kicad-cli.exe --version

import os
import sys
import platform
import subprocess

class DocGeneratorKiCLI:
    def __init__(self, KICAD_CLI: str = None, project_name=None, project_path: str = None):
        self.projectName = project_name
        self.projectPath = project_path
        self.kicad_cli2 = KICAD_CLI
        
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
            error_msg = f"KiCad CLI failed: {result.stderr}"
            print("❌ Error:", error_msg)
            raise RuntimeError(error_msg)
        else:
            print(f"✅ PDF generated successfully at: {output_pdf}")
    
    def generate_pcb_pdf_front(self, pcb_path: str, output_pdf: str):
        """
        Exports PCB to PDF.

        pcb_path: WSL- or Windows-style path to .kicad_sch
        output_pdf: path to write the PDF (relative or absolute)
        """
        # If we're in WSL and calling the Windows exe, convert paths
        if self.current_os() == "wsl" and self.kicad_cli.lower().endswith(".exe"):
            # pcb_path = self.wsl_to_windows_path(pcb_path)
            # output_pdf = self.wsl_to_windows_path(os.path.abspath(output_pdf))
            pcb_path = pcb_path
            output_pdf = output_pdf

        print("Calling KiCad CLI:", self.kicad_cli)
        print("Schematic:", pcb_path)
        print("Output PDF:", output_pdf)

        result = subprocess.run([
            self.kicad_cli,
            "pcb", "export", "pdf",
            "-l", "F.SilkS,Edge.Cuts,F.Fab,F.CrtYd",
            "-o", output_pdf,
            pcb_path
        ], capture_output=True, text=True)

        if result.returncode != 0:
            error_msg = f"KiCad CLI failed: {result.stderr}"
            print("❌ Error:", error_msg)
            raise RuntimeError(error_msg)
        else:
            print(f"✅ PDF generated successfully at: {output_pdf}")
                    
    def generate_pcb_pdf_bottom(self, pcb_path: str, output_pdf: str):
        """
        Exports PCB to PDF.

        pcb_path: WSL- or Windows-style path to .kicad_sch
        output_pdf: path to write the PDF (relative or absolute)
        """
        # If we're in WSL and calling the Windows exe, convert paths
        if self.current_os() == "wsl" and self.kicad_cli.lower().endswith(".exe"):
            # pcb_path = self.wsl_to_windows_path(pcb_path)
            # output_pdf = self.wsl_to_windows_path(os.path.abspath(output_pdf))
            pcb_path = pcb_path
            output_pdf = output_pdf

        print("Calling KiCad CLI:", self.kicad_cli)
        print("Schematic:", pcb_path)
        print("Output PDF:", output_pdf)

        result = subprocess.run([
            self.kicad_cli,
            "pcb", "export", "pdf",
            "-m",
            "-l", "B.SilkS,Edge.Cuts,B.Fab,B.CrtYd",
            "-o", output_pdf,
            pcb_path
        ], capture_output=True, text=True)

        if result.returncode != 0:
            error_msg = f"KiCad CLI failed: {result.stderr}"
            print("❌ Error:", error_msg)
            raise RuntimeError(error_msg)
        else:
            print(f"✅ PDF generated successfully at: {output_pdf}")
            
    def generate_step(self, pcb_path: str, output_step: str):
        """
        Exports a KiCad PCB to a STEP 3D model file.

        Parameters:
            pcb_path (str): Path to the .kicad_pcb file.
            output_step (str): Path to the output .step file.
        """
        print("Calling KiCad CLI:", self.kicad_cli)
        print("PCB Input:", pcb_path)
        print("STEP Output:", output_step)

        result = subprocess.run([
            self.kicad_cli,
            "pcb", "export", "step",
            "--output", output_step,
            "--subst-models",      # Substitute missing 3D models with placeholders
            "--include-tracks",    # Include tracks in the model
            "--include-zones",     # Include zones in the model
            "--no-dnp",            # Exclude Do Not Populate components
            pcb_path
        ], capture_output=True, text=True)

        if result.returncode != 0:
            print("❌ Error exporting STEP file:")
            print(result.stderr)
            raise RuntimeError(f"KiCad STEP export failed: {result.stderr}")
        else:
            print(f"✅ STEP file generated at: {output_step}")
    
    
    def generate_vrml(self, pcb_path: str, output_vrml: str):
        """
        Exports a KiCad PCB to a VRML 3D model file.

        Parameters:
            pcb_path (str): Path to the .kicad_pcb file.
            output_vrml (str): Path to the output .wrl file.
        """
        print("Calling KiCad CLI:", self.kicad_cli)
        print("PCB Input:", pcb_path)
        print("VRML Output:", output_vrml)

        result = subprocess.run([
            self.kicad_cli,
            "pcb", "export", "vrml",
            "-f",
            "--output", output_vrml,
            pcb_path
        ], capture_output=True, text=True)
        

        if result.returncode != 0:
            print("❌ Error exporting VRML file:")
            print(result.stderr)
            raise RuntimeError(f"KiCad VRML export failed: {result.stderr}")
        else:
            print(f"✅ VRML file generated at: {output_vrml}")

    def generate_pcb_render(self, pcb_path: str, orientation: str, output_img: str):
        """
        Generates a top render (SVG) of the PCB using KiCad CLI.
        
        Args:
            pcb_path (str): Path to the .kicad_pcb file.
            output_img (str): Path to the output .svg file (or .png if post-converted).
            kicad_cli_path (str): Path to the kicad-cli executable (default: assumes in PATH).
        """
        cmd = [
            self.kicad_cli,
            "pcb", "render",
            "--output", output_img,
            "--width", "1920",
            "--height", "1080",
            "--quality", "high",
            "--preset", "default",
        ]
        # Determine CLI args based on orientation
        orientation = orientation.lower()
        if orientation == "top":
            cmd += ["--side", "top"]
        elif orientation == "bottom":
            cmd += ["--side", "bottom"]
        elif orientation == "isotop":
            cmd += ["--rotate", "315,340,315"]
        elif orientation == "isobottom":
            cmd += ["--rotate", "150,340,45"]
        else:
            raise ValueError(f"❌ Unknown orientation: {orientation}")
                    
        
        
        cmd.append(pcb_path)
        result = subprocess.run(cmd, capture_output=True, text=True)

        # result = subprocess.run([
        #     self.kicad_cli,
        #     "pcb", "render",
        #     "--output", output_img,
        #     "--side", "top",
        #     "--width", "1920",
        #     "--height", "1080",
        #     # "--background", "#FFFFFF",  # White background
        #     "--quality", "high",
        #     "--preset", "default",
        #     pcb_path
        # ], capture_output=True, text=True)

        if result.returncode != 0:
            raise RuntimeError(f"❌ KiCad CLI render failed:\n{result.stderr}")
        else:
            print(f"✅ Top PCB render (SVG) saved at: {output_img}")        
 #*************************************************************************************##
 
if __name__ == "__main__":
    # You could replace these with values from a QFileDialog in your GUI
    #wsl_sch = "/mnt/c/Users/user/Documents/kicad6/fish_alert/fish_alert/src/fish_alert.kicad_sch"
    mwsl_sch = r"C:\Users\ujuzi\Documents\python\kitest\ONE\SRC\ONE\ONE.kicad_pcb"
    #win_sch = r"C:\Users\user\Documents\kicad6\fish_alert\fish_alert\src\fish_alert.kicad_sch"

    # Pick the right one based on the environment
    #sch = wsl_sch if DocGeneratorKiCLI.is_wsl() else win_sch
    out = "./fish_alert.pdf"

    gen = DocGeneratorKiCLI()
    gen.test_cli()
    gen.generate_pcb_render(mwsl_sch, "isobottom", "fish_alert.png")
    #gen.generate_sch_pdf(sch, out)
