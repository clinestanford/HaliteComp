"""
Turtle bot:
Load the closest starting planet as much as possible.
If the closest planet is full, move to the next closest planet.
"""
# Let's start by importing the Halite Starter Kit so we can interface with the Halite engine
import hlt
# Then let's import the logging module so we can print out information
import logging

from collections import OrderedDict
import time

# GAME START
game = hlt.Game("Blastoise")
# Then we print our start message to the logs
logging.info("Starting Blastoise")

shipsBeingAttacked = []
def shipActions(team_ships,game_map,turn):
    # Here we define the set of commands to be sent to the Halite engine at the end of the turn
    command_queue = []
    startTime = int(round(time.time() * 1000))

    for ship in team_ships:
        currentTime = int(round(time.time() * 1000))
        if(currentTime - startTime > 1990):
            break;
        # skip the docked planets
        if ship.docking_status != ship.DockingStatus.UNDOCKED:
            continue

        entities_by_distance = game_map.nearby_entities_by_distance(ship)
        entities_by_distance = OrderedDict(sorted(entities_by_distance.items(), key=lambda t: t[0]))
        closest_friendly_planets = []
        closest_enemy_ships = []
        closest_enemy_planets = []
        closest_open_planets = []
        for distance in entities_by_distance:
            entity = entities_by_distance[distance][0]
            if(isinstance(entity, hlt.entity.Planet)):
                if(not entity.is_owned() or (not entity.is_full() and ship.owner == entity.owner)):
                    closest_open_planets.append(entity)
                if(ship.owner != entity.owner):
                    closest_enemy_planets.append(entity)
                if(ship.owner == entity.owner):
                    closest_friendly_planets.append(entity)
            elif(isinstance(entity, hlt.entity.Ship)):
                if(entity not in team_ships):
                    closest_enemy_ships.append(entity)

        # attack everything after turn 70
        if turn > 100:
            if(len(closest_enemy_ships)> 0):
                navigate_command = ship.navigate(
                    ship.closest_point_to(closest_enemy_ships[0]),
                    game_map,
                    speed=int(hlt.constants.MAX_SPEED),
                    ignore_ships=False
                )
                if(navigate_command):
                    command_queue.append(navigate_command)
                    continue

        # attack ships that are close to your
        if(len(closest_enemy_ships) > 0):
            target_ship = closest_enemy_ships[0]
            if(ship.calculate_distance_between(target_ship) < 10):
                navigate_command = ship.navigate(
                    ship.closest_point_to(target_ship),
                    game_map,
                    speed=int(hlt.constants.MAX_SPEED),
                    ignore_ships=False)
                if (navigate_command and not target_ship.id in shipsBeingAttacked):
                    shipsBeingAttacked.append(target_ship.id)
                    command_queue.append(navigate_command)
                    continue

        # go to the closest non docked planet:
        if len(closest_open_planets) > 0:
            target_planet = closest_open_planets[0]

            if (ship.can_dock(target_planet)):
                command_queue.append(ship.dock(target_planet))
                continue
            else:
                # don't go to planets far away
                if(ship.calculate_distance_between(target_planet) < 50):
                    navigate_command = ship.navigate(
                        ship.closest_point_to(target_planet),
                        game_map,
                        speed=int(hlt.constants.MAX_SPEED),
                        ignore_ships=False)
                    if navigate_command:
                        command_queue.append(navigate_command)
                        continue

        # hang out at the closest friendly planet
        if(len(closest_friendly_planets) > 0):
            target_planet = closest_friendly_planets[0];
            navigate_command = ship.navigate(
                ship.closest_point_to(target_planet),
                game_map,
                speed=int(hlt.constants.MAX_SPEED),
                ignore_ships=False)
            if navigate_command:
                command_queue.append(navigate_command)
                continue

    return command_queue

def runTurn(turn):
    # Update the map for the new turn and get the latest version
    game_map = game.update_map()

    # For every ship that I control
    team_ships = game_map.get_me().all_ships()

    command_queue = shipActions(team_ships,game_map,turn)

    # Send our set of commands to the Halite engine for this turn
    game.send_command_queue(command_queue)

turn = 0
while True: # Loop is one turn
    runTurn(turn)
    turn = turn + 1
    # TURN END
# GAME END