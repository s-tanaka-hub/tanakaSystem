"""
経路探索などを行う
"""
import math
import networkx as nx
import db #LinkCheck関数のために追加した
import time #実行時間計測のために

#クリックされた点を含む最小の矩形領域
def rectangleArea(points):
    print("クリックされた点を含む最小の矩形")
    min_lat = float('inf')
    max_lat = float('-inf')
    min_lng = float('inf')
    max_lng = float('-inf')

    for point in points:
        lat, lng = point[0], point[1]
        min_lat = min(min_lat, lat)
        max_lat = max(max_lat, lat)
        min_lng = min(min_lng, lng)
        max_lng = max(max_lng, lng)

    return max_lat, min_lng, min_lat, max_lng

#座標の最近傍ノードを取得
def nearestNode(p, link):
    dist = float('inf')
    nearestNode = None
    for line in link:
        for point in line:
            d = math.sqrt((p[0] - point[0])**2 + (p[1] - point[1])**2)
            if d < dist:
                dist = d
                nearestNode = point
    return nearestNode

#Gを連結グラフにする
def connectGraph(G):
    if not nx.algorithms.components.is_connected(G):
        components = list(nx.algorithms.components.connected_components(G))
        for i in range(len(components) - 1):
            if not nx.algorithms.components.is_connected(G):
                component1 = components[i]
                component2 = components[i + 1]
                node1 = next(iter(component1))
                node2 = next(iter(component2))
                G.add_weighted_edges_from([(node1, node2, float('inf'))])

#最短経路
def shortestPath(p1, p2, link, G):
    print("最短経路_pathSearch.py")
    #最近傍ノードを取得
    p1 = nearestNode(p1, link)
    p2 = nearestNode(p2, link)
    print("p1:", p1 , ",p2:" , p2) #中身知る用
    print(f"p1 の型: {type(p1)}")

   

    

    #最短経路探索
    path_str = nx.dijkstra_path(G, str(p1), str(p2))
    #print("path_str:", path_str) #中身知る用
   
    #最短経路の経路長
    length = 0
    length = nx.dijkstra_path_length(G, str(p1), str(p2) )
    print("length(最短経路):", length, ",type(length):", type(length)) #中身知る用
       
    #結果をstrから戻して返却
    path = []
    for line in path_str:
        path.append([float(x) for x in line.strip('[]').split(',')])
    return path, length
    
#最短経路,かずほ作
def shortestPath2(p1, p2, link, length):
    print("最短経路_pathSearch.py")
    #最近傍ノードを取得
    p1 = nearestNode(p1, link)
    p2 = nearestNode(p2, link)
    print("p1:", p1 , ",p2:" , p2) #中身知る用
    print(f"p1 の型: {type(p1)}")

    #networkxのグラフを生成
    edges = []
    for i in range(len(link)):
        edges.append((str(link[i][0]), str(link[i][1]), length[i]))
    G = nx.Graph()
    G.add_weighted_edges_from(edges)
    print("G:", G) #中身知る用
    #print("list(G.nodes):",list(G.nodes)) #中身知る用
    connectGraph(G)

    #最短経路探索
    path_str = nx.dijkstra_path(G, str(p1), str(p2))
    #print("path_str:", path_str) #中身知る用
   
    #最短経路の経路長
    length = 0
    length = nx.dijkstra_path_length(G, str(p1), str(p2) )
    print("length(最短経路):", length, ",type(length):", type(length)) #中身知る用
       
    #結果をstrから戻して返却
    path = []
    for line in path_str:
        path.append([float(x) for x in line.strip('[]').split(',')])
    return path, length    

