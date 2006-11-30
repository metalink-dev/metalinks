#include "HashPieces.ih"
std::string HashPieces::name() const
{
	if(d_pieces.size() > 0)
		return d_pieces[0]->name() + "pieces";
	return "pieces";
}
