# GPA & CGPA Calculator with Grade Predictor

## Overview
A Python-based academic planning tool that calculates GPA and CGPA while helping students predict the grades required to achieve their target CGPA. Built with Streamlit, it calculates current GPA and CGPA based on course credits and grades, accepts a target CGPA as user input, and predicts the required GPA in upcoming semesters. It also analyzes individual course credit weights and estimates the grades needed in each subject to achieve the desired CGPA.

## Features
- Calculates semester GPA based on subject grades and credit weights.
- Calculates cumulative CGPA across semesters.
- Saves a running history of past semesters, with the ability to expand, review, or delete individual entries.
- Allows users to set an ideal/target CGPA.
- Predicts the required GPA in the upcoming semester to reach the target CGPA.
- Estimates required grades for individual courses based on their credit weight, letting users lock in known grades and solve for the rest.
- Automatically saves and reloads progress between sessions, so data isn't lost on restart.
- Provides personalized academic planning insights.

## Technologies Used
- Python
- Streamlit (web interface)
- Pandas (tabular data handling)
- JSON (local data persistence)
- Data Structures (Lists, Dictionaries)

## Future Improvements
- Support multiple grading systems.
- Add data visualization for academic progress (e.g. CGPA trend over semesters).
- Export semester history as a downloadable CSV/transcript.
- Deploy publicly for easy sharing.
