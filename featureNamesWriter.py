"""
Copyright (c) 2015 Adobe Systems Incorporated. All rights reserved.

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""


import os
import sys

kLanguageFolderName = "localefiles"
kFeaturesFolderName = "feafiles"
kStylisticSetsTotal = 20

"""
index: name in English
value: tuple of
		- Windows language ID (https://www.microsoft.com/typography/otspec/name.htm)
		- language tag conforming to IETF specification BCP 47 (http://en.wikipedia.org/wiki/List_of_ISO_639-1_codes)
"""
languagesDict = {
	"Chinese S"  : ("0804", "zh-CN"),
	"Chinese T"  : ("0404", "zh-TW"),
	"Czech"      : ("0405", "cs"),
	"Danish"     : ("0406", "da"),
	"Dutch"      : ("0413", "nl"),
	"English GB" : ("0809", "en"),
	"English US" : ("0409", "en"),
	"Finnish"    : ("040B", "fi"),
	"French CA"  : ("0C0C", "fr"),
	"French FR"  : ("040C", "fr"),
	"German"     : ("0407", "de"),
	"Greek"      : ("0408", "el"),
	"Hindi"      : ("0439", "hi"),
	"Hungarian"  : ("040E", "hu"),
	"Italian"    : ("0410", "it"),
	"Japanese"   : ("0411", "ja"),
	"Korean"     : ("0412", "ko"),
	"Malayalam"  : ("044C", "ml"),
	"Marathi"    : ("044E", "mr"),
	"Norwegian"  : ("0414", "nb"),
	"Polish"     : ("0415", "pl"),
	"Portuguese" : ("0416", "pt"),
	"Russian"    : ("0419", "ru"),
	"Spanish ES" : ("040A", "es"),
	"Spanish MX" : ("080A", "es"),
	"Swedish"    : ("041D", "sv"),
	"Turkish"    : ("041F", "tr"),
	"Ukrainian"  : ("0422", "uk"),
}


def readFile(filePath):
	file = open(filePath, 'r')
	fileContent = file.read().splitlines()
	file.close()
	return fileContent


def writeFile(filePath, contentsList):
	file = open(filePath, 'w')
	file.writelines([x + os.linesep for x in contentsList])
	file.close()


def writefeatureNamesFiles(languageFilesContentsDict, parentDir):
	languagesList = languagesDict.keys()
	languagesList.sort()
	
	for index in range(kStylisticSetsTotal):
		ssFileName = "featureNamesSS%02d.fea" % (index + 1)
		ssFilePath = os.path.join(parentDir, kFeaturesFolderName, ssFileName)
	
		outputList = ["featureNames {"]
		
		for language in languagesList:
			outputList.append("\t# %s" % language)
			languageID = languagesDict[language][0]
			languageTag = languagesDict[language][1]
			rawLocalizedString = languageFilesContentsDict[languageTag][index]
			unicodeLocalizedString = rawLocalizedString.decode('utf8')
			asciiLocalizedString = ""
			macromanLocalizedString = ""
			
			for uniChar in unicodeLocalizedString:
				charInt = ord(uniChar)
				if charInt < 128:
					asciiLocalizedString += chr(charInt)
					macromanLocalizedString += chr(charInt)
				else:
					asciiLocalizedString += "\\%04X" % charInt
					try:
						macromanChar = uniChar.encode('macroman')
						macromanLocalizedString += "\\%X" % ord(macromanChar)
					except UnicodeEncodeError:
						pass
			
			# add the Mac name for English. Makeotfexe requires at least one Mac name, otherwise it won't compile the features
			if language == "English US":
				outputList.append('''\tname 1 0 0 "%s";''' % macromanLocalizedString)
			
			outputList.append('''\tname 3 1 0x%s "%s";\n''' % (languageID, asciiLocalizedString))
		
		outputList.append("};")
		writeFile(ssFilePath, outputList)


def processLanguageFiles(parentDir):
	languageFilesContentsDict = {}
	
	for language in languagesDict:
		languageCode = languagesDict[language][1]
		
		# skip processing the same file more than once (some locales share the same file)
		if languageCode in languageFilesContentsDict:
			continue
		
		langFilePath = os.path.join(parentDir, kLanguageFolderName, languageCode + ".txt")
		
		if os.path.isfile(langFilePath):
			fileContentList = readFile(langFilePath)
		else:
			print >> sys.stderr, "ERROR: The %s language file could not be found." % language
			continue
		
		if len(fileContentList) == kStylisticSetsTotal:
			languageFilesContentsDict[languageCode] = fileContentList
		else:
			print >> sys.stderr, "ERROR: The %s file (%s.txt) does not have %s lines." % (language, languageCode, kStylisticSetsTotal)
			continue
	
	return languageFilesContentsDict


def run():
	parentDir = os.path.dirname(os.path.abspath(__file__))
	
	languageFilesContentsDict = processLanguageFiles(parentDir)
	
	if languageFilesContentsDict:
		writefeatureNamesFiles(languageFilesContentsDict, parentDir)
	
	print "Done!"

if __name__ == "__main__":
	run()
