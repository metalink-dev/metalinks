# setup.py
from distutils.core import setup
import py2exe

manifest = """
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1"
manifestVersion="1.0">
<assemblyIdentity
    version="0.0.0.1"
    processorArchitecture="x86"
    name="Controls"
    type="win32"
/>
<description>Metalink editor</description>
<dependency>
    <dependentAssembly>
        <assemblyIdentity
            type="win32"
            name="Microsoft.Windows.Common-Controls"
            version="6.0.0.0"
            processorArchitecture="X86"
            publicKeyToken="6595b64144ccf1df"
            language="*"
        />
    </dependentAssembly>
</dependency>
</assembly>
"""

setup(
##    windows = [
##        #{
##        #    "script": "metalink_editor.py",
##        #    "icon_resources": [(1, "metalink.ico")],
##        #    "other_resources": [(24,1,manifest)]
##        #},
##    ],
    console = ["meditor.py"],
    data_files=[('', ["metalink_small.png", "metalink_small.ico", "metalink.png", "license.txt", "changelog.txt", "readme.txt"])],
)
