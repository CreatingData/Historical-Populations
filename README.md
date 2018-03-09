![The municipal places in this dataset, by year of maximum population](Maxpop.png)

This is a dataset and code that merges three major sources of historical US population data.

It is part of the in-progress [*Creating Data* digital monograph](http://creatingdata.us/). If citing, please
cite that project in addition to this repo. Eg: "Schmidt, Benjamin. *Creating Data: The Invention of Information in the nineteenth century American State.* http://creatingdata.us"

A fuller description of data and method is contained in the file `extended_description.md` and on the project page.

The sources are:

1. Every Wikipedia page with a population box.
2. A manually entered set of CSVs by Wikipedia editor Jacob Alperin-Sheriff (which is mostly, but not entirely, on wikipedia).
3. A set of historical populations compiled by Stanford's CESTA: U.S. Census Bureau and Erik Steiner, Spatial History Project, Center for Spatial and Textual Analysis, Stanford University.

There are many process files here. The most useful files are likely:

* [merged.csv](merged.csv) (The union dataset.)
* The files in `wikipedia_state_data/`, which include the parsed contents of all Wikipedia population boxes in the United States
* The files in [wiki_census](wiki_census), which are the sources Alperin-Sheriff used to build the wikipedia page.

There are all sorts of errors here. Since this is built up programatically, I'm not interested in corrections to individual data points, although I encourage you
to correct the Wikipedia pages. I have made some efforts to merge duplicate cities in the `merged.csv` file, but there are many cases of double-counting of various sorts.

The wikipedia set is about 4x bigger than the CESTA one. The following maps show roughly the original contributions of each dataset:

![Sources of cities](City%20Sources.png)

Also included is the code that performs extraction from a wikipedia dump, and which performs the merge
(including a few examples of errors and differences between sets.)
These are mostly in ipython notebooks, with a little bit in R notebooks.
Most of the operational python code is broken out into the `.py` files which are imported.


