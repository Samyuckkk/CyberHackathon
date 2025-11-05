Secure STAT 🚑: A Modern, Post-Quantum Secure Hospital Command Dashboard

Introduction

Secure STAT is a high-fidelity frontend prototype developed for the CyberHackathon. It addresses critical security challenges in real-time healthcare data transmission by simulating a "smart" hospital command center designed to receive and display live patient vital signs from in-transit ambulances using secure-by-design, next-generation cryptographic protocols.

This project demonstrates how two primary cybersecurity threats—data integrity and connection confidentiality—can be mitigated using advanced, future-proof techniques.

📖 The Problem

The transmission of real-time patient data (vitals, location) from an ambulance to a receiving hospital is highly sensitive and vulnerable, posing risks to patient safety and privacy:

Data Tampering (Integrity Risk): An attacker could intercept and subtly alter a patient's vital signs (e.g., changing heart rate or SpO₂ readings). If hospital staff trust this altered data, it could lead to incorrect preparation or catastrophic misdiagnosis upon arrival.

Eavesdropping & Quantum Risk (Confidentiality Risk): Current standard encryption (like RSA and ECC) is vulnerable to being broken by large-scale quantum computers, magnifying the risk of catastrophic data theft (eavesdropping) in the near future.

✨ Our Secure Solution

Secure STAT is a dashboard prototype that not only visualizes critical data but also symbolizes a cutting-edge, secure-by-design architecture. It employs Post-Quantum Cryptography (PQC) and cryptographic verification to ensure that data is both private and unaltered.

🔒 Cybersecurity Features (Simulated Indicators)

The core innovation is demonstrated through these simulated, real-time status indicators in the Ambulance Details Modal:

🛡️ Data Integrity and Verification

Merkle Tree Verification (Verified - Merkle Check OK): This is the core integrity mechanism. It simulates cryptographic verification of every vital stream data packet against a Merkle root, providing an unbreakable guarantee that no data points were tampered with during transmission.

🌐 Post-Quantum Confidentiality

Hybrid Post-Quantum Cryptography (Active - Hybrid PQC): This addresses the future threat of quantum computing. It simulates securing the entire TLS connection using both classic and a new, quantum-resistant algorithm (e.g., Kyber), ensuring the data channel is safe from even quantum eavesdropping.

🚀 Operational Features (Functional Prototype)

Real-time Fleet Command: A clean, responsive dashboard providing a system-wide view of all active ambulances and aggregated system averages.

Actionable Vitals Snapshot: Key vitals (HR, SpO₂, BP) are displayed directly on the main dashboard cards for immediate, life-critical operational awareness.

Detailed Patient View: The modal provides a full-screen display of all five vitals, a simulated live-updating trend chart, and the full response timeline.

Geospatial Tracking: Integrated map shows the ambulance's live location and destination (Vishwaraj Hospital, Pune).

Contextual Localization: All mock patient and doctor names are localized for immediate relevance in the Indian context.

Clinical Aesthetic: Professional, deep blue (#0052CC) theme with a clean interface and accessible contrast, ideal for a critical medical environment.

💻 Tech Stack

This project is a single-file, pure frontend application prototype. No build step is required.

HTML5 & JavaScript (ES6+): Core structure, dynamic routing, modal logic, and interactivity.

Tailwind CSS: Used exclusively for styling, layout, and mobile-first responsive design.

Chart.js: Powering all data visualizations (live-updating line charts and the fleet overview doughnut chart).

Lucide Icons: Used for clean, professional iconography.

🏃 How to Run

This is a single-file, pure frontend application. No build step is required.

Clone the repository:

git clone [https://github.com/Samyuckkk/CyberHackathon.git](https://github.com/Samyuckkk/CyberHackathon.git)


Open the secure-stat-teal.html file in any modern web browser.
