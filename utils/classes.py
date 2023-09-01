from utils.tools import pd
from numpy import nan
import utils.tools as t
from math import floor


class RandLog:
	def __init__(self, pool, chosen, random_for):
		self.pool = pool
		self.chosen = chosen
		self.random_for: str = random_for


class Vote:
	def __init__(self, ballots: pd.DataFrame, seats):
		self.seats = seats
		self._original_expired: int = 0

		# init-ing weight and support columns
		for column in ballots.columns:
			if ballots[column][0] is None:
				ballots[column] = [nan] * len(ballots[column])

		ballots, self._original_expired = t.delete_expired(ballots)
		ballots = t.recalc_support(ballots)
		ballots["Weight"] = [1] * len(ballots["Supports"])

		self._original_ballots: pd.DataFrame = t.deepcopy(ballots)
		self.quota = floor((len(ballots) / (self.seats + 1)) + 1)
		self.tabulation_rounds: list[TabulationRound] = []

	def get_original_ballots(self) -> pd.DataFrame:
		return t.deepcopy(self._original_ballots)

	def get_original_expired(self) -> int:
		return t.deepcopy(self._original_expired)

	def get_all_candidates(self) -> list[str]:
		return self._original_ballots.columns[:-2]

	def get_all_elected(self) -> list[str]:
		elected = []
		for tabulation_round in self.tabulation_rounds:
			elected = elected + tabulation_round.elected
		return elected

	def get_all_eliminated(self) -> list[str]:
		eliminated = []
		for tabulation_round in self.tabulation_rounds:
			eliminated = eliminated + tabulation_round.eliminated
		return eliminated

	def get_all_random_logs(self) -> list[list[RandLog]]:
		rand_log_list = []
		for tabulation_round in self.tabulation_rounds:
			rand_log_list.append(tabulation_round.random_log)
		return rand_log_list

	def get_election_votes(self, elected: str) -> int:
		for tabulation_round in self.tabulation_rounds:
			if elected in tabulation_round.elected:
				return tabulation_round.get_starting_vote_count()[elected]

	def add_tabulation_round(self) -> str:
		if len(self.get_all_elected()) < self.seats and len(self.get_all_elected()) + len(self.get_all_eliminated()) != len(self.get_all_candidates()):
			if self.tabulation_rounds:
				new_round = TabulationRound(t.deepcopy(self.tabulation_rounds[-1].outgoing_ballots), self)
			else:
				new_round = TabulationRound(t.deepcopy(self._original_ballots), self)

			self.tabulation_rounds.append(new_round)
			return "success"
		else:
			return "full"


