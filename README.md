# Android-Resources
A repo to host some scripts or resources helpful for those developing on android

## String resource converter ##
I created a Python script to assist in populating the appropriate resource folders with the translated strings, read from a csv file.

### How to use ###

#### Creating the CSV file ####
You'll need to store the translated strings in a csv file, where the first row indicates the language/language locale of the resource, and the first column is the resource name. 

The format of the first column is important to determine what type of resource we're adding. 
If it's a String, we prefix "string#", so the ID would be: 
```
string#my_resource_string
```
If it's a Plural with items "one" and "other", we prefix "plural#" and add the item suffix denoted by a "$":
```
plural#my_resource_string$one
plural#my_resource_string$other
```

An example would be:

|         ID         |  English  |  German  | Japanese | Italian |
|--------------------|-----------|----------|----------|---------|
|    string#hello    |   Hello   |   Hallo  | こんにちは |  Ciao   |
|    string#world    |   World   |   Welt   |    世界   |  Mondo  |
| plural#dollar$one  | 1 Dollar  | 1 Dollar |   1ドル   | Dollaro |
| plural#dollar$other| %d Dollars|%d Dollars|   %dドル  | Dollari |

Note that I did a non-exhaustive simple string matching for the language locale, so the easiest way is to either label the column with the name of the language and the locale, or just the raw locale string (e.g. en_US)

The script will then append the strings to the bottom of the appropriate resource files, so in the above case, into values/strings.xml, values-de/strings.xml, values-ja/strings.xml, etc. 

#### Running the script ####
Put the script in the root folder of the project you want to populate strings for, and run the script with the path to the CSV file, e.g. python convertStrings.py ~/path/to/file.csv

If it ran correctly, it will print out the strings read and the file paths it put those strings in.
