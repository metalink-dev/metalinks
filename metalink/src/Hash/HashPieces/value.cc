#include "HashPieces.ih"
std::string const &HashPieces::value() const
{
		static std::string value;
	assert(false);
			ostringstream ost;
			ost << "<pieces length=\"" << d_size << "\">";
			for(vector<Hash>::size_type i(0);
				i < d_pieces.size();
				++i)
			{
				ost << "\t\t\t<hash type=\"" << d_pieces[i]->name() << "\">"
 			<< d_pieces[i]->value()
 			<< "</hash>\n";
			}
			ost << "</pieces>";
			value = ost.str();
			return value;
}
