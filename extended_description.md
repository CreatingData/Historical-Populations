# Historical population statistics of United States cities and towns

Historical population statistics are at the heart of the Census's
data-gathering authority, and *in theory* the amount of data available
is extraordinary. For every census save 1890, the vast majority of the
original census schedules are preserved, and in most cases even
digitized through sources like ancestry.com and IPUMS at the
University of Minnesota Population Center.

In practice, tabulating the granular census up into cities, towns, and
counties remains mostly impossible. The place names used by the census
are not retained in many of the IPUMS files, and in any case
full-count data is only available after a 72 year windowing period.

County level population data exists in an excellent form, compiled
across a variety of characteristics.[@haines_historical_2010] These
surveys make it fairly easy to get fine grained estimates in the parts
of the country where counties form reasonably well-distributed units
of government.

Census-derived city- or place-based data is considerably harder to get
in aggregate form. There are two major sources I use in this project.

### CESTA City Population data.

The census bureau has periodically
  published lists of all cities with populations over 2,500 persons;
  at some point this set was digitized internally. A team at
  Stanford's CESTA center cleaned this data and has begun to
  supplement it with a number of state-led efforts to digitize
  historical populations, including in Arkansas, California, Colorado,
  Iowa, and Oregon. This data uses a broad definition of "place"
  before 1940, and something approximating the current
  census-designated-place afterwards. The CESTA data contains
  approximately 7,500 places from the Census Bureau lists, and a few
  thousand more from miscellaneous other sources. Populations for
  cities are only sometimes present before the period when they exceed
  2,500 population.  These miscellaneous other sources include some of
  the best extant information on a number of states. Together, this
  dataset contains about 62,000 non-zero entry (a little fewer than
  ten years per city).

### Wikipedia Population data

The most extensive digital dataset of
  populations is scattered across Wikipedia, the online
  encyclopedia. The published decennial census volumes contain
  information on a variety of towns with populations below 2,500. To
  my knowledge, the largest-scale efforts to digitize these volumes
  has been undertaken by Jacob Alperin-Sheriff, who undertake the work
  while a graduate student at Georgia Tech. (He is now works in
  cryptographer for the government). Posting the populations to
  Wikipedia under the username "DemocraticLuntz," he entered
  approximate 25,000 cities and counties from the census, accounting
  for about 237,707 non-zero entries. This includes, by his account,
  every incorporated place in the country and every non-incorporated
  place in several states, mostly in the Northeast. In addition to
  Alperin-Sheriff's work, a number of other wikipedia editors have
  adopted states or smaller regions; for instance, another editor
  entered the populations of all Massachusetts cities and towns from
  the 1850 census onward.

  Wikipedia uses so-called "templates" to enter in semi-structured
  data, including populations. Most US historical population data uses
  one of three templates (`US Census Population`, `USCensusPop`, or
  `Historical Populations` with type of "United States"). I have
  downloaded a dump of the entire Wikipedia dataset and examined the
  text of all articles to see if these templates are present; a set of
  filters then winnows this large set down to only places in the
  United States. (This method also yields remarkably detailed data for
  France and Austria, as well as less comprehensive detail for a
  variety of places around the world; I do not know the extent to
  which this represents manual data entry for other historical places,
  as opposed to simple reformatting of existing digital datasets.

  Alperin-Sherriff has sent me the files he used to update Wikipedia
  pages.
  
  A variety of other editors have made their own edits to different
  sections, sometimes at great scale. User `rossdegenstein`, for
  example, seems to have filled out hundreds of population places
  around North Dakota.

Each of these datasets contains slight differences from the others.
  Alperin-Sheriff's edits, for example, are only about 99% consistent
  with the actual numbers on Wikipedia. (In many cases, it appears he
  entered numbers but did not upload them because articles already
  contained information; in others, falsely keyed information was
  corrected.)  The CESTA set diverges even further, agreeing with
  Alperin-Sheriff 97% of the time. In many of these cases, the CESTA
  set has entered rounded numbers; in others there are obvious digit
  transpositions, and in still more there are differences that don't
  appear to be simple miskeying, in which it is possible the longer
  census municipality lists differ from the frontmatter of major
  cities. In a few cases, it appears that one source or the other has
  an entire city's row shifted off by 10 years.
  
## Reconciliation Strategy

In compiling a more complete list of place name populations, I have
adopted the following strategy.

First, create several "upstream" datasets consisting of various subsets of
the data listed above. As a general rule, I estimate the quality to be be
in the following order:

1. Census-originating data from the CESTA-Stanford set.
2. State-level data from the CESTA-Stanford set.
3. Other wikipedia edits.
4. The Alperin-Sheriff set in cases where it was not posted to
   wikipedia.
5. Lahnmeyer data from the CESTA-Stanford set (which is usually rounded to the nearest hundredth.)

Second, merge rows together by state. The first merging pass looks for
entries with at least three identical non-zero entries. (This
threshold is sufficient to avoid any collisions in the entire CESTA
dataset), or a complete overlap when one set has entries only for one
or two years. (This is common in cities, for instance, that first
enter the census in 2000.) In some cases--for instance, when the CESTA
set has only rounded numbers from Lahnmeyer-- this results in
duplicate versions of a city.

In the 1-3% of cases where estimates differ between sets, I choose the
population number(s) that most closely match a constant rate of growth
between the nearest agreed-upon points.  This filters out egregious
errors (which seem to exist in both wikipedia and CESTA sets), but
probably does not do much do actually get correct population numbers
when it's a simple digit transposition at the end of the number.

For coordinates, I prefer Wikipedia coordinates to CESTA ones, because
the CESTA coordinates are generally centroids that may lay outside a
city's historical boundaries. For example: CESTA provides two points
for New York City, one in Brooklyn and one in Queens. Neither of these
were in the city before the late-19th century. The Wikipedia location,
from the USGS, is on the location of city hall downtown, which has
been part of the city considerably longer.
