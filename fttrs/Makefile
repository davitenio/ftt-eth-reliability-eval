NUM_SLAVES = 3

fttrs.prism: fttrs.pp
	prismpp fttrs.pp $(NUM_SLAVES) > fttrs.prism

fttrs.pp: fttrs.base ../common.inc ../rewards.inc
	../process_include.py fttrs.base > fttrs.pp
