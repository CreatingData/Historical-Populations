# This Python file uses the following encoding: utf-8

import bz2
import regex as re
import mwparserfromhell as mw
import provinces

us_states = provinces.us_states
ca_provinces = provinces.canadian_provinces

# Removes double brackets and links.
_stripper_re = re.compile(r"[\[\{]{2}(?:[^\]]*\|)?([^\]]*)[\]\}]{2}")

def value_for_table_entry(key, text):
    my_re = r"\| ?" + key + r"[^=]*=(.*)"
    matches = re.findall(my_re,text)
    if matches:    
        m = matches[0]
        # Ugly; remove anything after a link out starts
        m = re.sub("&lt.*&gt.*","",m)
        m = re.sub(_stripper_re,r"\1",m)
        m = m.strip()
        return m
    else:
        raise NoSuchAttribute
    
def settle_type(self):

    settlematch_re = r"\| ?settlement_type.*=(.*)"
    any_type_match_re = r"\| ?type.*=(.*)"
    
    if re.search("Infobox Settlement", self.text[:4000],re.IGNORECASE):
        for my_key in [r"settlement_type",r"type"]:
            try:
                m = value_for_table_entry(my_key,self.text[:4000])
#                m = m.replace("&lt;!-- e.g. Town, Village, City, etc.--&gt;","")
                return m
            except NoSuchAttribute:
                continue
            
    if "eobox" in self.text[:2000] and "ettlement" in self.text[:2000]:
        try:
            return value_for_table_entry(r"category",self.text[:2000])
        except NoSuchAttribute:
            pass

        
    if "Census Area" in self.text:
        return "Census Area"
    if "Infobox NRHP" in self.text[:1000]:
        return "NHRP"
    if "Infobox Island" in self.text[:1000]:
        return "Island"
    if "Infobox Town AT" in self.text[:1000]:
        return "Town"

    if re.search(r"\[\[Unincorporated Community\]\]", self.text[:1000],re.IGNORECASE):
        return "Unincorporated Community"


    if re.search("Infobox French Commune", self.text[:1000],re.IGNORECASE):
        return "Commune"
    if re.search("Infobox U.S. county", self.text[:1000],re.IGNORECASE):
        return "US County"
    if re.search("Infobox U.S. State", self.text[:1000],re.IGNORECASE):
        return "US State"
    if self.title in us_states and self.title != "Georgia":
        return "US State"
    if self.title=="Georgia (U.S. state)" or self.title=="Washington (state)":
        return "US State"
    if re.search("Infobox Metropolitan Area", self.text[:1000],re.IGNORECASE):    
        return "Metropolitan Area"
    if re.search("Infobox Military (installation|structure)", self.text[:1000],re.IGNORECASE):
        return "Military Installation"    
    if re.search("Plantation (Maine)|plantation", self.text[:1000],re.IGNORECASE):
        return "Plantation"

    try:
        m = value_for_table_entry(r"official name",self.text[:1000])
        print m
        
    except:
        pass
    t = self.title.split(",",1)[0]
    
    in_text = re.findall(r"'''" + t + r"''' (?:is|was) an? ([^ ]+ ?[^ ]+|\[\[+[^\]]{,40}\]\]) (?:(?:located)? ?in |that existed)",self.text[:5000])
    if in_text:
        print "Using " + in_text[0]
        return re.sub(_stripper_re,r"\1",in_text[0])
    if "(" in t and ")" in t:
        # Star Prairie (town), Wisconsin -> 'town'
        return t.split("(")[1][:-1]
    
    return "Unknown"

        
def get_keyval(line):
    # Extremely lightweight parsing of the XML. Should work?
    
    if line.startswith("    <"):
        keyend = line.find(">")
        valueend = line.rfind("<")
        if valueend < keyend:
            # Then there's only one set of double brackets
            return None
        key = line[5:keyend]
        value = line[keyend+1:valueend]
        return (key,value)
    else:
        return None
    
