# 🎧 Groovy.io – AI-Powered DJ Web App

**Groovy.io** is an AI-driven DJ web app that intelligently analyzes two songs and finds the best transition points to mix them seamlessly. It’s designed to mimic how a real DJ thinks about beat-matching, phrasing, energy, and flow. Creating smooth, musically-aware transitions in real time.

## 🚀 Features

- 🎶 **AI-Powered Song Analysis**  
  Analyzes tempo, energy, structure, and lyrical content to identify ideal transition points between two tracks.

- 🔁 **Dynamic Crossfading**  
  Automatically aligns beats, keys, and bars for smooth transitions, mimicking professional DJ techniques.

- 🧠 **Smart Chorus Detection**  
  Uses repeated lyric segments to detect and target chorus sections for impactful drop-ins.

- ⏱️ **Real-Time Processing**  
  Multithreaded design ensures fast analysis and mixing, even on large tracks.

## 🚀 Live Demo

🔗 [Video](https://youtu.be/XrrPRttvvnA)

## 🛠️ Tech Stack
**🔧 Backend & Audio Processing**   
**Python** - Core language for audio analysis and mixing/transition logic  
**Flask** - REST API for interfacing with the frontend  
**Rubber Band Library** - High-quality tempo and pitch shifting  
**Faster-Whisper** - Fast and accurate lyrics extraction  
**FFmpeg & Pydub** - Audio decoding, slicing, and mixing  
**Multithreading & Parallel Processing** - Accelerates song analysis and rendering  

**💻 Frontend**  
**React** - Component-based UI for dynamic interaction  
**JavaScript, HTML, CSS** - Standard web technologies  
**Tailwind CSS** - Utility-first CSS framework for responsive, modern styling  

**🗄️ Database**    
**MongoDB (NoSQL)** - Stores user data, song metadata, and session history  

## 📁 Project Structure

```text
Groovy.io/
├── my-app/
    ├── src/
        ├── assets/          # Icons and images
        ├── components/      # Navigation layout
        ├── pages/           # All the site's frontend and functionality
        ├── python/          # Handles audio transitions/mixing and database functions
        ├── App.jsx          # Routing structure for React application
        ├── Index.js         # Entry point of our React application
        ├── firebase.js      # Sets up authentication and Firestore database
        ├── index.css        # Custom styling
        └── main.jsx         # Core structure needed to render our app
├── uploads/                 # Stores our songs
└── README.md                # Project documentation
```

## 🧪 How to Use

1. Clone the repo:
```bash
git clone https://github.com/chrisjiang7/Groovy.io.git
cd Groovy.io
```
2. Install dependencies:
```bash
git clone https://github.com/chrisjiang7/Groovy.io.git
cd Groovy.io
```
3. Run the app with two audio files:
```bash
python main.py song1.mp3 song2.mp3
```
4. Output will be saved in /temp/output_mix.mp3

⚠️ Ensure all libraries are installed and available in your system PATH.

## 🧰 Future Improvements

- Add web-based UI with drag-and-drop song input
- Integrate Spotify or YouTube audio support
- Enable manual override for DJs to choose transition points
- Improve transition/mixing algorithms
- Playlist Queue Support – Allow users to queue or upload a full playlist, enabling the system to automatically analyze and continuously mix tracks in sequence for a seamless listening experience.

