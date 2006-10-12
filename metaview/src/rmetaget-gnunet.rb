#!/usr/bin/env ruby
#
#	rmetaget-gnunet - A Metalinks record downloader for GNUnet
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
#               "This is my second every Ruby program..."
#
#
#
#

#Ugly ugly showhelp code
ARGV.each {|option|
	if /(-h)|(--help)/.match(option)
		puts 'rmetaget-gnunet will run gnunet-download on all files'
		puts 'in the Metalinks XML record given as the first argument.'
		puts 'It doesn\'t support any options except for -h and --help'
		puts ''
		puts 'rmetaget-gnunet [-h|--help] <record.metalinks.xml>'
		exit(1)
	end
}

#Hungry hungy hippos code
require 'rexml/document'
    
def gnunet(xml)
	#gnunet://ecrs/chk/[key].[query].size
	links = Hash.new
	xml.elements.each("metalinks/metalink"){
		|link|
		line = 'gnunet://ecrs/chk/'
		line += link.elements['digests/digest[@dtype="gnunet070file"]'].text
		line += '.'
		line += link.elements['digests/digest[@dtype="gnunet070query"]'].text
		line += '.'
		line += link.elements['size'].text
		links[link.elements['filename'].text] = line;
	}
	return links
end
		
xmlfile = ''
begin                 
	xmlfile = File.new(ARGV[0])
	links = gnunet(REXML::Document.new(xmlfile));
	links.collect { |key|
		##Remove illegal content in key
		valid = key[0].gsub(/["$@#]/, '_')
		puts "Running gnunet-download #{valid}"
		if system("gnunet-download -o \"#{valid}\" \"#{key[1]}\"")
			puts "DONE downloading #{valid}"
		else
			puts "FAILED to download #{valid}"
		end
	}	
	
rescue StandardError => ex
	puts "We had a problem with something... this information might help:"
	puts ex
end


