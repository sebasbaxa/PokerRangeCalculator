from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from config import db, Config
from models import Range, RangeHand
from calculator.objects import Card, Hand, CardRange
from calculator.logic import MakeRange
from calculator.simulation import RunSimulations
import json
import time
from threading import Thread
from queue import Queue
import traceback

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

db.init_app(app)

# Create tables
with app.app_context():
    db.create_all()

maker = MakeRange()
settings = {"num_simulations": 100}

# For live updates
simulation_queues = {}

rank_char = {14: 'A', 13: 'K', 12: 'Q', 11: 'J', 10: 'T',
             9: '9', 8: '8', 7: '7', 6: '6', 5: '5',
             4: '4', 3: '3', 2: '2'}

def hand_label(hand: Hand) -> str:
    r1, r2 = hand.card1.rank, hand.card2.rank
    s1, s2 = hand.card1.suit, hand.card2.suit
    a, b = rank_char[r1], rank_char[r2]
    if r1 == r2:
        return f"{a}{a}"
    suited = (s1 == s2)
    if r1 > r2:
        return f"{a}{b}{'s' if suited else 'o'}"
    return f"{b}{a}{'s' if suited else 'o'}"

def get_or_create_range(role: str) -> Range:
    """Get or create hero/villain range"""
    range_obj = Range.query.filter_by(role=role).first()
    if not range_obj:
        range_obj = Range(name=f"{role.capitalize()} Range", role=role)
        db.session.add(range_obj)
        db.session.commit()
    return range_obj

def db_range_to_card_range(range_obj: Range) -> CardRange:
    """Convert DB Range to CardRange object"""
    card_range = CardRange()
    for rh in range_obj.hands:
        hand = Hand(
            Card(rh.card1_suit, rh.card1_rank),
            Card(rh.card2_suit, rh.card2_rank)
        )
        card_range.add(hand)
    return card_range

def hand_exists_in_range(range_id: int, card1_suit: str, card1_rank: int, card2_suit: str, card2_rank: int) -> bool:
    """Check if a hand already exists in the range (canonicalized)"""
    # Create a temporary RangeHand to canonicalize the input
    temp = RangeHand(
        range_id=range_id,
        card1_suit=card1_suit,
        card1_rank=card1_rank,
        card2_suit=card2_suit,
        card2_rank=card2_rank
    )
    temp.canonicalize()
    
    # Now check with canonicalized values
    exists = RangeHand.query.filter_by(
        range_id=range_id,
        card1_suit=temp.card1_suit,
        card1_rank=temp.card1_rank,
        card2_suit=temp.card2_suit,
        card2_rank=temp.card2_rank
    ).first()
    
    return exists is not None

@app.get("/api/health")
def health():
    return jsonify({"ok": True})