#最少右左折数探索(最少ストローク数)
from collections import defaultdict
def NumberOfMinStrokes(p1, p2, link, node_to_linkids, linkid_to_strokeid, strokeid_to_intersections):
    print("最少右左折数探索_pathSearch.py")
    #print(f"link: {link} \n link_id:{link_id}")
    start_time = time.time() #開始時間

    #最近傍ノードを取得
    start_node = nearestNode(p1, link)
    goal_node = nearestNode(p2, link)
    print("スタートノード:", start_node , ",ゴールノード:" , goal_node) #中身知る用

    #startNodeが属するストローク
    startStrokes = node_to_stroke(start_node, node_to_linkids, linkid_to_strokeid)
    #goalNodeが属するストローク
    goalStrokes = node_to_stroke(goal_node, node_to_linkids, linkid_to_strokeid)
    print(f"スタートストローク:{startStrokes},ゴールストローク:{goalStrokes}")

    #最少ストローク数探索
    visited = set(startStrokes)  #訪問済みストローク集合(L(n))
    frontier = set(startStrokes) #n本のストロークでたどり着くことができるストロークの集合(1本の場合スタートストローク，日浦さんのパワポでいうL(n))
    count = 1  # n=1
    frontiers = [set(frontier)] # すべてのfrontierをリストで保持（初期状態で0番目にスタート用を追加）
    # ゴールストローク（goal_strokes）のいずれかがvisitedに含まれるまでループ
    while not goalStrokes.issubset(visited):
        print(f"count:{count}")
        next_frontier = set()
        for sid in frontier:
            # 各現ストロークが交差するストローク集合
            intersectings = strokeid_to_intersections.get(sid, set())
            for s_next in intersectings:
                if s_next not in visited:
                    next_frontier.add(s_next)                
        if not next_frontier:
            print(F"たどり着けない場合_minStrokesPath_pathSearch.py")
            # たどり着けない場合
            return -1
        visited |= next_frontier
        frontier = next_frontier
        frontiers.append(set(frontier))
        #print(f"visited:{visited}(count={count})")       
        #frontiersを1リストずつ改行してプリント表示
        # for i, frontier in enumerate(frontiers):
        #     print(f"frontier {i}: {frontier}")
        # 早期終了（この時点でゴールストロークに到達したら break）
        if goalStrokes & visited:
            print(F"ゴールストローク発見，ループを終了")
            break    
        count += 1 #まだゴールストロークに到達していないので，countUP
    
    end_time = time.time()  # 終了時間
    print(f"最少右左折数探索の探索時間: {end_time - start_time:.6f} 秒")
    return frontiers # len(frontiers)-1 が最少右左折数

