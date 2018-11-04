import gamelib
import random
import math
import warnings
from sys import maxsize

"""
Most of the algo code you write will be in this file unless you create new
modules yourself. Start by modifying the 'on_turn' function.

Advanced strategy tips: 

Additional functions are made available by importing the AdvancedGameState 
class from gamelib/advanced.py as a replcement for the regular GameState class 
in game.py.

You can analyze action frames by modifying algocore.py.

The GameState.map object can be manually manipulated to create hypothetical 
board states. Though, we recommended making a copy of the map to preserve 
the actual current map state.
"""

class AlgoStrategy(gamelib.AlgoCore):
    def __init__(self):
        super().__init__()
        random.seed()
        self.first_turn_filters = [[0,13],[1,12],[2,11],[3,10],[6,9],[7,9],[17,9],[20,9],[21,9],[24,10],[25,11],[26,12],[27,13]]
        self.first_turn_destructors = [[4,9],[8,9],[19,9],[23,9]]
        self.first_turn_pings = [[9,4],[9,4],[9,4],[9,4],[9,4]]
        self.frontline_exits = [[2, 13], [9, 13], [18, 13], [25, 13]]
        self.no_wall_zone = [[5,8],[6,7],[7,6],[8,5],[9,4],[10,3],[11,2],[12,1],[13,0],
                             [14,0],[15,1],[16,2],[17,3],[18,4],[19,5],[20,6],[21,7],[22,8],[4,11],[5,11],[5,10],[23,11],[22,11],[22,10]]
        # contains fourth row and areas further back that you generally want to spam attackers from
        for j in range(5, 23):
            self.no_wall_zone.append([j, 10])
        self.fifth_row_wall = []
        for k in range(4, 24):
            self.fifth_row_wall.append([k, 9])
        self.left_corner = [[0,13],[1,13],[1,12],[2,12],[2,11],[3,11],[3,10],[4,10]]
        self.right_corner = [[27,13],[26,13],[26,12],[25,12],[25,11],[24,11],[24,10],[23,10]]
        self.third_row_wall = []
        for l in range(6, 22):
            self.third_row_wall.append([l, 11])

    def on_game_start(self, config):
        """ 
        Read in config and perform any initial setup here 
        """
        gamelib.debug_write('Configuring your custom algo strategy...')
        self.config = config
        global FILTER, ENCRYPTOR, DESTRUCTOR, PING, EMP, SCRAMBLER, UNITS
        FILTER = config["unitInformation"][0]["shorthand"]
        ENCRYPTOR = config["unitInformation"][1]["shorthand"]
        DESTRUCTOR = config["unitInformation"][2]["shorthand"]
        PING = config["unitInformation"][3]["shorthand"]
        EMP = config["unitInformation"][4]["shorthand"]
        SCRAMBLER = config["unitInformation"][5]["shorthand"]
        UNITS = [FILTER, ENCRYPTOR, DESTRUCTOR, PING, EMP, SCRAMBLER]


    def on_turn(self, turn_state):
        """
        This function is called every turn with the game state wrapper as
        an argument. The wrapper stores the state of the arena and has methods
        for querying its state, allocating your current resources as planned
        unit deployments, and transmitting your intended deployments to the
        game engine.
        """
        game_state = gamelib.GameState(self.config, turn_state)
        gamelib.debug_write('Performing turn {} of your custom algo strategy'.format(game_state.turn_number))
        #game_state.suppress_warnings(True)  #Uncomment this line to suppress warnings.

        #self.starter_strategy(game_state)
        if game_state.turn_number == 0:
            strat = [first_turn_filters, [], first_turn_destructors, first_turn_pings, [], []]
        else:
            strat = self.game_strategy(game_state)
        for i in range(0, 6):
            deploy(units[x], strat[x], game_state)
        game_state.submit_turn()
        
    def filter_blocked_locations(self, locations, game_state):
        filtered = []
        for location in locations:
            if not game_state.contains_stationary_unit(location):
                filtered.append(location)
        return filtered
    
    def game_strategy(self, game_state):
        placements = [[], [], [], [], [], []]
        for breachpoint in self.breach_list:
            # if the breach is near the corners, try to defend them
            if breachpoint[1] > 9:
                buildpoint = breachpoint
                while not game_state.can_spawn(FILTER, buildpoint) or buildpoint in no_wall_zone:
                    buildpoint[0] = buildpoint[0] + random.randint(1,3) - 2
                    buildpoint[1] = buildpoint[1] + random.randint(1,3) - 2
                    if not game_state.game_map.in_arena_bounds(self, buildpoint):
                        buildpoint = breachpoint
                game_state.attempt_spawn(FILTER, buildpoint)
                game_state.debug_write('shoring up the location {}'.format(breachpoint))
        for filter in 
                
        
    def deploy(self, unit_type, coordinates, game_state):
        game_state.attempt_spawn(unit_type, coordinates)
    

if __name__ == "__main__":
    algo = AlgoStrategy()
    algo.start()
