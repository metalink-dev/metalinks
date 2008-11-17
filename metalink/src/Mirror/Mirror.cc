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



#include "Mirror.ih"

Mirror::Mirror(std::string const &path,
	std::string const &preference,
	std::string const &location,
	std::string const &type)
	:
	d_path(path),
	d_preference(0),
	d_location(location),
	d_type(type)
{
	
	istringstream p(preference);
	p >> d_preference;


	//Try to parse the location from the path if the location is empty
	//Maybe I should add a boost regex here ;)
	//GetHostname
	string::size_type hspos = path.find("//");
	if(hspos != string::npos)
	{
		//Find the second /
		string::size_type hepos = path.find('/', hspos +2);
		if(hepos != string::npos)
		{
			//Get host
			string host = path.substr(hspos +2 , hepos - hspos - 2);
			_debugLevel3("Found host: " << host << " from " << path);
			string::size_type ppos = host.rfind('.');
			if(ppos != string::npos)
			{
				string landcode = host.substr(ppos + 1);
				_debugLevel1("Found top level domain: " << landcode);
				string const landcodes(" ac ad ae af ag ai al am an ao aq ar as at au aw ax az ba bb bd be bf bg bh bi bj bm bn bo br bs bt bv bw by bz ca cc cd cf cg ch ci ck cl cm cn co cr cu cv cx cy cz de dj dk dm do dz ec ee eg eh er es et eu fi fj fk fm fo fr ga gb gd ge gf gg gh gi gl gm gn gp gq gr gs gt gu gw gy hk hm hn hr ht hu id ie il im in io iq ir is it je jm jo jp ke kg kh ki km kn kp kr kw ky kz la lb lc li lk lr ls lt lu lv ly ma mc md me mg mh mk ml mm mn mo mp mq mr ms mt mu mv mw mx my mz na nc ne nf ng ni nl no np nr nu nz om pa pe pf pg ph pk pl pm pn pr ps pt pw py qa re ro rs ru rw sa sb sc sd se sg sh si sj sk sl sm sn so sr st su sv sy sz tc td tf tg th tj tk tl tm tn to tp tr tt tv tw tz ua ug uk um us uy uz va vc ve vg vi vn vu wf ws ye yt yu za zm zw ");
				if(landcodes.find(" " + landcode + " ") != string::npos)
					d_location = landcode;
			}
		}
	}
}
