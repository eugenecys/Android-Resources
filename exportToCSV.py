import os
import csv
import xml.etree.ElementTree as ET
import string
import xml.etree.cElementTree as ET
from xml import etree
from xml.etree import ElementTree
import csv
from collections import OrderedDict
import sys

class CommentedTreeBuilder(ElementTree.TreeBuilder):
    def __init__(self, *args, **kwargs):
        super(CommentedTreeBuilder, self).__init__(*args, **kwargs)

    def comment(self, data):
        self.start(ElementTree.Comment, {})
        self.data(data)
        self.end(ElementTree.Comment)




def parseXML(xmlfile):
    parser = ET.XMLParser(target=CommentedTreeBuilder())

    # create element tree object
    tree = ET.parse(xmlfile, parser)

    # get root element
    root = tree.getroot()
    ##
    # 1#string#dmusic_download_goto_music_settings
    # 2#plural#dmusic_artist_confirm_delete_cloud_msg#one
    # 3#plural#dmusic_artist_confirm_delete_cloud_msg#other
    # 4#plural#dmusic_genre_confirm_delete_cloud_msg#one
    # 5#plural#dmusic_genre_confirm_delete_cloud_msg#other
    ##
    # create dictionary for string items
    stringArr = []
    #translatable
    stringItems = OrderedDict()
    # iterate news items
    for item in root:
        if (item.tag == 'string'):
            stringItems['string#'+item.attrib['name']] = getEncodedValue(item.text);
            #try:
            #    stringItems['translatable'] = item.attrib['translatable'];
            #except KeyError, e:
            #    stringItems['translatable'] = True;
        else:
            pluralElements = item.findall('./item')
            #print 'plurals'
            for pluralItem in pluralElements:
                    stringItems['plural#'+item.attrib['name']+"$"+pluralItem.attrib['quantity']] = pluralItem.text;
                    #try:
                    #    stringItems['translatable'] = pluralItem.attrib['translatable'];
                    #except KeyError, e:
                    #    stringItems['translatable'] = True;
    # return dictionary
    #print stringItems
    return stringItems

def getEncodedValue(valueStr):
    return valueStr




def saveArrToCSV(strArr, localeArr, outputfile):
    # open a file for writing
    with open(outputfile, 'w') as csv_file:
        # create the csv writer object
        csvwriter = csv.writer(csv_file)

        resident_head = []
        NoneType = type(None)

        #Write the HeaderBar
        resident = []
        i=0;
        resident_head.append('KEY')
        while i<len(localeArr):
            resident_head.append(localeArr[i])
            i=i+1
        csvwriter.writerow(resident_head)

        sourceDict = strArr[0]['items']
        for key,values in sourceDict.items():
            resident = []
            resident.append(key)
            if values == None:
                resident.append("")
            else:
                resident.append(values.encode('utf-8'))
            i=1;
            while i<len(strArr):
                otherValue = strArr[i]['items'].get(key,"")
                if(otherValue == None):
                    resident.append("")
                else:
                    resident.append(otherValue.encode('utf-8'))
                i +=1
            csvwriter.writerow(resident)
        csv_file.close()


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


def main():
    reload(sys)  
    sys.setdefaultencoding('utf-8')
    outputfile = "translations_file.csv"
    # parse xml file
    translations = {};
    xmlDir = findXmlDir()
    inputData = {'US': xmlDir + '/strings.xml', 'en-CA': xmlDir + '-en-rCA/strings.xml', 'fr-CA': xmlDir + '-fr-rCA/strings.xml'}

    for key,values in inputData.items():
        stringItems = parseXML(values)
        tempDict = {}
        tempDict['locale'] = key;
        tempDict['items'] = stringItems;
        translations[len(stringItems)] = tempDict

    translationsArr = [ ]
    localeArr=[]
    for key in sorted(translations.iterkeys(), reverse = True):
        translationsArr.append(translations[key])
        print translations[key]['locale']," - ",len(translations[key]['items'])
        localeArr.append(translations[key]['locale'])


    saveArrToCSV(translationsArr, localeArr, outputfile)


if __name__ == "__main__":
    # calling main function
    main()
