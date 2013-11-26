from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
from rabbits import RabbitFun

# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/runningrabbits_rpc',)

# Create server
server = SimpleXMLRPCServer(("localhost", 8000),
                            requestHandler=RequestHandler)
server.register_introspection_functions()

games = {}

class RabbitRPC:
    def getRunningGames(self):
        return map(lambda (k,v): {'name': k, 'map_size': v.getMapSize(), 'rabbits': v.getRabbits(), 'info':v.getExtendedStatus(), 'status':v.getStatus()}, games.iteritems())
		
    def createGame(self, name, map_size, rabbit_count):
		if games.has_key(name):
			raise Exception("Game "+ name+ "already exists!")
		else:
			games[name] = RabbitFun(name, int(map_size), int(rabbit_count))
			print games[name]
		return []
		
    def startGame(self, name):
		print "start", name
		if games.has_key(name) and games[name].getStatus() == 'created':
			games[name].start()
			return True
		else:
			raise Exception("Game "+ name+ "already started or does not exists!")
		
	
server.register_instance(RabbitRPC())
server.register_introspection_functions()
# Run the server's main loop
server.serve_forever()