class WikipediaParser(object):
    def __init__(self,dump_location):
        self.f = bz2.BZ2File(dump_location)
    def filter(self,article):
        return True
    
    def page_yielder(self):
        printing = False
        queue = []
        for line in self.f:
            if line=="  <page>\n":
                printing = True
                
            elif line=="  </page>\n":
                yield queue
                queue = []
                printing = False
                
            else:
                if printing:
                    queue.append(line)
                    
    def __iter__(self):
        for page in self.page_yielder():
            title = None
            id = None
            text = ""
            inside_text = False
            for line in page:
                if not inside_text:
                    if line.endswith("</title>\n"):
                        _,title = get_keyval(line)
                    elif line.endswith("</id>\n"):
                        try:
                            _,id = get_keyval(line)
                        except:
                            continue
                    elif line.startswith("      <text"):
                        textstart = line.find(">")
                        text = line[textstart + 1:]
                        inside_text = True
                if inside_text:
                    if line.endswith("</text>\n"):
                        inside_text = False
                        text += line[:-9]
                    else:
                        text += line
            yield WikipediaArticle(title,id,text)
            
class NoSuchAttribute(Exception):
    pass

def parse_row(row):
    try:
        y,rest = row.split("=",1)
        pop = int(rest.replace(",",""))
        y = int(y)
    except:
        return None
    return (y,pop)

def parse_bars(row):
    try:
        _,y,p = row.split("|")
        return((int(y),int(p.replace(",",""))))
    except:
        return None

import requests as r

