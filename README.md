# 📦 Persistent Queues with Redis (Middleware Technology PVL)

**Course:** Middleware Technology  
**Team Members:**  
1. Donato Giuliano, 1003007
2. Sheyenne  Klempar, 
3. Marvin Kickel,   
4. Sema Ünal, 

---

## 🧩 1. Project Overview

This project demonstrates the **Persistent Queue Pattern** using a small distributed system.  
The goal is to ensure that **tasks remain durable and are not lost**, even if the processing component (Consumer) crashes or is intentionally paused.

To achieve this, the system uses **Redis** as a persistent, reliable message broker.

The web UI visualizes:

- the current queue size  
- the worker status (running / stopped)  
- live processing results  
- export of all data as JSON  

---

## 🏗 2. System Architecture

The system consists of **three decoupled Docker containers**:

### **1. Producer (Flask Web UI)**  
- Accepts numbers from the user  
- Pushes tasks into Redis using `LPUSH`  
- Shows real-time queue state  
- Allows pausing/resuming the worker  
- Displays processed results  
- Provides JSON export functionality  

### **2. Redis (Middleware / OSS Tool)**  
- Acts as the persistent queue  
- Stores all tasks reliably  
- Buffers tasks even when the worker is offline  
- Enables full decoupling of Producer and Consumer  

### **3. Consumer (Background Worker)**  
- Continuously retrieves tasks using `BRPOP`  
- Simulates heavy work through a 6-second delay  
- Computes `x²` and stores results back into Redis  
- Automatically continues after restart or failure  

---

## 4. 🚀 How to Run the System
### **1. Prerequisites
- Docker
- Docker Compose

### **2. Start the System
`
docker-compose up --build -d
`

Dashboard accessible at:
👉 http://localhost:8080

### **3. Stop the System
docker-compose down

## 5. 🧪 Resilience Demonstration (Lab Task)

This experiment demonstrates that the system remains reliable even when the worker is stopped or crashes.  
All tasks stay safely stored in Redis until processing resumes.

### **1. Stop the Worker**  
Click the red **STOP** button in the dashboard.  
The worker switches to *paused mode* and no longer consumes tasks.

### **2. Submit Tasks**  
Enter several numbers and click **Submit Task**.  
The queue begins to fill up and the UI updates in real time.

### **3. Observe Queue Behavior**  
All incoming tasks remain stored in Redis.  
No data is lost, even when the worker is completely offline.

### **4. Restart the Worker**  
Click the green **START** button.  
The worker reconnects and processes all buffered tasks one by one (with a 6-second delay per item).

### **5. Export State (Optional)**  
Use the **⬇ Download JSON** option to export the current queue and result history for auditing or debugging.

---

## 6. 📂 Project Structure

The project is organized into three main components, each running in its own Docker container.

- producer: Flask web interface (task submission + live dashboard)
- consumer: Background worker that processes queued tasks
- docker-compose.yml: Orchestration file for all services
- README.md: Documentation
