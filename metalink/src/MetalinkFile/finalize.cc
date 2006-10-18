#include "MetalinkFile.ih"

void MetalinkFile::finalize()
{
	std::ostringstream record;
	record << "\t<file name=\"" << Globals::XMLQuotedSafe(d_filename) << "\">\n";
	if(d_sizeSet)
		record << "\t\t<size>126023668</size>\n";
 	record << "\t\t<verification>\n";
 	_foreach(v, d_vers)
 	{
 		record << "\t\t\t<hash type=\"" << v->first << "\">"
 			<< v->second
 			<< "</hash>\n";
 	}
  record << "\t\t</verification>\n";
  record << "\t\t<resources>\n";
  _foreach(p, d_paths)
  	record << "\t\t\t<url type=\"" << p->first << "\">" << Globals::XMLSafe(p->second) << "</url>\n";
 	record << "\t\t</resources>\n";
	record << "\t</file>";
	assign(record.str());
}
