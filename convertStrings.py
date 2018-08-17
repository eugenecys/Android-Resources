import os
import sys
import json
import lxml.etree as ET

from csv import reader

class Translation:
    def __init__(self, sId, isPlural):
        self.isPlural = isPlural
        self.id = sId
        self.pluralIds = []
        self.strings = {}
        self.id = ""

    def addString(self, locale, translationString, pluralId = None):
        if self.isPlural and pluralId is None:
            print('Tried to add string "' + pluralId + ': ' + translationString + '" to ' + self.id + ', ignoring.')
            return
        if self.isPlural:
            if pluralId not in self.strings:
                self.strings[pluralId] = {}
                self.pluralIds.append(pluralId)
            self.strings[pluralId][locale] = translationString
        else:
            self.strings[locale] = translationString

    def addStrings(self, locales, strs, pluralId = None):
        print('Adding strings to ' + self.id + ' for ' + str(locales) + ' with strings ' + str(strs))
        if self.isPlural and pluralId is None:
            print('Tried to add strings "' + pluralId + '" to ' + self.id + ', ignoring.')
            return
        if self.isPlural:
            if pluralId not in self.strings:
                self.strings[pluralId] = {}
                self.pluralIds.append(pluralId)
            for i in range(len(locales)):
                self.strings[pluralId][locales[i]] = strs[i]
        else:
            for i in range(len(locales)):
                self.strings[locales[i]] = strs[i]

    def getString(self, locale, pluralId = None):
        if self.isPlural:
            return self.strings[pluralId][locale]
        else:
            return self.strings[locale] 

def main():
    args = sys.argv[1:]
    if not args or len(args) == 0:
        print("No arguments given!")
        return   

    content = getTranslationsContent()
    stringIds, indices, translations = parseTranslationsFile(content)
    locales = [getLocale(s) for s in indices]
    xmlDir = findXmlDir()
    if not xmlDir:
        print('Unable to find resource folder. Please place in root folder of Android project')
    writeToFiles(xmlDir, indices, stringIds, translations)


def parseTranslationsFile(content):
    lineCount = 0
    translations = {}
    ids = []
    for line in content:
    	if lineCount == 0:
            localeIndices = [getLocale(localeSt) for localeSt in scrubStrings(line[1:])]
            lineCount+=1
        else:

            strings = scrubStrings(line)
            xid = getId(strings[0])
            pId = None
            if isPlural(strings[0]):
                pId = getPluralId(strings[0])

            if xid not in translations:
                translations[xid] = Translation(xid, isPlural(strings[0]))

            translations[xid].addStrings(localeIndices, strings[1:], pId)
            if xid not in ids:
                ids.append(xid)
            

    return ids, localeIndices, translations
    

def getId(string):
    if '#' in string:
        strings = string.split('#')
        string = strings[len(strings) - 1]
        if '$' in string:
            return string.split('$')[0]
        return string
    return string

def isPlural(string):
    return 'plural' in string

def getPluralId(string):
    if '$' in string:
        strings = string.split('$')
        return strings[len(strings) - 1]
    return None



def getTranslationsContent():
    args = sys.argv[1:]
    if not args or len(args) == 0:
        return None
    try:
        result = []
        with open(args[0], 'rt') as csv_file:
            csvReader = reader(csv_file, delimiter=',')
            for line in csvReader:
 	          result.append(line)
            csv_file.close()
        return result
    except:
        print("Unable to open translations file")
        return
    
def scrubStrings(strings):
    for i in range(len(strings)):
        strings[i] = strings[i].rstrip()
    return strings

def getLocale(localeLanguage):
    loc = localeLanguage.lower()
    if 'french' in loc or 'fr' in loc:
        if 'canada' in loc or 'ca' in loc:
    	    return 'fr-rCA'
	return 'fr'
    if 'mx' in loc or 'mex' in loc:
    	return 'es-rMX'
    if 'jp' in loc or 'jap' in loc:
        return 'ja'
    if 'de' in loc or 'ger' in loc:
        return 'de'
    if 'es' in loc or 'spa' in loc:
        return 'es'
    if 'it' in loc:
        return 'it'
    if 'en' in loc:
	if 'ca' in loc:
	    return 'en-rCA'
        return ''

def findXmlDir():
    dirs = [d for d in os.listdir('.') if os.path.isdir(os.path.join('.',d))]
    if 'src' in dirs:
        return 'src/main/res/values'
    if 'res' in dirs:
        return 'res/values'
    if 'values' in dirs:
        return 'values'
    if 'main' in dirs:
        return 'main/res/values'
    return None


def writeToFiles(xmlDir, localeIndices, stringIds, translations):
    for index in localeIndices:
        locale = getLocale(index)
        path = xmlDir

    	if locale:
    	    path = xmlDir + '-' + locale
            path += '/strings.xml'

    	if not os.path.exists(os.path.dirname(path)):
    	    try:
                os.makedirs(os.path.dirname(path))
    	    except:
                print('Unable to create directory for ' + path)
	

        writeToFile(path, locale, stringIds, translations)

	
def writeToFile(path, locale, stringIds, translations):
    #parser = ET.XMLParser(remove_blank_text = True)
    tree = ET.parse(path)
    root = tree.getroot()
    ids = {}
    lastItemLine = 0
    
    # Replace all existing strings with those in the translations object, if any
    for item in root:
        if 'name' not in item.attrib:
            continue
        ids[item.get('name')] = item
        lastItemLine = item.sourceline

    # We start appending the xmls below the last item in the xml
    lastItemLine += 1


    for sId in stringIds:
        print(locale + ': ' + sId)
        translation = translations[sId]
        if sId in ids:
            node = ids[sId]
            if (node.tag == 'plurals') != translation.isPlural:
                print('ERROR: ' + sId + ' is node type ' + node.tag + ' while translation isPlural = ' + str(translation.isPlural))
                return
        else:
            node = ET.Element('plurals' if translation.isPlural else 'string', name = sId)
            node.sourceline = lastItemLine
            lastItemLine += 1
            node.tail = '\n    '
            root.append(node)


        if node.tag == 'string':
            if node.text:
                print('String id "' + sId + '":' + node.text + ' already exists in ' + path + ', replacing it with ' + translation.getString(locale))
            node.text = translation.getString(locale).decode("utf-8")
        else:
            pluralElements = node.findall('./item')
            plurals = {}
            for pluralItem in pluralElements:
                pluralId = pluralItem.get('quantity')
                plurals[pluralId] = pluralItem

            for pluralId in translation.pluralIds:
                if pluralId in plurals:
                    pluralItem = plurals[pluralId]
                else:
                    pluralItem = ET.Element("item", quantity = pluralId)
                    pluralItem.tail = '\n        '
                    node.append(pluralItem)
                
                if pluralItem.text:
                    print('String id "' + sId + '$' + pluralId + '":' + pluralItem.text + ' already exists in ' + path + ', replacing it with ' + translation.getString(locale, pluralId))                    

                pluralItem.text = translation.getString(locale, pluralId).decode("utf-8")

    for item in root:
        if 'name' in item.attrib:
            if not item.tail == '\n':
                item.tail = '\n    '


    tree = ET.ElementTree(root)
    tree.write(path, encoding = "UTF-8", pretty_print = True, xml_declaration = True)


def getCurrentTranslations(path):
    if not os.path.exists(os.path.dirname(path)):
        return []

def escapeString(string):
    return string.replace("'", r"\'").replace('"', r'\"')


main()
