"""
==============================================================================
Smart City Network Simulation & Congestion Analysis - Localhost Web Server
Project: Smart City Network Simulation and Congestion Analysis
Framework: Flask
Description:
    Provides an interactive web dashboard hosted on localhost (http://127.0.0.1:5000)
    for real-time simulation, parameter tuning, Leaky Bucket visualization,
    and comparative congestion analysis.
==============================================================================
"""

import os
import sys
import json
from flask import Flask, render_template, request, jsonify, send_from_directory

# Ensure local modules can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from python_simulation.simulate_smart_city import SmartCitySimulator
from src_leaky_bucket.leaky_bucket import LeakyBucket

app = Flask(__name__, static_folder="static", template_folder="templates")

# Serve generated graph images if requested
@app.route("/graphs/<path:filename>")
def serve_graph(filename):
    graphs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results", "graphs")
    return send_from_directory(graphs_dir, filename)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/simulate", methods=["POST"])
def api_simulate():
    data = request.get_json() or {}
    use_leaky_bucket = bool(data.get("use_leaky_bucket", False))
    buffer_capacity = int(data.get("buffer_capacity", 15))
    bottleneck_mbps = float(data.get("bottleneck_mbps", 3.5))
    cctv_rate_kbps = float(data.get("cctv_rate_kbps", 2800))
    emergency_rate_kbps = float(data.get("emergency_rate_kbps", 1500))

    sim = SmartCitySimulator(sim_duration=10.0, time_step=0.05)
    # Customize device rates dynamically
    sim.devices[2]["rate_kbps"] = cctv_rate_kbps
    sim.devices[3]["rate_kbps"] = max(1000.0, cctv_rate_kbps * 0.9)
    sim.devices[6]["rate_kbps"] = emergency_rate_kbps

    res = sim.run_scenario(
        use_leaky_bucket=use_leaky_bucket,
        buffer_capacity=buffer_capacity,
        bottleneck_mbps=bottleneck_mbps
    )

    # Categories
    categories = {
        1: {"name": "Traffic Signals (1 & 2)", "color": "#3498db"},
        2: {"name": "CCTV Surveillance (1 & 2)", "color": "#e74c3c"},
        3: {"name": "Pollution Sensor", "color": "#2ecc71"},
        4: {"name": "Smart Street Lighting", "color": "#f39c12"},
        5: {"name": "Emergency Services", "color": "#9b59b6"}
    }

    flows = []
    for fid, meta in categories.items():
        sent = res["flow_sent"].get(fid, 0)
        delivered = res["flow_delivered"].get(fid, 0)
        dropped = res["flow_dropped"].get(fid, 0)
        drop_rate = (dropped / sent * 100.0) if sent > 0 else 0.0
        flows.append({
            "fid": fid,
            "name": meta["name"],
            "color": meta["color"],
            "sent": sent,
            "delivered": delivered,
            "dropped": dropped,
            "drop_rate": round(drop_rate, 2),
            "pdr": round(100.0 - drop_rate, 2)
        })

    emergency_pdr = next((f["pdr"] for f in flows if f["fid"] == 5), 0.0)

    return jsonify({
        "status": "success",
        "parameters": {
            "use_leaky_bucket": use_leaky_bucket,
            "buffer_capacity": buffer_capacity,
            "bottleneck_mbps": bottleneck_mbps,
            "cctv_rate_kbps": cctv_rate_kbps,
            "emergency_rate_kbps": emergency_rate_kbps
        },
        "time_series": res["time_series"],
        "throughput_log": [round(val, 2) for val in res["throughput_log"]],
        "buffer_occupancy_log": res["buffer_occupancy_log"],
        "packet_drops_log": res["packet_drops_log"],
        "metrics": {
            "total_sent": res["total_sent"],
            "total_delivered": res["total_delivered"],
            "total_dropped": res["total_dropped"],
            "pdr": round(res["pdr"], 2),
            "drop_rate": round(100.0 - res["pdr"], 2),
            "avg_throughput_kbps": round(res["avg_throughput_kbps"], 2),
            "avg_throughput_mbps": round(res["avg_throughput_kbps"] / 1000.0, 3),
            "emergency_pdr": emergency_pdr
        },
        "flows": flows
    })

@app.route("/api/tcp_vs_udp", methods=["GET"])
def api_tcp_vs_udp():
    sim = SmartCitySimulator()
    res = sim.simulate_tcp_vs_udp()
    return jsonify({
        "status": "success",
        "time_series": res["time_series"],
        "tcp_cwnd": [round(c, 2) for c in res["tcp_cwnd"]],
        "tcp_throughput": [round(t, 2) for t in res["tcp_throughput"]],
        "udp_throughput": [round(u, 2) for u in res["udp_throughput"]],
        "queue_len": res["queue_len"]
    })

@app.route("/api/leaky_bucket", methods=["POST"])
def api_leaky_bucket():
    data = request.get_json() or {}
    capacity = float(data.get("capacity", 20))
    leak_rate = float(data.get("leak_rate", 5))
    pattern = data.get("traffic_pattern", [4, 10, 18, 15, 6, 3, 20, 5, 2, 0])

    lb = LeakyBucket(capacity=capacity, leak_rate=leak_rate)
    summary = lb.run_simulation(pattern)

    return jsonify({
        "status": "success",
        "capacity": capacity,
        "leak_rate": leak_rate,
        "history": lb.history,
        "summary": {
            "total_arrived": summary["total_arrived"],
            "total_leaked": summary["total_leaked"],
            "total_dropped": summary["total_dropped"],
            "drop_rate_pct": round(summary["drop_rate_pct"], 2)
        }
    })

@app.route("/api/trace_sample", methods=["GET"])
def api_trace_sample():
    trace_type = request.args.get("type", "baseline")
    fname = "smart_city_baseline.tr" if trace_type == "baseline" else "smart_city_leaky_bucket.tr"
    trace_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results", "trace_samples", fname)
    
    sample_lines = []
    if os.path.exists(trace_path):
        with open(trace_path, "r") as f:
            for _ in range(50):
                line = f.readline()
                if not line:
                    break
                sample_lines.append(line.strip())
                
    return jsonify({
        "status": "success",
        "filename": fname,
        "lines": sample_lines
    })

if __name__ == "__main__":
    print("======================================================================")
    print(" Smart City Network Simulation Web Dashboard Starting...")
    print(" Access Web UI at: http://127.0.0.1:5000 or http://localhost:5000")
    print("======================================================================")
    app.run(host="127.0.0.1", port=5000, debug=False)
