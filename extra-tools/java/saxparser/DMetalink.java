/*
	This file is part of the saxparser for Java from the Metalinks tools project
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

import java.util.*;


/** Metalink data container class
*/
public class DMetalink
{
	/**
		The workhorse of the system
	*/
	public class FileEntry
	{
		public HashMap hashlist;
		public ArrayList uris;
		public String filename;
		
		public FileEntry(String name)
		{
			filename = name;
			hashlist = new HashMap();
			uris = new ArrayList();
		}
		public String sha1()
		{
			return (String) hashlist.get("sha1");
		}
		//magnet:?xt=urn:sha1:YNCKHTQCWBTRNJIV4WNAE52SJUQCZO5C&dn=Great+Speeches+-+Martin+Luther+King+Jr.+-+I+Have+A+Dream.mp3
		public String magnet()
		{
			String dn = filename.replaceAll(" ", "+").replaceAll("&", "&amp;");
			if(this.sha1() != null)
				return "magnet:?xt=urn:sha1:"+this.sha1()+"&dn="+dn;
			return null;
		}
	}
	
	public ArrayList files;
	
	public DMetalink()
	{
		files = new ArrayList();
	}
	
	
	/** Start a new file, with a given filename
	*/
	public void newFile(String filename)
	{
		files.add(new FileEntry(filename));
		System.out.println(this.files.size());
	}
	//Add a link to the last started file
	public void addLink(String uri)
	{
		//TODO allow for type, preference etc.
		FileEntry f = (FileEntry) files.get(files.size() -1);
		f.uris.add(uri);
		System.out.println(uri);
	}
	public void addHash(String type, String value)
	{
		FileEntry f = (FileEntry) files.get(files.size() -1);
		f.hashlist.put(type, value);
		System.out.println("Adding hash: "+value);
	}
	public String toString()
	{
		String s = new String();
		s += files.size() + " files known\n";
		for(int i = 0; i < files.size(); ++i)
		{
			FileEntry f = (FileEntry) files.get(i);
			s += "FileEntry("+i+"): " + f.filename +"\n";
			ArrayList uris = f.uris;
			for(int e = 0; e < uris.size(); ++e)
				s += "  url(" + e + ")= " + uris.get(e).toString() + "\n";
			Iterator hi = f.hashlist.entrySet().iterator();
			while(hi.hasNext())
			{
				Map.Entry hash = (Map.Entry) hi.next();
				s += "  hash(" + hash.getKey() + ")= " + hash.getValue() + "\n";
			}
		}
		return s;
	}
}