#最少右左折経路(最少ストローク経路)
from collections import defaultdict
def minStrokesPath(p1, p2, link, length, nodeid_to_nodeCoords, linkid_to_linkCoords,linkid_to_length, linkid_to_nodeids, node_to_linkids, linkid_to_strokeid, strokeid_to_linkids, strokeid_to_intersections):
    print("最少右左折経路_pathSearch.py")
    start_time = time.time() #開始時間

    #最近傍ノードを取得
    start_node = nearestNode(p1, link)
    goal_node = nearestNode(p2, link)
    print("スタートノード:", start_node , ",ゴールノード:" , goal_node) #中身知る用

    #startNodeが属するストローク
    startStrokes = node_to_stroke(start_node, node_to_linkids, linkid_to_strokeid)
    #goalNodeが属するストローク
    goalStrokes = node_to_stroke(goal_node, node_to_linkids, linkid_to_strokeid)
    print(f"スタートストローク:{startStrokes},ゴールストローク:{goalStrokes}")

    # len(frontiers)-1 が最少右左折数
    frontiers  = NumberOfMinStrokes(p1, p2, link, node_to_linkids, linkid_to_strokeid, strokeid_to_intersections)
 
    #最少ストローク数で到達できる経路の列挙(この中で一番距離が短い経路が最少ストローク数経路となる)
    minStrokePaths = []
    n = len(frontiers) - 1
    #from collections import deque
    queue = deque()
    # queueには (現在のストロークID列, 現在のfrontiersインデックス, 交差ノードIDリスト) を格納
    for goal in goalStrokes:
        if goal in frontiers[n]:
            queue.append( ([goal], n, []) )  # 最初は交差ノードなし
    while queue:
        current_path, idx, intersection_nodes = queue.popleft()
        current_stroke = current_path[-1]
        if idx == 0:
            # 経路と交差ノードリストはstart→goalの順にして格納
            minStrokePaths.append((current_path[::-1], intersection_nodes[::-1]))
            continue
        prev_strokes = frontiers[idx-1]
        for prev in prev_strokes:
            intersect_nodes_dict = strokeid_to_intersections.get(current_stroke, {})
            if prev in intersect_nodes_dict:
                intersect_node = intersect_nodes_dict[prev]
                queue.append( (current_path + [prev], idx-1, intersection_nodes + [intersect_node]) )
    print("最少右左折経路候補（経路, 交差ノード）:", minStrokePaths)

    min_path_coords = None
    min_length = float('inf')
    last_pt = None
    #最少右左折経路候補ごとにループ
    for stroke_path, node_path in minStrokePaths:  # stroke_path: [S1, S2, ...], node_path: [N1, N2, ...]
        all_coords = []
        total_len = 0.0
        s_start_node = start_node
        #print(f"s_start_node:{s_start_node}")
        #print(type(s_start_node))
        #ストロークごとにループ
        for i in range(len(stroke_path)):
            sid = stroke_path[i]
            #print(f"sid:{sid}, s_start_node:{s_start_node}")
            #print(type(s_start_node))
            # 目的ノード: 最後だけgoal_node、それ以外は交差ノード
            if i == len(stroke_path) - 1:
                #goal_nodeは座標表現だから,一度id表現に変換
                for nodeid, coords in nodeid_to_nodeCoords.items():
                    if coords == goal_node:
                        target_nodeid = nodeid
                        #print(f"target_nodeid(goal_nodeのid):{target_nodeid}")            
                        break
            else:
                target_nodeid = node_path[i]
                #print(f"target_nodeid:{target_nodeid}")

            linkids = strokeid_to_linkids[sid]
            #print(f"linkids:{linkids}")
            idx_start1 = None
            idx_start2 = None
            for idx, lid in enumerate(linkids):
                # print(f"[lid]:{lid}")
                if lid not in linkid_to_nodeids:
                    #print(f"[lid]:{lid}, linkid_to_nodeidsに存在しないlinkid.次のlinkを探索:")
                    continue
                # リンクの両端ノードIDを取得&それぞれのノードIDから座標を取得
                n1_id, n2_id = linkid_to_nodeids[lid]
                #print(f"[lid]:{lid}, n1_id:{n1_id},n2_id:{n2_id},")
                #print(type(n1_id))
                n1_coords = nodeid_to_nodeCoords.get(n1_id)
                n2_coords = nodeid_to_nodeCoords.get(n2_id)
                #print(f"n1_coords:{n1_coords},n2_coords:{n2_coords}")
                #print(type(n1_coords))
                #このストロークでの最初のリンクを探す(候補は最大2つ,特定のノードの左右どちらか), start座標(s_start_node)と各ノード座標を比較，合致した場合次のリンクも調べる
                if s_start_node == n1_coords or s_start_node == n2_coords:
                    idx_start1 = idx
                    #print(f"s_start_node と合致")
                    next_idx = idx_start1 + 1
                    if next_idx < len(linkids):
                        next_lid = linkids[next_idx]
                        if next_lid in linkid_to_nodeids:
                            n1_next_id, n2_next_id = linkid_to_nodeids[next_lid]
                            n1_next_coords = nodeid_to_nodeCoords.get(n1_next_id)
                            n2_next_coords = nodeid_to_nodeCoords.get(n2_next_id)
                            if s_start_node == n1_next_coords or s_start_node == n2_next_coords:
                                idx_start2 = idx + 1
                                #print(f"次のリンク {next_lid} も s_start_node と合致しました。")
                    #print(f"idx_start:{idx_start}")
                    break
            if idx_start1 is None:
                print(f"エラー: s_start_node {s_start_node} と合致するノードが見つかりませんでした。")
            #print(f"idx_start1:{idx_start1},idx_start2:{idx_start2}")
            # このストロークで通るリンク列を調べる,両端交互に探索して交差ノード(最後はgoalNode)到達するまで
            La, Lb = [], []
            #上で求めたこのストロークでの最初のリンクを投入しとく
            if idx_start1 is not None:
                Lb.append(linkids[idx_start1])  # 降順側に先行投入
                #print(f"linkids[idx_start1]:{linkids[idx_start1]}")
            if idx_start2 is not None:
                La.append(linkids[idx_start2])  # 昇順側に先行投入
                #print(f"linkids[idx_start2]:{linkids[idx_start2]}")
                right_idx = idx_start2 + 1
            else:
                right_idx = idx_start1 + 1
            left_idx = idx_start1 - 1

            reached_side = None
            result_links = []
            while right_idx < len(linkids) or left_idx >= 0:
                if right_idx < len(linkids):
                    lid = linkids[right_idx]
                    if lid not in linkid_to_nodeids:
                        print(f"[La] linkid_to_nodeidsに{lid}が存在しません。skipします。")
                        right_idx += 1
                        continue
                    La.append(lid)
                    n1, n2 = linkid_to_nodeids[lid]
                    right_idx += 1
                    if target_nodeid in (n1, n2):
                        reached_side = 'La'
                        #print(f"target_nodeidを発見,La")
                        break
                    print(f"La: {La}")
                if left_idx >= 0:
                    lid = linkids[left_idx]
                    if lid not in linkid_to_nodeids:
                        print(f"[Lb] linkid_to_nodeidsに{lid}が存在しません。skipします。")
                        left_idx -= 1
                        continue
                    Lb.append(lid)
                    n1, n2 = linkid_to_nodeids[lid]
                    left_idx -= 1
                    if target_nodeid in (n1, n2):
                        reached_side = 'Lb'
                        #print(f"target_nodeidを発見,Lb")
                        break
                    print(f"Lb: {Lb}")
            # どちらか先に到達した側のリンク列だけ採用しスタートリンクを挟む
            if reached_side == 'La':
                result_links =  La
                print(f"リンク列: {result_links}(La)")
            elif reached_side == 'Lb':
                result_links = Lb 
                print(f"リンク列: {result_links}(Lb)")
                # result_links = list(reversed(Lb)) 

            
            #result_links = []
            # result_links.insert(len(Lb), linkids[idx_start1]) #

            # 座標列構築
            coords_path = []
            for idx2, lid2 in enumerate(result_links):
                coord_pair = linkid_to_linkCoords[lid2]
                print(f"lid2:{lid2}, coord_pair: {coord_pair}")
                #startノードを最初に座標列入れてもう一方を次に入れる,coords_pathが空なら
                # if not coords_path:
                if not last_pt:
                    n1, n2 = linkid_to_nodeids[lid2]
                    n1_coords = nodeid_to_nodeCoords[n1]  
                    n2_coords = nodeid_to_nodeCoords[n2]
                    if s_start_node == n1_coords:
                        coords_path.extend(coord_pair)
                        last_pt = n2_coords
                    elif s_start_node == n2_coords:
                        coords_path.extend(coord_pair[::-1])
                        last_pt = n1_coords
                    else:
                        print(f"aaa")
                        print(f"s_start_node: {s_start_node}, linkid_to_nodeids[lid2]:{linkid_to_nodeids[lid2]}, n1_coords:{n1_coords},n2_coords:{n2_coords}")

                #追加するリンクの2点の座標のうち，座標列の最後の点じゃない方を追加．2点の座標どちらも一致しない場合はエラー出力
                else:
                    # last_pt = coords_path[-1]
                    # last_pt = all_coords[-1]
                    if last_pt == coord_pair[0]:
                        coords_path.append(coord_pair[1])
                        last_pt = coords_path[-1]
                    elif last_pt == coord_pair[1]:
                        coords_path.append(coord_pair[0])
                        last_pt = coords_path[-1]
                    else:
                        print(f"エラー:last_pt({last_pt})がリンク{lid2}（{coord_pair}）のどちらの端点にも一致しません")
                        print(f"lid2:{lid2}, coord_pair: {coord_pair}, last_pt:{last_pt}")
                    
                print(f"coords_path: {coords_path}")
            total_len += sum(linkid_to_length[lid] for lid in result_links)
            if all_coords and coords_path:
                if all_coords[-1] == coords_path[0]:
                    all_coords.extend(coords_path[1:])
                else:
                    all_coords.extend(coords_path)
            else:
                all_coords.extend(coords_path)
            #print(f"coords_path: {coords_path}")
            # 次ストローク用開始点を更新&
            #s_start_node = target_nodeid
            s_start_node = nodeid_to_nodeCoords[target_nodeid]


        if total_len < min_length:
            min_length = total_len
            min_path_coords = all_coords

    print("最少右左折経路の座標:", min_path_coords)
    print("その距離:", min_length)
    end_time = time.time()  # 終了時間
    print(f"最少右左折経路の探索時間(最少右左折数探索も含む): {end_time - start_time:.6f} 秒")
    return min_path_coords, min_length
        
    #return minStrokesPath, min_length
    # return startStrokes, goalStrokes  
    return coords_path, total_length 

