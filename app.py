from flask import Flask, render_template, request, jsonify
import random

app = Flask(__name__)

# ─── FCFS ───────────────────────────────────────────────────────────────────
def fcfs(requests, head):
    steps, total, pos = [], 0, head
    for r in requests:
        seek = abs(r - pos)
        total += seek
        steps.append({"from": pos, "to": r, "seek": seek})
        pos = r
    return {"steps": steps, "total": total, "order": [s["to"] for s in steps]}

# ─── SSTF ───────────────────────────────────────────────────────────────────
def sstf(requests, head):
    steps, total, pos = [], 0, head
    pending = list(requests)
    while pending:
        closest = min(pending, key=lambda x: abs(x - pos))
        seek = abs(closest - pos)
        total += seek
        steps.append({"from": pos, "to": closest, "seek": seek})
        pos = closest
        pending.remove(closest)
    return {"steps": steps, "total": total, "order": [s["to"] for s in steps]}

# ─── SCAN ───────────────────────────────────────────────────────────────────
def scan(requests, head, disk_size=200, direction="right"):
    steps, total, pos = [], 0, head
    left  = sorted([r for r in requests if r < head])
    right = sorted([r for r in requests if r >= head])

    if direction == "right":
        seq = right + ([disk_size - 1] if right and right[-1] != disk_size - 1 else []) + list(reversed(left))
    else:
        seq = list(reversed(left)) + ([0] if left and left[0] != 0 else []) + right

    for r in seq:
        seek = abs(r - pos)
        total += seek
        steps.append({"from": pos, "to": r, "seek": seek})
        pos = r

    return {"steps": steps, "total": total, "order": [s["to"] for s in steps]}

# ─── C-SCAN ──────────────────────────────────────────────────────────────────
def cscan(requests, head, disk_size=200, direction="right"):
    steps, total, pos = [], 0, head
    left  = sorted([r for r in requests if r < head])
    right = sorted([r for r in requests if r >= head])

    def add(frm, to):
        nonlocal pos, total
        seek = abs(to - frm)
        total += seek
        steps.append({"from": frm, "to": to, "seek": seek, "jump": False})
        pos = to

    def jump(frm, to):
        nonlocal pos, total
        seek = abs(to - frm)
        total += seek
        steps.append({"from": frm, "to": to, "seek": seek, "jump": True})
        pos = to

    if direction == "right":
        for r in right:
            add(pos, r)
        if pos != disk_size - 1:
            add(pos, disk_size - 1)
        jump(pos, 0)
        for r in left:
            add(pos, r)
    else:
        for r in reversed(left):
            add(pos, r)
        if pos != 0:
            add(pos, 0)
        jump(pos, disk_size - 1)
        for r in reversed(right):
            add(pos, r)

    return {"steps": steps, "total": total, "order": [s["to"] for s in steps]}

# ─── LOOK ───────────────────────────────────────────────────────────────────
def look(requests, head, direction="right"):
    steps, total, pos = [], 0, head
    left  = sorted([r for r in requests if r < head])
    right = sorted([r for r in requests if r >= head])

    seq = (right + list(reversed(left))) if direction == "right" else (list(reversed(left)) + right)

    for r in seq:
        seek = abs(r - pos)
        total += seek
        steps.append({"from": pos, "to": r, "seek": seek})
        pos = r

    return {"steps": steps, "total": total, "order": [s["to"] for s in steps]}

# ─── C-LOOK ──────────────────────────────────────────────────────────────────
def clook(requests, head, direction="right"):
    steps, total, pos = [], 0, head
    left  = sorted([r for r in requests if r < head])
    right = sorted([r for r in requests if r >= head])

    def add(frm, to, jump=False):
        nonlocal pos, total
        seek = abs(to - frm)
        total += seek
        steps.append({"from": frm, "to": to, "seek": seek, "jump": jump})
        pos = to

    if direction == "right":
        for r in right:
            add(pos, r)
        if left:
            add(pos, left[0], jump=True)        # jump to smallest
            for r in left[1:]:
                add(pos, r)
    else:
        for r in reversed(left):
            add(pos, r)
        if right:
            add(pos, right[-1], jump=True)      # jump to largest
            for r in reversed(right[:-1]):
                add(pos, r)

    return {"steps": steps, "total": total, "order": [s["to"] for s in steps]}

# ─── RSS ─────────────────────────────────────────────────────────────────────
def rss(requests, head):
    steps, total, pos = [], 0, head
    pending = list(requests)
    random.shuffle(pending)
    for r in pending:
        seek = abs(r - pos)
        total += seek
        steps.append({"from": pos, "to": r, "seek": seek})
        pos = r
    return {"steps": steps, "total": total, "order": [s["to"] for s in steps]}

# ─── LIFO ────────────────────────────────────────────────────────────────────
def lifo(requests, head):
    steps, total, pos = [], 0, head
    stack = list(requests)          # last element served first
    while stack:
        r = stack.pop()
        seek = abs(r - pos)
        total += seek
        steps.append({"from": pos, "to": r, "seek": seek})
        pos = r
    return {"steps": steps, "total": total, "order": [s["to"] for s in steps]}

