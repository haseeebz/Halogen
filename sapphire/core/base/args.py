import argparse


class SapphireArgs():

    def __init__(self):
        self.make_parser()

        self.dev: bool = False

        self.load_args()

    def make_parser(self):

        self.parser = argparse.ArgumentParser(
            prog = "sapphire",
            description = "Boots up Sapphire. See --help for help."
        )

        self.parser.add_argument(
            "--dev", 
            help = "Run sapphire in dev mode.", 
            default = False, 
            action = "store_true"
        )

    def load_args(self):
        args = self.parser.parse_args()
        self.dev = args.dev