#第n道なり優先最短経路
import heapq
from collections import deque
def nMinStrokeShortestPath(
    Graph, p1, p2,
    link, length,
    nodeid_to_nodeCoords, linkid_to_linkCoords, linkid_to_length,
    linkid_to_nodeids, node_to_linkids,
    linkid_to_strokeid, strokeid_to_linkids, strokeid_to_intersections
):
    print("第n道なり優先最短経路_pathSearch.py")
    start_time = time.time()
    
    # 最近傍ノードは[lat, lon]のリストで返す
    start_node = str(nearestNode(p1, link))
    goal_node  = str(nearestNode(p2, link))
    print("スタートノード:", start_node , ",ゴールノード:" , goal_node)

    frontiers  = NumberOfMinStrokes(p1, p2, link, node_to_linkids, linkid_to_strokeid, strokeid_to_intersections)
    numberOfMinStrokes = len(frontiers) - 1
    print(f"最少右左折数: {len(frontiers)-1} ")

    # 全ノードへの最短距離計算
    shortestLengths_fromGoal = nx.single_source_dijkstra_path_length(Graph, str(goal_node))
    print(f"all_lengths(goal_nodeから全ノードへの最短距離)を計算．shortestLengths_fromGoal.get(start_node):{shortestLengths_fromGoal.get(start_node)}")
    # print("all_lengths(goal_nodeから全ノードへの最短距離):", shortestLengths_fromGoal)


    stop_print = False #printをするか否かのフラグ
    pop_count =0
    maxStrokes = float('inf')

    hq = []
    results = []

    start_path = [start_node]
    heapq.heappush(hq, [shortestLengths_fromGoal.get(start_node), 0, start_path, 0])
   
    while hq:
        f_value, g_value, node_path, stroke_count = heapq.heappop(hq)
        pop_count=pop_count+1
        if stroke_count >= maxStrokes: #ゴール時に行なう枝切りがうまくいかなかったから，これで代用
            print("発見されたストローク数以上だからcontinue")
            continue
        if not stop_print:
            print(f"[POP] f={f_value}, g={g_value}, path[-1]={node_path[-1]}, stroke_count={stroke_count}")
        curr_node = node_path[-1]

        #ゴール判定
        if curr_node == goal_node:   
            results.append({
                'node_path': node_path[:],
                'distance': g_value,
                'stroke_count': stroke_count,
            })
            # print(f"ゴール発見.results:{results}")
            # ゴールかつ stroke_count==min_strokes で終了
            if stroke_count == numberOfMinStrokes:
                print("探索終了,stroke_count == numberOfMinStrokesを満たした.")
                break
            else:
                # # hqからstroke_count > goal_strokesの要素を除外
                # print(f"枝刈り,")
                # hq = [item for item in hq if item[3] < stroke_count]
                # heapq.heapify(hq)
                
                maxStrokes=stroke_count
                continue  
        for next_node in Graph.neighbors(curr_node):
            # 訪問済み判定
            if str(next_node) in [str(x) for x in node_path]:
                continue
            #ストロークカウント判定
            # [現ノード-次のノード]間のストロークID
            edge_data = Graph.get_edge_data(curr_node, next_node)
            this_stroke_id = edge_data['strokeID']
            #[現ノード-1つ前のノード]間のストロークID
            if len(node_path) >= 2:
                prev_node = str(node_path[-2])
                prev_edge_data = Graph.get_edge_data(prev_node, curr_node)
                prev_stroke_id = prev_edge_data['strokeID']
                new_stroke_count = stroke_count + (1 if prev_stroke_id != this_stroke_id else 0)
            else:
                # 初手,node_pathが1つ(startノードだけ)の時
                new_stroke_count = 1

            edge_length = edge_data['weight']
            next_path = node_path + [next_node]
            next_g = g_value + edge_length
            next_h = shortestLengths_fromGoal.get(next_node)
            next_f = next_g +next_h 

            heapq.heappush(hq, [next_f, next_g, next_path, new_stroke_count])
            if not stop_print:
                print(f"[PUSH] f={next_f}, g={next_g}, path[-1]={next_path[-1]}, stroke_count={new_stroke_count}")

            # if not stop_print:
            #     print("Heap全要素:")
            #     for i, item in enumerate(hq):
            #         print(f"  {i}: f={item[0]}, g={item[1]}, path={item[2]}, stroke_count={item[3]}")

    paths = [res['node_path'] for res in results]
    lengths = [res['distance'] for res in results]

    end_time = time.time()
    print("===== pathsの中身 =====")
    for i, res in enumerate(results):
        path = res['node_path']
        length = res['distance']
        stroke_count = res['stroke_count']
        print(f"経路 {i+1}: ストローク数 = {stroke_count}, 距離 = {length}  ")
        print(f"経路座標列:{path}, ノード列長さ= {len(path)}") 
    # print(f"pop_count:{pop_count}")
    print(f"第n道なり優先最短経路の探索時間: {end_time - start_time:.6f} 秒")
    return paths, lengths
   
