/*
 * sha1.h
 *
 * Originally witten by Steve Reid <steve@edmweb.com>
 * 
 * Modified by Aaron D. Gifford <agifford@infowest.com>
 * Modified by Hampus Wessman <hw@vox.nu> (2008)
 *
 * NO COPYRIGHT - THIS IS 100% IN THE PUBLIC DOMAIN
 *
 * The original unmodified version is available at:
 *    ftp://ftp.funet.fi/pub/crypt/hash/sha/sha1.c
 *
 * THIS SOFTWARE IS PROVIDED BY THE AUTHOR(S) AND CONTRIBUTORS ``AS IS'' AND
 * ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR(S) OR CONTRIBUTORS BE LIABLE
 * FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 * DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
 * OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
 * HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
 * LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
 * OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
 * SUCH DAMAGE.
 */

#ifndef SHA1_H
#define SHA1_H

#include "util/tstr.h"
#include <boost/cstdint.hpp>
#include <string>

typedef boost::uint32_t sha1_quadbyte;
typedef boost::uint8_t sha1_byte;

#define SHA1_BLOCK_LENGTH 64
#define SHA1_DIGEST_LENGTH 20

// The SHA1 structure:
typedef struct _SHA_CTX {
    sha1_quadbyte state[5];
    sha1_quadbyte count[2];
    sha1_byte buffer[SHA1_BLOCK_LENGTH];
} SHA_CTX;

void SHA1_Init(SHA_CTX *context);
void SHA1_Update(SHA_CTX *context, const sha1_byte *data, unsigned int len);
void SHA1_Update(SHA_CTX *context, const std::string data);
void SHA1_Final(sha1_byte digest[SHA1_DIGEST_LENGTH], SHA_CTX* context);

class SHA1Gen
{
public:
    SHA1Gen()
    {
        init();
    }
    SHA1Gen(std::string data)
    {
        init();
        update(data);
    }
    void init()
    {
        SHA1_Init(&_ctx);
        _final = false;
    }
    void update(std::string data)
    {
        if(!_final) {
            SHA1_Update(&_ctx, data);
        }
    }
    void final()
    {
        if(!_final) {
            SHA1_Final(_digest, &_ctx);
            _final = true;
        }
    }
    tstr::tstring hex()
    {
        if(!_final) final();
        return tstr::data2hex(_digest, SHA1_DIGEST_LENGTH);
    }
private:
    bool _final;
    sha1_byte _digest[SHA1_DIGEST_LENGTH];
    SHA_CTX _ctx;
};

#endif

