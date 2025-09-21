import cv2
import mediapipe as mp
import numpy as np
from typing import Dict, List, Tuple, Optional
import base64
from io import BytesIO
from PIL import Image


class VideoAnalyzer:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_pose = mp.solutions.pose
        self.mp_hands = mp.solutions.hands
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

    def analyze_frame(self, image_data: str) -> Dict:
        """Analyze a single frame for interview metrics"""
        try:
            # Decode base64 image
            image_bytes = base64.b64decode(image_data.split(',')[1])
            image = Image.open(BytesIO(image_bytes))
            frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            results = {
                'eye_contact': self._analyze_eye_contact(frame),
                'posture': self._analyze_posture(frame),
                'facial_expressions': self._analyze_expressions(frame),
                'hand_gestures': self._analyze_hand_gestures(frame),
                'confidence_score': 0.0
            }
            
            # Calculate overall confidence
            results['confidence_score'] = self._calculate_confidence(results)
            return results
            
        except Exception as e:
            return {
                'eye_contact': {'score': 5.0, 'feedback': 'Unable to detect eyes'},
                'posture': {'score': 5.0, 'feedback': 'Unable to detect posture'},
                'facial_expressions': {'score': 5.0, 'feedback': 'Unable to detect expressions'},
                'hand_gestures': {'score': 5.0, 'feedback': 'Unable to detect gestures'},
                'confidence_score': 0.0,
                'error': str(e)
            }

    def _analyze_eye_contact(self, frame) -> Dict:
        """Analyze eye contact quality"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)
        
        if not results.multi_face_landmarks:
            return {'score': 5.0, 'feedback': 'Face not detected'}
        
        face_landmarks = results.multi_face_landmarks[0]
        
        # Get eye landmarks
        left_eye_indices = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
        right_eye_indices = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
        
        # Calculate eye openness
        left_eye_openness = self._calculate_eye_openness(face_landmarks, left_eye_indices, frame.shape)
        right_eye_openness = self._calculate_eye_openness(face_landmarks, right_eye_indices, frame.shape)
        
        avg_openness = (left_eye_openness + right_eye_openness) / 2
        
        # Calculate gaze direction (simplified)
        gaze_score = self._calculate_gaze_direction(face_landmarks, frame.shape)
        
        # Combine metrics
        eye_score = (avg_openness * 0.6 + gaze_score * 0.4) * 10
        
        if eye_score >= 8:
            feedback = "Excellent eye contact - maintaining good engagement"
        elif eye_score >= 6:
            feedback = "Good eye contact - occasional glances away are normal"
        elif eye_score >= 4:
            feedback = "Moderate eye contact - try to look at camera more often"
        else:
            feedback = "Poor eye contact - focus on maintaining eye contact with interviewer"
        
        return {'score': min(10.0, max(0.0, eye_score)), 'feedback': feedback}

    def _analyze_posture(self, frame) -> Dict:
        """Analyze body posture"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb_frame)
        
        if not results.pose_landmarks:
            return {'score': 5.0, 'feedback': 'Body not detected'}
        
        landmarks = results.pose_landmarks.landmark
        
        # Analyze shoulder alignment
        left_shoulder = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER]
        right_shoulder = landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]
        
        shoulder_diff = abs(left_shoulder.y - right_shoulder.y)
        
        # Analyze head position
        nose = landmarks[self.mp_pose.PoseLandmark.NOSE]
        shoulder_center_y = (left_shoulder.y + right_shoulder.y) / 2
        
        head_position = nose.y - shoulder_center_y
        
        # Calculate posture score
        posture_score = 10.0
        feedback_parts = []
        
        if shoulder_diff > 0.05:  # Shoulders not level
            posture_score -= 2
            feedback_parts.append("Keep shoulders level")
        
        if head_position < -0.1:  # Head too far forward
            posture_score -= 2
            feedback_parts.append("Keep head upright")
        
        if posture_score >= 8:
            feedback = "Excellent posture - professional and confident"
        elif posture_score >= 6:
            feedback = "Good posture with minor adjustments needed"
        elif posture_score >= 4:
            feedback = "Moderate posture - focus on sitting upright"
        else:
            feedback = "Poor posture - sit up straight and maintain professional appearance"
        
        if feedback_parts:
            feedback += f". Areas to improve: {', '.join(feedback_parts)}"
        
        return {'score': max(0.0, posture_score), 'feedback': feedback}

    def _analyze_expressions(self, frame) -> Dict:
        """Analyze facial expressions"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)
        
        if not results.multi_face_landmarks:
            return {'score': 5.0, 'feedback': 'Face not detected'}
        
        face_landmarks = results.multi_face_landmarks[0]
        
        # Analyze smile
        smile_score = self._calculate_smile_intensity(face_landmarks, frame.shape)
        
        # Analyze eyebrow position (confidence indicator)
        eyebrow_score = self._calculate_eyebrow_position(face_landmarks, frame.shape)
        
        # Combine expression metrics
        expression_score = (smile_score * 0.6 + eyebrow_score * 0.4) * 10
        
        if expression_score >= 8:
            feedback = "Excellent expressions - confident and engaging"
        elif expression_score >= 6:
            feedback = "Good expressions - natural and professional"
        elif expression_score >= 4:
            feedback = "Moderate expressions - try to be more expressive"
        else:
            feedback = "Limited expressions - work on showing confidence and engagement"
        
        return {'score': min(10.0, max(0.0, expression_score)), 'feedback': feedback}

    def _analyze_hand_gestures(self, frame) -> Dict:
        """Analyze hand gestures and movement"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        
        if not results.multi_hand_landmarks:
            return {'score': 5.0, 'feedback': 'Hands not detected - consider using hand gestures'}
        
        # Count hands detected
        num_hands = len(results.multi_hand_landmarks)
        
        # Analyze hand position and movement
        gesture_score = 5.0
        feedback_parts = []
        
        if num_hands == 1:
            gesture_score += 1
            feedback_parts.append("One hand visible")
        elif num_hands == 2:
            gesture_score += 2
            feedback_parts.append("Both hands visible")
        
        # Check if hands are in good position (not covering face)
        for hand_landmarks in results.multi_hand_landmarks:
            wrist = hand_landmarks.landmark[0]
            if wrist.y < 0.3:  # Hand near face
                gesture_score -= 1
                feedback_parts.append("Avoid covering face with hands")
        
        if gesture_score >= 8:
            feedback = "Excellent hand usage - natural and professional gestures"
        elif gesture_score >= 6:
            feedback = "Good hand gestures - appropriate and controlled"
        elif gesture_score >= 4:
            feedback = "Moderate hand usage - consider using more gestures"
        else:
            feedback = "Limited hand gestures - use natural hand movements to emphasize points"
        
        if feedback_parts:
            feedback += f". Observations: {', '.join(feedback_parts)}"
        
        return {'score': min(10.0, max(0.0, gesture_score)), 'feedback': feedback}

    def _calculate_eye_openness(self, landmarks, eye_indices, frame_shape) -> float:
        """Calculate how open the eyes are"""
        try:
            eye_points = []
            for idx in eye_indices:
                landmark = landmarks.landmark[idx]
                eye_points.append([landmark.x * frame_shape[1], landmark.y * frame_shape[0]])
            
            eye_points = np.array(eye_points)
            
            # Calculate eye aspect ratio (simplified)
            vertical_dist = np.linalg.norm(eye_points[1] - eye_points[5])
            horizontal_dist = np.linalg.norm(eye_points[0] - eye_points[3])
            
            if horizontal_dist == 0:
                return 0.5
            
            ear = vertical_dist / horizontal_dist
            return min(1.0, max(0.0, ear * 2))  # Normalize to 0-1
            
        except:
            return 0.5

    def _calculate_gaze_direction(self, landmarks, frame_shape) -> float:
        """Calculate gaze direction (simplified)"""
        try:
            # Use nose and eye positions to estimate gaze
            nose = landmarks.landmark[1]  # Nose tip
            left_eye = landmarks.landmark[33]
            right_eye = landmarks.landmark[362]
            
            # Calculate if looking forward (toward camera)
            eye_center_x = (left_eye.x + right_eye.x) / 2
            nose_x = nose.x
            
            # If nose is close to eye center, looking forward
            gaze_score = 1.0 - abs(nose_x - eye_center_x) * 2
            return max(0.0, min(1.0, gaze_score))
            
        except:
            return 0.5

    def _calculate_smile_intensity(self, landmarks, frame_shape) -> float:
        """Calculate smile intensity"""
        try:
            # Use mouth corner landmarks
            left_mouth = landmarks.landmark[61]
            right_mouth = landmarks.landmark[291]
            
            # Calculate mouth width (smile indicator)
            mouth_width = abs(right_mouth.x - left_mouth.x)
            
            # Normalize based on face width
            face_width = abs(landmarks.landmark[234].x - landmarks.landmark[454].x)
            
            if face_width == 0:
                return 0.5
            
            smile_ratio = mouth_width / face_width
            return min(1.0, max(0.0, (smile_ratio - 0.3) * 2))  # Normalize
            
        except:
            return 0.5

    def _calculate_eyebrow_position(self, landmarks, frame_shape) -> float:
        """Calculate eyebrow position (confidence indicator)"""
        try:
            # Use eyebrow landmarks
            left_eyebrow = landmarks.landmark[70]
            right_eyebrow = landmarks.landmark[300]
            
            # Calculate eyebrow height (higher = more confident)
            eyebrow_height = (left_eyebrow.y + right_eyebrow.y) / 2
            
            # Normalize (this is a simplified approach)
            return min(1.0, max(0.0, (0.5 - eyebrow_height) * 2))
            
        except:
            return 0.5

    def _calculate_confidence(self, results: Dict) -> float:
        """Calculate overall confidence score from all metrics"""
        scores = [
            results['eye_contact']['score'],
            results['posture']['score'],
            results['facial_expressions']['score'],
            results['hand_gestures']['score']
        ]
        
        return sum(scores) / len(scores) if scores else 0.0
