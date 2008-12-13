/*
	This file is part of the metalink program
	Copyright (C) 2008  A. Bram Neijt <bneijt@gmail.com>

  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program.  If not, see <http://www.gnu.org/licenses/>.

*/








#include "Options.ih"
#define _addOpt(VAR, SHORT, LONG, DESC)	Glib::OptionEntry SHORT ## _e; SHORT ## _e.set_long_name(#LONG); SHORT ## _e.set_short_name( #SHORT[0]); SHORT ## _e.set_description(DESC); add_entry(SHORT ## _e, opt.VAR)
#define _addLOpt(VAR, LONG, DESC)	Glib::OptionEntry LONG ## _e; LONG ## _e.set_long_name(#LONG); LONG ## _e.set_description(DESC); add_entry(LONG ## _e, opt.VAR)


Options::Options()
	:
	Glib::OptionGroup("main_group", "Main options", "General commandline options")
{

//Usage:
//  metalink [options] (input files or --md5) < (mirror list) > (metalinkfile)

//General options:
//  -h [ --help ]         Produce a help message
  opt.help = false;
  _addOpt(help, h, help, "Produce a help message");

//  --version             Print out the name and version
  opt.version = false;
  _addLOpt(version, version, "Print out the name and version");

//  --md5 arg             Generate metalink from md5sum file(s)
  _addLOpt(md5files, md5, "Generate metalink from md5sum file(s)");

//  --addpath arg         Append a path to the mirrors ('/' is not checked)
  _addLOpt(addpath, addpath, "Append a path to the mirrors ('/' is not checked)");

//  --headerfile arg      Include file after the root element declaration.
  _addLOpt(headerfile, headerfile, "Include file after the root element declaration.");

//  --nomirrors           Don't read mirrors from stdin
	opt.nomirrors = false;
  _addLOpt(nomirrors, nomirrors, "Don't read mirrors from stdin");

//  --hashlist            List hashes only (implies nomirrors)
	opt.hashlist = false;
  _addLOpt(hashlist, hashlist, "List hashes only (implies nomirrors)");

//  --desc arg            Add metalink description
  _addLOpt(desc, desc, "Add metalink description");

//Digest options:

//  -d [ --digest ] arg   Include given digest
  _addOpt(digests, d, digest, "Include given digest");

//  --mindigests          Include: md5 sha1
	opt.mindigests = false;
  _addLOpt(mindigests, mindigests, "Include: md5 sha1");

//  --somedigests         Include: md5 sha1 ed2k
	opt.somedigests = false;
  _addLOpt(somedigests, somedigests, "Include: md5 sha1 ed2k");

//  --alldigests          Include all possible digests
	opt.alldigests = false;
  _addLOpt(alldigests, alldigests, "Include all possible digests");
  



/*  Glib::OptionEntry entry5;
  entry5.set_long_name("list");
  entry5.set_short_name('l');
  entry5.set_description("The List");
  add_entry_filename(entry5, m_arg_list);
  */
}