@app.route("/api/settings", methods=["GET", "POST"])
def api_settings():
    if request.method == "GET":
        return jsonify(settings)
    data = request.get_json(silent=True) or {}
    try:
        v = int(data.get("num_simulations", 100))
        if v <= 0:
            raise ValueError("num_simulations must be positive")
        settings["num_simulations"] = v
        return jsonify({"success": True, "num_simulations": v})
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route("/api/ranges/hero", methods=["GET", "POST", "DELETE"])
def api_hero_range():
    try:
        range_obj = get_or_create_range('hero')
        
        if request.method == "GET":
            return jsonify({"hands": [h.to_hand_dict() for h in range_obj.hands]})
        
        if request.method == "POST":
            hands_data = (request.json or {}).get("hands", [])
            added_count = 0
            skipped_count = 0
            
            print(f"Attempting to add {len(hands_data)} hands to hero range")
            
            for h_data in hands_data:
                try:
                    # Validate hand data
                    if not h_data.get('card1') or not h_data.get('card2'):
                        print(f"Skipping invalid hand data: {h_data}")
                        skipped_count += 1
                        continue
                    
                    card1 = h_data['card1']
                    card2 = h_data['card2']
                    
                    # Check if hand already exists
                    if hand_exists_in_range(range_obj.id, card1['suit'], card1['rank'], 
                                           card2['suit'], card2['rank']):
                        print(f"Hand already exists: {card1['rank']}{card1['suit']} {card2['rank']}{card2['suit']}")
                        skipped_count += 1
                        continue
                    
                    # Add the hand
                    rh = RangeHand.from_hand_dict(range_obj.id, h_data)
                    db.session.add(rh)
                    added_count += 1
                    print(f"Added hand: {card1['rank']}{card1['suit']} {card2['rank']}{card2['suit']}")
                    
                except Exception as e:
                    print(f"Error adding hand: {e}")
                    print(f"Hand data: {h_data}")
                    skipped_count += 1
                    continue
            
            db.session.commit()
            print(f"Committed: {added_count} added, {skipped_count} skipped")
            return jsonify({"success": True, "added": added_count, "skipped": skipped_count})
        
        # DELETE
        count = RangeHand.query.filter_by(range_id=range_obj.id).delete()
        db.session.commit()
        return jsonify({"success": True, "deleted": count})
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in hero_range: {traceback.format_exc()}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/ranges/villain", methods=["GET", "POST", "DELETE"])
def api_villain_range():
    try:
        range_obj = get_or_create_range('villain')
        
        if request.method == "GET":
            return jsonify({"hands": [h.to_hand_dict() for h in range_obj.hands]})
        
        if request.method == "POST":
            hands_data = (request.json or {}).get("hands", [])
            added_count = 0
            skipped_count = 0
            
            print(f"Attempting to add {len(hands_data)} hands to villain range")
            
            for h_data in hands_data:
                try:
                    if not h_data.get('card1') or not h_data.get('card2'):
                        print(f"Skipping invalid hand data: {h_data}")
                        skipped_count += 1
                        continue
                    
                    card1 = h_data['card1']
                    card2 = h_data['card2']
                    
                    if hand_exists_in_range(range_obj.id, card1['suit'], card1['rank'],
                                           card2['suit'], card2['rank']):
                        print(f"Hand already exists: {card1['rank']}{card1['suit']} {card2['rank']}{card2['suit']}")
                        skipped_count += 1
                        continue
                    
                    rh = RangeHand.from_hand_dict(range_obj.id, h_data)
                    db.session.add(rh)
                    added_count += 1
                    print(f"Added hand: {card1['rank']}{card1['suit']} {card2['rank']}{card2['suit']}")
                    
                except Exception as e:
                    print(f"Error adding hand: {e}")
                    print(f"Hand data: {h_data}")
                    skipped_count += 1
                    continue
            
            db.session.commit()
            print(f"Committed: {added_count} added, {skipped_count} skipped")
            return jsonify({"success": True, "added": added_count, "skipped": skipped_count})
        
        # DELETE
        count = RangeHand.query.filter_by(range_id=range_obj.id).delete()
        db.session.commit()
        return jsonify({"success": True, "deleted": count})
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in villain_range: {traceback.format_exc()}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.post("/api/hands/generate")
def api_generate_hands():
    try:
        data = request.json or {}
        t = data.get("type")
        r1 = data.get("rank1")
        r2 = data.get("rank2")
        
        print(f"Generate hands request: type={t}, rank1={r1}, rank2={r2}")
        
        # Validate inputs
        if not t or r1 is None:
            return jsonify({"error": "Missing required fields"}), 400
        
        r1 = int(r1)
        if r2 is not None:
            r2 = int(r2)
        
        # Validate rank values
        if r1 < 2 or r1 > 14:
            return jsonify({"error": "Invalid rank1 value"}), 400
        if r2 is not None and (r2 < 2 or r2 > 14):
            return jsonify({"error": "Invalid rank2 value"}), 400
        
        if t == "pocket":
            hands = maker.pocket_pair(r1)
        elif t == "suited":
            if r2 is None:
                return jsonify({"error": "rank2 required for suited hands"}), 400
            hands = maker.suited_hand(r1, r2)
        elif t == "offsuit":
            if r2 is None:
                return jsonify({"error": "rank2 required for offsuit hands"}), 400
            hands = maker.offsuit_hand(r1, r2)
        else:
            return jsonify({"error": f"Invalid type: {t}"}), 400
        
        hands_json = [h.to_dict() for h in hands]
        print(f"Generated {len(hands_json)} hands")
        return jsonify({"hands": hands_json})
        
    except Exception as e:
        print(f"Error generating hands: {traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500

@app.post("/api/simulate")
def api_simulate():
    """Start simulation and return immediately with a task ID"""
    try:
        num = (request.json or {}).get("num_simulations", settings["num_simulations"])
        num = int(num)
        
        if num <= 0:
            return jsonify({"error": "num_simulations must be positive"}), 400

        # Load ranges from DB
        hero_range_db = get_or_create_range('hero')
        villain_range_db = get_or_create_range('villain')
        
        hero_range = db_range_to_card_range(hero_range_db)
        villain_range = db_range_to_card_range(villain_range_db)
        
        if not hero_range.card_range:
            return jsonify({"error": "Hero range is empty"}), 400
        if not villain_range.card_range:
            return jsonify({"error": "Villain range is empty"}), 400

        # Create a unique task ID
        import uuid
        task_id = str(uuid.uuid4())
        
        # Create queue for this simulation
        simulation_queues[task_id] = Queue()
        
        # Start simulation in background thread
        def run_simulation():
            try:
                results = {}
                for idx, hand in enumerate(hero_range.card_range):
                    temp = CardRange()
                    temp.add(hand)
                    win, vill_win, split = RunSimulations(temp, villain_range, [], num).run()
                    label = hand_label(hand)
                    results[label] = {
                        "win_rate": win,
                        "hand": hand.to_dict()
                    }
                    
                    # Send progress update
                    progress = {
                        "type": "progress",
                        "label": label,
                        "win_rate": win,
                        "completed": idx + 1,
                        "total": len(hero_range.card_range)
                    }
                    simulation_queues[task_id].put(progress)
                
                # Send completion
                simulation_queues[task_id].put({"type": "complete", "results": results})
            except Exception as e:
                print(f"Simulation error: {traceback.format_exc()}")
                simulation_queues[task_id].put({"type": "error", "error": str(e)})
        
        thread = Thread(target=run_simulation)
        thread.daemon = True
        thread.start()
        
        return jsonify({"task_id": task_id})
        
    except Exception as e:
        print(f"Error starting simulation: {traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500

@app.get("/api/simulate/stream/<task_id>")
def simulate_stream(task_id):
    """Server-Sent Events endpoint for live updates"""
    def generate():
        if task_id not in simulation_queues:
            yield f"data: {json.dumps({'type': 'error', 'error': 'Invalid task ID'})}\n\n"
            return
        
        queue = simulation_queues[task_id]
        
        while True:
            try:
                msg = queue.get(timeout=30)
                yield f"data: {json.dumps(msg)}\n\n"
                
                if msg.get("type") in ["complete", "error"]:
                    # Clean up
                    if task_id in simulation_queues:
                        del simulation_queues[task_id]
                    break
            except:
                # Timeout - send keepalive
                yield f": keepalive\n\n"
    
    return Response(generate(), mimetype='text/event-stream')

@app.get("/api/debug/ranges")
def debug_ranges():
    """Debug endpoint to see all hands in ranges"""
    try:
        hero_range_db = get_or_create_range('hero')
        villain_range_db = get_or_create_range('villain')
        
        hero_range = db_range_to_card_range(hero_range_db)
        villain_range = db_range_to_card_range(villain_range_db)
        
        hero_labels = {}
        for hand in hero_range.card_range:
            label = hand_label(hand)
            hero_labels[label] = {
                'card1': f"{hand.card1.rank}{hand.card1.suit}",
                'card2': f"{hand.card2.rank}{hand.card2.suit}"
            }
        
        villain_labels = {}
        for hand in villain_range.card_range:
            label = hand_label(hand)
            villain_labels[label] = {
                'card1': f"{hand.card1.rank}{hand.card1.suit}",
                'card2': f"{hand.card2.rank}{hand.card2.suit}"
            }
        
        return jsonify({
            'hero': {
                'count': len(hero_range.card_range),
                'labels': hero_labels
            },
            'villain': {
                'count': len(villain_range.card_range),
                'labels': villain_labels
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True, threaded=True)