"""
FlaskでサーバをたててWeb上で地図を表示する
"""
from flask import Flask, render_template, request, jsonify
import db, pathSearch
import networkx as nx

app = Flask(__name__)
dictionary_data = {} #辞書用，作成した辞書をグローバル変数として使用するため

@app.route("/")
def leafletMap():
    return render_template("index.html")

# 田中の研究では使用していない(高橋システム従来のもの)，いろんな経路探索できる用
@app.route('/process_ajax', methods=['POST'])
def process_ajax():
    if request.method == 'POST':
        #リクエストからデータを取得
        data = request.get_json()  
        points = data['points']
        startPoint = data['startPoint']
        endPoint = data['endPoint']
        #print("Points data:", points) #中身知る用

        if startPoint:
            points.append(startPoint)
        if endPoint:
            points.append(endPoint)

        #データベースから道路データを取得
        y1, x1, y2, x2 = pathSearch.rectangleArea(points)
        link, length = db.getRectangleRoadData1(y1, x1, y2, x2)

        #経路探索
        print("経路探索_main.py")
        #print("points[0]:" , points[0] , " ,points[1]:" , points[1])
        #path = pathSearch.shortestPath(points[0], points[1], link, length)
        #path = pathSearch.MST(link, length)
        #path = pathSearch.steiner(points, link, length)
        path, len = pathSearch.traveling(points, link, length)
  
        #return jsonify({'path': path})
        return jsonify({'path': path, 'len': len})
    
    else:
        return jsonify({'message': 'Invalid request method'})


#最短経路探索
@app.route('/shortestPath', methods=['POST'])
def shortestPath():
    print("最短経路探索_main.py")
    if request.method == 'POST':
        #リクエストからデータを取得
        data = request.get_json()  
        points = data['points']
        startPoint = data['startPoint']
        endPoint = data['endPoint']
        #print("Points data:", points) #中身知る用

        if startPoint:
            points.append(startPoint)
        if endPoint:
            points.append(endPoint)

        #データベースから道路データを取得
        y1, x1, y2, x2 = pathSearch.rectangleArea(points)
        link, length = db.getRectangleRoadData1(y1, x1, y2, x2)

        

        #経路探索
        print("経路探索_main.py")
        #print("points[0]:" , points[0] , " ,points[1]:" , points[1])
        Graph = dictionary_data['Graph']
        path, len = pathSearch.shortestPath(points[0], points[1], link, Graph  )
        print(f"path:{path}")
        #return jsonify({'path': path})
        return jsonify({'path': path, 'len': len})
    
    else:
        return jsonify({'message': 'Invalid request method'})

