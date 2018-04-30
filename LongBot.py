import hlt
import logging

from collections import OrderedDict

game = hlt.Game("LongBot")
logging.info("Starting LongBot")
start_direction = []
#no_go_planets = []
turns = 0
start_turns_strategy = 12

while True:
	game_map = game.update_map()
	command_queue = []

	turns+=1
	iterator = 0

	team_ships = game_map.get_me().all_ships()
	for ship in team_ships:
		if ship.docking_status != ship.DockingStatus.UNDOCKED:
			if turns < start_turns_strategy:
				iterator+=1
			continue

		entities_by_distance = game_map.nearby_entities_by_distance(ship)
		entities_by_distance = OrderedDict(sorted(entities_by_distance.items(), key=lambda t:t[0]))

		closest_enemy_ships = [entities_by_distance[distance][0] for distance in entities_by_distance if isinstance(entities_by_distance[distance][0], hlt.entity.Ship) and entities_by_distance[distance][0] not in team_ships]
		
		closest_planets_not_owned = game_map.all_planets()
		
		closest_unowned = []
		for planet in closest_planets_not_owned:
			if planet.owner == ship.owner:
				pass
			else:
				closest_unowned.append([planet,ship.calculate_distance_between(planet)])

		closest_unowned.sort(key=lambda x:x[1])

		
		if turns <= 1:
			target_planet = closest_unowned[iterator+3][0]
			iterator+=1
			start_direction.append(target_planet)
		elif turns < start_turns_strategy:
			logging.info(ship)
			logging.info(start_direction[iterator])
			logging.info("couldn't access it")
			target_planet = start_direction[iterator]
			iterator+=1


			if ship.can_dock(target_planet):
				command_queue.append(ship.dock(target_planet))
				continue
			else:
				navigate_command = ship.navigate(ship.closest_point_to(target_planet),
												game_map,
												speed = int(hlt.constants.MAX_SPEED),
												ignore_ships=True)
				if navigate_command:
					command_queue.append(navigate_command)
					logging.info(navigate_command)
					continue

		elif len(closest_unowned) > 0:
			target_planet = closest_unowned[0][0]
			if target_planet.is_owned():
				docked_enemy_ships = target_planet.all_docked_ships()
				navigate_command = ship.navigate(ship.closest_point_to(docked_enemy_ships[0]),
											game_map,
											speed = int(hlt.constants.MAX_SPEED),
											ignore_ships=True)
				if navigate_command:
					command_queue.append(navigate_command)
					continue
			elif ship.can_dock(target_planet):
				command_queue.append(ship.dock(target_planet))
				continue

			else:	
				navigate_command = ship.navigate(ship.closest_point_to(target_planet),
												game_map,
												speed = int(hlt.constants.MAX_SPEED),
												ignore_ships=True)
				if navigate_command:
					command_queue.append(navigate_command)
					continue
		elif len(closest_enemy_ships) > 0:
			logging.info("made it here")
			target_ship = closest_enemy_ships[0]
			navigate_command = ship.navigate(
								ship.closest_point_to(target_ship),
								game_map,
								speed=int(hlt.constants.MAX_SPEED),
								ignore_ships=False)
			if navigate_command:
				command_queue.append(navigate_command)
				continue
	game.send_command_queue(command_queue)