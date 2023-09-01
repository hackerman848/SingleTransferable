import gspread
import utils.tools as t
import utils.classes as c

sa = gspread.service_account(filename = "service_account.json")


def load(sheet: str, tab_name: str) -> list[list[str]]:
	sh = sa.open(sheet)
	wks = sh.worksheet(tab_name)
	return wks.get_all_values()


def write_results(sheet: str, output_tab: str, vote_inc) -> None:
	sh = sa.open(sheet)
	wks = sh.worksheet(output_tab)

	vote: c.Vote = t.deepcopy(vote_inc)

	wks.update("AA3:AA12", [
		[len(vote.get_original_ballots()) + vote.get_original_expired()],
		[len(vote.get_original_ballots())],
		[vote.get_original_expired()],
		[],
		[],
		[vote.seats]
	])
	wks.update("AA11", vote.quota)

	writer = []
	for elected_person in vote.get_all_elected():
		elected_vote_count = vote.get_election_votes(elected_person)
		writer.append([elected_person, '', '', '', '', '', '', vote.tabulation_rounds[0].get_starting_vote_count()[elected_person], '', '', elected_vote_count])
	wks.update("D5:N34", writer)

	random_logs = vote.get_all_random_logs()

	writer = []
	for i, logs in enumerate(random_logs):
		tab_round = i + 1
		for log in logs:
			log: c.RandLog
			writer.append([f"Round {tab_round}", '', '', '', '', log.chosen, '', '', '', '', "; ".join(log.pool), '', '', '', '', '', '', '', '', '', '', '', '', log.random_for])
	wks.update("AD5:BD34", writer)

	for i, tabulation_round in enumerate(vote.tabulation_rounds):
		writer = []
		for person in tabulation_round.get_all_starting_candidates():
			if person in tabulation_round.elected:
				event = "Elected"
			elif person in tabulation_round.eliminated:
				event = "Eliminated"
			else:
				event = "- -"

			if tabulation_round.outgoing_ballots is not None:
				try:
					turn2 = tabulation_round.outgoing_vote_count[person]
				except KeyError:
					turn2 = "- -"
			else:
				turn2 = "<no transfer>"

			writer.append([person, '', '', '', '', '', '', '', '', '', '', '', '', '', tabulation_round.get_starting_vote_count()[person], '', '', '', turn2, '', '', '', event])

		if i % 3 == 0:
			columns = ("C", "Y")
		elif i % 3 == 1:
			columns = ("AE", "BA")
		else:
			columns = ("BG", "CC")

		row_1 = (i // 3) * 34 + 39
		row_2 = row_1 + 29

		wks.update(f"{columns[0]}{row_1}:{columns[1]}{row_2}", writer)


pass
