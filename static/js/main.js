var mapElement = document.getElementById('map');

// 初期座標
var center = [35.16066808015237, 136.92640764889583];
// 初期ズームレベル
var zoom_level = 14;

var map = L.map(mapElement,{closePopupOnClick: false}).setView(center, zoom_level);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors',
  maxZoom: 18
}).addTo(map);

const redIcon = L.icon({
  iconUrl: "https://esm.sh/leaflet@1.9.2/dist/images/marker-icon.png",
  iconRetinaUrl: "https://esm.sh/leaflet@1.9.2/dist/images/marker-icon-2x.png",
  shadowUrl: "https://esm.sh/leaflet@1.9.2/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  tooltipAnchor: [16, -28],
  shadowSize: [41, 41],
  className: "icon-red",
});

var points = [];
var getDataPoints = [];
var startPoint = [];
var endPoint = [];
var markerType = "getData";
var startMarkerFlag = false;
var endMarkerFlag = false;
var button1Active = false;
var button2Active = false;
var button3Active = false;
var button4Active = false;

// マウスクリックで緯度経度の取得とマーカー設置
function onMapClick(e) {
  switch(markerType) {
    case "getData":
      if (getDataPoints.length >= 2) {
        break;  // 2個までしか追加できない
      }
      L.marker(e.latlng, { icon: redIcon })
        .on('click', onGetDataMarkerClick)
        .addTo(map)
        .bindPopup('データ取得範囲', {autoClose:false})
        .openPopup();
      getDataPoints.push([e.latlng.lat, e.latlng.lng]);
      break;
    case "location":
      if (points.length >= 2) {
        break;
      }
      L.marker(e.latlng).on('click', onMarkerClick).addTo(map);
      points.push([e.latlng.lat, e.latlng.lng]);
      break;
    //以下２つは使ってない↓
    case "start":
      if(startMarkerFlag) {
        break;
      }
      startMarker = L.marker(e.latlng,{ icon: redIcon }).on('click', onStartMarkerClick).addTo(map)
                      .bindPopup('出発地点',{autoClose:false}).openPopup();
      startPoint = [e.latlng.lat, e.latlng.lng];
      startMarkerFlag = true;
      break;
    case "end":
      if(endMarkerFlag) {
          break;
        }
        endMarker = L.marker(e.latlng,{ icon: redIcon }).on('click', onEndMarkerClick).addTo(map)
                      .bindPopup('到着地点',{autoClose:false}).openPopup();
        endPoint = [e.latlng.lat, e.latlng.lng];
        endMarkerFlag = true;
      break;
    default:
      break;
  }
}
map.on('click', onMapClick);

//マーカーをクリックしたら削除
function onMarkerClick(e) {
  var index = points.findIndex( item => JSON.stringify( item ) ===
                                  JSON.stringify([e.target.getLatLng().lat, e.target.getLatLng().lng]));
  console.log(index);
  if (index > -1){
    points.splice(index, 1)
  }
  map.removeLayer(e.target);
}

function onGetDataMarkerClick(e) {
  getDataPoints = getDataPoints.filter(
    pt => !(pt[0] === e.target.getLatLng().lat && pt[1] === e.target.getLatLng().lng)
  );
  map.removeLayer(e.target);
}

function onStartMarkerClick(e) {
  startPoint = [];
  map.removeLayer(e.target);
  startMarkerFlag = false;
}

function onEndMarkerClick(e) {
  endPoint = [];
  map.removeLayer(e.target);
  endMarkerFlag = false;
}

/*
const button1Text = document.getElementById('button1Text');
// 経路探索ボタンのクリックイベント
$('#btn_TSP').click(function() {
  button1Active = !button1Active; // 状態を反転させる

  if (button1Active) {
    $(this).addClass('active'); // ボタンが押されている表示にする
    var requestData = {
            points:points,
            startPoint:startPoint,
            endPoint:endPoint
        };
    $.ajax({
        url: '/process_ajax',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(requestData),
        success: function(response) {
            var path = response.path;
            var len = response.len;
            // 経路を表示
            polyline = L.polyline(path, { color: 'red' })
            polyline.addTo(map);
            var len_round = Math.round(len * Math.pow(10, 3) ) / Math.pow(10, 3);
            button1Text.textContent = '経路長：'+len_round+'km';
            $('#button1Text').removeClass('hidden');
        }
    });
  } else {
    $(this).removeClass('active'); // ボタンが押されていない表示にする
    if (polyline) {
      map.removeLayer(polyline); // polyline を地図から削除
    }
    $('#button1Text').addClass('hidden');
  }
});
*/

