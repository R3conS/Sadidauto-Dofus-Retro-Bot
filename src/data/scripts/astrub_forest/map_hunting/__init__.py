from .map_hunting_anticlock import Anticlock
from .map_hunting_clockwise import Clockwise
from .map_hunting_north import North
from .map_hunting_east import East
from .map_hunting_south import South
from .map_hunting_west import West

map_data = {
    "af_anticlock": Anticlock.data,
    "af_clockwise": Clockwise.data,
    "af_north": North.data,
    "af_east": East.data,
    "af_south": South.data,
    "af_west": West.data
}
