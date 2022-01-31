function paint_chart(){
	document.getElementById('kchart').innerHTML = "";
	var chartWidth = document.getElementById('kchart').width;
	var chartHeigth = document.getElementById('kchart').height;
	var chart = LightweightCharts.createChart(document.getElementById('kchart'), {
		width: chartWidth,
		height: chartHeigth,
		layout: {
			backgroundColor: 'transparent',
			textColor: 'rgba(255, 255, 255, 0.9)',
		},
		grid: {
			vertLines: {
				color: 'transparent',
			},
			horzLines: {
				color: 'transparent',
			},
		},
		crosshair: {
			mode: LightweightCharts.CrosshairMode.Normal,
		},
		rightPriceScale: {
			borderColor: 'rgba(197, 203, 206, 0.8)',
		},
		timeScale: {
			timeVisible: true,
			borderColor: 'rgba(197, 203, 206, 0.8)',
		},
	});
 
	function resizeChart() {
		chart.applyOptions({ width: $('#kchart').width(), height: $('#kchart').height() })
	}
	
	const ro = new ResizeObserver(entries => {
		for (let entry of entries) {
		  resizeChart();
		}
	  });
	  
	ro.observe(document.getElementById('kchart'))

	var candleSeries = chart.addCandlestickSeries({
		upColor: '#70FFFF',
		downColor: '#FFFF0A',
		borderDownColor: '#FFFF0A',
		borderUpColor: '#70FFFF',
		wickDownColor: '#FFFFFF',
		wickUpColor: '#FFFFFF',
	});


	var coin = document.getElementById("coin_pair");
	var time_int = document.getElementById("timeInterval");
	var data_out = {
			coin: coin.value,
			time_int: time_int.value
	};

	fetch('/home/chart', {
		method: "POST",
		credentials: "include",
		body: JSON.stringify(data_out),
		cahce: "no-cache",
		headers: new Headers({
			"Content-Type": "application/json"
		})
		}).then((r) => r.json()).then((response)=> {
			console.log(response)
			candleSeries.setData(response);
		}).catch(function(error) {
			console.log("Fetch error: " + error);
	});

	var coinLower = String(coin.value).toLowerCase();
	console.log(coinLower)
	var timeLower = String(time_int.value).toLowerCase();
	console.log(timeLower)
	var url = "wss://stream.binance.us:9443/ws/" + coinLower + "@kline_" + timeLower;
	console.log(url)
	var binanceSocket = new WebSocket(url);
	binanceSocket.onmessage = function(event){
		//console.log(event.data);
		var message = JSON.parse(event.data);
		var candlestick = message.k;
		candleSeries.update({
			time: candlestick.t/1000,
			open: candlestick.o,
			high: candlestick.h,
			low: candlestick.l,
			close: candlestick.c
		})

	}


}


function bot_call(){

	var rsi_buy = document.getElementById("RSI_buy");
	var rsi_sell = document.getElementById("RSI_sell");
	var in_position = document.getElementById("in_position");
	var coin_pair_bot = document.getElementById("coin_pair_bot");
	var pass = document.getElementById("pass");
	var bot_data = {
		rsi_buy : rsi_buy.value,
		rsi_sell : rsi_sell.value,
		in_position : in_position.value,
		coin_pair_bot : coin_pair_bot.value,
		pass : pass.value
	};

	fetch('/home/bot', {
		method: "POST",
		credentials: "include",
		body: JSON.stringify(bot_data),
		cahce: "no-cache",
		headers: new Headers({
			"Content-Type": "application/json"
		})
		}).then((r) => r.json()).then((response)=> {
			console.log(response);
		}).catch(function(error) {
			console.log("Fetch error: " + error);
	});

}