<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="sv" lang="sv">

<head>
	<title>Custom Mini Downloader</title>
</head>

<body>
    <h1>Custom Mini Downloader</h1>
    <form action="get_downloader.php" method="POST">
        <table style="border-style: none;">
            <tr> <td style="width: 18ex;">URL:</td> <td><input type="text" name="url" size="75" value="http://hampus.vox.nu/mini_downloader/OOo_2.4.1_Win32Intel_install_wJRE_en-US.exe.metalink" /></td> </tr>
            <tr> <td>Target filename:</td> <td><input type="text" name="filename" size="75" value="OOo_2.4.1_Win32Intel_install_wJRE_en-US.exe.metalink" /></td> </tr>
            <tr> <td>Window title:</td> <td><input type="text" name="title" size="75" value="OpenOffice.org 2.4.1" /></td> </tr>
            <tr> <td>Welcome message:</td> <td><input type="text" name="welcome" size="75" value="Ready to download OpenOffice.org installer!" /></td> </tr>
            <tr> <td>Launch file:</td> <td><input type="text" name="launchfile" size="75" value="OOo_2.4.1_Win32Intel_install_wJRE_en-US.exe" /></td> </tr>
            <tr> <td>Launch label:</td> <td><input type="text" name="launchbtn" size="75" value="Launch installer" /></td> </tr>
            <tr> <td>Launch?:</td> <td><select name="launch"><option value ="YES">Yes</option><option value ="NO">No</option></select></td> </tr>
            <tr> <td></td> <td style="text-align: right;"><input type="submit" value="Download" /></td> </tr>
        </table>
    </form>
    <p>Source code is available at the <a href="http://sourceforge.net/projects/metalinks/">sourceforge project</a>.</p>
    <div style="max-width: 80ex;">
        <h2>License:</h2>
        <p>Copyright (c) 2008 Hampus Wessman. All rights reserved.</p>
        <p>Redistribution and use in source and binary forms, with or without
        modification, are permitted provided that the following conditions are met:</p>
        <ol>
            <li>Redistributions of source code must retain the above copyright notice,
            this list of conditions and the following disclaimer.</li>
            <li>Redistributions in binary form must reproduce the above copyright notice,
            this list of conditions and the following disclaimer in the documentation
            and/or other materials provided with the distribution.</li>
        </ol>
        <p>THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
        AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
        IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
        DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE
        FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
        DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
        SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
        CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
        OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
        OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.</p>
    </div>
</body>

</html>