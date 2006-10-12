#!/usr/bin/env ruby
#
#	metalinks-view - A Metalinks record viewer written in Ruby
#
# This program is free software; you can redistribute it and/or
#	modify it under the terms of the GNU General Public License
#	as published by the Free Software Foundation; either version 2
#	of the License, or (at your option) any later version.
#
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with this program; if not, write to the Free Software
#	Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
#
#
#	Copyright (C) 2005  A. Bram Neijt <bneijt@gmail.com>
#               "This is my first every Ruby program..."
#
#
#
#
#

require 'rexml/document'
require 'gnome2'

class Viewer < Gtk::Window
    TITLE = "Metalinks record viewer"
    NAME = "MetalinksViewer" 
    VERSION = "0.0.3"
    
		def gnunet()
			#gnunet://ecrs/chk/[key].[query].size
			lines = Array.new
			@xml.elements.each("metalinks/metalink"){
				|link|
				line = 'gnunet://ecrs/chk/'
				line += link.elements['digests/digest[@dtype="gnunet070file"]'].text
				line += '.'
				line += link.elements['digests/digest[@dtype="gnunet070query"]'].text
				line += '.'
				line += link.elements['size'].text
				
				lines.push(line)
			}
			@tv.buffer.set_text(lines.join("\n"))
		end
		
		def ed2k()
			#ed2k://|file|firefox-1.0.7.installer.tar.gz|8622490|fc5bdf45d46005e3ccde403a253c6437|/
			lines = Array.new
			@xml.elements.each("metalinks/metalink"){
				|link|
				line = 'ed2k://|'
				line += link.elements['filename'].text
				line += '|'
				line += link.elements['size'].text
				line += '|'
				line += link.elements['digests/digest[@dtype="ed2k"]'].text
				line += '|/'
				
				lines.push(line)
			}
			@tv.buffer.set_text(lines.join("\n"))
		end
		
		def md5()
			lines = Array.new
			@xml.elements.each("metalinks/metalink"){
				|link|
				line = link.elements['digests/digest[@dtype="md5"]'].text + '  ' + link.elements['filename'].text
				lines.push(line)
			}
			@tv.buffer.set_text(lines.join("\n"))
		end

		def magnet()
			lines = Array.new
			@xml.elements.each("metalinks/metalink"){
				|link|
				line = 'magnet:?xt=urn:sha1:' + link.elements['digests/digest[@dtype="sha1"]'].text
				## Translate spaces first
				##line += '&dn=' + link.elements['filename'].text if link.elements['filename'].text
				lines.push(line)
			}
			@tv.buffer.set_text(lines.join("\n"))
		end

		def sha1()
			lines = Array.new
			@xml.elements.each("metalinks/metalink"){
				|link|
				line = link.elements['digests/digest[@dtype="sha1"]'].text + '  ' + link.elements['filename'].text
				lines.push(line)
			}
			@tv.buffer.set_text(lines.join("\n"))
		end
		
		def sha512()
			lines = Array.new
			@xml.elements.each("metalinks/metalink"){
				|link|
				line = link.elements['digests/digest[@dtype="sha512"]'].text + '  ' + link.elements['filename'].text
				lines.push(line)
			}
			@tv.buffer.set_text(lines.join("\n"))
		end
		
    def initialize(fileInformation, filename)
    
    		@xml = REXML::Document.new fileInformation if filename != ''

				
				    		
        # Initialize window.
        super(Gtk::Window::TOPLEVEL)
        self.set_title(TITLE)
        
        set_default_size(500, 200)
				@vbox = Gtk::VBox.new()
	
				@menu = Gtk::MenuBar.new()
				@type = Gtk::MenuItem.new("_View")
				@types = Gtk::Menu.new()
				
				#Menu Items
				item = Gtk::MenuItem.new("_GNUnet")
				item.signal_connect("activate") { gnunet }
				@types.append(item)
				
				item = Gtk::MenuItem.new("_eDonkey2000")
				item.signal_connect("activate") { ed2k }
				@types.append(item)
				
				item = Gtk::MenuItem.new("M_agnet links")
				item.signal_connect("activate") { magnet }
				@types.append(item)

				item = Gtk::MenuItem.new("_MD5 sums")
				item.signal_connect("activate") { md5 }
				@types.append(item)

				item = Gtk::MenuItem.new("SHA_1 sums")
				item.signal_connect("activate") { sha1 }
				@types.append(item)

				item = Gtk::MenuItem.new("SHA_512 sums")
				item.signal_connect("activate") { sha512 }
				@types.append(item)
			
				@type.set_submenu(@types)
				
				@menu.append(@type)
				
				@vbox.pack_start(@menu, false)
				@menu.show_all


				
				@tv = Gtk::TextView.new()
				@tv.wrap_mode = Gtk::TextTag::WRAP_CHAR
				if filename != ''
					@tv.buffer.set_text("Opened and read:\n\t" + filename + "\nPlease choose a type from the View menu.\n\nFor more information, or to help out, visit:\n\thttp://metalinks.sourceforge.net")
				else
					@tv.buffer.set_text("Error opening file or none given on commandline.")
				end

				@vbox.pack_start_defaults(@tv)
				
				add(@vbox)

        signal_connect("destroy") do 
            Gtk.main_quit
            exit!
        end
    end
end
begin
	files = ARGV.collect { |x| x unless x =~ /^-/ }

	Gnome::Program.new(Viewer::NAME,
	                   Viewer::VERSION)
	xmlfile = ''
	begin                 
		xmlfile = File.new(ARGV[0])
	rescue StandardError => ex
		ARGV[0] = ''
	end

	Viewer.new(xmlfile, ARGV[0]).show_all
	Gtk.main
rescue StandardError => ex
		puts ex.to_s
		puts "\n"
end

