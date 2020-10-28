import requests
import re
import json
import pickle
from urllib.request import urlopen
from bs4 import BeautifulSoup
from mtgsdk import Card
import pandas as pd
import csv
from tqdm import tqdm
import matplotlib.pyplot as plt
import numpy as np
__author__ = "Connor Nelson"
"""
Project Secondus
I scraped MTG golffish in order to gather data on the types of decks and popular
cards that are currently being played within standard. Once I got the card names
I analyzed them using an MTG card API in order to collect data on the cards such
as type, set and basically any information I could possibly need. I then combined all
of the data from the different decks and sorted the cards by the set that they came from
then I counted the amount of differnt card types that had been produced and weighting the amount
that each card counted by the quantity that the orignial deck contained. It also saveds all of the
decks with extra information to a folder and loads them in in order to increase the speed of the program.
I also parse the wiki pages from the rules page postd and maintaineed by Wizards of the Coast in order
to get the current sets in standard. The program is also future proof, which was a majority struggles I had with the project.
"""


main_page_url = "https://www.mtggoldfish.com/"
standard_meta_url = "https://www.mtggoldfish.com/metagame/standard#paper"
standard_set_info_url = "https://mtg.gamepedia.com/Standard"

def get_deck_url_list(url):
	"""
	Simply gets a list of the links to the top 12 decks on the page that displays them from MTG Goldfish
	"""
	meta_page = urlopen(url)
	#print(standard_meta_page.text)
	page_object = BeautifulSoup(meta_page, "html.parser")
	test = page_object.find("div", {"class" : "clearfix"})
	object_list = page_object.findAll("div", {"class" : "archetype-tile-description"})
	link_list = []
	for i in object_list:
		link = i.findAll("a")
		link_list.append(main_page_url + link[1]["href"])
		return link_list

"""
Starts the creation of the card dictionary by adding keys for each card and the value has a dictionary with
the quanity equal to the quantity parsed from the deck page.
"""
def get_card_dict(url):

	deck_page = urlopen(url)
	page_object = BeautifulSoup(deck_page, "html.parser")
	card_object_list = page_object.find("div", {"class" : "tab-pane", "id" : "tab-paper"}).findAll("td", {"class" : "deck-col-card"})
	card_list = []
	quantity_list =[]
	get_num = re.compile("\d+")
	for i in card_object_list:
		card = i.find("a").text
		card_list.append(card)
		quanitity_object_list = page_object.find("div", {"class" : "tab-pane", "id" : "tab-paper"}).findAll("td", {"class" : "deck-col-qty"})
		for i in quanitity_object_list:
			quantity_list.append(int(get_num.search(i.text).group(0)))
	# print(len(quantity_list))
	# print(len(card_list))
	card_dict = {}
	for i in range(len(quantity_list)):
		card_dict[card_list[i]] = {"quantity" : quantity_list[i]}
		return card_dict
"""
Uses the MTG Card API to get data on a cat with a name. Returns a dictionary with all of the data on the card.
"""
def get_card_info(card_name):
	if "//" in card_name: # Deals with dual cards and changes the name in order for the card to be searched for.
		card_name = card_name[0:card_name.index("/") - 1]
	card = requests.get("https://api.magicthegathering.io/v1/cards" , params = {"name" : card_name}).text
	return json.loads(card)["cards"][0]

"""
This method goes to the page given(url) and gets the name of the deck
is being displayed by that webpage
"""
def get_deck_name(url, index):

	get_name_1 = re.compile(".+(?=\s\sSuggest)")
	get_name_2 = re.compile(".+(?=\sby)")
	deck_page = urlopen(url)
	page_object = BeautifulSoup(deck_page, "html.parser")
	name = page_object.find("h2", {"class" : "deck-view-title"}).text
	if index < 12:
		return get_name_1.search(name).group(0)
		return get_name_2.search(name).group(0)
"""
Turns the csv that are saved on computer in to dictionary containing the names
of the decks as the keys and a dictionary of the cards in each deck as the value.
"""
def import_csv_dict():

	csv_dict = {}
	name_list = get_name_list()
	for i in name_list:
		df = pd.read_csv("Data/" + i + '.csv')
		csv_dict[i] = df
		return csv_dict
"""
Loads the name list from file
"""
def get_name_list():

	with open("Data/names.pkl", "rb") as fp:
		name_list = pickle.load(fp)
		return name_list
"""
Redownloads all of the data from goldfish and gets the data from the api
autosaves all of the new csv files to a folders as well as it
overwrites previous ones in order to update.
Also gets the names from the dekcs that it is saving and saves that to a text
file for later use
"""
def get_data_from_goldfish():

	deck_link_list = get_deck_url_list(standard_meta_url)
	for i in tqdm(range(12)):
		# if i == 0:
		# 	print("Top Decks")
		# if i == 12:
		# 	print("Budget Decks:")
		name = get_deck_name(deck_link_list[i], i)
		# print(name)
		cards_dict = get_card_dict(deck_link_list[i])
		for k in cards_dict.keys():
			indvid_card_dict = get_card_info(k)
			indvid_card_dict["Deck"] = name
			for j in indvid_card_dict:
				cards_dict[k][j] = indvid_card_dict[j]
		# print(cards_dict)
		pd.DataFrame.from_dict(cards_dict, orient='index').to_csv("Data/" + name + ".csv")
		name_list = []
		for i in tqdm(range(12)):
			name = get_deck_name(deck_link_list[i], i)
			name_list.append(name)
			print(name_list)
			with open("Data/names.pkl", "wb") as fp:
				pickle.dump(name_list, fp)
