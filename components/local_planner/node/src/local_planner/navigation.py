"""A module providing navigation services"""

import json
from time import sleep
from math import dist
from random import choice
from typing import Callable, List, Tuple
from dataclasses import dataclass, field

import rospy

from local_planner.core import Vehicle
from local_planner.route_planning.route_annotation import AnnRouteWaypoint
from local_planner.config import town_spawns
from local_planner.route_planning.xodr_converter import XODRConverter, XodrMap
from local_planner.route_planning.route_planner import RoutePlanner


def load_town_param() -> str:
    while True:
        try:
            town = rospy.get_param('competition/town_name')
            print("Town is: ", town)
            break
        except KeyError:
            print('waiting for town rosparam')
            sleep(0.1)
    return town


def load_spawn_positions() -> List[Tuple[float, float]]:
    """Retrieve a list of possible spawn positions"""
    active_town = load_town_param()
    print("Is unknown town:", active_town not in town_spawns.spawns)
    return town_spawns.spawns[active_town]


def load_xodr_map() -> XodrMap:
    active_town = load_town_param()
    map_path = f"/app/res/xodr/{active_town}.xodr"
    return XODRConverter.read_xodr(map_path)


@dataclass
class CompetitionDrivingService:
    """Representing a proxy for computing the competition route."""
    vehicle: Vehicle
    update_route: Callable[[List[AnnRouteWaypoint]], None]
    map: XodrMap = None

    def __post_init__(self):
        if not self.map:
            self.map = load_xodr_map()

    def run_routing(self):
        """Launch the competition driving service. This will request a new route
         to the goal from the rosparam service."""
        while True:
            if not self.vehicle.is_ready:
                print('vehicle not ready yet!')
                sleep(0.1)
                continue

            goal_pos = CompetitionDrivingService._get_destination_from_rosparams()
            route = RoutePlanner.generate_waypoints(
                self.vehicle.pos, goal_pos, self.vehicle.orientation_rad, self.map)
            self.update_route(route)
            print('route found, shutting down navigation task')
            break

    @staticmethod
    def _get_destination_from_rosparams() -> Tuple[float, float]:
        while True:
            try:
                goal_x = float(rospy.get_param('competition/goal/position/x'))
                goal_y = float(rospy.get_param('competition/goal/position/y'))
                return (goal_x, goal_y)
            except Exception as err:
                print(f'error: {err}')
                print('waiting for competition rosparam ...')
                sleep(0.1)


@dataclass
class InfiniteDrivingService:
    """Representing a proxy for requesting navigation services."""
    vehicle: Vehicle
    update_route: Callable[[List[AnnRouteWaypoint]], None]
    destinations: List[Tuple[float, float]] = None
    current_dest: Tuple[float, float] = None
    map: XodrMap = None

    def __post_init__(self):
        if self.destinations is None:
            self.destinations = load_spawn_positions()
        if not self.map:
            self.map = load_xodr_map()

    def run_routing(self):
        """Launch the infinite driving mode. This will always request new routes
        to random destinations whenever the car completes the previous route."""
        list_except = lambda l, e: [x for x in l if x != e]

        while True:
            if not self.vehicle.is_ready:
                print('vehicle not ready yet!')
                sleep(0.1)
                continue

            if self.current_dest is None:
                self.current_dest = self.vehicle.pos

            if dist(self.vehicle.pos, self.current_dest) > 10.0:
                sleep(0.1)
                continue

            print('computing new route ...')
            self.current_dest = choice(list_except(self.destinations, self.current_dest))
            route = RoutePlanner.generate_waypoints(
                self.vehicle.pos, self.current_dest, self.vehicle.orientation_rad, self.map)
            self.update_route(route)
