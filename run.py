#!/usr/bin/env python3

from BACKUP import *

if __name__ == "__main__":
	try:
		paths = StoreSearch88()
		if paths is False:
			raise Exception("No Formatted Drives Found")
		else:
			create88(*paths)
	except Exception as e:
		print(f"MAIN SECTION ERROR : {e}")
	# regen88(ReferencePath)
	input(" -- FINISHED!")
