#include "HashPieces.ih"
std::string const &HashPieces::value() const
{
	static std::string value;
	//assert(false);
	ostringstream ost;
	for(vector<Hash>::size_type i(0);
		i < d_pieces.size();
		++i)
	{
		if(i > 0)
			ost << ":";
		ost << d_pieces[i]->value();
	}
	value = ost.str();
	return value;
}