#第n道なり優先最短経路，ボツ
import heapq
from collections import deque
def nMinStrokeShortestPath2(
    Graph, p1, p2,
    link, length,
    nodeid_to_nodeCoords, linkid_to_linkCoords, linkid_to_length,
    linkid_to_nodeids, node_to_linkids,
    linkid_to_strokeid, strokeid_to_linkids, strokeid_to_intersections
):
    print("第n道なり優先最短経路_pathSearch.py")
    start_time = time.time()
    
    # 最近傍ノードは[lat, lon]のリストで返す
    start_node = nearestNode(p1, link)  # [lat, lon]
    goal_node  = nearestNode(p2, link)
    print("スタートノード:", start_node , ",ゴールノード:" , goal_node)

    # # networkxへのノードには全てstr([lat, lon])を使う
    # edges = []
    # for i in range(len(link)):
    #     node1 = link[i][0]               # [lat, lon]
    #     node2 = link[i][1]               # [lat, lon]
    #     edges.append((str(node1), str(node2), length[i]))
    # G = nx.Graph()
    # G.add_weighted_edges_from(edges)
    # connectGraph(G)

     
    # 全ノードへの最短距離計算
    shortestLengths_fromGoal = nx.single_source_dijkstra_path_length(Graph, str(goal_node))
    print("all_lengths(goal_nodeから全ノードへの最短距離)を計算")
    # print("all_lengths(goal_nodeから全ノードへの最短距離):", shortestLengths_fromGoal)


    # スタートとゴールのリンク・ストローク
    start_link_ids = node_to_linkids.get(tuple(start_node), [])
    goal_link_ids  = node_to_linkids.get(tuple(goal_node), [])
    goal_strokes = set(linkid_to_strokeid.get(lid) for lid in goal_link_ids if lid in linkid_to_strokeid)

    hq = []
    results = []
    visited = dict()
    output_NumberOfStrokes = None
    best_result_for_stroke = {}  # ← ここに追加（ストローク数ごとの最短経路管理用）

    # # 初期push（スタート座標から全ストローク分）
    # for start_link in start_link_ids:
    #     stroke_id = linkid_to_strokeid.get(start_link)
    #     if stroke_id is None:
    #         continue
    #     g_value = 0.0 #日浦さんの修論での経路長，g値
    #     next_node_key = str(start_node)
    #     h_value = shortestLengths_fromGoal.get(next_node_key, 0)  # ヒューリスティック値
    #     f_value = g_value + h_value
    #     heapq.heappush(hq, (
    #         f_value,                     # 優先度：f値
    #         h_value,                     #目的地までの最短経路長
    #         g_value,                     # 実経路長
    #         1,                           # ストロークカウント
    #         tuple(start_node),           # 現ノード
    #         stroke_id,                   # 現ストローク
    #         [list(start_node)],          # ノード経路
    #         [start_link],                # リンク経路
    #         [stroke_id]                  # ストローク経路    
    # ))
    for start_link in node_to_linkids.get(tuple(start_node), []):
        stroke_id = linkid_to_strokeid[start_link]
        # start_linkの両端ノードを取得し、start_nodeじゃない方をnext_nodeとする
        n1, n2 = linkid_to_nodeids[start_link]
        next_node = n1 if n2 == start_node else n2

        g_value =linkid_to_length[start_link]         # 距離やヒューリスティックなど必要に応じて計算
        # next_node_key = str(list(next_node))  # もしくは str(next_node)、どちらかコードに合ったほう
        next_node_key = str(next_node)
        h_value = shortestLengths_fromGoal.get(next_node_key, 0)  # デフォルト値は0やinfなど
        f_value =g_value + h_value        # 1本目の長さ：linkid_to_length[start_link]
        stroke_count = 1      # 最初の道なりだから1

        heapq.heappush(hq, (
            f_value,
            h_value,
            g_value,
            stroke_count,
            next_node,         # ←「現ノード」は隣接ノード
            stroke_id,
            [start_node, next_node],  # [list(start_node), list(next_node)],  # ノード経路
            [start_link],                        # リンク経路
            [stroke_id]                          # ストローク経路
        ))

    print("------ heapq要素(初期PUSH後) ------")
    for i, entry in enumerate(hq):
        print(f"{i}: {entry}")
    print("------ ここまで ------")   
    found_first_path = False  # 最初の経路発見フラグ，ターミナルに最初の経路までのみを出力するために(アルゴリズムには不必要)    
    # n = 10  # 最大10本
    n = float('inf')
    while hq and len(results) < n:
        # if not found_first_path: #最初の経路発見までのみをターミナル出力するためもの
        #     # print(f"hq:{hq}")
        #     print("------ heapq全要素（f値とノードのみ） ------")
        #     for i, entry in enumerate(hq):
        #         f_val = entry[0]
        #         node_info = entry[4]  # curr_node, next_node など目的のノード座標
        #         print(f"{i}: f={f_val:.4f}, node={node_info}")
        #     print("------ ここまで ------")
        f_value, h_value, g_value, stroke_count, curr_node, curr_stroke, node_path, link_path, stroke_path = heapq.heappop(hq)
        if not found_first_path: #最初の経路発見までのみをターミナル出力するためもの
            print(f"POP: f={f_value:.4f}, g={g_value:.4f}, h={h_value:.4f}, strokes={stroke_count}, node={curr_node}, stroke={curr_stroke}")
        key = (curr_node, curr_stroke)
        if key in visited:
            prev_stroke_count, prev_dist = visited[key]
            if (stroke_count, g_value) >= (prev_stroke_count, prev_dist):
                continue
        visited[key] = (stroke_count, g_value)

        # ゴール条件: ノード座標とストローク
        if curr_node == tuple(goal_node) and curr_stroke in goal_strokes:
            print(f"ゴールに到達: node={curr_node}, f={f_value:.4f}, g={g_value:.4f}, strokes={stroke_count}, stroke={curr_stroke}")
            found_first_path = True
            # もしoutput_NumberOfStrokesが設定済みかつ現在のstroke_countがそれより大きければ追加しない
            if (output_NumberOfStrokes is not None) and (stroke_count > output_NumberOfStrokes):
                continue
            # 現在のstroke_countがoutput_NumberOfStrokesより小さければ更新
            if (output_NumberOfStrokes is None) or (stroke_count < output_NumberOfStrokes):
                output_NumberOfStrokes = stroke_count
            prev_entry = best_result_for_stroke.get(stroke_count)
            if prev_entry is None:
                # 新規ストローク数なので結果追加
                idx = len(results)
                results.append({
                    'stroke_count': stroke_count,
                    'distance': g_value,
                    'node_path': [list(pt) for pt in node_path],
                    'link_path': link_path[:],
                    'stroke_path': stroke_path[:]
                })
                best_result_for_stroke[stroke_count] = (g_value, idx)
            else:
                #経路長が短い順番に結果が出るハズだからこれいらないんじゃね？
                prev_dist, idx = prev_entry
                if g_value < prev_dist:
                    # 距離が短ければ更新
                    results[idx] = {
                        'stroke_count': stroke_count,
                        'distance': g_value,
                        'node_path': [list(pt) for pt in node_path],
                        'link_path': link_path[:],
                        'stroke_path': stroke_path[:]
                    }
                    best_result_for_stroke[stroke_count] = (g_value, idx)
            continue

        # output_NumberOfStrokesを使って、枝刈り
        if (output_NumberOfStrokes is not None) and (stroke_count + 1 > output_NumberOfStrokes):
            continue
        # 現ノード座標からつながるリンクID
        next_link_ids = node_to_linkids.get(curr_node, [])
        for link_id in next_link_ids:
            if link_id not in linkid_to_nodeids or link_id not in linkid_to_strokeid:
                continue
            n1, n2 = linkid_to_nodeids[link_id]
            
            # n1/n2がint（ノードID）型なら座標リストへ変換！
            n1_coords = tuple(nodeid_to_nodeCoords[n1]) if isinstance(n1, int) else tuple(n1)
            n2_coords = tuple(nodeid_to_nodeCoords[n2]) if isinstance(n2, int) else tuple(n2)

                        # curr_nodeがどちらかと一致する側→もう一方に進む
            next_node = n2_coords if n1_coords == curr_node else n1_coords
            next_stroke = linkid_to_strokeid[link_id]
            stroke_increased = 0 if next_stroke == curr_stroke else 1
            
            next_g = g_value + linkid_to_length[link_id]
            next_node_key = str(list(next_node) )
            # next_node_key = str(next_node) 
            next_h = shortestLengths_fromGoal.get(next_node_key, 0)
            # if not found_first_path: #最初の経路発見までのみをターミナル出力するためもの
            #     print(f"next_node_key:{next_node_key}, 型: {type(next_node_key)}")
            #     print(f"next_h:{next_h}")
            next_f = next_g + next_h
            heapq.heappush(hq, (
                next_f,                                 # f値で優先度付け
                next_h, #目的地までの最短経路長，実際にはheapqの要素にする必要はないハズ(h=f-gだから)
                next_g,                            # 実経路長                
                stroke_count + stroke_increased,
                next_node,
                next_stroke,
                node_path + [list(next_node)],
                link_path + [link_id],
                stroke_path + [next_stroke]
            ))
            if not found_first_path: #最初の経路発見までのみをターミナル出力するためもの
                print(f"PUSH: f={next_f:.4f}, g={next_g:.4f}, h={next_h:.4f}, strokes={stroke_count}, node={next_node}, stroke={next_stroke}")
        if not found_first_path: #最初の経路発見までのみをターミナル出力するためもの
            print("------ heapq全要素（f値とノードのみ） ------")
            for i, entry in enumerate(hq):
                f_val = entry[0]
                node_info = entry[4]  # curr_node, next_node など目的のノード座標
                print(f"{i}: f={f_val:.4f}, node={node_info}")
            print("------ ここまで ------")
    paths = [res['node_path'] for res in results]
    lengths = [res['distance'] for res in results]

    end_time = time.time()
    print("===== pathsの中身 =====")
    for i, res in enumerate(results):
        path = res['node_path']
        length = res['distance']
        stroke_count = res['stroke_count']
        print(f"経路 {i+1}: ストローク数 = {stroke_count}, 距離 = {length}  ")
        # print(f"経路座標列:{path}, ノード列長さ= {len(path)}") 
    print(f"第n道なり優先最短経路の探索時間: {end_time - start_time:.6f} 秒")
    return paths, lengths
             
 