# ─── N-STEP SCAN ─────────────────────────────────────────────────────────────
def n_step_scan(requests, head, n=3):
    steps, total, pos = [], 0, head
    groups = [requests[i:i+n] for i in range(0, len(requests), n)]
    for grp in groups:
        for r in sorted(grp):
            seek = abs(r - pos)
            total += seek
            steps.append({"from": pos, "to": r, "seek": seek})
            pos = r
    return {"steps": steps, "total": total, "order": [s["to"] for s in steps]}

# ─── F-SCAN ──────────────────────────────────────────────────────────────────
def fscan(requests, head):
    """
    F-SCAN: divides requests into two queues. Active queue (Q1) is served
    with a SCAN sweep; new arrivals go to Q2. When Q1 is exhausted, swap.
    Here we simulate by splitting the list in half as Q1/Q2.
    """
    steps, total, pos = [], 0, head
    mid = len(requests) // 2
    q1, q2 = list(requests[:mid if mid else len(requests)]), list(requests[mid:])

    def sweep(queue):
        nonlocal pos, total
        left  = sorted([r for r in queue if r < pos])
        right = sorted([r for r in queue if r >= pos])
        for r in right + list(reversed(left)):
            seek = abs(r - pos)
            total += seek
            steps.append({"from": pos, "to": r, "seek": seek})
            pos = r

    sweep(q1)
    if q2:
        sweep(q2)

    return {"steps": steps, "total": total, "order": [s["to"] for s in steps]}

# ─── ALGO REGISTRY ───────────────────────────────────────────────────────────
ALGORITHMS = {
    "fcfs":        ("FCFS",        fcfs),
    "sstf":        ("SSTF",        sstf),
    "scan":        ("SCAN",        scan),
    "cscan":       ("C-SCAN",      cscan),
    "look":        ("LOOK",        look),
    "clook":       ("C-LOOK",      clook),
    "rss":         ("RSS",         rss),
    "lifo":        ("LIFO",        lifo),
    "nstep":       ("N-Step SCAN", n_step_scan),
    "fscan":       ("F-SCAN",      fscan),
}

EXPLANATIONS = {
    "fcfs":  "Requests are served in the order they arrive. Simple but can cause high seek times if requests are scattered.",
    "sstf":  "Always jumps to the nearest request first, minimising immediate seek time — but risks starvation of distant tracks.",
    "scan":  "The head sweeps in one direction servicing all requests, hits the end of the disk, then reverses. Like an elevator.",
    "cscan": "Like SCAN but the head only services requests in one direction; it jumps back to the start without servicing on the return trip.",
    "look":  "Like SCAN but the head only travels as far as the last request in each direction — no need to reach the physical disk end.",
    "clook": "Like C-SCAN but jumps back to the smallest (or largest) pending request rather than the disk boundary.",
    "rss":   "Requests are picked at random. Used mainly as a baseline benchmark to highlight how much smarter algorithms save.",
    "lifo":  "Last request added is served first. Efficient for temporal locality but can starve older requests indefinitely.",
    "nstep": "Requests are batched into groups of N and each batch is served in sorted order. Prevents indefinite postponement (starvation).",
    "fscan": "Two-queue variant of SCAN. During a sweep the active queue is frozen; new arrivals queue up for the next sweep, eliminating starvation.",
}

# ─── ROUTES ──────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html", algorithms=ALGORITHMS, explanations=EXPLANATIONS)

@app.route("/run", methods=["POST"])
def run():
    data = request.json
    try:
        requests_list = [int(x) for x in str(data["requests"]).split(",") if x.strip()]
        head = int(data["head"])
        disk_size = int(data.get("disk_size", 200))
        direction = data.get("direction", "right")
        n = int(data.get("n", 3))
        algo = data["algorithm"]
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    fn_name, fn = ALGORITHMS.get(algo, (None, None))
    if fn is None:
        return jsonify({"error": "Unknown algorithm"}), 400

    import inspect
    sig = inspect.signature(fn)
    kwargs = {}
    if "disk_size" in sig.parameters: kwargs["disk_size"] = disk_size
    if "direction"  in sig.parameters: kwargs["direction"]  = direction
    if "n"          in sig.parameters: kwargs["n"]          = n

    result = fn(requests_list, head, **kwargs)
    result["name"] = fn_name
    result["explanation"] = EXPLANATIONS[algo]
    result["head"] = head
    result["requests"] = requests_list
    return jsonify(result)

@app.route("/compare", methods=["POST"])
def compare():
    data = request.json
    try:
        requests_list = [int(x) for x in str(data["requests"]).split(",") if x.strip()]
        head = int(data["head"])
        disk_size = int(data.get("disk_size", 200))
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    results = {}
    import inspect
    for key, (label, fn) in ALGORITHMS.items():
        sig = inspect.signature(fn)
        kwargs = {}
        if "disk_size" in sig.parameters: kwargs["disk_size"] = disk_size
        if "direction"  in sig.parameters: kwargs["direction"]  = "right"
        if "n"          in sig.parameters: kwargs["n"]          = 3
        r = fn(list(requests_list), head, **kwargs)
        results[key] = {"label": label, "total": r["total"]}

    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True)
