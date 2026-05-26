"""Entry point for the Mind Parliament simulation."""

from dotenv import load_dotenv
load_dotenv()  # must run before mind_simulation imports so Settings() sees the values

from mind_simulation.mind import main


if __name__ == "__main__":
    main()
