# Art.OEM - Project Overview

## Project Description
Portfolio and e-commerce site for 3D printed and painted artwork, split into two distinct sections:

1. **Personal Art Gallery**: Curated, meaningful pieces (Instagram-style)
2. **Commercial Shop**: High-volume prints (Shopify-style store)

## Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.11)
- **Database**: PostgreSQL (Cloud SQL) / SQLite for dev
- **ORM**: SQLAlchemy
- **APIs to integrate**:
  - Instagram API (for personal art sync)
  - Facebook API (for personal art sync)
  - Shopify API (for commercial store integration)

### Frontend
- **Framework**: React with Vite
- **Styling**: Tailwind CSS
- **Routing**: React Router

### Deployment
- **Platform**: Google Cloud
- **Backend**: Cloud Run
- **Images**: Cloud Storage
- **Project**: eng-skyline-470621-s4

### Design
- **Theme**: Dark mode
- **Colors**: Purple / Black / Teal
- **Style**:
  - Personal gallery: Instagram-style grid layout
  - Commercial: Shopify-style product pages

## Data Models

### Personal Art Item
- ID
- Title
- Description (short for grid, long for detail page)
- Images (multiple per item)
- Tags (for filtering)
- Availability status (for sale / display only)
- Buy link (if available)
- Instagram post ID (for API sync)
- Facebook post ID (for API sync)
- Created/Updated timestamps

### Commercial Product
- ID
- Title
- Description
- Images
- Price
- Quantity/Stock
- Shopify product ID (for sync)
- Tags/Categories
- Created/Updated timestamps

## Features

### Personal Art Gallery
- Instagram-style grid view
- Clickthrough to detail pages with:
  - Multiple images (gallery/carousel)
  - Long description
  - Availability indicator
  - Buy link if available
- Tag-based filtering (stub initially)
- Dark theme with custom colors

### Commercial Shop
- Shopify-style product grid
- Product detail pages
- Shopping cart (stub initially)
- Checkout flow (stub initially)
- **Integration with Shopify** for actual commerce

## API Integrations (Future)

### Instagram API
- Sync personal art posts
- Pull images and captions
- Link Instagram posts to art items

### Facebook API
- Sync personal art posts
- Cross-post capability
- Link Facebook posts to art items

### Shopify API
- Sync commercial products
- Handle inventory
- Process orders through Shopify
- Webhook integration for updates

## Project Structure
```
art.oem/
├── backend/
│   ├── venv/                          # Python virtual environment
│   ├── app/
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── models/
│   │   │   ├── personal_art.py
│   │   │   └── commercial_product.py
│   │   ├── schemas/
│   │   │   ├── personal_art.py
│   │   │   └── commercial_product.py
│   │   ├── routers/
│   │   │   ├── personal.py
│   │   │   ├── commercial.py
│   │   │   ├── instagram.py          # Future
│   │   │   ├── facebook.py           # Future
│   │   │   └── shopify.py            # Future
│   │   └── integrations/             # Future
│   │       ├── instagram.py
│   │       ├── facebook.py
│   │       └── shopify.py
│   ├── requirements.txt
│   └── tests/
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── PersonalGallery/
│   │   │   └── CommercialShop/
│   │   ├── components/
│   │   └── App.jsx
│   ├── tailwind.config.js
│   └── package.json
├── docs/
│   ├── project-overview.md           # This file
│   └── api.md                         # Future
└── .claude/
    └── rules.md
```

## Implementation Phases

### Phase 1: Backend Foundation (IN PROGRESS)
- ✅ Project structure
- FastAPI setup
- Data models
- Database configuration
- Basic CRUD endpoints

### Phase 2: Frontend Foundation
- React + Vite setup
- Tailwind configuration (dark theme)
- Routing
- Shared components

### Phase 3: Personal Gallery
- Grid view
- Detail pages
- Image handling
- Tag filtering (stub)

### Phase 4: Commercial Shop
- Product grid
- Product details
- Cart (stub)
- Checkout (stub)

### Phase 5: API Integrations
- Instagram API integration
- Facebook API integration
- Shopify API integration

### Phase 6: Deployment
- Cloud Run setup
- Cloud Storage configuration
- CI/CD pipeline
- Domain configuration

## Development Principles
- Incremental development with frequent check-ins
- Test-driven development (TDD)
- Code review for every change
- No batch implementations
- Always use venv for Python development

## Environment
- **GCP Project**: eng-skyline-470621-s4
- **Service Account**: 239182350066-compute@developer.gserviceaccount.com
- **Python**: 3.11.2
- **Node**: 18.20.4
- **Platform**: Linux (GC Compute instance)
