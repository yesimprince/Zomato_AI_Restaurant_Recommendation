# Prompt for Google Stitch: Desktop App Design for Zomato AI Recommender

You can copy and paste the following prompt into Google Stitch (or any other coding assistant) to generate the desktop application for your project.

---

**Role**: You are an expert desktop application developer and UI/UX designer.

**Task**: Build a stunning, premium desktop application for an AI-Powered Restaurant Recommendation System (inspired by Zomato).

## Context
We are building a system that takes user preferences, pre-filters a restaurant dataset, and uses a Large Language Model (Groq/LLaMA) to rank and explain the best restaurant recommendations. The core logic and REST API (FastAPI) are already built and running locally. You are responsible for building the native Desktop Presentation Layer that communicates with this local API.

## Input Requirements (Preference Form)
Create a beautiful, intuitive form or sidebar in the desktop app to collect the following user preferences:
- **Location**: Required (Text input or dropdown, e.g., "Bangalore")
- **Budget**: Required (Radio buttons, segmented control, or custom selector: Low, Medium, High)
- **Minimum Rating**: Required (Slider from 0.0 to 5.0)
- **Cuisine**: Optional (Text input or multi-select dropdown, e.g., "Italian")
- **Additional Preferences**: Optional (Free-text textarea, e.g., "family-friendly, quick service, outdoor seating")

## Output Requirements (Results Display)
Once the backend returns the recommendations, display them in a visually appealing format in the main content area (e.g., interactive cards or a sleek list view). Each result must show:
- **Rank Badge**: Visual indicator of the rank (1st, 2nd, 3rd...)
- **Restaurant Name**: Prominent heading
- **Cuisine**: E.g., "Italian, Continental"
- **Rating**: Star rating or bold numeric score (e.g., 4.5 ⭐️)
- **Estimated Cost**: E.g., "₹1200 for two"
- **AI-Generated Explanation**: A dedicated section explaining exactly why this restaurant matches the user's preferences.

## UX/UI & Aesthetic Requirements
- **Premium Native Feel**: Do not build a basic, generic-looking window. Use modern desktop design principles.
- **Dynamic Aesthetics**: Implement features like glassmorphism (acrylic/mica effects if supported by the OS), subtle micro-animations on hover, smooth transitions, and a curated color palette (must include a sleek dark mode).
- **Loading States**: Display a compelling loading state (e.g., skeleton cards or a custom "AI is analyzing restaurants..." animation) while the API request is in flight.
- **Active Filters**: Show a summary of the applied filters above the results.
- **Empty States**: If no results are found, show a friendly empty state suggesting the user broaden their filters.

## Tech Stack Constraints
*(Note to developer: Adapt this based on the desktop framework you prefer to use)*
- **Option A (Tauri + React/Vite)**: Use Tauri with React and Tailwind CSS. Focus on a lightweight, blazing-fast native feel using Rust for the backend shell and shadcn/ui for the frontend components.
- **Option B (Electron + Next.js/React)**: Use Electron. Build a highly polished, responsive interface using Tailwind CSS, ensuring it feels like a native app (hide default window borders, implement custom title bars).
- **Option C (Python - CustomTkinter / PyQt6)**: If keeping everything in Python, use CustomTkinter or PyQt6 with a modern stylesheet (QSS) to avoid the "dated 90s" look. It must look sleek, vibrant, and modern.

Please provide the code to scaffold this desktop application, build the UI layout, and integrate with the local REST API (`POST http://localhost:8000/api/v1/recommend`).
