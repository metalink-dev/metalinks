Metalink Editor Readme
by Hampus Wessman

Thanks for downloading Metalink Editor!

Metalink Editor is open source and released under GNU GPL. If you have downloaded
the win32 installer everything should be straight forward. If you have the source
distribution you need to run the file "metalink_editor.py" with python. It might
be possible for you to just execute the file (make sure the file really is
"executable", if this would fail). Otherwise you need to run python with
"metalink_editor.py" as the argument.

The source distribution requires Python (works with 2.4 and 2.5, maybe with earlier
versions too) and wxPython. I have tested with wxPython 2.6 and that works.
The 2.4 version doesn't work at all and 2.5 have not been tested yet.

The interface should be quite easy to use. It works like most other editors.

I'll explain a few features in more detail though. One thing that is not very
obvious is how to edit an already entered URL. To do that simply double click it,
change the data and press "Change".

The scan button is another useful feature. If you have the file that is going to be
described in your new metalink available, just press "Scan.." and select it.
Metalink Editor will scan it for all possible data. It will fill in hashes, file
size and file names automatically for you! Notice that those fields will be locked
after scanning (or opening a file with similar data). To unlock the fields for
manual input you need to press "Clear". This clears all checksums and the file size.

You can choose a license from a combo box (or enter your own). If you choose one from
the list it will fill in an URL for you (some of them point to the latest version of
the license, others (eg. BSD) points to a template for that kind of licenses, on
OSI's website). For BSD, MIT and similar it's always recommended to enter an URL
pointing to a license for this specific file! CC and GNU licenses don't need any
special treatment.

More info will be added to the readme in the future.
Please send me an email if you have any questions!

/ Hampus Wessman (hw@vox.nu)
