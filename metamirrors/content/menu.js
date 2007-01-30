/*
MetaMirrors - MetaMirrors interface for Firefox
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
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

*/
var MetaMirrors = {
	prefs: null,
	username: "",
	
  startup: function()
  {
    var cm = document.getElementById("contentAreaContextMenu");
    cm.addEventListener("popupshowing", MetaMirrors.onContextMenuShow, false);
    
    this.prefs = Components.classes["@mozilla.org/preferences-service;1"]
         .getService(Components.interfaces.nsIPrefService)
         .getBranch("metamirrors.");
     this.prefs.QueryInterface(Components.interfaces.nsIPrefBranch2);
     this.prefs.addObserver("", this, false);
     
     this.username = this.prefs.getCharPref("username");
  },

  shutdown: function()
  {
    this.prefs.removeObserver("", this);
  },

  observe: function(subject, topic, data)
   {
     if (topic != "nsPref:changed")
       return;
 
     switch(data)
     {
       case "username":
         this.username = this.prefs.getCharPref("username");
         break;
     }
   },


	onContextMenuShow: function()
	{
	  gContextMenu.showItem("metamirrors-context-menu", false);
	  
	  //Must be savable link
	  if(! (gContextMenu.onSaveableLink || (gContextMenu.inDirList && gContextMenu.onLink)))
	  	return;

	  //Valid link: http or ftp, and not ending in a slash and not containing ? # = and not ending in those and /
	  if(gContextMenu.linkURL.match(/^(http|ftp):\/\/[^#?=]*[^\/#?=]$/) == null)
	  	return;
	  
	  //Blacklist some extensions
	  if(gContextMenu.linkURL.match(/\.(php|html|asp|xml|htmlz|js|css|rdf|shtml|phps|torrent|gpg)$/))
	  	return;
  
	  gContextMenu.showItem("metamirrors-context-menu", true);
	},
	
	
	upload: function()
	{
    gContextMenu.linkURL = "http://www.metamirrors.nl/backend/upload_hashfile.php?user=" + escape(this.username) + "&lnk=" + gContextMenu.linkURL;
	  gContextMenu.openLinkInTab();
	},
	autometalink: function()
	{
    gContextMenu.linkURL = "http://www.metamirrors.nl/backend/get.php?auto&lnk=" + gContextMenu.linkURL;
	  gContextMenu.openLinkInTab();
	},
	metalink: function()
	{
    gContextMenu.linkURL = "http://www.metamirrors.nl/backend/get.php?lnk=" + gContextMenu.linkURL;
	  gContextMenu.openLinkInTab();
	}
};

window.addEventListener("load", function(e) { MetaMirrors.startup(); }, false); 
window.addEventListener("unload", function(e) { MetaMirrors.shutdown(); }, false);
