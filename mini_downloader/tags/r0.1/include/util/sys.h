#ifndef SYS_H
#define SYS_H

#include "util/tstr.h"
#include <boost/cstdint.hpp>

namespace sys {

void truncate_file(tstr::tstring filename, boost::uint64_t size);

}

#endif