const button1Text = document.getElementById('button1Text');
// 経路探索ボタンのクリックイベント のコピー
$('#btn_dictionary').click(function() {
  button1Active = !button1Active; // 状態を反転させる

  if (button1Active) {
    $(this).addClass('active'); // ボタンが押されている表示にする
    var requestData = {
            // points:points,
            getDataPoints:getDataPoints
        };
    $.ajax({
        url: '/dictionary',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(requestData),
        success: function(response) {
            var path = response.path;
            var len = response.len;
            // 経路を表示
            // polyline = L.polyline(path, { color: 'blue' })
            // polyline.addTo(map);
            // var len_round = Math.round(len * Math.pow(10, 3) ) / Math.pow(10, 3);
            button1Text.textContent = '辞書データ作成完了';
            $('#button1Text').removeClass('hidden');
        }
    });
  } else {
    $(this).removeClass('active'); // ボタンが押されていない表示にする
    // if (polyline) {
    //   map.removeLayer(polyline); // polyline を地図から削除
    // }
    $('#button1Text').addClass('hidden');
  }
});

const button2Text = document.getElementById('button2Text');
// 最短経路探索ボタンのクリックイベント
//print("ボタン2_main.js") →JSでのターミナルへのコメント出力の方法が分からんかった
$('#btn_shortestPath').click(function() {
  button2Active = !button2Active; // 状態を反転させる

  if (button2Active) {
    $(this).addClass('active'); // ボタンが押されている表示にする
    var requestData = {
            points:points,
            startPoint:startPoint,
            endPoint:endPoint
        };
    $.ajax({
        url: '/shortestPath',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(requestData),
        success: function(response) {
            var path = response.path;
            var len = response.len;
            // 経路を表示
            polyline = L.polyline(path, { color: 'yellow' })
            polyline.addTo(map);
            var len_round = Math.round(len * Math.pow(10, 3) ) / Math.pow(10, 3);
            button2Text.textContent = '経路長：'+len_round+'km';
            $('#button2Text').removeClass('hidden');
        }
    });
  } else {
    $(this).removeClass('active'); // ボタンが押されていない表示にする
    if (polyline) {
      map.removeLayer(polyline); // polyline を地図から削除
    }
    $('#button2Text').addClass('hidden');
  }
});

const button3Text = document.getElementById('button3Text');
// 最少右左折経路探索ボタンのクリックイベント
//print("ボタン3_main.js") →JSでのターミナルへのコメント出力の方法が分からんかった
$('#btn_minimumStrokesPath').click(function() {
  button3Active = !button3Active; // 状態を反転させる

  if (button3Active) {
    $(this).addClass('active'); // ボタンが押されている表示にする
    var requestData = {
            points:points,
            startPoint:startPoint,
            endPoint:endPoint
        };
    $.ajax({
        url: '/minimumStrokesPath',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(requestData),
        success: function(response) {
            var path = response.path;
            var len = response.len;
            // 経路を表示
            polyline = L.polyline(path, { color: 'red' })
            polyline.addTo(map);
            var len_round = Math.round(len * Math.pow(10, 3) ) / Math.pow(10, 3);
            button3Text.textContent = '経路長：'+len_round+'km';
            $('#button3Text').removeClass('hidden');
        }
    });
  } else {
    $(this).removeClass('active'); // ボタンが押されていない表示にする
    if (polyline) {
      map.removeLayer(polyline); // polyline を地図から削除
    }
    $('#button3Text').addClass('hidden');
  }
});

