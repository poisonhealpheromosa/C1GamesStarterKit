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
        self.first_turn_filters = [[0,13],[1,12],[2,11],[3,10],[5,9],[7,9],[17,9],[20,9],[21,9],[24,10],[25,11],[26,12],[27,13]]
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
        self.left_corner_initial_layer = [[0,13],[1,12],[2,12],[3,11]]
        self.left_corner_second_layer = [[1,13],[2,12],[3,11],[4,10]]
        self.right_corner_initial_layer = [[27,13],[26,12],[25,11],[24,10]]
        self.right_corner_second_layer = [[26,13],[25,12],[24,11],[23,10]]
        self.corners_initial = self.left_corner_initial_layer + self.right_corner_initial_layer
        self.third_row_wall = []
        for l in range(6, 22):
            self.third_row_wall.append([l, 11])
        self.third_row_left_exit = [5,10]
        self.third_row_right_exit = [22,10]
        self.fifth_row_left_exit = [9,9]
        self.fifth_row_right_exit = [18,9]
        self.first_row_left_exit_single_layer = [3,12]
        self.first_row_right_exit_single_layer = [24,12]
        self.first_row_left_exit_double_layer = [4,12]
        self.first_row_right_exit_double_layer = [23,12]
        # exits blocked number is *2 for left, *3 for right
        self.fifth_row_exits_blocked = 1
        self.third_row_exits_blocked = 1
        self.first_row_exits_blocked = 1
        self.left_layers = 1
        self.right_layers = 1
        
        self.fifth_row_destructors = [[4,9],[8,9],[10,9],[17,9],[19,9],[23,9]]
        self.row_being_built = 5
        
        self.middle_row_center_destructors = [10,14],[15,14]
        self.middle_row_side_destructors = [6,14],[21,14]
        self.middle_row_left_firewalls = [[7,14],[8,14],[9,14]]
        self.middle_row_right_firewalls = [[16,14],[17,14],[18,14],[19,14],[20,14]]
        
        self.back_redirector_built = 0
        self.back_redirector_column = 13
        
        self.building_encryptors = False
        
        self.times_corner_attacked = 0
        
        self.enemy_frontlines = []
        for h in range(14, 19):
            enemy_frontlines.append(h)
        self.attacking_with_pings = True
        self.attacking_this_turn = True
        self.ping_spot = [9,4]

    def on_game_start(self, config):
        """ 
        Read in config and perform any initial setup here 
        """
        gamelib.debug_write('literally who says "algo" as short for "algorithm" i love this game but man that sounds so stupid')
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
        gamelib.debug_write('truth_of_cthaeh is currently sitting at number {} on the leaderboard'.format((game_state.turn_number) ** 2)
        #game_state.suppress_warnings(True)  #Uncomment this line to suppress warnings.

        #self.starter_strategy(game_state)
        if game_state.turn_number == 0:
            strat = [first_turn_filters, [], first_turn_destructors, first_turn_pings, [], []]
        else:
            strat = self.game_strategy(game_state)
        for i in range(0, 6):
            deploy(UNITS[i], strat[i], game_state)
        game_state.submit_turn()

                            
    def filter_blocked_locations(self, locations, game_state):
        filtered = []
        for location in locations:
            if not game_state.contains_stationary_unit(location):
                filtered.append(location)
        return filtered
    
                            
    def game_strategy(self, game_state):
        placements = [[], [], [], [], [], []]
        my_bits = game_state.get_resource(game_state.BITS, 0)
        my_cores = game_state.get_resource(game_state.CORES, 0)
        enemy_bits = game_state.get_resource(game_state.BITS, 1)
        enemy_cores = game_state.get_resource(game_state.CORES, 1)
        for corner_location in self.corners_initial:
            if not game_state.contains_stationary_unit(corner_location):
                placements[0].append(corner_location)
                self.times_corner_attacked += 1
                my_cores -= 1
        row_5_destructors = 0
        for destructor_location in self.fifth_row_destructors:
            if not game_state.contains_stationary_unit(destructor_location):
                if my_cores >= 3:
                    placements[2].append(destructor_location)
                    my_cores -= 3
                    row_5_destructors += 1
            else:
                row_5_destructors += 1
        if row_5_destructors >= 6 and row_being_built == 5:
            row_5_wall = 0
            empty_spots = []
            for t in range(4, 24):
                if game_state.contains_stationary_unit([t, 9]):
                    row_5_wall += 1
                else:
                    empty_spots.append([t, 9])
            if row_5_wall < 18:
                while my_cores > 0 and row_5_wall < 18:
                    place_to_build = random.randint(1, len(empty_spots))-1
                    placements[0].append(empty_spots.pop(place_to_build))
                    row_5_wall += 1
                    my_cores -= 1
                if row_5_wall == 18:
                    self.fifth_row_left_exit = [min(empty_spots[0][0],empty_spots[1][0]), 9]
                    self.fifth_row_right_exit = [max(empty_spots[0][0],empty_spots[1][0]), 9]
                    self.row_being_built = analyze_enemy_lines(game_state, 5)
        if my_cores > 5 and row_being_built != 5:
            for t in middle_row_center_destructors:
                if not game_state.contains_stationary_unit([t[0],t[1]-row_being_built]):
                    placements[2].append([t[0],t[1]-row_being_built])
                    my_cores -= 3
            for t in middle_row_left_filters:
                if not game_state.contains_stationary_unit([t[0],t[1]-row_being_built]):
                    placements[0].append([t[0],t[1]-row_being_built])
                    my_cores -= 1
        if my_cores > 5 and row_being_built != 5:
            for t in middle_row_side_destructors:
                if not game_state.contains_stationary_unit([t[0],t[1]-row_being_built]):
                    placements[2].append([t[0],t[1]-row_being_built])
        if building_encryptors:
            pass
        attacking_this_turn = analyze_should_attack(game_state)
        attacking_with_pings = analyze_attack_type(game_state)
        if attacking_this_turn:
            if attacking_with_pings:
                for y in range(my_bits):
                    placements[3].append(ping_spot)
        return placements
        
    def deploy(self, unit_type, coordinates, game_state):
        game_state.attempt_spawn(unit_type, coordinates)
    
                            
    def analyze_enemy_lines(self, game_state, furthest_row):
        expert_analysis = furthest_row
        dont_build_here = furthest_row + 1
        # determines where the opponent's furthest row forward is, so the best place to build to stay out of emp range
        # while not building a harmful double wall
        frontline_wall_list = [0, 0, 0, 0, 0]
        for frontline in enemy_frontlines:
            for b in range(4, 24):
                if game_state.contains_stationary_unit(b, frontline):
                    frontline_wall_list[frontline-14] += 1
        # finds where the enemy is building their front lines
        furthest_wall = 14
        for frontline_wall in frontline_wall_list:
            if frontline_wall > 7:
                frontline_wall = furthest_wall
                """if frontline_wall > 9:
                    building_encryptors = True"""
                break
            furthest_wall += 1
        if furthest_wall > dont_build_here:
            expert_analysis = furthest_wall
        return expert_analysis
                            
    def analyze_should_attack(self, game_state):
        return True
                            
    def analyze_attack_type(self, game_state):
        return True
                      
                            
if __name__ == "__main__":
    algo = AlgoStrategy()
    algo.start()
