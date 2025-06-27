# SmartSudo - AI-Powered Sudoku Game

## Overview

SmartSudo is an interactive web-based Sudoku game that combines traditional puzzle gameplay with AI-powered hints and algorithm visualization. The application provides multiple difficulty levels, intelligent hints using OpenAI's API, and educational visualizations of the backtracking algorithm used to solve Sudoku puzzles.

## System Architecture

### Frontend Architecture
- **Technology**: HTML5, CSS3, JavaScript (ES6+)
- **Framework**: Bootstrap 5 with custom dark theme
- **Structure**: Single-page application with modular JavaScript components
- **Key Features**: Interactive game board, real-time validation, visualization controls

### Backend Architecture
- **Framework**: Flask (Python 3.11)
- **Server**: Gunicorn WSGI server for production deployment
- **Architecture Pattern**: RESTful API with JSON responses
- **Deployment**: Replit autoscale deployment target

## Key Components

### Core Game Engine
- **SudokuGenerator**: Generates valid Sudoku puzzles using backtracking algorithm
- **Difficulty Levels**: Easy, Medium, Hard, Expert with varying cell removal counts
- **Validation**: Real-time puzzle validation and completion detection

### AI Integration
- **AI Hints Module**: OpenAI GPT-powered intelligent hints that provide strategic guidance
- **Fallback System**: Solution-based hints when AI is unavailable
- **Configuration**: Flexible API key management through config file or environment variables

### Visualization System
- **BacktrackingVisualizer**: Step-by-step visualization of the solving algorithm
- **Decision Tree**: Visual representation of algorithmic decision points
- **Interactive Controls**: Play, pause, step, and speed controls for educational purposes

### User Interface
- **Responsive Design**: Bootstrap-based responsive layout
- **Modern Styling**: Custom CSS with gradient borders and smooth transitions
- **Interactive Elements**: Number pad, cell selection, hint display system

## Data Flow

1. **Puzzle Generation**: Client requests new puzzle → Server generates using backtracking → Returns puzzle and solution
2. **Gameplay**: User interactions update client state → Validation occurs locally → Server validates on completion
3. **AI Hints**: Current puzzle state sent to server → OpenAI API processes puzzle → Strategic hint returned
4. **Visualization**: Server generates step-by-step solving process → Client renders animated visualization

## External Dependencies

### Python Packages
- **Flask**: Web framework and routing
- **OpenAI**: AI-powered hint generation
- **Gunicorn**: Production WSGI server
- **Flask-SQLAlchemy**: Database ORM (prepared for future features)
- **psycopg2-binary**: PostgreSQL adapter

### Frontend Libraries
- **Bootstrap 5**: UI framework with dark theme
- **Font Awesome**: Icon library
- **Browser APIs**: Local storage for game state persistence

### Infrastructure
- **Replit**: Hosting platform with Nix environment
- **PostgreSQL**: Database system (configured but not yet utilized)
- **OpenSSL**: Secure connections

## Deployment Strategy

### Environment Configuration
- **Nix Environment**: Stable channel with Python 3.11, OpenSSL, and PostgreSQL
- **Process Management**: Gunicorn with auto-reload for development
- **Port Configuration**: Internal port 5000, external port 80
- **Scaling**: Autoscale deployment target for traffic handling

### Security Considerations
- **API Key Management**: Environment variables and config file options
- **Session Management**: Flask secret key from environment
- **HTTPS Ready**: OpenSSL included for secure connections

## Changelog
- June 27, 2025. Initial setup

## User Preferences

Preferred communication style: Simple, everyday language.