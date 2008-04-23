import download
import console
import os

filedir = "testcases/"
filenames = os.listdir(filedir)

outfile = os.path.join(os.getcwd(), "OOo_2.3.1_Win32Intel_install_en-US.exe")
filesize = 112341981
checksums = {"sha1": "2c2849d173b1a5e6f8a3dc986383ee897bf4364d"}

for filename in filenames:
    if filename != ".svn":
        print "Running:", filename
        try:
            os.remove(outfile)
        except: pass
        
        progress = console.ProgressBar(55)
        results = download.download_metalink(filedir + filename, os.getcwd(), handler=progress.download_update)
        progress.download_end()

    ##    if outfile not in results:
    ##        print "FAIL: Download failed"
        if not os.access(outfile, os.F_OK):
            print "FAIL: File does not exist"
        elif os.stat(outfile).st_size != filesize:
            print "FAIL: Wrong file size"
        elif not download.verify_checksum(outfile, checksums):
            print "FAIL: Bad file checksum"
        else:
            print "PASS"
            
        print "---------------------------"
