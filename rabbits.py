import sys, random, time
import threading
from threading import Thread, Lock, Event, Condition
import urllib, urllib2, re

#game_over_event = Event()
#start_condition = Condition()
#game_over_event.clear()

class Field(Thread):
	_carrot_map = {}
	_size = 0
	_lock = Lock()
	_carrot_condition = Condition()
  
	def __init__(self, size, game_over_event):
		Thread.__init__(self)
		self._size = size
		#add carrots to map
		self._carrot_map = [( 1 if random.randrange(10) > 7 else 0) for i in range(size*size)]
		print self._carrot_map
		print "Map size: %dx%d, carrots: %d" % (size, size, self.getCarrotCount())
		self.game_over_event = game_over_event
		
	def eatCarrot(self, pos):
		index = pos[0] * self._size + pos[1]
		#echo "Eat carrot @ {$index} {$this->carrot_map[$index]}".PHP_EOL;
		# somehow $this->carrot_map[$index] = false; does nothing
		self._lock.acquire()
		#$map = $this->carrot_map;
		if (self._carrot_map[index]):
			self._carrot_map[index] = 0
			#this->carrot_map = $map; // according to examples, writing to the object scope will always cause locking
			#echo "Eaten carrot @ {$index} {$this->carrot_map[$index]}".PHP_EOL;
			self._lock.release()
			
			self._carrot_condition.acquire()
			self._carrot_condition.notify()
			self._carrot_condition.release()
			return 1
		
		self._lock.release()
		return 0
		
	
	def getCarrotCount(self):
		return sum(self._carrot_map)
	
	def isGameOver(self):
		print "isGameOver?", self.getCarrotCount() 
		return self.getCarrotCount() == 0
	
	
	def getNextCell(self, pos):
		(dx, dy) = (random.randint(-1, 1), 0)
		if (dx == 0):
			dy = random.randint(-1, 1)
		#print dx, dy
		pos = (abs((pos[0] + dy ) % self._size), abs((pos[1] + dx ) % self._size))

		return (pos, self.eatCarrot(pos))
	
	
	def run(self):
		self._carrot_condition.acquire()
		while(not self.isGameOver() ):
			#print "wait"
			self._carrot_condition.wait()
		self._carrot_condition.release()
		#print "game_over_event"
		self.game_over_event.set()
		print "game_over_event set"

class Rabbit(Thread):
	#_field = None
	#_pos = ()
	#name = ""
	#carrots = 0

	def __init__(self, name, field, pos, start_condition, game_over_event):
		Thread.__init__(self)
		print "Placing rabbit: %s to location [%d,%d]" % (name, pos[0], pos[1])
		self._field = field
		self._pos = pos
		self.name = name
		self.moves = 0
		self.start_condition = start_condition
		self.game_over_event = game_over_event
		self.carrots = 0

	def run(self):
		self.start_condition.acquire()
		self.start_condition.wait()
		self.start_condition.release()

		print "Rabbit: %s start @ %f" % (self.name, time.time())
		while (not self.game_over_event.is_set()):
			(pos, carrot) = self._field.getNextCell(self._pos);
			self.carrots += carrot
			print "Moving rabbit: %s from (%d, %d) to (%d,%d), found carrot? %d, carrots eaten: %d" % (self.name, self._pos[0], self._pos[1], pos[0], pos[1], carrot, self.carrots);
			if (carrot):
				print "Rabbit %s found carrot @ (%d,%d)" % (self.name, pos[0], pos[1])
			
			self._pos = pos;
			time.sleep(0.3);
		
		print "Rabbit "+self.name+" is exiting field, carrots eaten: "+str(self.carrots);
		#flush();
		
class RabbitFun(Thread):
	data = threading.local()
	"""
	_map_size = 10
	_names = []
	_rabbits = []
	_status = "created"
	field = None
	"""
	def __init__(self, name, map_size, rabbit_count):
		self._map_size = map_size
		print "Generating rabbit names...", 
		self.generateNames(rabbit_count)
		print "done"
		print self._names
		self.game_over_event = Event()
		self.start_condition = Condition()
		self.game_over_event.clear()
		
		self.field = Field(self._map_size, self.game_over_event)
		self._status = 'created'
		

		Thread.__init__(self)

	def run(self) :
		self._status = 'starting'
		
		self.field.start()
		start = int(time.time())+1
		self._rabbits = []
		#print self, "self._rabbits 1 ", self._rabbits
		for name in self._names:
			self._rabbits.append(Rabbit(name, self.field, (random.randint(0,self._map_size-1), random.randint(0,self._map_size-1)), self.start_condition, self.game_over_event))
		
		print self, "self._rabbits 2 ", self._rabbits
		
		for rabbit in self._rabbits:
			rabbit.start()
      
		self.start_condition.acquire()
		self.start_condition.notifyAll()
		self.start_condition.release()
		
		self._status = 'running'
    
		try:
			while not self.game_over_event.is_set():
				time.sleep(.1)
		except KeyboardInterrupt:
			print "attempting to close threads"
			self.game_over_event.set()
			print "threads successfully closed"
			
		self._status = 'stoping'

		for rabbit in self._rabbits:
			rabbit.join()
		print "rabbits joined"
		self.field.join()
		self._status = 'finished'
		
		winners = sorted(self._rabbits, key= lambda rabbit: rabbit.carrots, reverse=True);
		winner = winners[0];
		print "Winner is: %s with %d carrots!" % (winner.name, winner.carrots)

		print "Top:"
		for rabbit in winners:
			print "#%d: %s ate %d carrots!" % (0, rabbit.name, rabbit.carrots)
		
	def getMapSize(self):
		return self._map_size
		
	def getRabbitCount(self):
		return len(self._rabbits)
		
	def getRabbits(self):
		return self._names
	
			
	def getStatus(self):
		return self._status
		
	def getExtendedStatus(self):
		if self._status == 'created':
			return 'Press start to play the game'
		elif self._status == 'running':
			return 'Carrots remaining: %d' % self.getCarrotCount()
		elif self._status == 'finished':
			winners = sorted(self._rabbits, key= lambda rabbit: rabbit.carrots, reverse=True)
			winner = winners[0]
			return "Winner is: %s with %d carrots!" % (winner.name, winner.carrots)		
		else:
			return self._status
								
	def getCarrotCount(self):
		return self.field.getCarrotCount()
		
	def generateNames(self, count):
    #http://www.voidspace.org.uk/python/articles/urllib2.shtml
      
		url = 'http://listofrandomnames.com/index.cfm?generated'
		values = {'action' : 'main.generate',
				'numberof' : count,
				'nameType' : 'na',
				'fnameonly' : 1,
				'allit' : 1 }

		data = urllib.urlencode(values)
		req = urllib2.Request(url, data)
		response = urllib2.urlopen(req)
		the_page = response.read()
		#print the_page
		self._names = re.findall('<a class="firstname"[^>]+>([^<]+)</a>', the_page)
  
if __name__ == "__main__":
	fun = RabbitFun(int(sys.argv[1]), int(sys.argv[2]))
	fun.start()
	fun.join()
