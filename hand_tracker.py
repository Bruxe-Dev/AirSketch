"""
Hand Tracker Module
Handles webcam input and hand landmark detection using MediaPipe
"""

import cv2
import mediapipe as mp
import numpy as np
from typing import Optional, Tuple, List

class HandTracker:
    """Tracks hand landmarks and provides gesture detection capabilities"""
    
    def __init__(self, max_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.5):
        """
        Initialize the hand tracker
        
        Args:
            max_hands: Maximum number of hands to detect
            min_detection_confidence: Minimum confidence for hand detection
            min_tracking_confidence: Minimum confidence for hand tracking
        """
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Initialize MediaPipe Hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_hands,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        
        self.results = None
        self.frame_shape = None
        
    def find_hands(self, frame, draw=True):
        """
        Detect hands in the frame
        
        Args:
            frame: BGR image from webcam
            draw: Whether to draw hand landmarks on the frame
            
        Returns:
            Processed frame with optional hand landmarks drawn
        """
        # Convert BGR to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.frame_shape = frame.shape
        
        # Process the frame
        self.results = self.hands.process(rgb_frame)
        
        # Draw hand landmarks if requested
        if draw and self.results.multi_hand_landmarks:
            for hand_landmarks in self.results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS
                )
        
        return frame
    
    def get_finger_tip_position(self, hand_index=0) -> Optional[Tuple[int, int]]:
        """
        Get the position of the index finger tip
        
        Args:
            hand_index: Which hand to get (0 for first detected hand)
            
        Returns:
            (x, y) position in pixels, or None if no hand detected
        """
        if not self.results or not self.results.multi_hand_landmarks:
            return None
        
        if hand_index >= len(self.results.multi_hand_landmarks):
            return None
        
        # Index finger tip is landmark 8
        hand_landmarks = self.results.multi_hand_landmarks[hand_index]
        tip = hand_landmarks.landmark[8]
        
        # Convert normalized coordinates to pixel coordinates
        h, w, _ = self.frame_shape
        x = int(tip.x * w)
        y = int(tip.y * h)
        
        return (x, y)
    
    def get_all_landmarks(self, hand_index=0) -> Optional[List[Tuple[int, int]]]:
        """
        Get all 21 hand landmarks
        
        Returns:
            List of (x, y) positions for all landmarks, or None
        """
        if not self.results or not self.results.multi_hand_landmarks:
            return None
        
        if hand_index >= len(self.results.multi_hand_landmarks):
            return None
        
        hand_landmarks = self.results.multi_hand_landmarks[hand_index]
        h, w, _ = self.frame_shape
        
        landmarks = []
        for landmark in hand_landmarks.landmark:
            x = int(landmark.x * w)
            y = int(landmark.y * h)
            landmarks.append((x, y))
        
        return landmarks
    
    def is_pinching(self, hand_index=0, threshold=40) -> bool:
        """
        Detect if thumb and index finger are pinched together
        
        Args:
            hand_index: Which hand to check
            threshold: Maximum distance in pixels to consider as pinch
            
        Returns:
            True if pinching, False otherwise
        """
        landmarks = self.get_all_landmarks(hand_index)
        if not landmarks:
            return False
        
        # Thumb tip is landmark 4, index finger tip is landmark 8
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        
        # Calculate Euclidean distance
        distance = np.sqrt((thumb_tip[0] - index_tip[0])**2 + 
                          (thumb_tip[1] - index_tip[1])**2)
        
        return distance < threshold
    
    def count_fingers_up(self, hand_index=0) -> int:
        """
        Count how many fingers are extended
        
        Returns:
            Number of fingers up (0-5)
        """
        landmarks = self.get_all_landmarks(hand_index)
        if not landmarks:
            return 0
        
        fingers_up = 0
        
        # Thumb - special case (horizontal check)
        if landmarks[4][0] < landmarks[3][0]:  # Thumb tip left of thumb joint
            fingers_up += 1
        
        # Other fingers - check if tip is above the middle joint
        finger_tips = [8, 12, 16, 20]  # Index, middle, ring, pinky tips
        finger_joints = [6, 10, 14, 18]  # Corresponding joints
        
        for tip, joint in zip(finger_tips, finger_joints):
            if landmarks[tip][1] < landmarks[joint][1]:  # Tip is above joint
                fingers_up += 1
        
        return fingers_up
    
    def release(self):
        """Release resources"""
        self.hands.close()