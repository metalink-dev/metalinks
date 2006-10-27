#include "Metalink.ih"

//TODO indentation
std::string Metalink::from(std::vector< MetalinkFile > files, std::string const headerFile)
		{
			std::ostringstream out;
			out << "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n";
			out << "<metalink version=\"3.0\" xmlns=\"http://www.metalinker.org/\" generator=\"http://metalinks.sourceforge.net/\">\n";
			
	if(headerFile.size() > 0)
	{
		ifstream file(headerFile.c_str());
		file.unsetf(ios::skipws);
		if(file.is_open())
			copy(istream_iterator<char>(file),
				istream_iterator<char>(),
				ostream_iterator<char>(out)
				);
		else
		{
			cerr << "Warning: Could not open header file: " << headerFile << "\n";
			throw "Opening headerfile failed";
		}
	} 
 	out << "\n<files>\n";
			_foreach(file, files)
			{
				file->finalize();
				out << *file;
				out << "\n";
			}
 			out << "</files>\n";
			out << "</metalink>\n";
			return out.str();
		}
