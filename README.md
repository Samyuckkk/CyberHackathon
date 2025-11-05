Secure STAT 🚑

A Modern, Secure Hospital Command Dashboard

This project was developed for the CyberHackathon. It is a frontend prototype of a "smart" hospital dashboard designed to securely display real-time data from in-transit ambulances.

📖 The Problem

In modern healthcare, patient data is extremely sensitive. When data is transmitted from a moving ambulance to a hospital, it is vulnerable to two major threats:

Data Tampering: An attacker could intercept and alter the patient's vital signs, leading to incorrect treatment.

Eavesdropping: An attacker could steal patient data, violating privacy. This threat is magnified by the future risk of quantum computers breaking current encryption.

✨ Our Solution

Secure STAT is a dashboard prototype that not only visualizes critical data but also symbolizes a cutting-edge, secure-by-design architecture.

🚀 Key Features

Real-time Dashboard: A clean, responsive dashboard showing all active ambulances.

At-a-Glance Stats: Top-level cards for "Total Ambulances," "Critical," "Stable," and "Available."

Patient Vitals: A detailed modal for each ambulance shows live-updating charts for patient vitals (Heart Rate, SpO₂).

Live Location: The modal includes an embedded Google Map showing the ambulance's destination (Vishwaraj Hospital, Pune).

Indian Localization: All patient and doctor names are localized.

🔒 Cybersecurity Features

This dashboard simulates a UI for a system secured with next-generation protocols:

Merkle Tree Verification (Data Integrity):

The "Verified (Merkle Check OK)" status in the modal symbolizes that the stream of patient vitals (e.g., [80, 81, 80, 82]) is being cryptographically verified.

This proves that no data points have been altered, added, or deleted during transmission.

Hybrid Post-Quantum Cryptography (Connection Security):

The "Active (Hybrid PQC)" status symbolizes that the entire connection (TLS) is secured using both a classic algorithm AND a new, quantum-resistant algorithm.

This ensures the data channel is safe from eavesdropping, even from an attacker with a quantum computer.

💻 Tech Stack

HTML5: For semantic page structure.

Tailwind CSS: For all styling and responsive design.

JavaScript (ES6+): For interactivity, modal logic, and chart simulation.

Chart.js: For all live-updating line charts and the fleet overview doughnut chart.

🏃 How to Run

This is a single-file, pure frontend application. No build step is required.

Clone the repository:

git clone [https://github.com/Samyuckkk/CyberHackathon.git](https://github.com/Samyuckkk/CyberHackathon.git)


Open the secure-stat-teal.html file in any modern web browser.
