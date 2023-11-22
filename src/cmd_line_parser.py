import argparse


class Parser:

    @classmethod
    def parse_command_line(cls):
        """Parse command-line arguments."""
        parser = argparse.ArgumentParser(description="Select 'Bot' options.")
        parser.add_argument(
            "-s", "--script",
            help="Name of bot script. "
            "Available: " 
            "'af_anticlock', "
            "'af_clockwise', "
            "'af_north', "
            "'af_east', "
            "'af_south', "
            "'af_west'.",
            required=True
        )
        parser.add_argument(
            "-cn", "--character_name", 
            help="Character's name.",
            required=True
        )
        return parser.parse_args()
