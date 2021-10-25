
(function ($, window, document) {

    class HomeScript{
        constructor() {
            this.debug = false;
	    this.urlBox = this.debug ? "":"http://raspberrypi:5000/box";
            this.ticks_off = 0;
            this.eventPage();
        }

        eventPage(){
            let that = this;
            window.addEventListener('DOMContentLoaded', event => {
                const sidebarToggle = document.body.querySelector('#sidebarToggle');
                if (sidebarToggle) {
                    sidebarToggle.addEventListener('click', event => {
                        event.preventDefault();
                        document.body.classList.toggle('sb-sidenav-toggled');
                        localStorage.setItem('sb|sidebar-toggle', document.body.classList.contains('sb-sidenav-toggled'));
                    });
                }
            });

            document.getElementById("a1").innerHTML = 0;
	    document.getElementById("a2").innerHTML = 0;
	    document.getElementById("a3").innerHTML = 0;
	    document.getElementById("a4").innerHTML = 0;
	    document.getElementById("a5").innerHTML = 0;
	    document.getElementById("a6").innerHTML = 0;
	    document.getElementById("a7").innerHTML = 0;
	    document.getElementById("a8").innerHTML = 0;
            document.getElementById("g1").innerHTML = 0;
	    document.getElementById("g2").innerHTML = 0;
	    document.getElementById("g3").innerHTML = 0;
	    document.getElementById("g4").innerHTML = 0;
	    document.getElementById("g5").innerHTML = 0;
	    document.getElementById("g6").innerHTML = 0;
	    document.getElementById("g7").innerHTML = 0;
	    document.getElementById("g8").innerHTML = 0;
            document.getElementById("moget").innerHTML = 0;
            document.getElementById("mtget").innerHTML = 0;

            document.getElementById("gpio1_go").onclick = function() {that.gpio1_action()};
	    document.getElementById("gpio2_go").onclick = function() {that.gpio2_action()};
	    document.getElementById("gpio3_go").onclick = function() {that.gpio3_action()};
	    document.getElementById("gpio4_go").onclick = function() {that.gpio4_action()};
	    document.getElementById("gpio5_go").onclick = function() {that.gpio5_action()};
	    document.getElementById("gpio6_go").onclick = function() {that.gpio6_action()};
	    document.getElementById("gpio7_go").onclick = function() {that.gpio7_action()};
	    document.getElementById("gpio8_go").onclick = function() {that.gpio8_action()};

	    document.getElementById("mo_go").onclick = function() {that.mo_action()};
	    document.getElementById("mt_go").onclick = function() {that.mt_action()};
	    document.getElementById("reset").onclick = function() {that.reset_action()};


	    // Update state
            setInterval(function(){that.update_state();}, 500);
        }


	mo_action() {
            var val = document.getElementById("mo").value;

            var http = new XMLHttpRequest();
            http.open("POST", this.urlBox, true);
            http.setRequestHeader("Content-Type", "application/json");
            var data = JSON.stringify({"parameter": "sampleMO", "value": val});
            http.onload = function () {
              if(http.status == 200)
                alert("OK: command sent");
              else
                alert(http.status);
            };
            http.onerror = function() { alert('ERROR: no server response'); };
            http.send(data);
        }

	mt_action() {
            var val = document.getElementById("mt").value;

            var http = new XMLHttpRequest();
            http.open("POST", this.urlBox, true);
            http.setRequestHeader("Content-Type", "application/json");
            var data = JSON.stringify({"parameter": "sampleMT", "value": val});
            http.onload = function () {
              if(http.status == 200)
                alert("OK: command sent");
              else
                alert(http.status);
            };
            http.onerror = function() { alert('ERROR: no server response'); };
            http.send(data);
        }

	reset_action() {
	    var r = confirm("Reset Box?");
  	    if (r == true) {
                var txt = "You pressed OK!";
            }
	    else {
                return;
            }

            var http = new XMLHttpRequest();
            http.open("POST", this.urlBox, true);
            http.setRequestHeader("Content-Type", "application/json");
            var data = JSON.stringify({"parameter": "reset", "value": 1});
            http.onload = function () {
              if(http.status == 200)
                alert("OK: command sent");
              else
                alert(http.status);
            };
            http.onerror = function() { alert('ERROR: no server response'); };
            http.send(data);
        }

        gpio1_action() {
            var val = document.getElementById("val1").value;

            var http = new XMLHttpRequest();
            http.open("POST", this.urlBox, true);
            http.setRequestHeader("Content-Type", "application/json");
            var data = JSON.stringify({"parameter": "D1", "value": val});
            http.onload = function () {
              if(http.status == 200)
                alert("OK: command sent");
              else
                alert(http.status);
            };
            http.onerror = function() { alert('ERROR: no server response'); };
            http.send(data);
        }

	gpio2_action() {
            var val = document.getElementById("val2").value;

            var http = new XMLHttpRequest();
            http.open("POST", this.urlBox, true);
            http.setRequestHeader("Content-Type", "application/json");
            var data = JSON.stringify({"parameter": "D2", "value": val});
            http.onload = function () {
              if(http.status == 200)
                alert("OK: command sent");
              else
                alert(http.status);
            };
            http.onerror = function() { alert('ERROR: no server response'); };
            http.send(data);
        }

	gpio3_action() {
            var val = document.getElementById("val3").value;

            var http = new XMLHttpRequest();
            http.open("POST", this.urlBox, true);
            http.setRequestHeader("Content-Type", "application/json");
            var data = JSON.stringify({"parameter": "D3", "value": val});
            http.onload = function () {
              if(http.status == 200)
                alert("OK: command sent");
              else
                alert(http.status);
            };
            http.onerror = function() { alert('ERROR: no server response'); };
            http.send(data);
        }

	gpio4_action() {
            var val = document.getElementById("val4").value;

            var http = new XMLHttpRequest();
            http.open("POST", this.urlBox, true);
            http.setRequestHeader("Content-Type", "application/json");
            var data = JSON.stringify({"parameter": "D4", "value": val});
            http.onload = function () {
              if(http.status == 200)
                alert("OK: command sent");
              else
                alert(http.status);
            };
            http.onerror = function() { alert('ERROR: no server response'); };
            http.send(data);
        }

	gpio5_action() {
            var val = document.getElementById("val5").value;

            var http = new XMLHttpRequest();
            http.open("POST", this.urlBox, true);
            http.setRequestHeader("Content-Type", "application/json");
            var data = JSON.stringify({"parameter": "D5", "value": val});
            http.onload = function () {
              if(http.status == 200)
                alert("OK: command sent");
              else
                alert(http.status);
            };
            http.onerror = function() { alert('ERROR: no server response'); };
            http.send(data);
        }

	gpio6_action() {
            var val = document.getElementById("val6").value;

            var http = new XMLHttpRequest();
            http.open("POST", this.urlBox, true);
            http.setRequestHeader("Content-Type", "application/json");
            var data = JSON.stringify({"parameter": "D6", "value": val});
            http.onload = function () {
              if(http.status == 200)
                alert("OK: command sent");
              else
                alert(http.status);
            };
            http.onerror = function() { alert('ERROR: no server response'); };
            http.send(data);
        }

	gpio7_action() {
            var val = document.getElementById("val7").value;

            var http = new XMLHttpRequest();
            http.open("POST", this.urlBox, true);
            http.setRequestHeader("Content-Type", "application/json");
            var data = JSON.stringify({"parameter": "D7", "value": val});
            http.onload = function () {
              if(http.status == 200)
                alert("OK: command sent");
              else
                alert(http.status);
            };
            http.onerror = function() { alert('ERROR: no server response'); };
            http.send(data);
        }

	gpio8_action() {
            var val = document.getElementById("val8").value;

            var http = new XMLHttpRequest();
            http.open("POST", this.urlBox, true);
            http.setRequestHeader("Content-Type", "application/json");
            var data = JSON.stringify({"parameter": "D8", "value": val});
            http.onload = function () {
              if(http.status == 200)
                alert("OK: command sent");
              else
                alert(http.status);
            };
            http.onerror = function() { alert('ERROR: no server response'); };
            http.send(data);
        }


        // Get BOX state
        update_state() {
	    let that = this;
            var xmlHttp = new XMLHttpRequest();
            xmlHttp.onreadystatechange = function () {
                if (xmlHttp.readyState == 4 && xmlHttp.status == 200) {

		    that.ticks_off = 0;
		    document.getElementById("boxstate").style.backgroundColor = "green";

                    var resp = xmlHttp.responseText;
                    var json = JSON.parse(resp);

		    var statusIridium = json.boxdata.status_iridium;
		    var statusADC = json.boxdata.ADC_status;
		    var sMO = json.boxdata.sampleMO;
		    var sMT = json.boxdata.sampleMT;
		    var adc1 = json.boxdata.ADC1;
		    var adc2 = json.boxdata.ADC2;
		    var adc3 = json.boxdata.ADC3;
		    var adc4 = json.boxdata.ADC4;
		    var adc5 = json.boxdata.ADC5;
		    var adc6 = json.boxdata.ADC6;
		    var adc7 = json.boxdata.ADC7;
		    var adc8 = json.boxdata.ADC8;
		    var gpio1 = json.boxdata.D1;
		    var gpio2 = json.boxdata.D2;
		    var gpio3 = json.boxdata.D3;
		    var gpio4 = json.boxdata.D4;
		    var gpio5 = json.boxdata.D5;
		    var gpio6 = json.boxdata.D6;
		    var gpio7 = json.boxdata.D7;
		    var gpio8 = json.boxdata.D8;

                    if(statusIridium == "1")
                    	document.getElementById("irstate").style.backgroundColor = "green";
		    else if(statusIridium == "0")
			document.getElementById("irstate").style.backgroundColor = "red";
		    else
			document.getElementById("irstate").style.backgroundColor = "gray";

		    if(statusADC == "1")
                        document.getElementById("adcstate").style.backgroundColor = "green";
                    else if(statusADC == "0")
                        document.getElementById("adcstate").style.backgroundColor = "red";
		    else
			document.getElementById("adcstate").style.backgroundColor = "gray";

		    //if(statusADC == "1")
                    //    document.getElementById("dstate").style.backgroundColor = "green";
                    //else
                    //    document.getElementById("dstate").style.backgroundColor = "red";

                    document.getElementById("a1").innerHTML = adc1;
		    document.getElementById("a2").innerHTML = adc2;
		    document.getElementById("a3").innerHTML = adc3;
		    document.getElementById("a4").innerHTML = adc4;
		    document.getElementById("a5").innerHTML = adc5;
		    document.getElementById("a6").innerHTML = adc6;
		    document.getElementById("a7").innerHTML = adc7;
		    document.getElementById("a8").innerHTML = adc8;
                    document.getElementById("g1").innerHTML = gpio1;
		    document.getElementById("g2").innerHTML = gpio2;
		    document.getElementById("g3").innerHTML = gpio3;
		    document.getElementById("g4").innerHTML = gpio4;
		    document.getElementById("g5").innerHTML = gpio5;
		    document.getElementById("g6").innerHTML = gpio6;
		    document.getElementById("g7").innerHTML = gpio7;
		    document.getElementById("g8").innerHTML = gpio8;
                    document.getElementById("moget").innerHTML = sMO;
                    document.getElementById("mtget").innerHTML = sMT;
                }
                else{
		  that.ticks_off += 1;
		  if(that.ticks_off > 5) {
                        document.getElementById("boxstate").style.backgroundColor = "gray";
			document.getElementById("irstate").style.backgroundColor = "gray";
			document.getElementById("adcstate").style.backgroundColor = "gray";
			document.getElementById("dstate").style.backgroundColor = "gray";

			document.getElementById("a1").innerHTML = "0";
                    	document.getElementById("a2").innerHTML = "0";
                    	document.getElementById("a3").innerHTML = "0";
                    	document.getElementById("a4").innerHTML = "0";
                    	document.getElementById("a5").innerHTML = "0";
                    	document.getElementById("a6").innerHTML = "0";
                    	document.getElementById("a7").innerHTML = "0";
                    	document.getElementById("a8").innerHTML = "0";
                    	document.getElementById("g1").innerHTML = "0";
                    	document.getElementById("g2").innerHTML = "0";
                    	document.getElementById("g3").innerHTML = "0";
                    	document.getElementById("g4").innerHTML = "0";
                    	document.getElementById("g5").innerHTML = "0";
                    	document.getElementById("g6").innerHTML = "0";
                    	document.getElementById("g7").innerHTML = "0";
                    	document.getElementById("g8").innerHTML = "0";
                    	document.getElementById("moget").innerHTML = "0";
                    	document.getElementById("mtget").innerHTML = "0";
		  }
                }
	    }
            xmlHttp.open("GET", this.urlBox, true);
            xmlHttp.send(null);

        }

    }


    $.homeScript = new HomeScript();

}(jQuery, window, document));

