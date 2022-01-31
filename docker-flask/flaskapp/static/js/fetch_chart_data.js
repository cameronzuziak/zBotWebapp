function get_data() {
	var coin = document.getElementById("coin_pair");
	var period = document.getElementById("period");
	var data_out = {
		coin: coin.value,
		period: period.value
	};

	recieve = fetch('/home/chart', {
		method: "POST",
		credentials: "include",
		body: JSON.stringify(data_out),
		cahce: "no-cache",
		headers: new Headers({
			"Content-Type": "application/json"
		})
	}).then(function(response) {
		if (response.status !== 200) {
		  console.log(`Looks like there was a problem. Status code: ${response.status}`);
		  return;
		}
		response.json().then(function(data) {
		  console.log(data);
		});
	  })
	  .catch(function(error) {
		console.log("Fetch error: " + error);
	});
}