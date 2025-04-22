"""
データベースアクセスを行う
"""
import psycopg2

DBNAME = "osm_road_db"
USER = "postgres"
PASS = "usadasql"
URL = "rain-vm.yamamoto.nitech.ac.jp"
PORT = 5432

#矩形範囲の道路データを取得する
#(y1, x1):左上の緯度経度 (y2, x2):右下の緯度経度 n:範囲を拡大する倍率
def getRectangleRoadData(y1, x1, y2, x2, n = 1):
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
        for rs in docs:
            link.append([[float(rs[10]), float(rs[9])], [float(rs[12]), float(rs[11])]])
            length.append(float(rs[7]))
            #print("rs：",rs)       
    except Exception as e:
        print(e)
    
    
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
        link_IDs = []
        for row in rows:
            id, link_ids, stroke_length, stroke_clazz, wkt = row
            stroke_id.append(float(id))
            link_IDs.append(link_ids)
            #print(f"stroke_id:{stroke_id} links:{link_ids} length:{stroke_length} clazz:{stroke_clazz} wkt:{wkt}")
        print("stroke_id:",stroke_id)
        print("link_IDs:",link_IDs)
    
    #交差ストロークを獲得したい
    if not stroke_id:
        print("stroke_idリストが空です")
    else:
        # リストを SQL内で使える形に変換
        stroke_id_array_str = ','.join(map(str, stroke_id))
        sql = f"""
        SELECT stroke_id, intersect_stroke_id
        FROM stroke_v2.nagoya_intersect_stroke_table
        WHERE stroke_id = ANY(ARRAY[{stroke_id_array_str}])
        """
        cur.execute(sql)
        rows = cur.fetchall()
        
        # stroke_idごとに intersect_stroke_idをまとめるdict
        # 値はリストでもsetでも良い。ここではsetで重複排除＋検索高速化
        strokeID_to_intersectIDs = {}
        for stroke_id, intersect_stroke_id in rows:
            strokeID_to_intersectIDs.setdefault(stroke_id, set()).add(intersect_stroke_id)
        print("strokeID_to_intersectIDs:",strokeID_to_intersectIDs)


    cur.close()
    conn.close()

    return link, length