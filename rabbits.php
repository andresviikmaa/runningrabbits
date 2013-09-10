<pre>
<?php
// online version: http://b35729.zed.ee/ds/hw1/rabbits.php
// requirements: http://ee1.php.net/manual/en/book.pthreads.php
/*
	Future enchancments:
		Detect rabbit collisions.
			both rabbits die
			new rabbit is born
		Add wolf
		Mount brain into rabbits.
		Add graphics
*/
class Field extends Thread  {
	private $carrot_map;
	private $size;
	private $mutex;
	public function __construct($size) {
		$this->mutex = Mutex::create();
		$this->size = $size;
		// add carrots to map
		$this->carrot_map = array_map(function() { return rand(0, 10) > 7 ? true : false;} , array_fill(0, $size*$size, 0));
		echo "Map size: {$size}x{$size}, carrots: {$this->getCarrotCount()}".PHP_EOL;
	}
	
	protected function eatCarrot($pos) {
		$index = $pos[0] * $this->size + $pos[1];
		//echo "Eat carrot @ {$index} {$this->carrot_map[$index]}".PHP_EOL;
		// somehow $this->carrot_map[$index] = false; does nothing
		Mutex::lock($this->mutex);
		$map = $this->carrot_map;
		if ($map[$index]) {
			$map[$index] = false;
			$this->carrot_map = $map; // according to examples, writing to the object scope will always cause locking
			//echo "Eaten carrot @ {$index} {$this->carrot_map[$index]}".PHP_EOL;
			Mutex::unlock($this->mutex);
			return true;
		};
		Mutex::unlock($this->mutex);
		return false;
	}	
	public function getCarrotCount() {
		return array_sum($this->carrot_map);
	}
	public function isGameOver() {
		return $this->getCarrotCount() == 0;
	}
	
	public function getNextCell($pos) {
		$dx = rand(-1, 1);
		$dy = $dx == 0 ? (rand(0, 1) == 0 ? -1 : 1)  : 0;
		//echo "$dx, $dy".PHP_EOL;
		$pos[0] = ($pos[0] + $dy ) % $this->size;
		$pos[1] = ($pos[1] + $dx ) % $this->size;
		if ($pos[0] < 0) $pos[0] = 1;
		if ($pos[1] < 0) $pos[1] = 1;
		return array($pos, $this->eatCarrot($pos));
	}
	
	public function run() {
		while(!$this->isGameOver()) {
			#echo "Carrots remaining: {$this->getCarrotCount()}".PHP_EOL;
			sleep(0.5);
		}
		//echo "carrots remaining: {$this->getCarrotCount()}".PHP_EOL;
		echo "Game is over!".PHP_EOL;
		flush();
	}
}

class Rabbit extends Thread {
	private $field;
	private $pos;
	public $name;
	public $carrots;
	private $start_time;

	public function __construct($name, $field, $pos, $start_time){
		echo "Placing rabbit: {$name} to location [".$pos[0].",{$pos[1]}]".PHP_EOL;
		flush();
		$this->field = $field;
		$this->pos = $pos;
		$this->name = $name;
		$this->moves = 0;
		$this->start_time = $start_time;
	}

	public function run(){
		while (microtime(true) < $this->start_time);
		echo "Rabbit: {$this->name} start @ ".microtime(true).PHP_EOL;
		
		while (!$this->field->isGameOver()) {
			list($pos, $carrot) = $this->field->getNextCell($this->pos);
			$this->carrots += (int)$carrot;
			//echo "Moving rabbit: {$this->name} from ({$this->pos[0]}, {$this->pos[1]}) to [{$pos[0]},{$pos[1]}], found carrot? {$carrot}, carrots eaten: {$this->carrots}".PHP_EOL;
			if ($carrot) {
				echo "Rabbit {$this->name} found carrot @ ({$this->pos[0]}, {$this->pos[1]})".PHP_EOL;
				flush();
			}
			$this->pos = $pos;
			#sleep(0.3);
		}
		#echo "Rabbit {$this->name} is exiting field, carrots eaten: {$this->carrots}".PHP_EOL;
		#flush();
	}
	

}

		
class RabbitFun
{
	private $map_size = 10;
	private $names = array();
	private $rabbits = array();
	
	public function __construct($map_size, $rabbit_count){
		$this->map_size = $map_size;
		echo "Generating rabbit names...";
		$this->generateNames($rabbit_count);
		echo "done".PHP_EOL;
	}	
	
	public function run() {
		$field = new Field($this->map_size);
		#return;
		$field->start();
		$start = time()+1;
		foreach ($this->names as $name) {
			$this->rabbits[] = new Rabbit($name, $field, array(rand(0,$this->map_size-1), rand(0,$this->map_size-1)),$start);
		}
		foreach ($this->rabbits as $rabbit) {
			$rabbit->start();
		}
		foreach ($this->rabbits as $rabbit) {
			$rabbit->join();
		}
		$field->join();
		
		usort($this->rabbits, function($a, $b) {return $a->carrots < $b->carrots;})[0];
		$winner = $this->rabbits[0];
		echo "Winner is: {$winner->name} with {$winner->carrots} carrots!".PHP_EOL;
		flush();
		echo "Top:".PHP_EOL;
		foreach ($this->rabbits as $i => $rabbit) {
			echo "#".($i+1).": {$rabbit->name} ate {$rabbit->carrots} carrots!".PHP_EOL;
		}
	}
	protected function generateNames($count) {
		$opts = array('http' =>
		  array(
			'method'  => 'POST',
			'header' => "Connection: close\r\n".
                        "Content-Type: application/x-www-form-urlencoded\r\n",
                       
			'content' => http_build_query (array(
				'action' =>'main.generate',
				'numberof' => $count,
				'nameType' =>'na',
				'fnameonly' => 1,
				'allit' => 1,
			)),
			'timeout' => 60
		  )
		);
								
		$context  = stream_context_create($opts);
		$url = 'http://listofrandomnames.com/index.cfm?generated';
		$result = file_get_contents($url, false, $context, -1, 40000);	
		preg_match_all('#<a class="firstname"[^>]+>([^<]+)</a>#', $result, $matches);
		$this->names = $matches[1];
	}
}

if (isset($_SERVER["SERVER_NAME"])) {
?>
Some form should be here

<?php
	$fun = new RabbitFun(3, 3);
	$fun->run();
} else if ($argc == 3) {
	$fun = new RabbitFun($argv[1], $argv[2]);
	$fun->run();
} else {
	echo "Usage: php rabbits.php <field side length> <rabbit count>".PHP_EOL;
}
