import json
import random
from time import sleep
import copy

NEW_TILE_OPTIONS = [ 1, 2 ]
DIRECTION_OPTIONS = [ 'up', 'down', 'left', 'right']
BOARD_DIMENSIONS = {'row': 4, 'col': 4}


class Game:

	def __init__(self):

		# Create empty board
		self.board_data = [ [ 0 for i in range(BOARD_DIMENSIONS['row'])] for i in range(BOARD_DIMENSIONS['col'])]
		self.added_tiles_count = 0
		self.score = 0
		self.history = []

		# Game status: playing or lost
		self.game_status = "playing"

	def set_game_data(self, game_data):
		self.board_data = game_data["board_data"]
		self.added_tiles_count = game_data["added_tiles_count"]
		self.score = game_data["score"]
		self.game_status = "playing"
		#self.history = game_data["history"]

	# Prints out various stats before printing out the board
	def print_board_verbose(self):
		
		self.print_board()
		print("Score: {}".format(self.score))
		print("Total tiles added: {}".format(self.added_tiles_count))

	def print_board(self):
		for row in range(BOARD_DIMENSIONS['row']):
			row_string = '|\t'
			for col in range(BOARD_DIMENSIONS['col']):
				row_string += str(self.board_data[row][col])
				row_string += '\t'
			print("|---------------------------------------|")
			row_string += '|'
			print(row_string)
		print("|---------------------------------------|")
		print('\n')

	# Export the game in JSON format
	def export_game_data(self): 
		game_data = {
			"board_data": self.board_data,
			"added_tiles_count": self.added_tiles_count,
			"score": self.score,
			"history": self.history,
		}
		return game_data

	# Generate a new tile on the number provided
	def add_tile(self, tile_number):

		# Find an empty spot on the board
		empty_board_positions = self.get_positions_of_n(0)

		# Choose an empty slot to place the tile
		target_tile_coords = random.choice(empty_board_positions)

		# Place the new tile on the board
		self.board_data \
			[ target_tile_coords['row']] \
			[ target_tile_coords['col']] = tile_number

		# Record the move
		move_record = {
			'operation': 'add_tile',
			'coords': target_tile_coords,
			'tile_number': tile_number,
			'score': self.score,
			'added_tiles_count': self.added_tiles_count
		}
		self.history.append(move_record)

		# Increment total tiles added
		self.added_tiles_count += 1

		self.refresh_game_status()

	# Generate a new tile number from the list of possible options
	def add_random_tile(self):
		return self.add_tile(random.choice(NEW_TILE_OPTIONS))

	# Generates a list of coordinates that hold the specified tile
	def get_positions_of_n(self, target_tile_number):
		
		tiles_of_n = []
		row_number = 0
		column_number = 0

		for row in self.board_data:
			for tile in row:
				if tile == target_tile_number:
					matching_tile_coords = { 
						"row": row_number,
						"col": column_number 
					}
					tiles_of_n.append(matching_tile_coords)
				column_number += 1
			row_number += 1
			column_number = 0

		return tiles_of_n

	def move(self, direction):
		if direction not in DIRECTION_OPTIONS:
			print("Error: invalid move direction")
			return False
		

		# Record the move
		move_record = {
			'operation': 'move_board',
			'direction': direction,
			'score': self.score,
			'added_tiles_count': self.added_tiles_count
		}
		self.history.append(move_record)

		return self.move_board(direction)

	def generate_move_order(self, direction):

		move_order = []

		if direction == 'up':
			# move top down
			for row in range(BOARD_DIMENSIONS['row']):
				for col in range(BOARD_DIMENSIONS['col']):
					move_order.append([row, col])


		if direction == 'down':
			# move buttom up
			for row in range(BOARD_DIMENSIONS['row'] - 1, -1, -1):
				for col in range(0, BOARD_DIMENSIONS['col']):
					move_order.append([row, col])

		if direction == 'left':
			# move left to right
			for col in range(BOARD_DIMENSIONS['col']):
				for row in range(BOARD_DIMENSIONS['row']):
					move_order.append([row, col])

		if direction == 'right':
			# move right to left
			for col in range(BOARD_DIMENSIONS['col'] - 1, -1, -1):
				for row in range(BOARD_DIMENSIONS['row']):
					move_order.append([row, col])
		return move_order
		
	def refresh_game_status(self):
		for row in range(0, BOARD_DIMENSIONS['row']):
			for col in range(0, BOARD_DIMENSIONS['col']):
				if self.board_data[row][col] == 0:
					return False
		self.game_status = "lost"

	def move_board(self, direction):
		# Depending on the parameters passed in, this function will
		# iterate through all of the tiles on the board in such a way
		# that all tiles will be able to move fully and won't be blocked
		# by tiles that haven't moved yet.
		# If none of the tiles move, return False
		some_tiles_moved = False
		move_order = self.generate_move_order(direction)
		for move in move_order:
			if self.move_tile(move, direction):
				some_tiles_moved = True

		# Go through each tile and make sure none are negative
		for row in range(len(self.board_data)):
			for col in range(len(self.board_data[row])):
				if self.board_data[row][col] < 0:
					self.board_data[row][col] *= -1

		return some_tiles_moved

	def move_tile(self, tile_coords, direction):

		# Check to see if there is a tile in that space
		row_number, column_number = tile_coords
		if self.board_data[row_number][column_number] == 0:
			return False

		# Store current tile value
		tile_value = self.board_data[row_number][column_number] 

		# In case the tile cannot move in the specified direction, set default next position
		next_tile_position = tile_coords

		# Figure out where the next position of the tile will be
		next_position_found = False
		while(not next_position_found):
			potential_next_tile_position = self.get_next_tile_position(next_tile_position, direction)
			if self.move_is_valid(potential_next_tile_position, tile_value):
				next_tile_position = potential_next_tile_position
			else:
				next_position_found = True
		
		# Extract the coords for replacement
		row_number, column_number = next_tile_position
		original_row_number, original_column_number = tile_coords

		# Check to see if the tile moves at all
		if next_tile_position != tile_coords:
			
			if self.board_data[row_number][column_number] \
				== self.board_data[original_row_number][original_column_number]:

				# These tiles are the same and should combine, and the score should increase by the value of the combined tiles
				earned_points = self.board_data[original_row_number][original_column_number] * 2

				# Make it negative to show it's been combined once this move
				# and cannot be combined again.
				self.board_data[row_number][column_number] = earned_points * -1
				self.score += earned_points


			else:
				# Put tile in new position
				self.board_data[row_number][column_number] \
					= self.board_data[original_row_number][original_column_number]

			# Set old position to empty if the tile moved
			self.board_data[original_row_number][original_column_number] = 0

			# if the tile moved, return True
			return True

		else:
			# if the tile did not move, return false
			return False


	def get_next_tile_position(self, tile_coords, direction):
		row_number, column_number = tile_coords
		if direction == 'up':
				row_number -= 1
		if direction == 'down': 
			row_number += 1
		if direction == 'left':
			column_number -= 1
		if direction == 'right':
			column_number += 1
		return [row_number, column_number]

	def move_is_valid(self, tile_coords, tile_value):
		row_number, column_number = tile_coords
		if row_number >= 0 \
			and row_number < BOARD_DIMENSIONS['row'] \
			and column_number >= 0 \
			and column_number < BOARD_DIMENSIONS['col'] \
			and ( self.board_data[row_number][column_number] == 0 \
				or self.board_data[row_number][column_number] == tile_value ):
			return True
		return False



