"""
Welcome to your first Halite-II bot!

This bot's name is Settler. It's purpose is simple (don't expect it to win complex games :) ):
1. Initialize game
2. If a ship is not docked and there are unowned planets
2.a. Try to Dock in the planet if close enough
2.b If not, go towards the planet

Note: Please do not place print statements here as they are used to communicate with the Halite engine. If you need
to log anything use the logging module.
"""
# Let's start by importing the Halite Starter Kit so we can interface with the Halite engine
import hlt
# Then let's import the logging module so we can print out information
import logging

from collections import OrderedDict

# GAME START
# Here we define the bot's name as Settler and initialize the game, including communication with the Halite engine.
game = hlt.Game("StrongestPlanetBot")
# Then we print our start message to the logs
logging.info("Starting my StrongestPlanetBot!")

CLOSESTTHRESH = 4
TURNS = 10

prevShips = []
first = True
while True:
	# TURN START
	# Update the map for the new turn and get the latest version
	game_map = game.update_map()



	# Here we define the set of commands to be sent to the Halite engine at the end of the turn
	command_queue = []
	# For every ship that I control

	team_ships = game_map.get_me().all_ships()

	for ship in team_ships:
		if ship.docking_status != ship.DockingStatus.UNDOCKED:
			continue

		entities_by_distance = game_map.nearby_entities_by_distance(ship)
		entities_by_distance = OrderedDict(sorted(entities_by_distance.items(), key=lambda t: t[0]))

		closest_empty_planets = [entities_by_distance[distance][0] for distance in entities_by_distance if isinstance(entities_by_distance[distance][0], hlt.entity.Planet) and not entities_by_distance[distance][0].is_owned()]
		closest_enemy_ships = [entities_by_distance[distance][0] for distance in entities_by_distance if isinstance(entities_by_distance[distance][0], hlt.entity.Ship) and entities_by_distance[distance][0] not in team_ships]


		closest_planets = [entities_by_distance[distance][0] for distance in entities_by_distance if isinstance(entities_by_distance[distance][0], hlt.entity.Planet) and not entities_by_distance[distance][0].is_full()]
		thresh = CLOSESTTHRESH
		if CLOSESTTHRESH > len(closest_planets):
			thresh = len(closest_planets)
		planetsInRange = closest_planets[0:thresh]
		offset = 0
		for x in range(thresh):
			if planetsInRange[x].is_owned() and planetsInRange[x].owner.id == game_map.get_me().id and thresh+offset < len(closest_planets):
				planetsInRange[x] = closest_planets[thresh + offset]
				offset += 1

		if len(planetsInRange) > 0:
			targetPlanet = planetsInRange[0]
			for x in range(1, len(planetsInRange)):
				if planetsInRange[x].is_owned() and targetPlanet.is_owned():
					if planetsInRange[x].health > targetPlanet.health:
						targetPlanet = planetsInRange[x]

			if ship.can_dock(targetPlanet):
				command_queue.append(ship.dock(targetPlanet))
			else:
				navigate_command = ship.navigate(
					ship.closest_point_to(targetPlanet),
					game_map,
					speed=int(hlt.constants.MAX_SPEED),
					ignore_ships=False)
				if navigate_command:
					command_queue.append(navigate_command)


		# if TURNS == 0:
		# 	closest_owned_planets = [entities_by_distance[distance][0] for distance in entities_by_distance if isinstance(entities_by_distance[distance][0], hlt.entity.Planet) and entities_by_distance[distance][0].is_owned() and entities_by_distance[distance][0].owner.id != game_map.get_me().id]
		# 	thresh = CLOSESTTHRESH
		# 	if CLOSESTTHRESH > len(closest_owned_planets):
		# 		thresh = len(closest_owned_planets)
		# 	enemyPlanetsInRange = closest_owned_planets[0:thresh]

		# 	if len(enemyPlanetsInRange) > 0:
		# 		strongestPlanet = enemyPlanetsInRange[0]
		# 		logging.info("Going to get Enemy planets")
		# 		for x in range(len(enemyPlanetsInRange)):
		# 			if enemyPlanetsInRange[x].health > strongestPlanet.health:
		# 				strongestPlanet = enemyPlanetsInRange[x]

		# 		if ship.can_dock(strongestPlanet):
		# 			command_queue.append(ship.dock(strongestPlanet))
		# 		else:
		# 			navigate_command = ship.navigate(
		# 				ship.closest_point_to(strongestPlanet),
		# 				game_map,
		# 				speed=int(hlt.constants.MAX_SPEED),
		# 				ignore_ships=True)
		# 			if navigate_command:
		# 				command_queue.append(navigate_command)

		# elif TURNS > 0:
		# 	thresh = CLOSESTTHRESH
		# 	if CLOSESTTHRESH > len(closest_empty_planets):
		# 		thresh = len(closest_empty_planets)
		# 	emptyPlanetsInRange = closest_empty_planets[0:thresh]

		# 	if len(emptyPlanetsInRange) > 0:
		# 		targetPlanet = emptyPlanetsInRange[0]

		# 		if ship.can_dock(targetPlanet):
		# 			command_queue.append(ship.dock(targetPlanet))
		# 		else:
		# 			navigate_command = ship.navigate(
		# 				ship.closest_point_to(targetPlanet),
		# 				game_map,
		# 				speed=int(hlt.constants.MAX_SPEED),
		# 				ignore_ships=True)
		# 			if navigate_command:
		# 				command_queue.append(navigate_command)
		# 	TURNS -= 1

		elif len(closest_enemy_ships) > 0:
			logging.info(closest_enemy_ships[0])
			target_ship = closest_enemy_ships[0]
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
