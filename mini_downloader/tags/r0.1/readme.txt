Mini Downloader ReadMe
by Hampus Wessman <hw@vox.nu>

This is a small metalink downloader written in C++, using boost, libcurl and
expat. It can either be compiled so that it downloads a specific file and
then (optionally) launches it or be compiled into a "downloader template", which
can later be used to create a custom downloader by replacing text strings inside
the executable (they are marked in a special way, to make this easy).

src/web/ contains php files, which can be used to create custom downloaders from
a "downloader template" (mentioned above). The scripts should be easy to modify.

More documentation will be added later. See SConstruct to find out how it is
built (it's quite self-explanatory). "Downloader templates" are built by
defining CUSTOM_STRINGS. The compiled executables can be compressed using UPX,
but you can't add custom strings to a compressed downloader template. You can
compress it afterwards though.

See license.txt for license information.