def print_transition(boards, direction):


	print("Direction: {}".format(direction))
	for row in range(BOARD_DIMENSIONS['row']):
		row_string = ""
		for board in boards:
			row_string += '|'
			for col in board[row]:
				row_string += str(col)
				row_string += " "
			row_string += '|\t'
		print(row_string)
	print('\n')



def auto_play():

	# Start
	game = Game()
	history_tree = {}
	game.add_random_tile()

	while(game.game_status == 'playing'):
		sleep(0.05)


		#game.print_board_verbose()


		# Export the game data to be used for predictions
		game_data = copy.deepcopy(game.export_game_data())

		# try all possible moves for the next n moves and see which results in the highest score

		direction_scores = {}
		for direction in DIRECTION_OPTIONS:
			current_game = Game()
			current_game.set_game_data(copy.deepcopy(game_data))
			current_game.move(direction)
			current_game_data = copy.deepcopy(current_game.export_game_data())
			all_games = get_all_possible_games_after_n_moves(100, current_game_data)

			# Calculate the average score in the resulting games
			total_score = 0
			for game_data_iteration in all_games:
				total_score += game_data_iteration['score']
			average_score = total_score / len(all_games)

			direction_scores[direction] = average_score

		# Make the next move based on the highest score

		def sort_key(item):
			return item[1]

		# Sort the best directions
		sorted_directions = list(direction_scores.items())
		sorted_directions.sort(key = sort_key, reverse = True)

		# Iterate by highest average score
		for direction in sorted_directions:
			if game.move(direction[0]):

				# Add a tile to the game
				middle_board = copy.deepcopy(game.export_game_data()['board_data'])
				game.add_random_tile()

				print("Average score for that direction: {}".format(direction[1]))
				print_transition([game_data['board_data'], middle_board, game.export_game_data()['board_data']], direction[0])
				break


	print("Game over")
	game.print_board_verbose()
	return game.score
	

