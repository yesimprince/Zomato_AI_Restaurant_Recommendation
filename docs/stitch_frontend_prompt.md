# Prompt for Google Stitch: Frontend Design for Zomato AI Recommender

You can copy and paste the following prompt into Google Stitch (or any other coding assistant) to generate the frontend for your project. 

---

**Role**: You are an expert frontend developer and UI/UX designer.

**Task**: Build a stunning, premium frontend for an AI-Powered Restaurant Recommendation System (inspired by Zomato).

## Context
We are building a system that takes user preferences, pre-filters a restaurant dataset, and uses a Large Language Model (Groq/LLaMA) to rank and explain the best restaurant recommendations. You are responsible for building the Presentation Layer.

## Input Requirements (Preference Form)
Create a beautiful, intuitive form to collect the following user preferences:
- **Location**: Required (Text input or dropdown, e.g., "Bangalore")
- **Budget**: Required (Radio buttons or custom selector: Low, Medium, High)
- **Minimum Rating**: Required (Slider from 0.0 to 5.0)
- **Cuisine**: Optional (Text input or multi-select dropdown, e.g., "Italian")
- **Additional Preferences**: Optional (Free-text textarea, e.g., "family-friendly, quick service, outdoor seating")

## Output Requirements (Results Display)
Once the backend returns the recommendations, display them in a visually appealing format (e.g., interactive cards). Each result must show:
- **Rank Badge**: Visual indicator of the rank (1st, 2nd, 3rd...)
- **Restaurant Name**: Prominent heading
- **Cuisine**: E.g., "Italian, Continental"
- **Rating**: Star rating or bold numeric score (e.g., 4.5 ⭐️)
- **Estimated Cost**: E.g., "₹1200 for two"
- **AI-Generated Explanation**: A dedicated section explaining exactly why this restaurant matches the user's preferences.

## UX/UI & Aesthetic Requirements
- **Premium Feel**: Do not build a basic, boring UI. Use a modern design system. Implement dynamic aesthetics like glassmorphism, subtle micro-animations on hover, smooth transitions, and a curated color palette (potentially a sleek dark mode or vibrant food-app colors like Zomato red).
- **Loading States**: Display a compelling loading state (e.g., skeleton cards or a custom "AI is analyzing restaurants..." spinner) while the API request is in flight.
- **Active Filters**: Show a summary of the applied filters above the results so the user knows what they searched for.
- **Empty States**: If no results are found, show a friendly empty state suggesting the user broaden their filters.

## Tech Stack Constraints
*(Note: adjust this based on the chosen path in our architecture)*
- **If Streamlit**: Push Streamlit to its absolute visual limits using custom CSS, markdown, and columns to make it look less like a data dashboard and more like a consumer app.
- **If React/Next.js**: Use Tailwind CSS (with arbitrary values or a config) or shadcn/ui to build responsive, accessible, and highly polished components. Ensure mobile responsiveness.

Please provide the code to build this UI layout, including the form components, the results view, and the mock API integration state.
