# 📦 Persistent Queues with Redis (PVL)

**Course:** Middleware Technology  
**Team Members:**  
1. Donato Giuliano, 1003007
2. Sheyenne  Klempar, 1003122
3. Marvin Kickel, 20049957  
4. Sema Ünal, 20306005

---

## 🧩 1. Project Overview

This project demonstrates the Persistent Queue Pattern using a small distributed system.
To make the behavior of the queue more transparent and easy to understand, we intentionally added a simple web UI.
The interface helps visualize how tasks are queued, how persistence works when the worker is paused or stopped, and how the system recovers once the worker resumes.

For demonstration purposes, we use a very simple function `x²` so that the processing steps stay clear and the focus remains on the distributed-system pattern itself.

The web UI visualizes:

- the current queue size  
- the worker status (running / stopped)  
- live processing results  
- export of all data as JSON  

---

## 🏗 2. System Architecture

The system consists of **three decoupled Docker containers**:

### **2.1. Producer (Flask Web UI)**  
- Accepts numbers from the user  
- Pushes tasks into Redis using `LPUSH`  
- Shows real-time queue state  
- Allows pausing/resuming the worker  
- Displays processed results  
- Provides JSON export functionality  

### **2.2. Redis (Middleware / OSS Tool)**  
- Acts as the persistent queue  
- Stores all tasks reliably  
- Buffers tasks even when the worker is offline  
- Enables full decoupling of Producer and Consumer  

### **2.3. Consumer (Background Worker)**  
- Continuously retrieves tasks using `BRPOP`  
- Simulates heavy work through a 6-second delay  
- Computes `x²` and stores results back into Redis  
- Automatically continues after restart or failure  

---

## 3. 🚀 How to Run the System
### **3.1. Prerequisites**
- Docker (Running)
- Docker Compose

### **3.2. Start the System**
`
docker-compose up --build -d
`

Dashboard accessible at:
👉 http://localhost:8080

### **3.3. Stop the System**
docker-compose down

---

## 4. 🧪 Resilience Demonstration (Lab Task)

This experiment demonstrates that the system remains reliable even when the worker is stopped or crashes.  
All tasks stay safely stored in Redis until processing resumes.

### **4.1. Stop the Worker**  
Click the red **STOP** button in the dashboard.  
The worker switches to *paused mode* and no longer consumes tasks.

### **4.2. Submit Tasks**  
Enter several numbers and click **Submit Task**.  
The queue begins to fill up and the UI updates in real time.

### **4.3. Observe Queue Behavior**  
All incoming tasks remain stored in Redis.  
No data is lost, even when the worker is completely offline.

### **4.4. Restart the Worker**  
Click the green **START** button.  
The worker reconnects and processes all buffered tasks one by one (with a 6-second delay per item).

### **4.5. Export State (Optional)**  
Use the **⬇ Download JSON** option to export the current queue and result history for auditing or debugging.

---

## 5. 📂 Project Structure

The project is organized into three main components, each running in its own Docker container.

- producer: Flask web interface (task submission + live dashboard)
- consumer: Background worker that processes queued tasks
- redis: Lightweight middleware container that stores all tasks persistently and buffers them while the worker is offline
