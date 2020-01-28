/**
 * bot-controller
 *
 * @description :: Server-side actions for handling incoming requests.
 * @help        :: See https://sailsjs.com/docs/concepts/actions
 */

module.exports = {
  
  fn: async function () {
	const { exec } = require('child_process');

	const child = exec('python C:\\Users\\prese\\Desktop\\scripts\\discord\\threedogbot\\threedog_bot.py');

	child.stdout.on('data', (data) => {
        console.log(`child stdout:\n${data}`);

	});

	child.stderr.on('data', (data) => {
        console.log(`child stderr:\n${data}`);
	});

	var exec = require('child_process').exec;
	var bot_command = 'python threedog_bot.py C:\Users\prese\Desktop\scripts\discord\threedogbot.py';
	exec(bot_command, function(error, stdout, stderr) {
	});
	return {};
  }
};

