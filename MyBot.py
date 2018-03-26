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
game = hlt.Game("Settler")
# Then we print our start message to the logs
logging.info("Starting my Settler bot!")

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

		if len(closest_empty_planets) > 0:
			target_planet = closest_empty_planets[0]

			if ship.can_dock(target_planet):
				command_queue.append(ship.dock(target_planet))
			else:
				navigate_command = ship.navigate(
					ship.closest_point_to(target_planet),
					game_map,
					speed=int(hlt.constants.MAX_SPEED),
					ignore_ships=True)
				if navigate_command:
					command_queue.append(navigate_command)
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
