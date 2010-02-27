Metalink Editor's Readme
Hampus Wessman (hw@vox.nu)

ABOUT
-----

Metalink  Editor is  open source  and released  under GNU  GPL. It
allows  you  to create  and  edit  metalinks (see  metalinker.org)
with  its  easy-to-use GUI.  For  the  moment it  doesn't  support
every  kind of  metalink  (especially  not multi-file  metalinks),
but more  features will be added  in the future. It  allows you to
enter data  manually, but  can also scan  files on  your harddrive
to automatically enter file name,  file size and hashes (including
chunk checksums).

INSTALLATION
------------

The win32 installer works like  most other installers and installs
a shortcut in  the start-menu, as usual.  The source distribution,
on the  other hand, requires  some explanation. To begin  with you
need  to have  Python installed  (works  with 2.4  and 2.5,  maybe
with earlier versions too) and wxPython  2.6 or later (I know that
2.4 doesn't work).

  To run  the editor,  using the source  code, you  should execute
the file "metalink_editor.py" with python.  There are at least two
ways to do this.  The first one is to simply  execute the file. If
that doesn't work,  make sure that the file is  executable (ie has
the right file  permissions set). The second one is  to run python
instead and  specify the  file name  of the  python script  as the
first argument  (eg "python metalink_editor.py" in  same directory
as the  file). The  source code  should work  on any  system where
Python and wxPython runs (including Windows).

USAGE
-----

The user  interface should be quite  easy to use. It  works pretty
much like other  editors. There are a few features  that could use
some explanation though.

  One thing  that is not  very obvious is  how to edit  an already
entered URL.  To do that simply  double click it, change  the data
and press "Change".

  The scan  button might  need some explanation.  If you  have the
file that is going to be described in your new metalink available,
you can press  "Scan file..." and select it.  Metalink Editor will
then scan the file for all  possible data. It will fill in hashes,
file size and  file name automatically for you!  Notice that those
fields  will be  locked after  scanning  (or opening  a file  with
similar data). To  unlock the fields for manual input  you need to
press "Clear". This clears all checksums and the file size.

  When you scan a file the  editor will not only generate ordinary
hashes for the  whole file, but also so  called "chunk checksums".
These are hashes  (or checksums) of pieces of the  file. The whole
file is  divided into chunks of  equal size and for  each of these
chunks a  special checksum  is calculated. This  can then  be used
by download  clients to validate  a file while downloading  it and
if a chunk doesn't download  this single chunk can be redownloaded
(possibly from another  server) without the whole  file needing to
be redownloaded! You can change how the editor generates chunksums
under Options => Settings...

  You can choose  a license from a combo box (or  enter your own).
If you  choose one from the  list it will  fill in an URL  for you
(some of them  point to the latest version of  the license, others
(eg. BSD) points to a template for that kind of licenses, on OSI's
website).  For BSD,  MIT and  similar it  is recommended  to enter
an URL  pointing to a license  for this specific file.  CC and GNU
licenses don't need any special  treatment, but the URLs might not
point to the latest version...

Please send me an email if you have any questions!