
# imports
import random
import copy

# create the gene

pattern_size = 4 					# 2x2 pattern
assembly_size = pattern_size + 1 	# 3x3 assembly, considering L-shaped seed
num_tiles = pattern_size ** 2 		# 4 tiles

# for the south and west glues of each tile, we need to pick another tile to attach to
# how to index into, <south> * 2 * <num_tiles> + <west> * 2
# stored in pairs, north at index, east at index + 1
glue_table = [random.randint(1, num_tiles) for _ in range(2 * num_tiles ** 2)]

# create the L-shaped seed
# goes from top-left to bottom-right
seed = [random.randint(1, num_tiles) for _ in range(pattern_size * 2)]

# fill in the assembly
assembly = [[(0, 0, 0, 0) for _ in range(assembly_size)] for _ in range(assembly_size)]

northGlues = copy.copy(seed[pattern_size : pattern_size * 2])
eastGlue = -1

for row in range(1, assembly_size):

	# reset east glue, grab this row's east glue
	eastGlue = seed[assembly_size - 1 - row]

	for col in range(1, assembly_size):
		# grab known glues 
		# current tile's south is the below tile's north, same with east/west
		southGlue = northGlues[col - 1]
		westGlue = eastGlue

		# grab next glues
		index = (southGlue - 1) * 2 * num_tiles + (westGlue - 1) * 2
		northGlue = glue_table[index] # variable for clarity
		northGlues[col - 1] = northGlue # update actual value
		eastGlue = glue_table[index + 1]

		# add to assembly, swapped on the diagonal
		assembly[col][row] = (northGlue, eastGlue, southGlue, westGlue)

# need to draw assembly 90 degrees clockwise for familiar layout
for col in range(pattern_size, -1, -1):
	for row in range(pattern_size + 1):
			if row == 0 and col == 0:
				print(str(assembly[row][col]).rjust(20), end="")
			elif col == 0:
				print(str((seed[pattern_size - 1 + row], 0, 0, 0)).rjust(20), end="")
			elif row == 0:
				print(str((0, seed[pattern_size - col], 0, 0)).rjust(20), end="")
			else:
				print(str(assembly[row][col]).rjust(20), end="")
	print()
