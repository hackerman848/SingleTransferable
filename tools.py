from copy import deepcopy
from math import isnan, floor
import pandas as pd
from random import choice, shuffle


def shorten(item: str): #cleans 1st,2nd etc to just number
	# print("item = "+str(item))
	if len(str(item)) > 0 and str(item) != "nan":
		x= int(str(item)[:-2])
		# print(x) 
		return x
	return None


def recalc_support(ballots: pd.DataFrame) -> pd.DataFrame:
	adjusted_ballots = deepcopy(ballots)
	adjusted_ballots.drop(["Supports"], axis = 1, inplace = True, errors = "ignore")
	adjusted_ballots.drop(["Weight"], axis = 1, inplace = True, errors = "ignore")
	supports = []
	for i, line in adjusted_ballots.iterrows():
		line: dict = dict(line)
		first = True
		lowest = None
		person = None
		for key in line.keys():
			if isnan(line[key]):
				continue
			if first:
				lowest = line[key]
				person = key
				first = False
			else:
				if lowest > line[key]:
					lowest = line[key]
					person = key

		supports.append(person)

	ballots["Supports"] = supports
	return ballots


def delete_expired(ballots: pd.DataFrame) -> (pd.DataFrame, int):
	adjusted_ballots = deepcopy(ballots)
	delete_index = []
	for i, line in adjusted_ballots.iterrows():
		all_nan = True
		for j, item in line.items():
			if j == "Supports" or j == "Weight":
				break
			if not isnan(item):
				all_nan = False
				break
		if all_nan:
			delete_index.append(i)

	delete_index.reverse()
	for i in delete_index:
		adjusted_ballots.drop(axis = 0, index = i, inplace = True)
	return adjusted_ballots, len(delete_index)


def remove_electee_ballots(ballots: pd.DataFrame, electee: str) -> (pd.DataFrame, int):
	adjusted_ballots = deepcopy(ballots)
	delete_index = []
	for i, line in ballots.iterrows():
		support = line["Supports"]
		if support == electee:
			delete_index.append(i)

	delete_index.reverse()
	for i in delete_index:
		adjusted_ballots.drop(axis = 0, index = i, inplace = True)
	return adjusted_ballots, len(delete_index)


def get_vote_count(ballots: pd.DataFrame) -> dict[str: int]:
	vote_count: dict[str: int] = dict()
	for person in ballots.columns[:-2]:
		vote_count[person] = 0
	for i, line in ballots.iterrows():
		line: pd.Series
		support = line["Supports"]
		try:
			vote_count[support] = vote_count[support] + line["Weight"]
		except KeyError:
			vote_count[support] = line["Weight"]

	return vote_count


def surplus_calc(ballots: pd.DataFrame, vote_count: pd.Series, person: str, quota: int) -> pd.DataFrame:
	adjusted_ballots = deepcopy(ballots)
	personal_weight = (vote_count[person] - quota) / vote_count[person]
	adjusted_ballots["Weight"] = adjusted_ballots["Weight"] * personal_weight
	return adjusted_ballots

