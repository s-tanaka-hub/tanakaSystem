"""
FlaskでサーバをたててWeb上で地図を表示する
"""
from flask import Flask, render_template, request, jsonify
import db, pathSearch

app = Flask(__name__)

@app.route("/")
def leafletMap():
    return render_template("index.html")

@app.route('/process_ajax', methods=['POST'])
def process_ajax():
    if request.method == 'POST':
        #リクエストからデータを取得
        data = request.get_json()  
        points = data['points']
        startPoint = data['startPoint']
        endPoint = data['endPoint']

        if startPoint:
            points.append(startPoint)
        if endPoint:
            points.append(endPoint)

        #データベースから道路データを取得
        y1, x1, y2, x2 = pathSearch.rectangleArea(points)
        link, length = db.getRectangleRoadData(y1, x1, y2, x2)

        #経路探索
        #path = pathSearch.shortestPath(points[0], points[1], link, length)
        #path = pathSearch.MST(link, length)
        #path = pathSearch.steiner(points, link, length)
        path, len = pathSearch.traveling(points, link, length)
  
        return jsonify({'path': path, 'len': len})
    
    else:
        return jsonify({'message': 'Invalid request method'})
    
if __name__ == "__main__":
    app.run(host="133.68.17.14",port=80)

