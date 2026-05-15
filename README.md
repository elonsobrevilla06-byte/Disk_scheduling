# 🎛️ Hard Disk Drive (HDD) Scheduling Simulator

A Flask-based web application that visualizes and compares 10 different operating system disk scheduling algorithms. This tool calculates total seek time, step-by-step track movements, and helps users understand how an Operating System manages physical hardware bottlenecks.

---

## 📖 What is Disk Scheduling?

Think of your computer's hard drive like a physical library, and the disk head is the librarian. When you run programs, open files, or save games, hundreds of different apps constantly demand data from completely different tracks all at once. 

Because the mechanical parts of a traditional hard drive (the spinning platters and the moving read/write arm) are slow compared to the CPU, a massive bottleneck forms. **Disk scheduling** is the strategy the operating system uses to decide the absolute best order to service these data requests. 

### Why is it Important?
By selecting the right scheduling algorithm, the OS minimizes **seek time** (the physical time it takes for the disk arm to move to the correct track). This results in:
* **Faster loading times** for files and applications.
* **Higher system throughput** (getting more read/write work done per second).
* **Less wear and tear** on the physical hardware, extending the drive's lifespan.

---

## 🛠️ Supported Algorithms

| Algorithm | Student Breakdown |
| :--- | :--- |
| **FCFS** (First-Come, First-Served) | **The Fair but Dumb One.** Processes requests exactly as they arrive. Head constantly slides back and forth, wasting time. |
| **SSTF** (Shortest Seek Time First) | **The Greedy One.** Always jumps to whichever request is closest to its current position. Fast, but risks starving far-away tracks. |
| **SCAN** | **The Elevator.** Sweeps all the way to one physical end of the disk, then reverses direction to pick up remaining tracks on the way back. |
| **C-SCAN** (Circular SCAN) | **The One-Way Street.** Sweeps in one direction, then instantly "teleports" back to track 0 without servicing anything on the return trip. |
| **LOOK** | **The Smart Elevator.** Just like SCAN, but saves time by turning around early if there are no more requests left in that direction. |
| **C-LOOK** | **The Smart One-Way Street.** Just like C-SCAN, but only teleports back as far as the lowest pending request rather than hitting track 0. |
| **RSS** (Random Scheduling) | **The Chaotic One.** Shuffles and picks requests entirely at random. Used primarily as a baseline benchmark. |
| **LIFO** (Last-In, First-Out) | **The Stack.** Services the newest incoming request first. Great for local repetition, bad for old requests buried at the bottom. |
| **N-Step SCAN** | **The Anti-Starvation SCAN.** Freezes incoming requests into batches of *N*. Sweeps current batch before letting new entries cut in line. |
| **F-SCAN** | **The Two-Queue System.** Uses an active queue and a holding queue. New arrivals are completely locked away until the current sweep finishes. |

---

## ⚙️ Application Features

* **Single Run Mode (`/run`):** Processes a comma-separated array of track requests for a selected algorithm, calculating sequential path trajectories and total head movement.
* **Comparison Mode (`/compare`):** Simulates all 10 algorithms simultaneously under the identical input environment to clearly demonstrate which algorithm yields the lowest overhead.
* **Dynamic Configurations:** Supports customizable disk boundaries, beginning head positions, algorithm sweep direction, and custom chunk sizes ($N$) for batched scheduling.

---

## 🚀 Getting Started

### Prerequisites
Make sure you have Python 3 installed on your machine.

### Installation & Execution

1. **Clone this repository or extract the project files:**
2. **Install Flask**
```bash
pip install flask
```
3. Run the application:
```bash
python app.py
```
4. **Open your browser:**
   Navigate to `http://127.0.0.1:5000/` to explore the simulator interface.

---

## 🌐 API Endpoint Documentation

### 1. Execute Algorithm
* **Endpoint:** `/run`
* **Method:** `POST`
* **Payload Format:**
  ```json
  {
    "requests": "82,170,43,140,24,10,190",
    "head": 50,
    "disk_size": 200,
    "direction": "right",
    "n": 3,
    "algorithm": "sstf"
  }
