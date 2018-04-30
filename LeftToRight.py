import hlt
import logging

from collections import OrderedDict

game = hlt.Game("LeftToRight")
logging.info("Starting LeftToRight!")

#1 = go dock
#2 = attack ship
shipAction = 1

while True:
	# TURN START
	# Update the map for the new turn and get the latest version
	game_map = game.update_map()
	myId = game_map.get_me().id

	allPlanets = game_map.all_planets() #all planets on the board
	allShips = game_map._all_ships() #all ships on the board
	emptyPlanets = [x for x in allPlanets if (not x.is_owned())] #all empty planets
	emptyPlanets = sorted(emptyPlanets, key=lambda s: s.x) #empty planets sorted by their x-coordinate

	# Here we define the set of commands to be sent to the Halite engine at the end of the turn
	command_queue = []

	#Get my ships and the enemy ships
	team_ships = game_map.get_me().all_ships()
	enemyShips = [x for x in allShips if x not in team_ships]

	#If I have 8 or fewer ships, go dock to make more
	if(len(team_ships) <= 8):
		shipAction = 1
	#otherwise, go attack 
	else:
		shipAction = 2

	shipCount = 0

	for ship in team_ships:
		#if the ship is docked, skip it
		if ship.docking_status != ship.DockingStatus.UNDOCKED:
			continue
		
		
		planetcount = 0
		if len(emptyPlanets) > 0 and shipAction == 1:
			target_planet = emptyPlanets[0]
			# shipCount += 1
			# if(shipCount == len(emptyPlanets)):
			# 	shipCount = 0

			if (ship.can_dock(target_planet)):
				command_queue.append(ship.dock(target_planet))
			else:
				navigate_command = ship.navigate(
					ship.closest_point_to(target_planet),
					game_map,
					speed=int(hlt.constants.MAX_SPEED),
					ignore_ships=False)
				if navigate_command:
					command_queue.append(navigate_command)
		elif len(enemyShips) > 0:
			
			target_ship = enemyShips[shipCount]
			shipCount += 1
			if(shipCount == len(enemyShips)):
				shipCount = 0
				
			navigate_command = ship.navigate(
								ship.closest_point_to(target_ship),
								game_map,
								speed=int(hlt.constants.MAX_SPEED),
								ignore_ships=False)
			if navigate_command:
				command_queue.append(navigate_command)

	# Send our set of commands to the Halite engine for this turn
	game.send_command_queue(command_queue)
	# TURN END
# GAME END