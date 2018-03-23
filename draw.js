var width = 1000, height = 700;
var mouse = {x: 0, y:0, isDown: false};
var ball = {x: 250, y: 200, radius: 0};
var balls_arr = [], ans = [];
var opt_x, opt_y, opt_r = 0;
var n = 10;

function getMousePosition(e) {
	mouse.x = e.pageX - canvas.offsetLeft;
	mouse.y = e.pageY - canvas.offsetTop;
}

var mouseDown = function(e) {
	if(e.which == 1) {
		getMousePosition(e);
		ball.x = mouse.x;
		ball.y = mouse.y;
		ball.radius = 0;
		mouse.isDown = true;
	}
}

var dist = function(x1, y1, x2, y2) {
	return Math.sqrt((x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2));
}

var mouseUp = function(e) {
	if(e.which == 1) {
		getMousePosition(e);
		ball.radius = dist(mouse.x, mouse.y, ball.x, ball.y);
		mouse.isDown = false;
		var tmp = Object.assign({}, ball);
		balls_arr.push(tmp);
	}
}

var setup = function() {
	canvas = document.getElementById("myCanvas");
	ctx = canvas.getContext("2d");
	
	canvas.onmousemove = getMousePosition;
	canvas.onmousedown = mouseDown;
	canvas.onmouseup = mouseUp;

	ctx.fillStyle = "red";
	loopTimer = setInterval(loop, 1000 / 40);
}

var loop = function() {
	ctx.clearRect(0, 0, width, height);
	ctx.save();
	for(var i = 0; i < balls_arr.length; i++) {
		ctx.fillStyle = "red";
		ctx.beginPath();
		ctx.arc(balls_arr[i].x, balls_arr[i].y, balls_arr[i].radius, 0, 2*Math.PI, true);
		ctx.fill();
		ctx.closePath();
		ctx.restore();
	}
	for(var i = 0; i < ans.length; i++) {
		ctx.fillStyle = "green";
		ctx.beginPath();
		ctx.arc(ans[i].x, ans[i].y, ans[i].radius, 0, 2*Math.PI, true);
		ctx.fill();
		ctx.closePath();
		ctx.restore();
	}
	ctx.fillStyle = "yellow";
	ctx.beginPath();
	ctx.arc(opt_x, opt_y, opt_r, 0, 2*Math.PI, true);
	ctx.fill();
	ctx.closePath();
	ctx.restore();
	//console.log(balls_arr);
	//console.log(ctx.fillStyle);
	//console.log(ans);
}

setup();

var gen = 0;

var maxRadius = function(x, y) {
	var minDist = 100000000;
	for(var i = 0; i < balls_arr.length; i++) {
		var d = dist(balls_arr[i].x, balls_arr[i].y, x, y) - balls_arr[i].radius;
		if(d <= 0)	return 0;
		if(d < minDist)	minDist = d;
	}
	if(x - minDist < 0)			minDist = x;
	if(x + minDist > width)		minDist = width - x;
	if(y - minDist < 0)			minDist = y;
	if(y + minDist > height)	minDist = height - y;
	return minDist;
}

var crossover = function(a, b) {
	console.log(a);
	console.log(b);
	var r1 = (a.radius * a.radius) / ((a.radius * a.radius) + (b.radius * b.radius));
	var r2 = 1 - r1;
	ball.x = (a.x * r1) + (b.x * r2);
	ball.y = (a.y * r1) + (b.y * r2);
	ball.radius = maxRadius(ball.x, ball.y);
	if(ball.radius === 0) {
		if(r1 > r2)	ball.x = a.x, ball.y = a.y, ball.radius = a.radius;
		else		ball.x = b.x, ball.y = b.y, ball.radius = b.radius;
	}
	return ball;
}

var mutate = function(a) {
	var dice3 = Math.random();
	if(dice3 < 0.3) {
		var orignal_x = a.x, orignal_y = a.y, orignal_r = a.r;
		a.x += width/10 - (Math.floor(Math.random() * width))/5;
		if(a.x < 0)			a.x = 0;
		if(a.x > width)		a.x = width;
		a.y += height/10 - (Math.floor(Math.random() * height)/5);
		if(a.y < 0)			a.y = 0;
		if(a.y > height)	a.y = height;
		a.radius = maxRadius(a.x, a.y);
		if(a.radius == 0)	a.x = orignal_x, a.y = orignal_y, a.r = orignal_r;
	}
	return a;
}

var calc = function() {
	console.log("Generation: " + gen);
	gen++;
	if(gen == 1) {
		for(var i = 0; i < n; i++) {
			ball.x = Math.random() * width, ball.y = Math.random() * height;
			ball.radius = maxRadius(ball.x, ball.y);
			if(ball.radius != 0) {
				var tmp = Object.assign({}, ball);
				ans.push(tmp);
			} else {
				i--;
			}
		}
		return ;
	} else {
		var new_gen = [], p = [], tot = 0, prev = 0;
		for(var i = 0; i < n; i++) {
			tot += (ans[i].radius * ans[i].radius);
		}
		for(var i = 0; i < n; i++) {
			p.push(((ans[i].radius * ans[i].radius) / tot) + prev);
			prev += (ans[i].radius * ans[i].radius) / tot;
			console.log(prev);
		}
		for(var i = 0; i < n; i++) {
			var dice1 = Math.random(), dice2 = Math.random();
			var id1, id2;
			for(var j = 0; j < n; j++) {
				if(dice1 <= p[j]) {
					id1 = j;
					break;
				}
			}
			for(var j = 0; j < n; j++) {
				if(dice2 <= p[j]) {
					id2 = j;
					break;
				}
			}
			var tmp = mutate(crossover(ans[id1], ans[id2]));
			new_gen.push(Object.assign({}, tmp));
		}
		ans = new_gen;
	}
}

var optimal = function() {
	opt_x = 0, opt_y = 0, opt_r = 0;
	for(var t_x = 0; t_x <= width; t_x += 0.1) {
		for(var t_y = 0; t_y <= height; t_y += 0.1) {
			var tmp = maxRadius(t_x, t_y);
			if(tmp > opt_r) {
				opt_r = tmp;
				opt_x = t_x, opt_y = t_y;
			}
		} 
	}
}