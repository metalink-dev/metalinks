#include "HashPieces.ih"
std::string HashPieces::xml() const
	{
			ostringstream ost;
			assert(d_pieces.size() > 0);
			
			ost << "<pieces length=\"" << d_size << "\" type=\"" << d_pieces[0]->name() << "\">\n";

			for(vector<Hash>::size_type i(0);
				i < d_pieces.size();
				++i)
			{
				ost << "\t\t\t\t<hash piece=\"" << i << "\">"
 			<< d_pieces[i]->value()
 			<< "</hash>\n";
			}
			ost << "\t\t\t</pieces>";
			
			return ost.str();
	}
