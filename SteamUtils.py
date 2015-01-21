################################################################################
# Imports
################################################################################
from HTMLParser import HTMLParser
import urllib2
import sys

################################################################################
# TagParser
# Custom HTMLParser for obtaining tags from a steam store app page 
################################################################################
class TagParser(HTMLParser):
	def __init__(self, givenID):
		HTMLParser.__init__(self)
		self.appID = givenID
		self.inTagClass = False
		self.nestedDivs = 0
		self.inTagElement = False
		self.nestedLinks = 0
		self.tags = []

	def handle_starttag(self, tag, attrs):
		if tag == "div":
			# Check if this div has the class and appID we're expecting
			classFound = False
			appIDFound = False
			for name, value in attrs:
				if name == "class" and value == "glance_tags popular_tags":
					classFound = True
				if name == "data-appid" and value == str(self.appID):
					appIDFound = True

			if classFound and appIDFound:
				self.inTagClass = True

			if self.inTagClass:
				self.nestedDivs += 1

		if self.inTagClass and tag == "a":
			for name, value in attrs:
				if name == "class" and value == "app_tag":
					self.inTagElement = True

			if self.inTagElement:
				self.nestedLinks += 1

	def handle_endtag(self, tag):
		if tag == "div":
			if self.inTagClass:
				self.nestedDivs -= 1
				if self.nestedDivs == 0:
					self.inTagClass = False

		if tag == "a":
			if self.inTagElement:
				self.nestedLinks -= 1
				if self.nestedLinks == 0:
					self.inTagElement = False

	def handle_data(self, data):
		if self.inTagElement:
			strippedData = data.strip()
			self.tags.append(strippedData)

	def getTags(self):
		return self.tags


################################################################################
# error
# Report and react to an error
################################################################################
def error(message):
	print(message)
	sys.exit()

################################################################################
# getTagsForGame
# Get the list of tags that appear in a games product page on the steam store
################################################################################
def getTagsForGame(appID):
	url = "http://store.steampowered.com/app/" + str(appID)
	response = urllib2.urlopen(url)
	
	if response.geturl() != url:
		error("Retrieved unexpected resource")

	html = response.read()
	parser = TagParser(appID)
	parser.feed(html)

	tags = parser.getTags()
	return tags

################################################################################
# main
################################################################################
if __name__ == "__main__":
	idStr = raw_input("App ID > ")
	idInt = int(idStr)
	tags =  getTagsForGame(idInt)
	print("App %d has the following tags:" % (idInt))
	for tag in tags:
		print("%s," % (tag)),