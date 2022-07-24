"""
Trill Entrypoint
"""

from trill import Trill
import sys

if __name__ == "__main__":
	try:
		dj = Trill()
		dj.run()
	except KeyboardInterrupt:
		print("Keyboard interrupt detected.")
		sys.exit(0)