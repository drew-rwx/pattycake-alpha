
# imports
from collections import defaultdict
from ruamel.yaml import YAML
import datetime
import random
import copy
import sys
import os

class Organism:
	def __init__(self, pattern_size, mutation_rate):
		self.mutation_rate = mutation_rate
		self.pattern_size = pattern_size
		self.assembly_size = self.pattern_size + 1 # +1 for L-shaped seed
		self.num_tiles = self.pattern_size ** 2

		# for the south and west glues of each tile, we need to pick another tile to attach to
		# how to index into, <south> * 2 * <num_tiles> + <west> * 2
		# stored in pairs, north at index, east at index + 1
		self.glue_table = [random.randint(1, self.num_tiles) for _ in range(2 * self.num_tiles ** 2)]

		# create the L-shaped seed
		# goes from top-left to bottom-right
		self.seed = [random.randint(1, self.num_tiles) for _ in range(self.pattern_size * 2)]

		# each tile is a tuple of glues (N, E, S, W)
		self.assembly = [[(0, 0, 0, 0) for _ in range(self.assembly_size)] for _ in range(self.assembly_size)]

	def assembly_string(self):
		result = ""

		# need to draw assembly 90 degrees clockwise for familiar layout
		for col in range(self.pattern_size, -1, -1):
			for row in range(self.pattern_size + 1):
					if row == 0 and col == 0:
						result += str(self.assembly[row][col]).rjust(20)
					elif col == 0:
						result += str((self.seed[self.pattern_size - 1 + row], 0, 0, 0)).rjust(20)
					elif row == 0:
						result += str((0, self.seed[self.pattern_size - col], 0, 0)).rjust(20)
					else:
						result += str(self.assembly[row][col]).rjust(20)
			result += "\n"

		return result

	def __str__(self):
		result = ""

		result += "Assembly\n"
		result += self.assembly_string() + "\n\n"

		return result

	def simulate(self):
		# reset the assembly
		self.assembly = [[(0, 0, 0, 0) for _ in range(self.assembly_size)] for _ in range(self.assembly_size)]

		northGlues = copy.copy(self.seed[self.pattern_size : self.pattern_size * 2])
		eastGlue = -1

		for row in range(1, self.assembly_size):

			# reset east glue, grab this row's east glue
			eastGlue = self.seed[self.assembly_size - 1 - row]

			for col in range(1, self.assembly_size):
				# grab known glues 
				# current tile's south is the below tile's north, same with east/west
				southGlue = northGlues[col - 1]
				westGlue = eastGlue

				# grab next glues
				index = (southGlue - 1) * 2 * self.num_tiles + (westGlue - 1) * 2
				northGlue = self.glue_table[index] # variable for clarity
				northGlues[col - 1] = northGlue # update actual value
				eastGlue = self.glue_table[index + 1]

				# add to assembly, swapped on the diagonal
				self.assembly[col][row] = (northGlue, eastGlue, southGlue, westGlue)

	# return fitness score, which is simply the % of correctly placed tiles
	def fitness(self, pattern):
		return random.randint(1, 10) # TODO, write actual function

	def mutate(self):
		mutation = copy.copy(self.glue_table)
		mutating = True

		while mutating:
			i = random.randrange(len(mutation))
			mutation[i] = random.randrange(self.num_tiles)
			mutating = False if random.randrange(self.mutation_rate) == 0 else True

		return mutation


