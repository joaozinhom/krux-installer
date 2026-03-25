# hooks/linux/flatpak/post_build.py
import pathlib

providers_init = pathlib.Path(
    "build/krux-installer/linux/flatpak/io.selfcustody.krux-installer"
    "/app/briefcase/app_packages/kivy/input/providers/__init__.py"
)

content = providers_init.read_text()
patched = content.replace(
    "import kivy.input.providers.mtdev",
    "# import kivy.input.providers.mtdev  # patched: libmtdev not available",
)
providers_init.write_text(patched)
print("Patched kivy mtdev provider")