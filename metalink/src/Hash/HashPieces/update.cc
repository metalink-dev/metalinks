#include "HashPieces.ih"
void HashPieces::update(char const *bytes, unsigned int numbytes)
{
	//Check overflow
	//Update/finalize hash
	//Nexthash code
	if(numbytes == 0)
		return;
	
	assert(numbytes < d_size);

	//Add bytes till d_count is equal to blockSize
	if(numbytes + d_count < d_size)
	{
		d_h->update(bytes, numbytes);
		d_count += numbytes;
	}
	else
	{
		//Write last part of blockSize, blockSize - d_count;
		unsigned int head = d_size - d_count;
		d_h->update(bytes, head);
		d_h->finalize();
		d_pieces.push_back(d_h);
		
		
		unsigned int tail = numbytes - head;
		_debugLevel2("Push with overflow " << tail);
		
		d_h = new GCrypt(GCRY_MD_SHA1);
		d_count = 0;
		this->update(bytes + head, tail);
	}
}
