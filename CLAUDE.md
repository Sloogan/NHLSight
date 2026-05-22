# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# Project Context: NHL-ScoreSight (ScoreSight Fork)

## Project Overview
This project is a specialized fork of `royshil/scoresight`. The goal is to transform a generic, heavy OCR scoreboard reader into a lightweight, ultra-fast, and hardcoded computer vision tool dedicated exclusively to **EA Sports NHL** (broadcast/gameplay scoreboard).

The input video signal is always a perfect, digital 1080p or 4K capture (no camera shakes, no perspective distortion).

## Core Architecture Principles
1. **Zero Bloat**: Strip out all generic OCR engines (e.g., Tesseract, EasyOCR) if they add latency. Use optimized OpenCV template matching, color masking, or ultra-lightweight pixel logic for EA NHL's specific fonts.
2. **No Image Correction**: Remove camera stabilization, perspective warping, and lens correction. Assume the input frame is perfectly flat and static.
3. **High Framerate**: The pipeline must process frames at 60 FPS with minimal CPU/GPU overhead to prevent gameplay or stream stuttering.
4. **NHL Specificity**: Hardcode the logic around the EA Sports NHL "Scorebug".

## Target Data Fields (EA NHL Scorebug)
The pipeline must extract and output the following schema:
- `home_team` / `away_team`: 3-letter abbreviations (e.g., "NYR", "EDM").
- `home_score` / `away_score`: Integers (0-99).
- `time`: String ("MM:SS" or "SS.S" for final minute).
- `period`: Integer (1, 2, 3) or String ("OT", "SO").
- `home_pp` / `away_pp`: Boolean (Powerplay active status).
- `pp_time`: String (Powerplay clock remaining, if active).

## Coding Standards & Stack
- **Languages**: Python (OpenCV, NumPy).
- **UI Framework**: Keep PySide/PyQt but strip out 80% of the generic options. Simplify the UI to only show NHL configuration (or switch to pure CLI if instructed).
- **Output**: Clean JSON over local WebSocket/HTTP API, and direct `.txt` file writes for OBS Studio.

## Strict Rules for Claude Code Interaction
- **Do not** write or suggest generic OCR solutions.
- **Do not** add code for handling skewed or shaking video inputs.
- **Always** optimize for matrix operations using NumPy over raw Python loops.
- **Always** match against the official colors and contrast of EA NHL's UI (white text, high-contrast dark/colored backgrounds).
- **Refuse** to add features that deviate from the EA Sports NHL ecosystem.
