"""
データベースアクセスを行う
"""
import psycopg2

DBNAME = "osm_road_db"
USER = "postgres"
PASS = "usadasql"
URL = "rain-vm.yamamoto.nitech.ac.jp"
PORT = 5432



#矩形範囲の道路データを取得する，高橋システム従来の，リンクデータのみ
#(y1, x1):左上の緯度経度 (y2, x2):右下の緯度経度 n:範囲を拡大する倍率
def getRectangleRoadData1(y1, x1, y2, x2, n = 1):
    x = abs(x2-x1)
    y = abs(y2-y1)
    x1 = x1-x*(n-1)
    x2 = x2+x*(n-1)
    y1 = y1+y*(n-1)
    y2 = y2-y*(n-1)
    #print("y1:",y1,",x1:",x1,",y2:",y2,",x2:",x2,",n:",n,",x:",x,",y:",y)

    conn = psycopg2.connect(database=DBNAME, user=USER, password=PASS, host=URL, port=PORT)
    cur = conn.cursor()

    try:
        statement = "select  "\
                        "id, osm_name, osm_source_id, osm_target_id, clazz, source, target, km, cost, x1, y1, x2, y2, geom_way  "\
                    "from "\
                        "osm_japan_car_2po_4pgr  "\
                    "where "\
                        "st_intersects("\
                            "st_geomFromText("\
                                "'polygon(("+str(x1)+" "+str(y2)+","+str(x2)+" "+str(y2)+","+str(x2)+" "+str(y1)+","+str(x1)+" "+str(y1)+","+str(x1)+" "+str(y2)+"))', 4326),"\
                            "geom_way) "\
                        ""
        cur.execute(statement)
        docs = cur.fetchall()

        link = []
        length = []
        # link_id = []
        for rs in docs:

            link.append([[float(rs[10]), float(rs[9])], [float(rs[12]), float(rs[11])]])
            length.append(float(rs[7]))
            #print("rs：",rs)       
    except Exception as e:
        print(e)
    
    cur.close()
    conn.close()

    # return link, length, link_id #link_idはlinkCheck関数を使わないなら不必要
    return link, length


