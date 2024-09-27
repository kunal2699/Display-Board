(function() {
    var ct, cth, ctm, d, h, m, s, setTime;
  
    d = new Date;
  
    h = d.getHours();
  
    m = d.getMinutes();
  
    s = d.getSeconds();
  
    ct = function(v) {
      var t;
      t = v * 360 / 60;
      return t;
    };
  
    ctm = function(v) {
      var t;
      t = v * 360 / 60 + 6 * ct(s) / 360;
      return t;
    };
  
    cth = function(v) {
      var t;
      t = v * 360 / 12 + 30 * ct(m) / 360;
      return t;
    };
  
    setTime = function() {
      $('.w-second').css('transform', 'rotateZ(' + ct(s) + 'deg)');
      $('.w-minute').css('transform', 'rotateZ(' + ctm(m) + 'deg)');
      return $('.w-hour').css('transform', 'rotateZ(' + cth(h) + 'deg)');
    };
  
    $(document).ready(function() {
      return setTime();
    });
  
  }).call(this);

  function showTime(){
    var date = new Date();
    var h = date.getHours(); // 0 - 23
    var m = date.getMinutes(); // 0 - 59
    var s = date.getSeconds(); // 0 - 59
    var session = "AM";
    
    if(h == 0){
        h = 12;
    }
    
    if(h > 12){
        h = h - 12;
        session = "PM";
    }
    
    h = (h < 10) ? "0" + h : h;
    m = (m < 10) ? "0" + m : m;
    s = (s < 10) ? "0" + s : s;
    
    var time = h + ":" + m + ":" + s + " " + session;
    document.getElementById("MyClockDisplay").innerText = time;
    document.getElementById("MyClockDisplay").textContent = time;
    
    setTimeout(showTime, 1000);
    
}

showTime();