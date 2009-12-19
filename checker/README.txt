Metalink Checker



Metalink Checker is a command line application that checks or downloads(executes) metalink files. It downloads the files, checks their SHA1 or MD5 verification and verifies that the files are working.

It also checks general validity of the metalink (valid XML).


# Instructions:
#   1. You need to have Python installed.
#   2. To check PGP signatures you need to install gpg (http://www.gnupg.org) or gpg4win (http://www.gpg4win.org/)
#   3. Run on the command line using: python console.py
#
#   Usage: console.py [-c|-d] [options] arg1 arg2 ...
#
#   Options:
#     -h, --help            show this help message and exit
#     -d, --download        Actually download the file(s) in the metalink
#     -c, --check           Check the metalink file URLs
#     -f FILE, --file=FILE  Metalink file to check
#     -t TIMEOUT, --timeout=TIMEOUT
#                           Set timeout in seconds to wait for response
#                           (default=10)
#     -o OS, --os=OS        Operating System preference
#     -l LANG, --lang=LANG  Language preference (ISO-639/3166)
#     --country=LOC         Two letter country preference (ISO 3166-1 alpha-2)
#     -k DIR, --pgp-keys=DIR
#                           Directory with the PGP keys that you trust (default:
#                           working directory)
#     -p FILE, --pgp-store=FILE
#                           File with the PGP keys that you trust (default:
#                           ~/.gnupg/pubring.gpg)
#     -g GPG, --gpg-binary=GPG
#                           (optional) Location of gpg binary path if not in the
#                           default search path
# Library Instructions:
#   - Use as expected.
#
# import metalink
#
# files = metalink.get("file.metalink", os.getcwd())
# results = metalink.check_metalink("file.metalink")
