/*
	This file is part of the metalink program
	Copyright (C) 2007  A. Bram Neijt <bneijt@gmail.com>

	This program is free software; you can redistribute it and/or
	modify it under the terms of the GNU General Public License
	as published by the Free Software Foundation; either version 2
	of the License, or (at your option) any later version.

	This program is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.

	You should have received a copy of the GNU General Public License
	along with this program; if not, write to the Free Software
	Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

*/

#include "Options.ih"

#define _addOpt(SHORT, LONG, DESC)	Glib::OptionEntry SHORT ## _e; SHORT ## _e.set_long_name(#LONG); SHORT ## _e.set_short_name('SHORT'); SHORT ## _e.set_description(#DESC); add_entry(SHORT ## _e, m_arg_foo)


Options::Options()
	:
	Glib::OptionGroup("example_group", "description of example group", "help description of example group"),
  m_arg_foo(0),
  m_arg_boolean(false)
{
  Glib::OptionEntry entry1;
  entry1.set_long_name("foo");
  entry1.set_short_name('f');
  entry1.set_description("The Foo");
  add_entry(entry1, m_arg_foo);
      
  Glib::OptionEntry entry2;
  entry2.set_long_name("file");
  entry2.set_short_name('F');
  entry2.set_description("The Filename");
  add_entry_filename(entry2, m_arg_filename);
 
  Glib::OptionEntry entry3;
  entry3.set_long_name("goo");
  entry3.set_short_name('g');
  entry3.set_description("The Goo");
  m_arg_goo = "default-goo-value"; //We can choose a default to be used if the user doesn't specify this option.
  add_entry(entry3, m_arg_goo);
  
  Glib::OptionEntry entry4;
  entry4.set_long_name("activate_something");
  entry4.set_description("Activate something");
  add_entry(entry4, m_arg_boolean);
  
  Glib::OptionEntry entry5;
  entry5.set_long_name("list");
  entry5.set_short_name('l');
  entry5.set_description("The List");
  add_entry(entry5, m_arg_list);
  
  _addOpt(list, The List);
}

/*
metalink - Metalink XML generator
Version 0.3.3, Copyright (C) 2005 A. Bram Neijt <bneijt@gmail.com>
metalink comes with ABSOLUTELY NO WARRANTY and is licensed under GPLv2
Usage:
  metalink [options] (input files or --md5) < (mirror list) > (metalinkfile)

General options:
  -h [ --help ]         Produce a help message
  --version             Print out the name and version
  --md5 arg             Generate metalink from md5sum file(s)
  --addpath arg         Append a path to the mirrors ('/' is not checked)
  --headerfile arg      Include file after the root element declaration.
  --nomirrors           Don't read mirrors from stdin
  --hashlist            List hashes only (implies nomirrors)
  --desc arg            Add metalink description

Digest options:
  -d [ --digest ] arg   Include given digest
  --mindigests          Include: md5 sha1
  --somedigests         Include: md5 sha1 ed2k
  --alldigests          Include all possible digests

Supported algorithms are (-d options):
  md4 md5 sha1 sha256 sha384 sha512 rmd160 tiger crc32 ed2k gnunet sha1pieces

Mirror lists are single line definitions according to:
 [location [preference] [type] % ] <mirror base url>

Examples:
http://example.com/ as a mirror:
 echo http://example.com | metalink -d md5 -d sha1 *

http://example.com/ as a mirror with preference and location:
 echo us 10 % http://example.com | metalink -d md5 -d sha1 *

http://example.com/ as a mirror with preference only:
 echo 0 10 % http://example.com | metalink -d md5 *

Only P2P links:
 metalink --nomirrors -d sha1 -d ed2k -d gnunet *


*/
