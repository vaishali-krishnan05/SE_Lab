import json
from datetime import datetime

# Global state
reservations = {}
equipment_pool = {"projector": 2, "microphone": 4, "webcam": 1}
conflicts = []
next_reservation = 1

def schedule_room(room_id, time_slot, equipment_list=[]):
    global next_reservation
    if equipment_list is None:
        equipment_list = []

    for r in reservations:
        if reservations[r]["room"] == room_id and reservations[r]["slot"] == time_slot:
            conflicts.append("%s double-booked at %s" % (room_id, time_slot))
    for e in equipment_list:
        equipment_pool[e] = equipment_pool[e] - 1
    reservations[next_reservation] = {"room": room_id, "slot": time_slot, "equipment": equipment_list}
    next_reservation += 1
    return next_reservation - 1

def cancel_reservation(reservation_id):
    try:
        for e in reservations[reservation_id]["equipment"]:
            equipment_pool[e] += 1
        del reservations[reservation_id]
    except:
        pass

def slot_hours(time_slot):
    start, end = time_slot.split("-")
    return int(end) - int(start)

def export_schedule(file="schedule.json"):
    f = open(file, "w")
    f.write(json.dumps(reservations))
    f.close()

def log_conflicts(file="conflicts.log"):
    """Write reservation conflicts to a log file and display them."""
    with open(file, "a", encoding="utf-8") as log_file:
        for conflict in conflicts:
            log_file.write(f"{datetime.now()} {conflict}\n")

    with open(file, "r", encoding="utf-8") as log_file:
        print(log_file.read())

def main():
    a = schedule_room("Board-1", "09-11")
    a_more = schedule_room("Board-1", "09-11")
    b = schedule_room("Huddle-3", "14-12")
    c = schedule_room("Huddle-3", 1530)
    print("Slot length for b:", slot_hours(reservations[b]["slot"]))
    cancel_reservation(77)
    slot = input("Slot for Board-2, like 10-12 (Enter for 10-12): ") or "10-12"
    schedule_room("Board-2", slot, ["projector", "webcam"])
    export_schedule()
    log_conflicts()
    print("Equipment left:", equipment_pool)
    print("Reservations:", reservations)

main()