#リンク(ストローク)確認用
# def linkCheck(y1, x1, y2, x2, p1, p2,n):
def linkCheck(y1, x1, y2, x2, n):
    print("リンクチェック_pathSearch.py")

    # link, length, link_id = db.getRectangleRoadData1(y1, x1, y2, x2,n) #5個目の引数を入力に加えたら獲得するデータの範囲が変わる(通常n=1,n:範囲を拡大する倍率,数字が大きくなると範囲が大きく)
    link, length, link_id = db.getRectangleRoadData1(35.161659, 136.915446, 35.149409, 136.933791,6)#丸太町(左上)&御器所(右下)の範囲指定
    
    #実装できていない↓
    #リンクIDで探す
    SerchingLinkID = 1648027
    # SerchingLinkIDに対応するリンクの座標を取得
    try:
        idx = link_id.index(SerchingLinkID)
        outputLink = link[idx]
        outputLength = length[idx]
        print(f"outputLink: {outputLink}")
        print(f"outputLength: {outputLength}")
    except ValueError:
        #print(f"リンクID ({SerchingLinkID})はlink_idリストにありません")
        outputLink = None
        outputLength = None

    
    #path=outputLink #リンクをチェックしたい時
    path=link #データベースから獲得したリンクを全部表示
    length = outputLength
    return path, length
    # return startStrokes, goalStrokes  



