#!/bin/python3

######################################################################
# Developer :     Ayush Bairagi
# E-mail:         abairagi311@gmail.com
# Github profile: github.com/ayush3298
# project:
# ####################################################################

# Internal
import sys, os
import functools

# External
import requests
from PyQt5.QtWidgets import QMessageBox

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QFont

# UI Files
from mainUI import Ui_MainWindow

# Main GUI window, uses 'main.ui'
class MainWindow(Ui_MainWindow):
    
    # UI init
    def __init__(self, dialog):
        Ui_MainWindow.__init__(self)

        self.setupUi(dialog)



        # Article scroll area init
        self.articleList = []
        self.articleGBox, self.articleGLayout = self.InitArticleScrollarea()

        # Sources scroll area init
        self.sourceList = []
        self.sourceGBox, self.sourceGLayout = self.InitSourceScrollarea()
        self.currentSourceId = ""

        # Following scroll area init
        self.followingList = []
        self.followingGBox, self.followingGLayout = self.InitFollowScrollarea()
        self.LoadFollowed()

        # Get the all avaliable sources
        self.InsertSources(jsonRes=self.LoadSources(sourcesUrl="https://newsapi.org/v1/sources?language=en").json())

        # Get apikey
        
        self.apiKey = self.GetApiKey('api.txt')



        # Event handler init
        self.MainPage()
        self.InputManager()

    # Handles all GUI events on MainWindow static widget static widgetss
    def InputManager(self):
        # Refresh button
        self.refreshBtn.clicked.connect(self.ReloadArticles)
        
        # Changed category
        self.categoryCombobox.currentIndexChanged.connect(self.SelectionChange)

        # Follow button
        self.followBtn.clicked.connect(self.FollowCurrent)

        self.btnSearch.clicked.connect(self.SearchNews)


    def SearchNews(self):
        self.InsertArticles(jsonRes=self.LoadArticlesBy(
            apiUrl="https://newsapi.org/v2/everything?q={}&sortBy=publishedAt&language=en".format(self.txtSearch.text()),
            source='',
            apiKey=self.apiKey
        ).json())




    # Reload all articles from the current source
    def MainPage(self):
        self.InsertArticles(jsonRes=self.LoadArticlesBy(
            apiUrl="https://newsapi.org/v2/top-headlines?country=in",
            source='',
            apiKey=self.apiKey
        ).json())
    def ReloadArticles(self):
        if (len(self.currentSourceId) > 0):
            self.InsertArticles(jsonRes=self.LoadArticlesBy(
                apiUrl="https://newsapi.org/v1/articles",
                source=self.currentSourceId,
                apiKey=self.apiKey
            ).json())

    # Changed category from the combobox, display the sources from the selected category
    def SelectionChange(self):
        if (self.categoryCombobox.currentText() == "all"):
            self.InsertSources(jsonRes=self.LoadSources(sourcesUrl="https://newsapi.org/v1/sources?language=en").json())
        else:
            self.InsertArticles(jsonRes=self.LoadArticlesBy(
                apiUrl="https://newsapi.org/v2/top-headlines?country=us&category={}".format(self.categoryCombobox.currentText()),
                source='',
                apiKey=self.apiKey).json())
            self.InsertSources(jsonRes=self.LoadSources(sourcesUrl="https://newsapi.org/v1/sources?language=en&category=" + self.categoryCombobox.currentText()).json())

    # Appends the currently selected source to the following list
    def FollowCurrent(self):
        if (len(self.currentSourceId) > 0):
            if (self.currentSourceId not in self.followingList):
                self.followingList.append(self.currentSourceId)
                self.followBtn.setText("Unfollow")
                self.UpdateFollowed()
            elif (self.currentSourceId in self.followingList):
                self.followingList.remove(self.currentSourceId)
                self.followBtn.setText("Follow")
                self.UpdateFollowedRemoved()
            self.SaveFollowed() # Save each time

    # Creates the elements needed to propperly append widgets to the articles scrollarea
    def InitArticleScrollarea(self):
        # Create groupbox container
        gBox = QtWidgets.QGroupBox()
        gLayout = QtWidgets.QFormLayout()

        # Append articles scroll
        gBox.setLayout(gLayout)
        self.articleScroll.setWidget(gBox) # Append groupbox to scrollarea
        return gBox, gLayout # Return them back out the global variables, so they can be used in the UpdateScrollarea function as well.

    # Creates the elements needed to propperly append widgets to the sources scrollarea
    def InitSourceScrollarea(self):
        # Create groupbox container
        gBox  = QtWidgets.QGroupBox()
        gLayout = QtWidgets.QFormLayout()

        # Append to sources scroll
        gBox.setLayout(gLayout)
        self.sourcesScroll.setWidget(gBox)
        return gBox, gLayout # Return back just like for the articles

    # Creates the elements needed to propperly append widgets to the followed scrollarea
    def InitFollowScrollarea(self):
        # Create groupbox container
        gBox = QtWidgets.QGroupBox()
        gLayout = QtWidgets.QFormLayout()

        # Append to followed scroll
        gBox.setLayout(gLayout)
        self.followScroll.setWidget(gBox)
        return gBox, gLayout # Return references back out to global variables

    # Loads all the followed sources from a file
    def LoadFollowed(self):
        try:
            with open("followed.txt", "r") as loadFile:
                for line in loadFile:
                    self.currentSourceId = line.replace("\n", "")
                    self.followingList.append(self.currentSourceId)
                    self.UpdateFollowed()
        except Exception as e:
            pass

    # Saves the list of all followed sources to a file
    def SaveFollowed(self):
        with open("followed.txt", "w") as saveFile:
            for source in self.followingList:
                saveFile.write(source + "\n")

    # Inserts the last followed source which was appended to the self.follwingList
    def UpdateFollowed(self):
        followLabel = QtWidgets.QLabel()

        followLabel.mousePressEvent = functools.partial(self.SourceClicked, source_obj=followLabel)
        followLabel.setText("<a href='#'>" + self.currentSourceId + "</a>") 

        horiLayout = QtWidgets.QHBoxLayout()
        horiLayout.addWidget(followLabel)

        self.followingGLayout.addRow(horiLayout)

    # Finds and deletes the currentSourceId when the unfollow button is clicked
    def UpdateFollowedRemoved(self):
        for x in reversed(range(self.followingGLayout.count())):
            # Get element to delete
            currentElemText = self.followingGLayout.itemAt(x).itemAt(0).widget().text()
            if (currentElemText[12:len(currentElemText) - 4] == self.currentSourceId):
                # Remove QLabel from inner horiLayout
                take = self.followingGLayout.itemAt(x).takeAt(0).widget()
                take.deleteLater()

                # Remove horiLayout form followingGLayout
                takeLayout = self.followingGLayout.takeAt(x)
                takeLayout.deleteLater()

                # Break when found
                break

    # This can be done in a way better way, than to generate the entire formlay out each time and append each label
    def UpdateScrollarea(self):
        for item in self.articleList[len(self.articleList) - 1]:
            horiLayout = QtWidgets.QHBoxLayout()
            horiLayout.addWidget(item)

            self.articleGLayout.addRow(horiLayout)

    # Displays an information messagebox with the given title and text
    def DisplayMessagebox(self, title, text): 
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText(text)
        msg.setWindowTitle(title)
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.exec_()

    # Gets the apikey from the specifed file
    # The key should be on the first line of the file
    def GetApiKey(self, fileName):
        try:
            with open(fileName, "r") as keyFile:
                return keyFile.read()
        except Exception as e:
            self.DisplayMessagebox("Warning", "This application requires an api key to function!\nPlease go to: https://www.newsapi.org/ to get your key.\nThis key needs to be placed in a file called 'apikey.txt'.")
            return None

    # Loads the articles using requests
    def LoadArticlesBy(self, apiUrl, source, apiKey):
        payload = {'source': source, 'apiKey': apiKey}
        res = requests.get(apiUrl, params=payload)
        
        # Check status code
        if (res.status_code == 200):
            return res
        return None

    # Opens the clicked on label link
    def OpenLink(self, linkStr):
        QtGui.QDesktopServices.openUrl(QtCore.QUrl(linkStr))

    # Loads a given json  object containing articles onto the GUI
    def InsertArticles(self, jsonRes):
        # Clear from previous
        self.articleList = []
        for idx in reversed(range(self.articleGLayout.rowCount())):
            self.articleGLayout.removeRow(idx)


        # Insert new articles
        for article in jsonRes['articles']:
            readmoreLabel = QtWidgets.QLabel("<a href='" + article['url']  + "'>Read more.</a>")
            readmoreLabel.linkActivated.connect(self.OpenLink)
            font = QtGui.QFont()
            # font.setPointSize(12)
            font.setBold(True)
            # font.setWeight(75)

            if article['author'] is not None:
                try:
                    self.articleList.append([
                        # QtWidgets.QLabel('Source: ' + article['source']['name']),

                    ])
                except:pass
                try:

                    autherr=QtWidgets.QLabel('Author: '+article['author'])
            # Create articleList, this is the list where all elements are loaded from
                    self.articleList.append([
                        #QtWidgets.QLabel('Source: ' + article['source']['name']),
                        autherr,
                        QtWidgets.QLabel('Title: '+article['title']),
                        QtWidgets.QLabel(str('Published At: '+article['publishedAt'])[:24]),
                        QtWidgets.QLabel(article['description']),
                        readmoreLabel,
                        QtWidgets.QLabel('-'*160),
                        QtWidgets.QLabel()
                        ])
                    self.UpdateScrollarea()
                except:pass

    # Insert sources using the sourceList
    def UpdateSourcesScrollarea(self):
        horiLayout = QtWidgets.QHBoxLayout()
        horiLayout.addWidget(self.sourceList[len(self.sourceList) - 1])

        self.sourceGLayout.addRow(horiLayout)

    def GetImage(self,url):
        d = requests.get(url).read()

        return d

    # Loads all sources from the given URL, returns a respons object (None if status_code != 200)
    def LoadSources(self, sourcesUrl):
        res = requests.get(sourcesUrl)
        if (res.status_code == 200):
            return res
        return None

    # Source link clicked event - load the latest articles from the source
    def SourceClicked(self, event, source_obj=None):
        # Get source name
        sourceNameText = source_obj.text()
        sourceName = sourceNameText[12:len(sourceNameText) - 4]
        
        # Set label
        self.articleByLabel.setText("Articles by: " + sourceName)

        # Get and insert the articles from the clicked source
        sourceId = sourceName.lower()
        for ch in ['(', ')']:
            sourceId = sourceId.replace(ch, "")
        sourceId = sourceId.replace(" ", "-") 
        self.currentSourceId = sourceId

        # Set follow button text based on current source
        if (self.currentSourceId in self.followingList):
            self.followBtn.setText("Unfollow")
        else:
            self.followBtn.setText("Follow")

        self.InsertArticles(jsonRes=self.LoadArticlesBy(
            apiUrl="https://newsapi.org/v1/articles",
            source=sourceId,
            apiKey=self.apiKey
        ).json())

    # Inserts all sources from a given json object into the sources scroll area
    def InsertSources(self, jsonRes):
        # Clear from previous
        for idx in reversed(range(self.sourceGLayout.rowCount())):
            self.sourceGLayout.removeRow(idx)

        for source in jsonRes['sources']:
            label = QtWidgets.QLabel()
            # Makes the labels clickable links
            label.mousePressEvent = functools.partial(self.SourceClicked, source_obj=label)
            label.setText("<a href='#'>" + source['name'] + "</a>") 

            self.sourceList.append(label)
            self.UpdateSourcesScrollarea()

# Init
if __name__ == '__main__':

    # Init main GUI
    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QMainWindow()
    window.setWindowTitle('News')
    window.setWindowIcon(QtGui.QIcon('logo.png'))
    prog = MainWindow(window)
    # try:
    #     requests.get('https://www.google.com')
    #     print('google')
    # except:
    #     self.DisplayMessagebox(title='Cant Connect',text='please check your internet connection')
    #     exit()

    window.show()  # Actually show the window
    sys.exit(app.exec_())



