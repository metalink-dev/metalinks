/*
   Foreach.hh - C++ foreach preprocessor macro for STL containers

   Copyright (C) 2005 A. Bram Neijt <b.neijt@gmail.com>

   This program is free software; you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation; either version 2, or (at your option)
   any later version.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this program; if not, write to the Free Software Foundation,
   Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
*/
///\file
///\brief Preprosessor macro to define a STL iterator for loop: _foreach(iterator, container)


#ifndef _ccsys_FOREACH_H_INCLUDED_
#define _ccsys_FOREACH_H_INCLUDED_

//
// The triple expansion may seem daring, but it is needed to fully expand the __LINE__
// Which is needed for code like: foreach(iter, arrayOfVectors[0])
//

///\brief Preprosessor macro to define a STL iterator for loop: _foreach(iterator, container)
///
///The preprosessor instruction foreach takes a variable name and an iterator name and translates
///into a default for loop using the != operator. It should work with any forward iterator.
///For const iterators, there is the cforeach preprocessor macro.
///\section examples Examples
///\code
///vector<usnigned> numbers;
///numbers.push_back(10);
///_foreach(number, numbers)
///  cout << *number << "\n";
///\endcode
///
///DON'T!!!
///Don't use temporary const objects returned by functions, like: foreach(i, file.lines()).

#ifdef _foreach
#error _foreach already defined! This macro may have gone wild!
#endif

#define _foreach( iter, cont) for( __typeof__((cont).begin()) iter = (cont).begin(); iter != (cont).end(); ++iter)

//_INCLUDED
#endif
