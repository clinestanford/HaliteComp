import hlt
import logging

from collections import OrderedDict

game = hlt.Game("StrongestPlanetBot")
logging.info("Starting StrongestPlanetBot!")

ownedPlanets = []
cycleCount = 0
prevOwned = ''

while True:
	# TURN START
	# Update the map for the new turn and get the latest version
	game_map = game.update_map()

	#get a list of all planets on the map and check to see which are owned by me
	allPlanets = game_map.all_planets()
	for planet in allPlanets:
		if planet.is_owned() and planet.owner.id == game_map.get_me().id:
			ownedPlanets.append(planet)
	
	#if I only own 1 planet, check to see if it is the same as
	#the one owned on the last turn and increment cycleCount if that is the case
	if len(ownedPlanets) == 1:
		if prevOwned != '' and ownedPlanets[0].id == prevOwned.id:
			cycleCount += 1 
		else:
			prevOwned = ownedPlanets[0]
	else:
		cycleCount = 0
		ownedPlanets = []

	command_queue = []

	#a list of all the ships for my team
	teamShips = game_map.get_me().all_ships()

	for ship in teamShips:
		#skip the ship if it is currently docked, docking, or undocking
		if ship.docking_status != ship.DockingStatus.UNDOCKED:
			continue

		#get the nearby entities (ships and planets) to a ship and sort by distance
		nearbyEntities = game_map.nearby_entities_by_distance(ship)
		entitiesByDistance = OrderedDict(sorted(nearbyEntities.items(), key=lambda t: t[0]))

		#get subsets of the entitiesByDistance array
		closestEmptyPlanets = [entitiesByDistance[distance][0] for distance in entitiesByDistance if isinstance(entitiesByDistance[distance][0], hlt.entity.Planet) and not entitiesByDistance[distance][0].is_owned()]
		closestEnemyShips = [entitiesByDistance[distance][0] for distance in entitiesByDistance if isinstance(entitiesByDistance[distance][0], hlt.entity.Ship) and entitiesByDistance[distance][0] not in teamShips]
		closestEnemyPlanets = [entitiesByDistance[distance][0] for distance in entitiesByDistance if isinstance(entitiesByDistance[distance][0], hlt.entity.Planet) and entitiesByDistance[distance][0].is_owned() and entitiesByDistance[distance][0].owner.id != game_map.get_me().id]
		
		#if I have 8 or fewer ships, go mine other empty planets to make more
		if len(teamShips) <= 8:
			if len(closestEmptyPlanets) > 0:
				planets = closestEmptyPlanets
			else: #if there are no empty planets, go attack the strongest planet anyway
				planets = sorted(closestEnemyPlanets, key=lambda x: len(x._docked_ship_ids), reverse=True)
				if len(planets) > 0:
					firstIds = planets[0]._docked_ship_ids
					lastIds = planets[len(planets)-1]._docked_ship_ids
					if len(firstIds) == len(lastIds):
						planets = closestEnemyPlanets

		else: #sort the closestEnemyPlanets instead by the number of ships docked on the planets in descending order
			planets = sorted(closestEnemyPlanets, key=lambda x: len(x._docked_ship_ids), reverse=True)
			if len(planets) > 0:
				firstIds = planets[0]._docked_ship_ids
				lastIds = planets[len(planets)-1]._docked_ship_ids
				if len(planets) > 0 and len(firstIds) == len(lastIds):
					planets = closestEnemyPlanets

		if len(planets) > 0:
			#target the closest empty planet of the planet with the most ships docked
			targetPlanet = planets[0]

			#if the players are stuck in a cycle where both are dying at the same rate,
			#choose the next closest planet instead
			if cycleCount > 10 and len(planets) > 1:
				targetPlanet = planets[1]

			#if the targetPlanet is empty and the ship is close enough to dock, then dock
			if not targetPlanet.is_owned() and ship.can_dock(targetPlanet):
				command_queue.append(ship.dock(targetPlanet))

			#if the targetPlanet is empty but not close enough, move toward it
			elif not targetPlanet.is_owned():
				navigate_command = ship.navigate(
					ship.closest_point_to(targetPlanet),
					game_map,
					speed=int(hlt.constants.MAX_SPEED),
					ignore_ships=False)
				if navigate_command:
					command_queue.append(navigate_command)

			#if the targetPlanet is owned by an enemy, get a list of the ships
			#docked on the targetPlanet and begin to attack them
			else:
				dockedEnemyShips = targetPlanet.all_docked_ships()
				targetShip = dockedEnemyShips[0]
				navigate_command = ship.navigate(
								ship.closest_point_to(targetShip),
								game_map,
								speed=int(hlt.constants.MAX_SPEED),
								ignore_ships=True)
				if navigate_command:
					command_queue.append(navigate_command)

		#this statement will be hit if I have taken all planets 
		# but there are still enemy ships on the board
		elif len(closestEnemyShips) > 0:
			logging.info(closestEnemyShips[0])
			targetShip = closestEnemyShips[0]
			navigate_command = ship.navigate(
								ship.closest_point_to(targetShip),
								game_map,
								speed=int(hlt.constants.MAX_SPEED),
								ignore_ships=False)
			if navigate_command:
				command_queue.append(navigate_command)

	# Send our set of commands to the Halite engine for this turn
	game.send_command_queue(command_queue)
	# TURN END
# GAME END