#ノードが属するストロークを返す
def node_to_stroke(node, node_to_linkids, linkid_to_strokeid):
    #print("ノード→ストローク変換_pathSearch.py")
  
    # キー形式をtupleで正規化
    key = tuple(node)
    #print(f"入力ノード座標: {key}")

    # そのノードから出るリンクIDリスト取得
    linkids = node_to_linkids.get(key, [])
    #print(f"  このノードから出るリンクIDリスト: {linkids}")
    if not linkids:
        print(f"{node} に該当するリンクがありません")
        return set()
    
    strokeids = set()
    for lid in linkids:
        sid = linkid_to_strokeid.get(lid, None)
        #print(f"    リンクID {lid} のストロークID: {sid}")
        if sid is not None:
            strokeids.add(sid)
    #print(f"  このノードに関連するストロークIDのセット: {strokeids}")
    return strokeids
   
#-----------以下,田中のプログラムで使用していない(高橋システム従来のもの)----------------

#最小全域木
def MST(link, length):
    #networkxのグラフを生成
    edges = []
    for i in range(len(link)):
        edges.append((str(link[i][0]), str(link[i][1]), length[i]))
    G = nx.Graph()
    G.add_weighted_edges_from(edges)
    connectGraph(G)

    #最小全域木を構成
    t = nx.minimum_spanning_tree(G)
    path = []
    for edge in t.edges():
        start = [float(x) for x in edge[0].strip('[]').split(',')]
        end = [float(x) for x in edge[1].strip('[]').split(',')]
        path.append([start, end])
    return path

