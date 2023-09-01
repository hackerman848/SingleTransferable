from utils.tools import pd
import utils.tools as t
import utils.google_sheet as gs
import utils.classes as c


def start_calc(spreadsheet, input_tab, question, seats, output_tab):
	input_tab: list[list[str]] = gs.load(spreadsheet, input_tab)
	ballots = pd.DataFrame(input_tab[1:], columns = input_tab[0])
	removable = []
	for column in ballots.columns:
		if question not in column:
			removable.append(column)
	ballots.drop(removable, axis = 1, inplace = True)

	columns = []
	for item in ballots.columns:
		item = item.replace(f"{question} [", "").replace("]", "")
		columns.append(item)

	ballots.columns = columns
	ballots = ballots.applymap(t.shorten)
	# | | | | | Got Base Ballots | | | | |

	vote = c.Vote(ballots, seats)

	response = "success"
	while response == "success":
		response = vote.add_tabulation_round()

	gs.write_results(spreadsheet, output_tab, vote)


pass
