# Understanding The MTG Standard Metagame
In this project I did a full analysis of the Magic the Gathering standard metagame.  
All my code for scraping and graph creation can be found [here](secondus.py)  
My presentation on my discoveries can be found [here](https://github.com/Connor205/The-MTG-Standard-Metagame/blob/main/Secondus%20Presentation%20PDF.pdf)  
This project was completed in early 2019.  
# Project Description
I scraped MTG golffish in order to gather data on the types of decks and popular cards that are currently being played within standard. Once I got the card names I analyzed them using an MTG card API in order to collect data on the cards such as type, set and basically any information I could possibly need. I then combined all of the data from the different decks and sorted the cards by the set that they came from then I counted the amount of differnt card types that had been produced and weighting the amount that each card counted by the quantity that the orignial deck contained. It also saveds all of the decks with extra information to a folder and loads them in in order to increase the speed of the program. I also parse the wiki pages from the rules page postd and maintaineed by Wizards of the Coast in order to get the current sets in standard. The program is also future proof, which was a majority struggles I had with the project.


