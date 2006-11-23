#include "HashPieces.ih"
void HashPieces::finalize()
	{
	
			//If d_h, finalize and push
			if(d_h)
			{
				d_h->finalize();
				d_pieces.push_back(d_h);
				d_h = 0;
			}
	}
