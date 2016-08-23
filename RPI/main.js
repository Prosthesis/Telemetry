/* set up webserver */
var express = require('express'); // web server
app = express();
server = require('http').createServer(app);
io = require('socket.io').listen(server); //web socket server
var clientExists = false;

/* open the serial port */
var serialport = require("serialport"); // include the library
var SerialPort = serialport.SerialPort; // make a local instance of the library
// // Then you open the port using new(...)
var arduino = new SerialPort("/dev/ttyACM0", {  
	baudRate : 115200,
    dataBits : 8,
    parity : 'none',
    stopBits: 1,
    parser: serialport.parsers.readline("\n"),
    flowControl : false,
});
console.log("SerialPort setup...");

server.listen(8080); // start the server on port 8080
app.use(express.static('public')); // let the server know that ./public/ contains the static webpages	
var brightness = 0; // current brightness of led
console.log("server is running...");


arduino.on("open", function () {
	console.log('opened serial communication');

	io.sockets.on('connection', function (socket) { // gets called whenever a client connects
		clientExists = true;
		console.log("client connected = [ " + clientExists + " ] ");
	});

    // Listens to incoming data
	arduino.on('data', function(data) { 
		var dataString = data.toString();
		console.log('Data: ' + dataString);
		brightness = parseInt(dataString.substring(1));
		
		if(clientExists) 
		{
			io.sockets.emit('led', {value: brightness}); // send updated brightness to all connected clients
		}
	});  
});  




// list serial ports:
// serialport.list(function (err, ports) {
//   ports.forEach(function(port) {
//     console.log(port.comName);
//   });
// });



