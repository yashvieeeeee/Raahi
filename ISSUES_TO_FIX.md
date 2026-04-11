# Issues & Requirements

## 1. GPS Location Issue
- **Current**: Defaults to hardcoded 19.076, 72.8777 (Bandra-Kurla Complex)
- **Fix**: Should detect actual browser GPS or show location selector
- **Files to modify**: 
  - `backend/routes/web_routes.py` - add route to detect location
  - `frontend/templates/home.html` - add GPS detection UI
  - `frontend/static/app.js` - enhance GPS initialization

## 2. Compare Routes Section
- **Current**: Shows only the selected route in modal
- **Fix**: Show comparison between all routes (fastest, cheapest, cleanest)
- **File to modify**: `frontend/static/app.js` - enhance compare modal

## 3. Search Routes Button Styling
- **Current**: Becomes darker on hover
- **Fix**: Stay green, add shadow/glow effect on hover/click
- **File to modify**: `frontend/static/style.css` - add glow effect

## 4. CO2 Saved Negative Value (-5.12 kg)
- **Current**: auto_co2 - trip_co2 = negative when trip is less eco-friendly
- **Analysis**: Happens when selected mode (e.g., Bus) has HIGHER emissions than Auto baseline
- **Root cause**: Emissions calculation may be overestimating certain modes
- **Fix options**:
  - Validate emissions_calculator logic
  - Ensure Auto is always the highest baseline
  - Or clamp CO2 saved to minimum 0 (can't have negative savings)
- **File to check**: `backend/services/trip_service.py` and `raahi_ml/pipelines/emissions_pipeline.py`