def get_all_possible_games_after_n_moves(number_of_moves, starting_game_data):

	current_game_data = starting_game_data
	top_scorer = starting_game_data

	new_game_iterations = []
	new_game_iterations.append(starting_game_data)

	iteration_count = 0

	while(len(new_game_iterations) > 0 and current_game_data['added_tiles_count'] < number_of_moves and iteration_count < 10000):
		iteration_count += 1
		#print("Iteration: {}".format(iteration_count))
		if iteration_count % 1000 == 0:
			file = open("results.json", "w")
			"""for row in range(BOARD_DIMENSIONS['row']):
													row_string = '|\t'
													for col in range(BOARD_DIMENSIONS['col']):
														row_string += str(top_scorer['board_data'][row][col])
														row_string += '\t|\t'
													file.write("|---------------------------------------|\n")
													file.write(row_string + '\n')
												file.write("|---------------------------------------|\n")"""
		'''if len(new_game_iterations) > 100:
			def sort_key(iteration):
				return iteration['score'] / iteration['added_tiles_count']
			new_game_iterations.sort(key = sort_key, reverse = True)
			new_game_iterations = new_game_iterations[:20]'''

		#csleep(0.005)
		current_game_data = new_game_iterations.pop(0)

		current_game = Game()
		current_game.set_game_data(current_game_data)

		# Store the original iteration for printing later
		current_board_layout = copy.deepcopy(current_game.board_data)

		# Add a tile to the game
		#print("Current tiles added: {}".format(current_game_data['added_tiles_count']))
		current_game.add_random_tile()

		current_game_data = current_game.export_game_data()

		# Store the original iteration after adding a tile for printing later
		post_add_tile_board_layout = copy.deepcopy(current_game.board_data)

		for direction in DIRECTION_OPTIONS:
			# Create a new game object
			new_game = Game()

			# Set it up to be a copy of the current iteration
			new_game.set_game_data(copy.deepcopy(current_game_data))
			if new_game.move(direction):
				if new_game.game_status == "playing":
					new_game_iterations.append(new_game.export_game_data())
					post_move_board_layout = copy.deepcopy(new_game.board_data)
					# print_transition([current_board_layout, post_add_tile_board_layout, post_move_board_layout], direction)
					
			# Clear post move layout
			post_move_board_layout = []
			del new_game

		
		# Clear other data
		current_board_layout = []
		post_add_tile_board_layout = []
		#current_game.print_board_verbose()
		#print("History length: {}".format(len(current_game.history)))
		del current_game

		if top_scorer['score'] < current_game_data['score']:
			top_scorer = current_game_data

		#print("New game iterations: {}".format(len(new_game_iterations)))



	"""file = open("results.json", "w")
				for row in range(BOARD_DIMENSIONS['row']):
					file.write(top_scorer["board_data"][row])
					file.write('\n')"""
	#json.dumps(top_scorer, file)
	return new_game_iterations

def auto_play_loop():
	top_score = 0
	total_iterations = 0
	while(True):
		total_iterations += 1
		score = auto_play()
		if score > top_score:
			top_score = score
		sleep(1.5)
		print("Top score: {}\nTotal iterations: {}".format(top_score, total_iterations))

def normal_play():
	game = Game()
	game.add_random_tile()
	while(True):
		game.print_board_verbose()
		if game.move(input("Direction: ")):
			game.add_random_tile()

def main():
	#normal_play()
	auto_play_loop()

if __name__ == '__main__':
	main()

