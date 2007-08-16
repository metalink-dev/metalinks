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

#ifndef _Options_HH_INCLUDED_
#define	_Options_HH_INCLUDED_

#include <glibmm/optiongroup.h>

namespace bneijt
{

class Options: public Glib::OptionGroup
{
	public:
	Options();
  virtual bool on_pre_parse(Glib::OptionContext& context, Glib::OptionGroup& group)
{
  //This is called before the m_arg_* instances are given their values.
  // You do not need to override this method. This is just here to show you how,
  // in case you want to do any extra processing.
  return Glib::OptionGroup::on_pre_parse(context, group);
}  
  virtual bool on_post_parse(Glib::OptionContext& context, Glib::OptionGroup& group)
{
  //This is called after the m_arg_* instances are given their values.
  // You do not need to override this method. This is just here to show you how,
  // in case you want to do any extra processing.
  return Glib::OptionGroup::on_post_parse(context, group);
}
  virtual void on_error(Glib::OptionContext& context, Glib::OptionGroup& group)
{
  Glib::OptionGroup::on_error(context, group);
}  
  
  //These int instances should live as long as the OptionGroup to which they are added, 
  //and as long as the OptionContext to which those OptionGroups are added.
  int m_arg_foo;
  std::string m_arg_filename;
  Glib::ustring m_arg_goo;
  bool m_arg_boolean;
  Glib::OptionGroup::vecustrings m_arg_list;
	
};
} //Namespace
#endif