#シュタイナー木
def steiner(points, link, length):
    #ターミナルノード
    terminal = []
    for p in points:
        terminal.append(str(nearestNode(p, link)))

    #networkxのグラフを生成
    edges = []
    for i in range(len(link)):
        edges.append((str(link[i][0]), str(link[i][1]), length[i]))
    G = nx.Graph()
    G.add_weighted_edges_from(edges)
    connectGraph(G)

    #シュタイナー木を構成
    t = nx.algorithms.approximation.steinertree.steiner_tree(G, terminal_nodes=terminal, method='mehlhorn')
    path = []
    for edge in t.edges():
        start = [float(x) for x in edge[0].strip('[]').split(',')]
        end = [float(x) for x in edge[1].strip('[]').split(',')]
        path.append([start, end])
    return path

#巡回経路
def traveling(points, link, length):
    print("巡回経路_pathSearch.py")
    #通るポイント(都市)
    positions = []
    for p in points:
        positions.append(str(nearestNode(p, link)))

    #巡回セールスマン問題のためのグラフ
    G = nx.Graph()
    G.add_nodes_from(positions)

    #都市間の最短経路を求めるためのグラフ
    G_temp = nx.Graph()
    edges = []
    for i in range(len(link)):
        edges.append((str(link[i][0]), str(link[i][1]), length[i]))
    G_temp.add_weighted_edges_from(edges)

    #都市間の最短経路を求めて，Gのエッジとする
    for u in positions:
        for v in positions:
            if positions.index(u) < positions.index(v):
                G.add_edge(u, v, weight=nx.dijkstra_path_length(G_temp, u, v))
    
    #巡回セールスマン問題を解く
    tsp = list(nx.algorithms.approximation.traveling_salesman_problem(G))

    #巡回順に最短経路を求めて返却
    paths = []
    length = 0
    for i in range(len(tsp)-1):
        path_str = nx.dijkstra_path(G_temp, tsp[i], tsp[i+1])
        length += nx.dijkstra_path_length(G_temp, tsp[i], tsp[i+1])
        for line in path_str:
            paths.append([float(x) for x in line.strip('[]').split(',')])
    
    print("length(巡回経路):", length, ",type(length):", type(length)) #中身知る用
    return paths, length