#最少右左折経路探索
@app.route('/minimumStrokesPath', methods=['POST'])
def minimumStrokesPath():
    print("最少右左折経路探索_main.py")
    if request.method == 'POST':
        #リクエストからデータを取得
        data = request.get_json()  
        points = data['points']
        startPoint = data['startPoint']
        endPoint = data['endPoint']
        #print("Points data:", points) #中身知る用

        if startPoint:
            points.append(startPoint)
        if endPoint:
            points.append(endPoint)

        #データベースから道路データを取得
        y1, x1, y2, x2 = pathSearch.rectangleArea(points)
        #(y1, x1):左上の緯度経度 (y2, x2):右下の緯度経度 n:範囲を拡大する倍率 →もう使ってない(地図上でデータ取得範囲をクリックしている)
        n=2
        # link, length, nodeid_to_nodeCoords, linkid_to_linkCoords,linkid_to_length, linkid_to_nodeids, node_to_linkids, stroke_id, link_ids, strokeid_to_linkids, linkid_to_strokeid, strokeid_to_intersections = db.getRectangleRoadData(y1, x1, y2, x2,n)
        #print(f"link: {link} \n link_id:{link_id}")
        #print(f"strokeid_to_intersectids: {strokeid_to_intersections} ")
        # print(f"dictionary_data: {dictionary_data} ")
        link = dictionary_data['link']
        length = dictionary_data['length']
        nodeid_to_nodeCoords = dictionary_data['nodeid_to_nodeCoords']
        linkid_to_linkCoords = dictionary_data['linkid_to_linkCoords']
        linkid_to_length = dictionary_data['linkid_to_length']
        linkid_to_nodeids = dictionary_data['linkid_to_nodeids']
        node_to_linkids = dictionary_data['node_to_linkids']
        stroke_id = dictionary_data['stroke_id']
        link_ids = dictionary_data['link_ids']
        strokeid_to_linkids = dictionary_data['strokeid_to_linkids']
        linkid_to_strokeid = dictionary_data['linkid_to_strokeid']
        strokeid_to_intersections = dictionary_data['strokeid_to_intersections']

        #経路探索
        #print("points[0]:" , points[0] , " ,points[1]:" , points[1])
        path, len  = pathSearch.minStrokesPath(points[0], points[1], link, length, nodeid_to_nodeCoords, linkid_to_linkCoords,linkid_to_length, linkid_to_nodeids, node_to_linkids, linkid_to_strokeid, strokeid_to_linkids, strokeid_to_intersections)

        print(f"path:{path}")
        #return jsonify({'path': path})
        return jsonify({'path': path, 'len': len})
    
    else:
        return jsonify({'message': 'Invalid request method'})

#第n道なり優先最短経路
@app.route('/nMinStrokeShortestPath', methods=['POST'])
def nMinStrokeShortestPath():
    print("第n道なり優先最短経路_main.py")
    if request.method == 'POST':
        #リクエストからデータを取得
        data = request.get_json()  
        points = data['points']
        # startPoint = data['startPoint']
        # endPoint = data['endPoint']
        #print("Points data:", points) #中身知る用

        # if startPoint:
        #     points.append(startPoint)
        # if endPoint:
        #     points.append(endPoint)

        

        #辞書データをdef dictionaryから持ってくる
        Graph = dictionary_data['Graph']
        link = dictionary_data['link']
        length = dictionary_data['length']
        nodeid_to_nodeCoords = dictionary_data['nodeid_to_nodeCoords']
        linkid_to_linkCoords = dictionary_data['linkid_to_linkCoords']
        linkid_to_length = dictionary_data['linkid_to_length']
        linkid_to_nodeids = dictionary_data['linkid_to_nodeids']
        node_to_linkids = dictionary_data['node_to_linkids']
        stroke_id = dictionary_data['stroke_id']
        link_ids = dictionary_data['link_ids']
        strokeid_to_linkids = dictionary_data['strokeid_to_linkids']
        linkid_to_strokeid = dictionary_data['linkid_to_strokeid']
        strokeid_to_intersections = dictionary_data['strokeid_to_intersections']

        #経路探索
        #print("points[0]:" , points[0] , " ,points[1]:" , points[1])
        paths, lengths  = pathSearch.nMinStrokeShortestPath(Graph, points[0], points[1], link, length, nodeid_to_nodeCoords, linkid_to_linkCoords,linkid_to_length, linkid_to_nodeids, node_to_linkids, linkid_to_strokeid, strokeid_to_linkids, strokeid_to_intersections)

        # 地図描画のために型を整形, List[List[str]] → List[List[List[float]]]
        import ast
        paths = [[ast.literal_eval(pt) if isinstance(pt, str) else pt for pt in path] for path in paths]
        return jsonify({'paths': paths, 'lengths': lengths})

    
    else:
        return jsonify({'message': 'Invalid request method'})

