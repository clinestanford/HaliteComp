import hlt
import logging

from collections import OrderedDict

game = hlt.Game("StrongestPlanetBot")
logging.info("Starting my StrongestPlanetBot!")

while True:
	# TURN START
	# Update the map for the new turn and get the latest version
	game_map = game.update_map()

	command_queue = []

	team_ships = game_map.get_me().all_ships()

	for ship in team_ships:
		if ship.docking_status != ship.DockingStatus.UNDOCKED:
			continue

		entities_by_distance = game_map.nearby_entities_by_distance(ship)
		entities_by_distance = OrderedDict(sorted(entities_by_distance.items(), key=lambda t: t[0]))

		closest_empty_planets = [entities_by_distance[distance][0] for distance in entities_by_distance if isinstance(entities_by_distance[distance][0], hlt.entity.Planet) and not entities_by_distance[distance][0].is_owned()]
		closest_enemy_planets = [entities_by_distance[distance][0] for distance in entities_by_distance if isinstance(entities_by_distance[distance][0], hlt.entity.Planet) and entities_by_distance[distance][0].is_owned() and entities_by_distance[distance][0].owner.id != game_map.get_me().id and not entities_by_distance[distance][0].is_full()]
		closest_enemy_ships = [entities_by_distance[distance][0] for distance in entities_by_distance if isinstance(entities_by_distance[distance][0], hlt.entity.Ship) and entities_by_distance[distance][0] not in team_ships]

		if len(team_ships) <= 5:
			planets = closest_empty_planets
		else:
			planets = sorted(closest_enemy_planets, key=lambda x: x.health, reverse=True)

		if len(planets) > 0:
			target_planet = planets[0]
			if target_planet.is_owned():
				logging.info(len(planets))
				logging.info("targetPlanet health")
				logging.info(target_planet.health)
				logging.info("Last planet health")
				lastPlanet = planets[len(planets)-1]
				logging.info(lastPlanet.health)
			if not target_planet.is_owned() and ship.can_dock(target_planet):
				command_queue.append(ship.dock(target_planet))
			elif not target_planet.is_owned():
				navigate_command = ship.navigate(
					ship.closest_point_to(target_planet),
					game_map,
					speed=int(hlt.constants.MAX_SPEED),
					ignore_ships=False)
				if navigate_command:
					command_queue.append(navigate_command)
			else:
				entitiesNearPlanet = game_map.nearby_entities_by_distance(target_planet)
				entitiesNearPlanet = OrderedDict(sorted(entities_by_distance.items(), key=lambda t: t[0]))
				enemyShipsNearPlanet = [entitiesNearPlanet[distance][0] for distance in entitiesNearPlanet if isinstance(entitiesNearPlanet[distance][0], hlt.entity.Ship) and entitiesNearPlanet[distance][0] not in team_ships]

				target_ship = enemyShipsNearPlanet[0]
				navigate_command = ship.navigate(
								ship.closest_point_to(target_ship),
								game_map,
								speed=int(hlt.constants.MAX_SPEED),
								ignore_ships=False)
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
