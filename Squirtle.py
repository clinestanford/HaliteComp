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
game = hlt.Game("Squirtle")
# Then we print our start message to the logs
logging.info("Starting Squirtle")

VISION_DEPTH = 5 # how far can a ship see?
def shipActions(team_ships,game_map):
    # Here we define the set of commands to be sent to the Halite engine at the end of the turn
    command_queue = []
    startTime = int(round(time.time() * 1000))

    for ship in team_ships:
        currentTime = int(round(time.time() * 1000))
        if(currentTime - startTime > 1990):
            break
        if ship.docking_status != ship.DockingStatus.UNDOCKED:
            continue

        # Set up the closest entities arrays
        entities_by_distance = game_map.nearby_entities_by_distance(ship)
        entities_by_distance = OrderedDict(sorted(entities_by_distance.items(), key=lambda t: t[0]))
        closest_good_planets = []
        closest_friendly_ships = []
        for distance in entities_by_distance:
            entity = entities_by_distance[distance][0]
            if(isinstance(entity, hlt.entity.Planet)):
                if(not entity.is_owned() or (not entity.is_full() and ship.owner == entity.owner)):
                    closest_good_planets.append(entity)
            elif(isinstance(entity, hlt.entity.Ship)):
                if(entity in team_ships):
                    closest_friendly_ships.append(entity)

        # go to the closest non docked planet:
        if len(closest_good_planets) > 0:
            target_planet = closest_good_planets[0]

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
        # got to the closest friendly ship and pack together
        elif(len(closest_friendly_ships) > 2):
            target_ship = closest_friendly_ships[2];
            navigate_command = ship.navigate(
                ship.closest_point_to(target_ship),
                game_map,
                speed=int(hlt.constants.MAX_SPEED),
                ignore_ships=False)
            if navigate_command:
                command_queue.append(navigate_command)
    return command_queue

def runTurn():
    # Update the map for the new turn and get the latest version
    game_map = game.update_map()

    # For every ship that I control
    team_ships = game_map.get_me().all_ships()

    command_queue = shipActions(team_ships,game_map)

    # Send our set of commands to the Halite engine for this turn
    game.send_command_queue(command_queue)

while True: # Loop is one turn
    runTurn()
    # TURN END
# GAME END