"""
Goes to the MTG rules page and scrapes it for all of the current legal sets.
Was more difficult than anticipated because it displayed the future sets and current sets in the same table.
Making this work in any senerio with any number of legal standard sets had me isolating each element in order
to find the break in the table and then taking only the sets before it
"""
def get_legal_sets():
	page = urlopen(standard_set_info_url)
	page_object = BeautifulSoup(page, "html.parser")
	object_list = page_object.find("table", {'class' : 'wikitable'}).findAll('td')
	# print(object_list)
	for i in range(len(object_list)):
		object_list[i] = object_list[i].text
		# print(object_list[i])
	object_list.remove('Autumn 2021\n')
	break_index = object_list.index("Autumn 2022\n")
	object_list = object_list[0:break_index]
	set_list = [x for x in object_list if x !='']
	for i in range(len(set_list)):
		set_list[i] = set_list[i].rstrip()
	return set_list

"""
Uses the dictionary of CSVs to create a massive csv with all of the cards from the decks.
Then uses that in oder to create a dictionary with the number of creature, spell and enchantments cards
from each set and stores the information inside of a dictionary. Returns that dictionary.
"""
def get_data_dict():
	set_list = get_legal_sets()
	csv_dict = import_csv_dict()
	name_list = get_name_list()
	full_csv = pd.concat(list(csv_dict.values()), sort=False)
	set_info = {}
	for i in set_list:
		print(i)
		data_dict = {}
		set_cards = full_csv.loc[full_csv['setName'] == i]
		creature_cards = set_cards.loc[set_cards['types'] == "['Creature']"]
		spell_cards = set_cards.loc[set_cards['types'].isin(["['Sorcery']", "['Instant']"])]
		enchantment_cards = set_cards.loc[set_cards['types'] == "['Enchantment']"]
		data_dict['creatures'] = sum(creature_cards['quantity'])
		data_dict['spells'] = sum(spell_cards['quantity'])
		data_dict['enchantments'] = sum(enchantment_cards['quantity'])
		# data_dict['enchantments'] = ['creatures'] = set_cards.loc[set_cards['types'] == "['Enchantment']"].sum('quantity')
		set_info[i] = data_dict
	return set_info
"""
Does the plotting and the graph for comparing the sets and data
"""
def plotting_dict(data_dict):
	name_list = data_dict.keys()
	print(name_list)
	print(data_dict['Ixalan'].values())
	N = 3
	menMeans = (20, 35, 30, 35, 27)
	menStd =   (2, 3, 4, 1, 2)

	ind = np.arange(N)  # the x locations for the groups
	print(ind)
	width = 0.35       # the width of the bars
	fig = plt.figure()
	ax = fig.add_subplot(111)
	rects1 = ax.bar(ind*2 -width, tuple(data_dict['Ixalan'].values()), width, color='royalblue')
	rects2 = ax.bar(ind*2, data_dict['Rivals of Ixalan'].values(), width, color='seagreen')
	rects3 = ax.bar(ind*2 + width, data_dict['Dominaria'].values(), width, color='red')
	rects4 = ax.bar(ind*2 +2*width, data_dict['Core Set 2019'].values(), width, color='purple')
	ax.set_ylabel('Number of Cards Used in Top Decks')
	ax.set_xlabel('Type of Card')
	ax.set_title('Comparing Sets Within MTG Standard Metagame')
	ax.set_xticks(ind*2 + width)
	ax.set_xticklabels( ('Creatures', 'Spells', 'Enchantments') )
	ax.legend( (rects1[0], rects2[0], rects3[0],rects4[0]), list(name_list) )
	plt.show()

	# This code was my original attempt at getting the graphing to work modularly
	# creature_count = []
	# spells_count = []
	# enchantment_count = []
	# for i in name_list:
	# 	creature_count.append(data_dict[i]['creatures'])
	# 	spells_count.append(data_dict[i]['spells'])
	# 	enchantment_count.append(data_dict[i]['enchantments'])
	# creature_count = tuple(creature_count)
	# spells_count = tuple(spells_count)
	# enchantment_count = tuple(enchantment_count)
	# get_legal_sets()
	# name_list = get_name_list()
	# csv_dict = csv_dict()
	# full_csv = pd.concat(list(csv_dict.values()), sort=False)
	# creatures = full_csv.loc[full_csv['types'] == ['creature']]
	# creatures_by_set = creatures.groupby("setName", sort=True).aggregate('count')
	# print(creatures_by_set)
	# # with pd.option_context('display.max_rows', None, 'display.max_columns', None):
	# # 	print(by_set.to_string())
	# list_valid_sets = ["Ixalan", "Rivals of Ixalan", "Dominaria", "Core Set 2019", "Guilds Of Ravnica"]
	# for set_name in list_valid_sets:
	# 	plt.scatter(x = creatures_by_set[ creatures_by_set["quantity"] == set_name], y=creatures_by_set["quantity"])
	# plt.show()

if __name__ == '__main__':
	data_dict = get_data_dict()
	print(data_dict)

	#plotting_dict(data_dict)