#矩形範囲の道路データを取得する
#(y1, x1):左上の緯度経度 (y2, x2):右下の緯度経度 n:範囲を拡大する倍率
def getRectangleRoadData(y1, x1, y2, x2, n = 1):
    #main.pyの呼び出し箇所でnの値を入力している(必ずしもn=1じゃない)
    print(f"def getRectangleRoadData(y1, x1, y2, x2, n = {n}):、矩形範囲の道路データを取得する")
    x = abs(x2-x1)
    y = abs(y2-y1)
    x1 = x1-x*(n-1)
    x2 = x2+x*(n-1)
    y1 = y1+y*(n-1)
    y2 = y2-y*(n-1)
    #print("y1:",y1,",x1:",x1,",y2:",y2,",x2:",x2,",n:",n,",x:",x,",y:",y)

    print("ノードデータ&リンクデータを取得する")
    conn = psycopg2.connect(database=DBNAME, user=USER, password=PASS, host=URL, port=PORT)
    cur = conn.cursor()

    try:
        statement = "select  "\
                        "id, osm_name, osm_source_id, osm_target_id, clazz, source, target, km, cost, x1, y1, x2, y2, geom_way  "\
                    "from "\
                        "osm_japan_car_2po_4pgr  "\
                    "where "\
                        "st_intersects("\
                            "st_geomFromText("\
                                "'polygon(("+str(x1)+" "+str(y2)+","+str(x2)+" "+str(y2)+","+str(x2)+" "+str(y1)+","+str(x1)+" "+str(y1)+","+str(x1)+" "+str(y2)+"))', 4326),"\
                            "geom_way) "\
                        ""
        cur.execute(statement)
        docs = cur.fetchall()
        link = []
        length = [] #現状ではこれいらなさそう，linkid_to_lengthで距離を追加している
        node_to_linkids = {}
        nodeid_to_nodeCoords = {}
        linkid_to_linkCoords = {}
        linkid_to_nodeids = {}
        linkid_to_length = {}

        for rs in docs:
            pt1 = [float(rs[10]), float(rs[9])]   # x1, y1 => [経度, 緯度]
            pt2 = [float(rs[12]), float(rs[11])]  # x2, y2 => [経度, 緯度]
            link_id = int(rs[0])
            osm_source_id = int(rs[2])
            osm_target_id = int(rs[3])
            source = int(rs[5])
            target = int(rs[6])

            # リンク座標リスト
            link.append([pt1, pt2])
            # 長さ
            link_length = float(rs[7])
            length.append(float(rs[7]))
            # リンクIDから距離
            linkid_to_length[link_id] = link_length
            # リンクIDから座標
            linkid_to_linkCoords[link_id] = [pt1, pt2]
            # ノード座標→リンク
            for pt in [pt1, pt2]:
                key = tuple(pt)
                node_to_linkids.setdefault(key, []).append(link_id)
            # ノードID→座標
            if source not in nodeid_to_nodeCoords:
                nodeid_to_nodeCoords[source] = pt1
            if target not in nodeid_to_nodeCoords:
                nodeid_to_nodeCoords[target] = pt2
            # # ノードID→座標
            # if osm_source_id not in nodeid_to_nodeCoords:
            #     nodeid_to_nodeCoords[osm_source_id] = pt1
            # if osm_target_id not in nodeid_to_nodeCoords:
            #     nodeid_to_nodeCoords[osm_target_id] = pt2
            # リンクID→両端ノードID
            linkid_to_nodeids[link_id] = (source, target)

        # print("link:", link)
        # print("length:", length)
        # print("node_to_linkids:", node_to_linkids)
        # print("nodeid_to_nodeCoords:", nodeid_to_nodeCoords)
        # print("linkid_to_linkCoords:", linkid_to_linkCoords)
        # print("linkid_to_nodeids:", linkid_to_nodeids)
        # print("linkid_to_length:", linkid_to_length)
        

        
    except Exception as e:
        print(e)
    
    print("ストロークデータを取得する")
    #ストロークデータを獲得したい
    # クエリで取得したリンクIDリスト
    link_ids_in_area = [int(rs[0]) for rs in docs]

    if not link_ids_in_area:
        print("選択範囲に該当するリンクがありません")
    else:
        id_array_str = ','.join(map(str, link_ids_in_area))
        sql = f"""
        SELECT id, link_ids, stroke_length, stroke_clazz, ST_AsText(arc_series) AS wkt
        FROM stroke_v2.stroke_table
        WHERE EXISTS (
            SELECT 1 FROM unnest(string_to_array(link_ids, ',')) AS lid
            WHERE lid::int = ANY(ARRAY[{id_array_str}])
        )
        """
        cur.execute(sql)
        rows = cur.fetchall()
        stroke_id = []
        link_ids_inStroke = []
        for row in rows:
            id, link_ids, stroke_length, stroke_clazz, wkt = row
            stroke_id.append(int(id))
            link_ids_inStroke.append(link_ids)
            print(f"stroke_id:{stroke_id} links:{link_ids} length:{stroke_length} clazz:{stroke_clazz} wkt:{wkt}")
        # print("stroke_id:",stroke_id)
        # print("link_IDs:",link_IDs)

        # 1. ストロークID→リンクIDリスト
        strokeid_to_linkids = {}
        for sid, lidstr in zip(stroke_id, link_ids_inStroke):
            lid_int_list = [int(lid.strip()) for lid in lidstr.split(',')]
            strokeid_to_linkids[sid] = lid_int_list
        #print("strokeid_to_linkids:",strokeid_to_linkids)

        # 2. リンクID→ストロークID（1:1対応）
        linkid_to_strokeid = {}
        for sid, lid_list in strokeid_to_linkids.items():
            for lid in lid_list:
                linkid_to_strokeid[lid] = sid  # ひとつのリンクはひとつのストロークだけに属する
        #print("linkid_to_strokeid:",linkid_to_strokeid)

        # # 3. linkリストのindexから直接ストロークIDも取得できると便利なら
        # link_index_to_strokeID = {}
        # for idx, link_id in enumerate(link_ids_in_area):
        #     link_index_to_strokeID[idx] = linkid_to_strokeid.get(link_id, None)
        
    print("交差ストロークデータを取得する")
    #交差ストロークを獲得したい
    #strokeid_to_intersectionsは各ストロークに対して交差ストローク&交差ノードのデータ群がある
    if not stroke_id:
        print("stroke_idリストが空です")
    else:
        # リストを SQL内で使える形に変換
        stroke_id_array_str = ','.join(map(str, stroke_id))
        sql = f"""
        SELECT stroke_id, intersect_stroke_id, intersect_node_id
        FROM stroke_v2.nagoya_intersect_stroke_table
        WHERE stroke_id = ANY(ARRAY[{stroke_id_array_str}])
        """
        cur.execute(sql)
        rows = cur.fetchall()
        
        # { stroke_id: { intersect_stroke_id: intersect_node_id, ... }, ... }
        strokeid_to_intersections = {}
        for s_id, intersect_s_id, intersect_node_id in rows:
            if s_id not in strokeid_to_intersections:
                strokeid_to_intersections[s_id] = {}
            strokeid_to_intersections[s_id][intersect_s_id] = intersect_node_id

        #print(f"strokeid_to_intersectids: {strokeid_to_intersections} ")


    cur.close()
    conn.close()

    # 各辞書のデータ型を出力
    dicts = {
    "nodeid_to_nodeCoords": nodeid_to_nodeCoords,
    "linkid_to_linkCoords": linkid_to_linkCoords,
    "linkid_to_length": linkid_to_length,
    "linkid_to_nodeids": linkid_to_nodeids,
    "node_to_linkids": node_to_linkids,
    }
    if 'strokeid_to_linkids' in locals():
        dicts["strokeid_to_linkids"] = strokeid_to_linkids
    if 'linkid_to_strokeid' in locals():
        dicts["linkid_to_strokeid"] = linkid_to_strokeid
    if 'strokeid_to_intersections' in locals():
        dicts["strokeid_to_intersections"] = strokeid_to_intersections
    for name, d in dicts.items():
        print(f"{name}: {type(d)}")
        if d:
            key0 = next(iter(d))
            val0 = d[key0]
            print(f"  key type: {type(key0)}, value type: {type(val0)}")
            # 値がlist/dictなら中身も見る
            if isinstance(val0, list) and val0:
                print(f"    value[0] type: {type(val0[0])}")
            if isinstance(val0, dict) and val0:
                key1 = next(iter(val0))
                val1 = val0[key1]
                print(f"    value key type: {type(key1)}, value value type: {type(val1)}")
        else:
            print(f"  {name} is empty")
   

    return link, length, nodeid_to_nodeCoords, linkid_to_linkCoords, linkid_to_length, linkid_to_nodeids, node_to_linkids, stroke_id, link_ids_inStroke, strokeid_to_linkids, linkid_to_strokeid, strokeid_to_intersections

           