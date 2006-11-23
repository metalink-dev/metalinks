#include "HashPieces.ih"
std::string HashPieces::xml() const
	{
			ostringstream ost;
			
			ost << "<pieces length=\"" << d_size << "\">\n";

			for(vector<Hash>::size_type i(0);
				i < d_pieces.size();
				++i)
			{
				ost << "\t\t\t\t<hash type=\"" << d_pieces[i]->name() << "\" piece=\"" << i << "\">"
 			<< d_pieces[i]->value()
 			<< "</hash>\n";
			}
			ost << "\t\t\t</pieces>";
			
			return ost.str();
	}