class WikipediaArticle(object):
    
    def __init__(self,title,id=None,wikitext=None):
        self.title = title
        if id:
            self.id = id
            self.text = wikitext
        else:
            p = r.get(u"https://en.wikipedia.org/w/index.php?action=raw&title={}".format(title))
            self.text = p.content
            self.id = -1

    def mwparse(self):
        try:
            return self.mediawiki
        except:
            d = mw.parse(self.text).filter_templates()
            self.mediawiki = d
            return d

    def get_poptype(self):
        pass


    def drop_from_title(self):
        # A lot of places have placenames, but are not, truly, places.
        # Here's an attempt to come up with a partial list.
        
        for term in [
                "micropolitan area",
                "List of ",
                "Diocese of",
                "metropolitan area",
                "metroplex",
                "statistical area",
                "Statistical Area",                
                "Demographics of",
                "Demography of",                
                "History of",
                "Islam in",
                "Hinduism in",
                "Christianity in",
                "Slovaks in",
                "Population of",
                "Romanians in",
                "Jews in",
                "/sandbox",
                "/testcase",
                "/doc"
                ]:
            if re.search(term,self.title,re.IGNORECASE):
                return True
        for term in [
                " Area"," MSA"]:
            if self.title.endswith(term):
                return True

        for term in [
                "Infobox organization",
                "Infobox foobar",
                "Infobox ethnic group",
                "Infobox Ethnic group",                
                "Infobox country",
                "Infobox Canada electoral district",
                "Infobox London Borough",
                "Infobox rail line", # Some articles use population boxes for ridership
                "Infobox islands",# Seems to be mostly Ireland
                "Infobox St. Louis neighborhood",                ]:
            if term in self.text[:500]:
                return True

            
        return False
        
    
    def country(self):
        
        if "Infobox French commune" in self.text[:200]:
            return "FR"
        if "[http://www.insee.fr" in self.text[:300]:
            return "FR"
        
        if "USCensusPop" in self.text:
            return "US"
        
        if "US Census population" in self.text:
            return "US"
        
        if "Infobox Ort in Österreich" in self.text[:200]:
            return "AT"

        if "Infobox Region of Italy" in self.text[:200]:
            return "AT"        
        if "Districts of British India" in self.text[:500]:
            return "IN"

        if "{{Canada Census" in self.text:
            return "CA"

        if "type:landmark_region:US" in self.text[:1000]:
            return "US"
        
        state_guess = self.title.split(",")[-1].strip()

        if len(state_guess) > 1:
            if state_guess in us_states:
                return "US"
            if state_guess in provinces.canadian_provinces:
                return "CA"
            
        if "|region:" in self.text:
            start = self.text.index("|region:")
            place = self.text[start+8:start+14]
            if place[2]=="-" and (place[5]=="|" or place[5]=="_"):
                return place[:2]
            if place[2] in "|_-":
                if place[0] in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                    if place[1] in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                        return place[:2]
            print place
            print "***" + self.text[start+7:start+40] + "***"

        if "= Location in Turkey\n" in self.text[:500]:
            return "TR"

        if re.search(r"\n\|.?subdivision_type",self.text[:2500]):
            guess = self.country_from_subdivision()            
            return guess
            
        if "\n| subdivision_type1" in self.text[:2500]:
            self.text = self.text.replace("\n| subdivision_type1","\n|subdivision_type1")
        
        if "\n|subdivision_type1" in self.text[:2500]:
            guess = self.country_from_subdivision()
            return guess           


        if "{{Ireland-geo-stub}" in self.text:
            return "IE"
        if self.coords()[1] > -40:
            return "Unknown (Non-US)"

        
        return None


    def country_from_subdivision(self):

        block = re.findall(r"\n\|.?subdivision_type.*\n\|.*\n",self.text[:2500])[0]
        block = block.split("\n")[2]
        block = block.split("=")[1].strip()
        block = re.sub(r"[\[{\]\}]","",block)
        block = block.split("|")[-1]
        return block
    
    def country_from_subdivision1(self):
        start = self.text.index("\n|subdivision_type1")
        t = self.text[start+1:]
        rowend = t.index("\n")
        t = t[:rowend]
        matches = re.findall(r" of ([A-Za-z ]+)\|",t)
        countries = {"Mexico":"MX","Canada":"CA"}
        
        if matches:
            for match in matches:
                if match in countries:
                    return countries[match]
                else:
                    print "Using {} as a country".format(match)
                    return match
        else:
             print self.text[:2500]
             raise
        
        return None
    
    def historical_pops(self):
        templates = self.mwparse()
        poptemplates = [t for t in templates if t.name.rstrip() == "Historical populations"]
        if not poptemplates:
            raise NoSuchAttribute
        try:
            self.poptype = poptemplates[0].get("type").value.rstrip()
        except:
            self.poptype = "Unknown"
        
        oput = []
        for row in poptemplates[0].split(u"\n"):
            try:
                _,y,p = row.split("|")
                oput.append((int(y),int(p.replace(",",""))))
            except:
                pass
        return oput

    def census_pops_1(self):
        templates = self.mwparse()
        poptemplates = [t for t in templates if t.name.rstrip() == "US Census population" or t.name.rstrip() == "USCensusPop"]
        try:
            p = poptemplates[0].split("|")
            self.poptype = "Census"
        except IndexError:
            # Probably the text shows up outside a template?
            raise NoSuchAttribute
            
        out = []

        for r in p:
            try:
                y,v = r.split("=")
                out.append((int(y),int(v.replace("}",""))))
            except ValueError:
                continue
            except:
                raise
        if out:
            self.poptype = "Census"

            return out
        else:
            raise NoSuchAttribute
    
    def pops(self):
        """
        Search for a population template, and return the population.
        """

        if hasattr(self,"pop_cache"):
            if len(self.pop_cache)==0:
                pass
            elif self.pop_cache[-1][0] != 2010:
                pass
            else:
                return self.pop_cache

        ttypes = [
            ("US Census population",self.census_pops_1),
            ("USCensusPop",self.census_pops_1),
            ("Historical populations",self.historical_pops)
        ]


        
        for ttype,method in ttypes:
            if ttype in self.text:
                try:
                    self.pop_cache = method()
                    return self.pop_cache
                except NoSuchAttribute:
                    # Keep on trucking; this means the later methods will be tried,
                    # as well as the earlier ones.
                    continue
        try:
            self.pop_cache = self.town_pops()
            return self.pop_cache
        except:
            raise

    def parse_name_portions(self):
        splat = self.title.split(",")
        splat = [s.strip().rstrip() for s in splat]
        if len(splat)==3:
            return dict(zip(["place","county","state"],splat))
        elif len(splat)==2:
            return dict(zip(["place","state"],splat))
        elif len(splat)==1:
            return dict(zip(["state"],splat))
        else:
            print splat
            
    def state(self):
        try:
            state = self.parse_name_portions()["state"]
            st = us_states[state]
            return st
        except KeyError:
            pass

        try:
            name = value_for_table_entry("subdivision_name1", self.text[:5800])
            return us_states[name]
        except:
            pass

        try:
            name = value_for_table_entry("name", self.text[:1200])

            name = name.split(",")[-1].strip().rstrip()
            return us_states[name]
        except:
            pass

        # A few important places just don't match the mold.
        # This includes a lot of neighborhoods like Northern Liberties, PA
        # I see no places under 1000 that show major problems.
        presets = {
            "Georgia (U.S. state)":"GA",
            "St. Louis":"MO",
            "Washington, D.C.":"DC",
            "Washington (state)":"WA",
            "Maui":"HI",
            "New York City":"NY",
            "Los Angeles":"CA",
            "Louisville":"KY",
            "Philadelphia":"PA",
            "Manhattan":"NY",
            "Chicago":"IL",
            "Washington, D.C.":"DC"
        }

        try:
            return presets[self.title.split(",")[-1].strip()]
        except KeyError:
            if "Washington, D.C." in self.title:
                # Necessary because the comma screws things up.
                return "DC"
            raise NoSuchAttribute

    def is_county(self):
        parts = self.parse_name_portions()
        for k in ['place','county']:
            try:
                for g in ["county","parish","County","Parish"]:
                    if parts[k].endswith(g):
                        return True
            except KeyError:
                pass
        return False
        
    def town_pops(self):

        content = self.text
        
        splitter = None
        
        try:
            start = content.index("{{US Census population")
            method = parse_row
            splitter="|"
            
        except:
            pass
        try:
            start = content.index("{{USCensusPop")
            method = parse_row
            splitter="|"
        except:
            pass
        
        try:
            start = content.index("{{Historical populations")
            method = parse_bars
            splitter="|"
        except:
            pass

        if splitter is None:
            raise NoSuchAttribute

        
        def strip_internal_double_brackets(string):
            end_loc = content[start:].index("}}")
            next_open = content[start:].index("{{")        
        
        content = content[start+2:]

        
        if True:
            pass
        elif "{{Historical populations" in content:
            start = content.index("Historical populations\n|type= USA") + 34

        elif "{{Historical populations\n|type=USA" in content:
            start = content.index("Historical populations\n|type=USA") + 33
            splitter = "\n"
            method = parse_bars
        else:
            raise NoSuchAttribute
        
        area = content[(start):(start + 500)]
        bits = area.split(splitter)
        return [pair for pair in map(method,bits) if pair is not None]


    def __str__(self):
        return self.title + "\n" + ("=" * 80) + "\n" +  self.text[:500]

    def __repr__(self):
        return self.__str__()
    
    def boxes(self):
        
        try:
            return self._box_names
        except:        
            self._box_names = [t.name for t in self.mwparse()]
            return self._box_names
    
    def coords(self):
        utf = self.text
        try:
            start = utf.index("{{coord|") + 8
        except:
            return (None,None)
        utf = utf[start:]
        try:
            close = utf.index("}}")
        except ValueError:
            print utf[:100]
            close = 35
        coords = utf[0:close].split("|")

        try:
            # Assume S and W are marked negative unless otherwise
            # shifted.
            pair = "NE"
            if "." in coords[0] and "." in coords[1]:
                lat = float(coords[0])
                lon = float(coords[1])
            elif len(coords)>=4 and coords[1] in "NS" and coords[3][0] in "EW":
                pair = coords[1] + coords[3][0]
                lat = float(coords[0])
                lon = float(coords[2])                                   

            elif len(coords) > 5 and coords[2] in "NS" and coords[5][0] in "EW":
                pair = coords[2] + coords[5][0]                
                lat = float(coords[0]) + float(coords[1])/60
                lon = (float(coords[3]) + float(coords[4])/60)
            elif len(coords) > 7 and coords[3] in "NS" and coords[7][0] in "EW":
                pair = coords[3] + coords[7][0]
                coords = [c if c != '' else '0' for c in coords ]
                lat = float(coords[0]) + float(coords[1])/60 + float(coords[2])/60/60
                lon = (float(coords[4]) + float(coords[5])/60 + float(coords[6])/60/60)
            elif len(coords)==2:
                lat,lon = map(float,coords)
            elif coords[2][:5] in ["scale","regio"]:
                lat,lon = map(float,coords[:2])
            else:
                raise
            return lat_lon_adjust_negatives((lat,lon),pair)
        except:
            #print "BAD COORDS: {} for {}".format(coords,self.title)
            return (None,None)


def lat_lon_adjust_negatives(point,pair):
    point = list(point)
    NS,EW = pair
    if NS == "S":
        point[0] = point[0] * -1
    if EW == "W":
        point[1] = point[1] * -1
    return tuple(point)
