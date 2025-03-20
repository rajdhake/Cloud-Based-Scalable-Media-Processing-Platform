This project revolves around developing a scalable, efficient, and fully automated video-to-audio (MP4 to MP3) conversion service. The system is designed to handle user requests for video-to-audio conversion, manage large amounts of data (videos and audio files), and ensure smooth communication between various components using message queues.
The core functionality of the backend application is a Flask-based service written in Python. This application leverages custom-built services packaged into Docker images and deployed within a Kubernetes cluster. The primary purpose of the application is to convert MP4 videos to MP3 audio files.

# Primary Observations
1.	Out-of-Memory Errors Under High User Load:
The system encountered recurring out-of-memory (OOM) errors once the number of concurrent requests reached around 1000. This problem underscored the necessity for effective memory management in the converter service and appropriate resource distribution to manage peak traffic.
2.	Database Pod Restarts Leading to Data Loss: pods were often restarting because of inadequate resource allocation and elevated I/O demands. These restarts led to the service losing track of processed MP3 files, which caused user frustration and necessitated repeated conversion tasks.
3.	Converter Service Failures at High Load:
When under heavy load, the converter service turned into a bottleneck, struggling to handle requests effectively. 
<img width="338" alt="image" src="https://github.com/user-attachments/assets/26b30d5d-b3c1-49a1-adf5-93e50f2b8cb2" />
 
# Solution
1. A dynamic scheduling script was introduced, allowing the converter pod to automatically scale vertically according to resource consumption. This improvement guaranteed reliable service performance.
2.	Horizontal Scaling for Database Pods to manage the high input/output requirements and decrease the rate of pod restarts, horizontal scaling was implemented for pods. This approach balanced the load across several instances, enhancing resilience and availability of the database.
<img width="345" alt="image" src="https://github.com/user-attachments/assets/ba75001f-96c7-43f4-a3ee-86a2d9d9deab" />



# Project Setup

Before starting the project, ensure you have the following tools installed in the specified order:

1. **Docker**  
   [Installation Guide](https://www.youtube.com/watch?v=WDEdRmTCSs8)

2. **Kubectl**  
   [Installation Guide](https://www.youtube.com/watch?v=G9MmLUsBd3g)

3. **Minikube**  
   [Installation Guide](https://www.youtube.com/watch?v=xNefZ51jHKg)

4. **Python**  
   [Installation Guide](https://www.youtube.com/watch?v=TNAu6DvB9Ng)

5. **Chocolatey Package Installer**  
   [Installation Guide](https://www.youtube.com/watch?v=oL3YkT6cn50)

6. **k9s**  
   Install via Chocolatey:  
   ```bash
   choco install k9s

5. **MySQL**  
   [Installation Guide](https://www.youtube.com/watch?v=a3HJnbYhXUc)