class TabulationRound:
	def __init__(self, ballots, parent_vote):
		self.parent_vote: Vote = parent_vote
		self.random_log: list[RandLog] = []
		self.expired: int = 0

		self._starting_ballots: pd.DataFrame = t.deepcopy(ballots)
		self._starting_vote_count: dict[str: int] = t.get_vote_count(self._starting_ballots)

		self.elected: list[str] = []
		self.eliminated: list[str] = []

		self.outgoing_ballots: pd.DataFrame = None
		self.outgoing_vote_count: dict[str: int] = None

		if len(self.get_starting_ballots().columns[:-2]) == self.parent_vote.seats - len(self.parent_vote.get_all_elected()):
			for person in self.get_starting_ballots().columns[:-2]:
				self.elected.append(person)
		else:
			for person in self._starting_vote_count.keys():
				vote = self._starting_vote_count[person]
				if vote >= self.parent_vote.quota:
					self.election_round()
					break
			else:
				self.elimination_round()

	def get_starting_ballots(self) -> pd.DataFrame:
		return t.deepcopy(self._starting_ballots)

	def get_starting_vote_count(self) -> dict[str: int]:
		return t.deepcopy(self._starting_vote_count)

	def get_all_starting_candidates(self):
		return self._starting_vote_count.keys()

	def election_round(self):
		# get people with sufficient votes
		people = []
		elected_num = len(self.parent_vote.get_all_elected())
		for person in pd.Series(data = self._starting_vote_count).sort_values(ascending = False).keys():
			if self._starting_vote_count[person] >= self.parent_vote.quota:
				if elected_num + len(people) >= self.parent_vote.seats and self._starting_vote_count[person] != self._starting_vote_count[people[-1]]:
					break
				people.append(person)

		# elect 1
		if elected_num + len(people) > self.parent_vote.seats:
			actual = []
			while elected_num + len(actual) < self.parent_vote.seats:
				person = t.choice(people)
				self.random_log.append(RandLog(people, person, "elect"))
				people.remove(person)
				actual.append(person)
			self.elected += actual
			people = actual
		else:
			self.elected += people

		# make surplus adjustments
		surplus_people = []
		for person in people:
			if self.outgoing_ballots is None:
				self.outgoing_ballots = self.get_starting_ballots()

			if self._starting_vote_count[person] > self.parent_vote.quota:
				surplus_people.append(person)
			else:
				self.outgoing_ballots.drop([person], axis = 1, inplace = True)
				self.outgoing_ballots, deleted = t.remove_electee_ballots(self.outgoing_ballots, person)
				self.expired += deleted

		self.surplus_calc(surplus_people)

		# recalc vote_count after all is done
		self.outgoing_ballots, deleted = t.delete_expired(self.outgoing_ballots)
		self.expired += deleted
		self.outgoing_ballots = t.recalc_support(self.outgoing_ballots)
		self.outgoing_vote_count: dict[str: int] = t.get_vote_count(self.outgoing_ballots)

	def elimination_round(self):
		# get the lowest vote
		first = True
		lowest = None
		for person in self._starting_vote_count.keys():
			if first:
				lowest = self._starting_vote_count[person]
				first = False
			else:
				if self._starting_vote_count[person] < lowest:
					lowest = self._starting_vote_count[person]

		# get people with the lowest vote
		people = []
		for person in self._starting_ballots.columns[:-2]:
			if self._starting_vote_count[person] == lowest:
				people.append(person)

		# eliminate
		eliminated = t.choice(people)
		if len(people) > 1:
			self.random_log.append(RandLog(people, eliminated, "eliminate"))
		self.eliminated.append(eliminated)
		self.outgoing_ballots = t.recalc_support(self._starting_ballots.drop([eliminated], axis = 1, inplace = False))
		self.outgoing_ballots, deleted = t.delete_expired(self.outgoing_ballots)
		self.expired += deleted
		self.outgoing_vote_count = t.get_vote_count(self.outgoing_ballots)

	def surplus_calc(self, people):
		# personal weight
		people_dict = dict()
		for person in people:
			people_dict[person] = (self._starting_vote_count[person] - self.parent_vote.quota) / self._starting_vote_count[person]
		adjusted_ballots = t.deepcopy(self.outgoing_ballots)

		# drop person
		adjusted_ballots.drop(people, axis = 1, inplace = True)
		adjusted_ballots, deleted = t.delete_expired(adjusted_ballots)
		self.expired += deleted

		# adjust ballots
		new_weights = []
		for i, line in adjusted_ballots.iterrows():
			if line["Supports"] in people:
				new_weights.append(line["Weight"] * people_dict[line["Supports"]])
			else:
				new_weights.append(line["Weight"])
		adjusted_ballots["Weight"] = new_weights

		adjusted_ballots = t.recalc_support(adjusted_ballots)

		# save outcome
		self.outgoing_ballots = adjusted_ballots
		self.outgoing_vote_count: dict[str: int] = t.get_vote_count(self.outgoing_ballots)

	def get_last_ballots(self):
		if self.outgoing_ballots is not None:
			return t.deepcopy(self.outgoing_ballots)
		else:
			return t.deepcopy(self.get_starting_ballots())

	def get_last_votes(self):
		if self.outgoing_vote_count is not None:
			return t.deepcopy(self.outgoing_vote_count)
		else:
			return t.deepcopy(self.get_starting_vote_count())


pass
