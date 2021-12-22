"""
Module to provide for "-m pyscan" access to the module,
as if it was run from the console.
"""
import pyscan


def main():
    """
    Main entry point.  Exposed in this manner so that the setup
    entry_points configuration has something to execute.
    """
    pyscan.PyScan().main()


if __name__ == "__main__":
    main()
