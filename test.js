console.log("Starting Three Dog")

const { exec } = require('child_process');

const child = exec('python C:\\Users\\prese\\Desktop\\scripts\\discord\\threedogbot\\threedog_bot.py');

child.stdout.on('data', (data) => {
	console.log(`child stdout:\n${data}`);
	
});

child.stderr.on('data', (data) => {
	console.log(`child stderr:\n${data}`);
});