#辞書作成
@app.route('/dictionary', methods=['POST'])
def dictionary():
    print("dictionary(辞書作成)_main.py:") 
    if request.method == 'POST':
        global dictionary_data
        #リクエストからデータを取得
        data = request.get_json()  
        getDataPoints = data['getDataPoints']
        # startPoint = data['startPoint']
        # endPoint = data['endPoint']
        print("getDataPoints:", getDataPoints) #中身知る用

        
        #データベースから道路データを取得
        y1, x1, y2, x2 = pathSearch.rectangleArea(getDataPoints)
        n=1 #範囲を大きくする倍率
        link, length, nodeid_to_nodeCoords, linkid_to_linkCoords,linkid_to_length, linkid_to_nodeids, node_to_linkids, stroke_id, link_ids, strokeid_to_linkids, linkid_to_strokeid, strokeid_to_intersections = db.getRectangleRoadData(y1, x1, y2, x2,n)
        # --- ここでグラフを構築 ---
        Graph = nx.Graph()
        skipped_links = []  # 追加できなかったlink_idを記録
        for link_id, coords in linkid_to_linkCoords.items():
            try:
                n1, n2 = coords
                node1 = str(n1)
                node2 = str(n2)
                strokeID = linkid_to_strokeid[link_id]
                length = linkid_to_length[link_id]
                Graph.add_edge(node1, node2, weight=length, strokeID=strokeID)
            except KeyError as e:
                skipped_links.append(link_id)
        # 追加できなかったリンクの一覧をprint
        if skipped_links:
            print("addできなかったlink_id:", skipped_links)
        
        

        # for node1, node2, attrs in Graph.edges(data=True):
        #     print(f"node1: {node1}, node2: {node2}, weight: {attrs['weight']}, strokeID: {attrs['strokeID']}")
        dictionary_data = {
            'Graph':Graph,
            'link': link,
            'length': length,
            'nodeid_to_nodeCoords': nodeid_to_nodeCoords,
            'linkid_to_linkCoords': linkid_to_linkCoords,
            'linkid_to_length': linkid_to_length,
            'linkid_to_nodeids': linkid_to_nodeids,
            'node_to_linkids': node_to_linkids,
            'stroke_id': stroke_id,
            'link_ids': link_ids,
            'strokeid_to_linkids': strokeid_to_linkids,
            'linkid_to_strokeid': linkid_to_strokeid,
            'strokeid_to_intersections': strokeid_to_intersections,
        }
        
        # print("dictionary_data:", dictionary_data)
      
        print("辞書作成完了")
        return jsonify({'getDataPoints': getDataPoints}) #返すものは何でもいい
        # return jsonify({'path': path, 'len': len})
    
    else:
        return jsonify({'message': 'Invalid request method'})

#リンクチェック用
@app.route('/LinkCheck', methods=['POST'])
def LinkCheck():
    print("リンクチェック_main.py")
    if request.method == 'POST':
        #リクエストからデータを取得
        data = request.get_json()  
        points = data['points']
        getDataPoints = data['getDataPoints']
        startPoint = data['startPoint']
        endPoint = data['endPoint']
        #print("Points data:", points) #中身知る用

        # if startPoint:
        #     points.append(startPoint)
        # if endPoint:
        #     points.append(endPoint)

        #データベースから道路データを取得
        #y1, x1, y2, x2 = pathSearch.rectangleArea(points)
        y1, x1, y2, x2 = pathSearch.rectangleArea(getDataPoints) #データ取得範囲マーカーの場合
        n=1
       
        #経路探索
        print("経路探索_main.py")
        #print("points[0]:" , points[0] , " ,points[1]:" , points[1])
        #path, len = pathSearch.linkCheck(points[0], points[1], link, length, link_id, node_to_linkids, linkid_to_strokeid, strokeid_to_linkids, strokeid_to_intersectids)
        #path, len, = pathSearch.linkCheck(y1, x1, y2, x2, points[0], points[1],n)
        path, len, = pathSearch.linkCheck(y1, x1, y2, x2, n)
        print(f"path:{path}")
        #return jsonify({'path': path})
        # return jsonify({'path': path, 'len': len})
        return jsonify({'path': path, 'n': n})
    
    else:
        return jsonify({'message': 'Invalid request method'})

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=80)
