"""Provides command-line argument parsing functionality."""

import argparse


class Parser:
    """Holds methods related to command-line argument parsing.
    
    Methods
    ----------
    parse_command_line()
        Parse command-line arguments.

    """

    @classmethod
    def parse_command_line(cls):
        """Parse command-line arguments."""
        parser = argparse.ArgumentParser(description="Select 'Bot' options.")

        parser.add_argument("-s", "--script",
                            help="Name of bot script. "
                                 "Available: " 
                                 "'af_anticlock', "
                                 "'af_clockwise'.",
                            required=True)

        parser.add_argument("-cn", "--character_name", 
                            help="Character's name.",
                            required=True)

        parser.add_argument("-ov", "--official_version", 
                            help="Official or private 'Dofus Retro' server. "
                                 "Default = 'False'.",
                            default=False,
                            type=lambda x: cls.__str_to_bool(x))

        parser.add_argument("-dw", "--debug_window",
                            help="Launch visual debug window or not. "
                                 "Default = 'True'.",
                            default=True,
                            type=lambda x: cls.__str_to_bool(x))

        args = parser.parse_args()

        return args

    @classmethod
    def __str_to_bool(cls, argument):
        """Convert 'str' argument values to 'bool'."""
        if isinstance(argument, bool):
            return argument
        elif str(argument).lower() in ["true", "yes", "t", "y", "1"]:
            return True
        elif str(argument).lower() in ["false", "no", "f", "n", "0"]:
            return False
        else:
            raise argparse.ArgumentTypeError("Boolean value expected.")