const button4Text = document.getElementById('button4Text');
// 第n道なり優先最短経路探索ボタンのクリックイベント
var polylines_nMinStroke = []; //LeafletのL.polylineで描画した線を後でまとめて消す時などのために配列に保存しておきます
$('#btn_nMinStrokeShortestPath').click(function() {
  button4Active = !button4Active; // 状態を反転させる
  if (button4Active) {
    $(this).addClass('active'); // ボタンが押されている表示にする
    var requestData = {
            points:points,
            // getDataPoints:getDataPoints,
            // startPoint:startPoint,
            // endPoint:endPoint
        };
    $.ajax({
        url: '/nMinStrokeShortestPath',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(requestData),
        success: function(response) {
          
          var paths= response.paths;
          console.log("paths:"+paths+", paths.length(要素の数):"+paths.length);
          var colors = ['pink','blue','green','orange','brown','red','purple'];
          var maxWeight = 15;
          var minWeight = 3;
          var step = 3;
          for (var i = 0; i < paths.length; i++) {
            console.log("i:"+i);
            var weight = Math.max(maxWeight - i * step, minWeight);
            var poly = L.polyline(paths[i], {
                  color: colors[i % colors.length],
                  weight: weight,
                  // dashArray: i ? "10,10" : null  // 2本目以降は点線例
            });
            poly.addTo(map);
            polylines_nMinStroke.push(poly);
          
          }
          button4Text.textContent = '取得経路数:' + paths.length;
          $('#button4Text').removeClass('hidden');

          
          // var path = response.path;
          // console.log("path:"+path);
          // // var n = response.n;
          // polyline = L.polyline(path, { color: 'purple' })// 経路を表示
          // polyline.addTo(map);
        }

    });
  } else {
    $(this).removeClass('active'); // ボタンが押されていない表示にする
      polylines_nMinStroke.forEach(function(poly) { map.removeLayer(poly); });
      polylines_nMinStroke = [];  
      console.log("polylines_nMinStroke:"+polylines_nMinStroke);

    // polylines_nMinStroke.forEach(function(poly) {
      //   map.removeLayer(poly);
      // });
      // polylines_nMinStroke = [];
    
    // if (polyline) {
    //   map.removeLayer(polyline); // polyline を地図から削除
    // }
    $('#button4Text').addClass('hidden');
  }
});

const button5Text = document.getElementById('button5Text');
// リンク(ストローク)確認用ボタンのクリックイベント
$('#btn_LinkCheck').click(function() {
  button5Active = !button5Active; // 状態を反転させる
  if (button5Active) {
    $(this).addClass('active'); // ボタンが押されている表示にする
    var requestData = {
            points:points,
            getDataPoints:getDataPoints,
            startPoint:startPoint,
            endPoint:endPoint
        };
    $.ajax({
        url: '/LinkCheck',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(requestData),
        success: function(response) {
            var path = response.path;
            var n = response.n;
            polyline = L.polyline(path, { color: 'green' })// 経路を表示
            polyline.addTo(map);
            button5Text.textContent = '範囲倍率：n='+n;
            $('#button5Text').removeClass('hidden');
        }
    });
  } else {
    $(this).removeClass('active'); // ボタンが押されていない表示にする
    if (polyline) {
      map.removeLayer(polyline); // polyline を地図から削除
    }
    $('#button5Text').addClass('hidden');
  }
});

var mamlistboxdiv;
var mamlistboxa;
var mamlistbox;
var mamlistbox_active=false;
window.addEventListener("load",function(){
  mamlistboxdiv=document.querySelector(".mamListBox>a>div");
  mamlistboxa=document.querySelector(".mamListBox>a");
  mamlistbox=document.querySelector(".mamListBox>select");
  mamlistboxa.addEventListener("click",function(event){
    if(mamlistbox_active==false){
      mamlistbox.style.display = "block";
      mamlistbox_active=true;
      mamlistbox.focus();
    }else{
      mamlistbox_active=false;
    }
  });
  mamlistbox.addEventListener("blur",function(){
    mamlistbox.style.display = "none";
  });
  mamlistbox.addEventListener("click",function(){
    mamlistboxdiv.innerHTML = mamlistbox.querySelectorAll('option')[mamlistbox.selectedIndex].innerHTML;
    mamlistbox_active=false;
    mamlistbox.blur();
    markerType = mamlistbox.value;
  });
  document.documentElement.addEventListener("click",mamListboxOtherClick);
});
function mamListboxOtherClick(event){
  if(event.target==mamlistboxdiv){return;}
  if(event.target==mamlistboxa){return;}
  if(event.target==mamlistbox){return;}
  mamlistbox_active=false;
}
