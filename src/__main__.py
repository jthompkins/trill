"""
ThreeDog Entrypoint
"""

from threedog import ThreeDog
import sys

if __name__ == "__main__":
	try:
		dj = ThreeDog()
		dj.run()
	except KeyboardInterrupt:
		print("Keyboard interrupt detected.")
		sys.exit(0)
	#client = discord.Client()
	#client.run(threedog_bot_constants.THREEDOG_CODE)