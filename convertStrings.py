import os
import sys
import json

from csv import reader

def main():
    args = sys.argv[1:]
    if not args or len(args) == 0:
        print("No arguments given!")
        return   

    translationsFile = getTranslationsFile()
    stringIds, indices, translations = parseTranslationsFile(translationsFile)
    locales = [getLocale(s) for s in indices]
    dir = findXmlDir()
    if not dir:
        print('Unable to find resource folder. Please place in root folder of Android project')
    writeToFiles(dir, indices, stringIds, translations)

def parseTranslationsFile(file):
    lineCount = 0
    translations = {}
    ids = []
    for line in file:
    	if lineCount == 0:
            localeIndices = scrubStrings(line[1:])
            for locale in localeIndices:
                translations[locale] = {}
	    lineCount+=1
	else:
            strings = scrubStrings(line)
            id = strings[0]
	    ids.append(id)
            strings = strings[1:]
            for i in range(len(localeIndices)):
                translations[localeIndices[i]][id] = strings[i]
    return ids, localeIndices, translations

def getTranslationsFile():
    args = sys.argv[1:]
    if not args or len(args) == 0:
        return None
    try:
        result = []
        with open(args[0], 'r') as csv_file:
            csvReader = reader(csv_file)
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


def writeToFiles(dir, indices, stringIds, translations):
    for index in indices:
	locale = getLocale(index)
	path = dir

	if locale:
	    path = dir + '-' + locale
        path += '/strings.xml'
	if not os.path.exists(os.path.dirname(path)):
	    try:
		os.makedirs(os.path.dirname(path))
	    except:
		print('Unable to create directory for ' + path)
	f = open(path, 'a+')
	print ("Writing " + index + " translations to " + path)
	f.write('\n\n\n')
	
	strings = translations[index]
	for id in stringIds:
	    resourceString = escapeString(strings[id])
	    f.write('<string name="' + id + '">' + resourceString + '</string>\n')

	f.close()
	
def escapeString(string):
    return string.replace("'", r"\'").replace('"', r'\"')


main()
