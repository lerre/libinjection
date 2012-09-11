libinjection
============

SQL / SQLI tokenizer parser analyzer.

See
[http://www.client9.com/projects/libinjection/](http://www.client9.com/projects/libinjection/)
for details and presentations.

To use:
look at sqli_cli.cpp, reader.c as examples, but it's as simple as this:

   // clean up input... always makes input smaller.
   len = sqli_qs_normalize(linebuf, len);
   
   // test it.  1 = is isql, 0 = benign
   bool issqli = is_sqli(&sf, linebuf, len);

Copyright (c) 2012 Nick Galbreath
[GPL v2 License](/COPYING.txt) commercial licenses available.
Send requests to nickg@client9.com

The goal of the GPL license is have commericial parties get in
contact, not to restrict usage.  I'm happy to re-license if need be.
