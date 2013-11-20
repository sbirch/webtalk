import time

timers = []

def tick(label=None):
	timers.insert(0, (label, time.time()))

def tock():
	label, st = timers.pop(0)
	elapsed = (time.time() - st)
	if elapsed < 1:
		elapsed = '%.1fms' % (elapsed*1000.0)
	else:
		elapsed = '%.2fs' % elapsed
	if label != None:
		print '%s took %s' % (label, elapsed)
	else:
		print '%s' % elapsed