class PATSApproximator:
    def setup(self, config_file="default.yaml"):
        path = os.path.join("configs", config_file)
        with open(path, "r") as f:
            yaml = YAML()
            config = yaml.load(f)

            # The size of the pattern, not including the L seed
            self.pattern_size = config["pattern_size"]

            # Will generate a pattern, or use the predefined pattern from the config
            if config["random_pattern"]:
                self.pattern = [
                    random.randrange(2)
                    for _ in range((config["pattern_size"]) ** 2)
                ]
            else:
                pattern = []

                for row in range(len(config["pattern"])):
                    for col in range(len(config["pattern"][row])):
                        pattern.append(config["pattern"][row][col])

                self.pattern = pattern

            self.generation = 0
            self.gene_count = config["gene_count"]

            # Fill the gene pool
            self.gene_pool = [
                Organism(config["pattern_size"], config["mutation_rate"])
                for _ in range(config["gene_count"])
            ]

    def intro(self):
        # print logo
        intro = """
          Pattycake

              (
              )
         __..---..__
     ,-='  /  |  \\  `=-.
    :--..___________..--;
     \\.,_____________,./
            """

        print(intro)

    def help(self):
        # formatting
        spacing = "   "
        ljust_characters = 15

        # make strings
        help_string = (spacing + "help").ljust(
            ljust_characters
        ) + ": print this strings"
        info_string = (spacing + "info").ljust(
            ljust_characters
        ) + ": print info about current system"
        run_string = (spacing + "run [x]").ljust(
            ljust_characters
        ) + ": run [x] generations"
        autorun_string = (spacing + "autorun").ljust(
            ljust_characters
        ) + ": run until stopped (ctrl+c)"
        best_string = (spacing + "best").ljust(
            ljust_characters
        ) + ": print best gene of this generation"
        printall_string = (spacing + "printall").ljust(
            ljust_characters
        ) + ": print all genes, best gene first"
        writeall_string = (spacing + "writeall").ljust(
            ljust_characters
        ) + ": write all genes to file <generation #>.txt"
        quit_string = (spacing + "quit").ljust(ljust_characters) + ": quit the program"

        # print strings
        print("Commands:")
        print(help_string)
        print(info_string)
        print(run_string)
        print(autorun_string)
        print(best_string)
        print(printall_string)
        print(writeall_string)
        print(quit_string)

    def info(self):
        print("*** Information ***")
        print("Pattern Size:", self.pattern_size, "X", self.pattern_size)

        for r in range(self.pattern_size):
            for c in range(self.pattern_size):
                print(self.pattern[self.pattern_size * r + c], end=" ")
            print()

        print("Gene Pool Size:", len(self.gene_pool))
        print("Generation:", self.generation)

    def run(self, generationsToRun: int, quiet=False):
        for _ in range(generationsToRun):
            self.generation += 1

            score = defaultdict(float)

            # run simulation on all genes
            for g in self.gene_pool:
                g.simulate()
                fitness = g.fitness(self.pattern)
                score[str(g.seed) + str(g.glue_table)] = fitness

            # sort the gene pool
            self.gene_pool = sorted(self.gene_pool, key=lambda x: score[str(x.seed) + str(x.glue_table)])

            # TODO
            # check if we met the threshold
            # if we did, find the # tiles used (in case smaller than goal), record the best organism, reset with a smaller glue_table
            # if not, continue until we do!

            # print best gene info
            if not quiet:
                print("*** Generation", self.generation, "Best ***")
                print(self.gene_pool[0])

            # mutate the bottom 3/4 of genes
            for i in range(len(self.gene_pool) // 4, len(self.gene_pool)):
                self.gene_pool[i].glue_table = self.gene_pool[i].mutate()

    def autorun(self):
        print("Starting generation " + str(self.generation + 1) + "...")
        running = True

        while running:
            try:
                self.run(1, quiet=True)
                if self.generation % 100 == 0:
                    print("*** Generation", self.generation, "***")
                    self.writeall()
                    self.writebest()

            except KeyboardInterrupt:
                running = False
                print("Stopping at generation", self.generation)

    def printall(self):
        for geneIndex in range(self.gene_count):
            print("*** *** Gene", geneIndex + 1, "*** ***")
            print(self.gene_pool[geneIndex])

    def best(self):
        print("*** Best Gene of Generation", self.generation, "***")
        print(self.gene_pool[0])

    def writebest(self):
        path = os.path.join("organisms", str(self.id), "best.txt")

        # create directory if needed
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "a") as f:
            f.write("*** Best Organism of Generation " + str(self.generation) + " ***\n")
            f.write(str(self.gene_pool[0]))

    def writeall(self):
        path = os.path.join(
            "organisms", str(self.id), "generation_" + f"{self.generation:012}" + ".txt"
        )

        # create directory if needed
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            for geneIndex in range(self.gene_count):
                f.write("*** *** Organism " + str(geneIndex + 1) + " *** ***\n")
                f.write(str(self.gene_pool[geneIndex]))

    def cli(self):
        # check if config was passed for setup
        if len(sys.argv) > 1:
            config_file = sys.argv[1]
            self.setup(config_file)
        else:
            self.setup()  # use default.yaml instead, no config passed

        # get the id of this run for file output
        self.id = datetime.datetime.now()
        self.id = (
            str(self.id.date())
            + "-"
            + f"{self.id.hour:02}"
            + f"{self.id.minute:02}"
            + f"{self.id.second:02}"
        )

        # initial
        self.intro()
        self.help()
        self.run(1, True)
        self.writeall()
        self.writebest()

        # main loop
        running = True
        while running:
            # grab command
            inp = input("> ")
            inp = inp.split(" ")
            print()

            # execute command
            if inp[0] == "help" or inp[0] == "h":
                self.help()

            elif inp[0] == "info" or inp[0] == "i":
                self.info()

            elif inp[0] == "run" or inp[0] == "r":
                # grab additional parameters
                generations = 1
                if len(inp) > 1:
                    generations = int(inp[1])

                self.run(generations)

            elif inp[0] == "rq":
                # grab additional parameters
                generations = 1
                if len(inp) > 1:
                    generations = int(inp[1])

                self.run(generations, quiet=True)

            elif inp[0] == "autorun" or inp[0] == "a":
                self.autorun()

            elif inp[0] == "best" or inp[0] == "b":
                self.best()

            elif inp[0] == "printall" or inp[0] == "p":
                self.printall()

            elif inp[0] == "writeall" or inp[0] == "w":
                self.writeall()

            elif inp[0] == "quit" or inp[0] == "q":
                running = False

            else:
                print("INVALID COMMAND")

        print("Goodbye!")


#
# main
#
if __name__ == "__main__":
    runner = PATSApproximator()
    runner.cli()