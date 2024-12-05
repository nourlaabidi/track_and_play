# Track and Play 🎮🖐️  

**Collaborators:** [Nour Laabidi](https://github.com/nourlabidi) & [Nouha Ben Hamada](https://github.com/nouhabenhamada)

## Description  
**Track and Play** is a collection of gesture-controlled games powered by computer vision! Players can use simple hand gestures (up, down, left, and right) to control characters in fun and interactive games.  

This project combines **YOLOv8n** for real-time hand gesture recognition and **Pygame** for game development. It includes:  
- A **maze game** where players navigate through a labyrinth.  
- A **climb wall game** where players climb a wall by directing the character with gestures.  

## Key Features  
- **Gesture Detection:** Recognizes hand gestures (up, down, left, right) using a YOLOv8n model trained on a custom dataset.  
- **Game Integration:** Two games developed using Pygame and integrated into a unified platform.  
- **Branches:**  
  - `main`: Includes the full integration of both games and the gesture recognition model.  
  - `maze`: Contains the standalone Maze game.  
  - `climb_wall`: Contains the standalone Climb Wall game.
## Dataset and model
1. **Dataset Preparation:**
   Data Collection: We collected a dataset with hand gestures (up, down, left, right).
   Data Annotation & Augmentation: Used [Roboflow](https://roboflow.com/) to annotate and augment the dataset for training.
2. **Model Training:**
   The gesture recognition model was trained using YOLOv8n to classify the position of the hand gestures.
## Demo  
[Watch the demo video]
![image](https://github.com/user-attachments/assets/d3f19ca4-4f7e-4477-8c22-de33e251ef95)
![image](https://github.com/user-attachments/assets/75fac13a-2ebd-47eb-9e0b-01d4e3f2be07)
![image](https://github.com/user-attachments/assets/50987453-494f-4941-ae1c-0a3d8dc4bbf6)


## Installation  

Follow these steps to set up and run the project:  

1. **Clone the Repository:**  
   ```bash  
   git clone https://github.com/nourlaabidi/track_and_play.git  
   cd track_and_play  
2. **Set Up a Virtual Environment:**
    ```bash
      python -m venv venv  
      source venv/bin/activate
3. **Install Dependencies::**
   ```bash
   pip install -r requirements.txt  
4. **Run the Project::**
    ```bash
    python main.py 
