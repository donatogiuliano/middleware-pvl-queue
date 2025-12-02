import os
import time
import json
import redis
import datetime
import pytz

# --- REDIS KONFIGURATION ---
REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
QUEUE_NAME = 'potentiation_queue'
RESULTS_KEY = 'latest_results'
CONTROL_KEY = 'consumer_control'

# Warten auf Redis
while True:
    try:
        r = redis.Redis(host=REDIS_HOST, port=6379, db=0)
        r.ping()
        print(f"CONSUMER: Erfolgreich mit Redis verbunden.")
        break
    except Exception as e:
        print(f"CONSUMER: Warte auf Redis ({e})...")
        time.sleep(5)

# Hauptschleife
while True:
    try:
        # 1. Prüfe STOP-Flag
        control_status = r.get(CONTROL_KEY)
        if control_status and control_status.decode('utf-8') == 'STOPPED':
            time.sleep(2)
            continue 
        
        # 2. Auftrag holen
        item = r.brpop(QUEUE_NAME, timeout=1) 
        
        if item:
            queue_name, task_data_bytes = item
            task_data = json.loads(task_data_bytes.decode('utf-8'))
            
            x = task_data.get('x', 0)
            task_id = task_data.get('id', 'N/A')
            
            print(f"CONSUMER: Starte Aufgabe {task_id[:8]}...")
            
            # --- BERECHNUNG ---
            result = x ** 2
            
            # HIER DIE ÄNDERUNG: 6 Sekunden schlafen
            time.sleep(6) 
            
            # Zeitumrechnung für Deutschland (CET)
            utc_now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
            cet_tz = pytz.timezone('Europe/Berlin')
            cet_now = utc_now.astimezone(cet_tz)

            # Ergebnis speichern
            result_data = {
                'id': task_id,
                'x': x,
                'result': result,
                'timestamp': cet_now.strftime("%H:%M:%S")
            }
            
            r.hset(RESULTS_KEY, task_id, json.dumps(result_data))

            print(f"CONSUMER: Fertig: {x}^2 = {result}")
            
    except Exception as e:
        print(f"CONSUMER: Fehler: {e}")
        time.sleep(5)