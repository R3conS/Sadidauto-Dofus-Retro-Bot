import argparse


class Parser:

    AVAILABLE_SCRIPTS = {
        "af_anticlock": "Astrub Forest - Anticlockwise pathing.",
        "af_clockwise": "Astrub Forest - Clockwise pathing.",
    }
    AVAILABLE_SERVERS = [
        "Boune",
        "Allisteria",
        "Fallanster",
        "Semi-like" # Abrak.
    ]

    @classmethod
    def parse_command_line(cls):
        parser = argparse.ArgumentParser(description="Provide 'Bot' options.")
        parser.add_argument(
            "--script", "-s", 
            choices=cls.AVAILABLE_SCRIPTS.keys(),
            help=f"Script name. Available: {', '.join(cls.AVAILABLE_SCRIPTS.keys())}.",
            required=True
        )
        parser.add_argument(
            "--character_name", "-cn", 
            required=True
        )
        parser.add_argument(
            "--server_name", "-sn", 
            choices=cls.AVAILABLE_SERVERS,
            required=True
        )
        return parser.parse_args()
