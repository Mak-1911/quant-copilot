# Quant Copilot API Documentation

## Overview
Quant Copilot is a quantitative trading strategy platform that allows users to generate, backtest, and manage trading strategies using AI. The backend is built with FastAPI and provides comprehensive endpoints for strategy management, backtesting, and leaderboard functionality.

## Architecture Overview

### Core Components
- **FastAPI Application**: Main web framework
- **SQLModel**: Database ORM with SQLite/PostgreSQL support
- **Redis**: Caching and OTP storage
- **Backtrader**: Strategy backtesting engine
- **Google Gemini**: LLM for strategy generation and explanation
- **JWT Authentication**: Token-based auth with email OTP verification

### Database Models
- **User**: User management
- **Strategy**: Strategy storage
- **LeaderboardEntry**: Performance tracking
- **StrategyBlueprint**: Visual strategy builder schema

## Authentication Flow

### 1. OTP-Based Authentication
The application uses email-based OTP authentication instead of traditional passwords.

#### Flow:
1. User requests OTP with email
2. System generates 6-digit OTP, stores in Redis (10min expiry)
3. OTP sent via SMTP email
4. User verifies OTP
5. System issues JWT token (15-day expiry)
6. Token required for protected endpoints

#### Endpoints:
- `POST /auth/request-otp`
- `POST /auth/verify-otp`

## API Endpoints Reference

### Authentication Routes (`/auth`)

#### Request OTP
```http
POST /auth/request-otp
Content-Type: application/json

{
  "email": "user@example.com"
}
```

**Response:**
```json
{
  "message": "OTP sent to your email."
}
```

#### Verify OTP
```http
POST /auth/verify-otp
Content-Type: application/json

{
  "email": "user@example.com",
  "otp_code": "123456"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

### Strategy Generation Routes

#### Generate Strategy from Prompt
```http
POST /generate
Content-Type: application/json

{
  "user_prompt": "Create a moving average crossover strategy"
}
```

**Response:**
```json
{
  "generated_code": "import backtrader as bt\n\nclass Strategy(bt.Strategy):\n    ..."
}
```

#### Translate Blueprint to Code
```http
POST /builder/translate
Content-Type: application/json

{
  "asset": "RELIANCE.NS",
  "timeframe": "1d",
  "entry": [
    {
      "indicator": "sma",
      "operator": "crosses_above",
      "value": null,
      "params": {
        "lookback": 20
      }
    }
  ],
  "exit": [
    {
      "indicator": "sma",
      "operator": "crosses_below", 
      "value": null,
      "params": {
        "lookback": 50
      }
    }
  ],
  "risk": {
    "stop_loss": 5.0,
    "take_profit": 10.0
  },
  "position_sizing": "fixed"
}
```

**Response:**
```json
{
  "prompt": "Build a strategy on RELIANCE.NS using 1d candles...",
  "generated_code": "import backtrader as bt\n..."
}
```

### Strategy Management Routes

#### Save Strategy (Protected)
```http
POST /strategy/save
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "My Strategy",
  "prompt": "Moving average strategy", 
  "code": "import backtrader as bt\n..."
}
```

**Response:**
```json
{
  "message": "Strategy saved successfully",
  "strategy_id": 123
}
```

#### List All Strategies
```http
GET /strategy/list?strategy_id=123
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "MA Crossover",
    "prompt": "Create moving average strategy",
    "code": "import backtrader as bt\n...",
    "created_at": "2023-12-01T10:00:00"
  }
]
```

#### Get Specific Strategy
```http
GET /strategy/{strategy_id}
```

**Response:**
```json
{
  "id": 1,
  "name": "MA Crossover", 
  "prompt": "Create moving average strategy",
  "code": "import backtrader as bt\n...",
  "created_at": "2023-12-01T10:00:00"
}
```

#### Delete Strategy
```http
DELETE /strategy/{strategy_id}
```

**Response:**
```json
{
  "status": "deleted"
}
```

### Backtesting Routes

#### Run Backtest
```http
POST /backtest
Content-Type: application/json

{
  "strategy_code": "import backtrader as bt\n...",
  "ticker": "RELIANCE.NS"
}
```

**Response:**
```json
{
  "start_value": 100000,
  "end_value": 110000,
  "pnl": 10000
}
```

#### Generate Plot
```http
POST /plot
Content-Type: application/json

{
  "strategy_code": "import backtrader as bt\n...",
  "ticker": "RELIANCE.NS"
}
```

**Response:**
```json
{
  "data": [...],
  "layout": {...}
}
```

### Strategy Analysis Routes

#### Explain Strategy
```http
POST /explain
Content-Type: application/json

{
  "strategy_code": "import backtrader as bt\n..."
}
```

**Response:**
```json
{
  "explanation": "This strategy uses moving average crossover..."
}
```

### Export Routes

#### Export Strategy Code
```http
GET /export/code/{strategy_id}
```

**Response:** File download (.py)

#### Export Strategy Results as CSV  
```http
GET /export/csv/{strategy_id}
```

**Response:** File download (.csv)

### Leaderboard Routes (Protected)

#### Submit Strategy to Leaderboard
```http
POST /leaderboard/submit
Authorization: Bearer <token>
Content-Type: application/json

{
  "strategy_id": 123,
  "strategy_name": "My Strategy",
  "code": "import backtrader as bt\n...",
  "dataset": "default",
  "ticker": "RELIANCE.NS"
}
```

**Response:**
```json
{
  "entry_id": 456,
  "metrics": {
    "Sharpe Ratio": 1.5,
    "Max Drawdown": -0.05,
    "Total Return": 0.15
  },
  "score": 85.2
}
```

#### Get Top Performers
```http
GET /leaderboard/top?period=daily&dataset=default&limit=50
```

**Query Parameters:**
- `period`: "daily" | "weekly" | "alltime" (default: "daily")
- `dataset`: Filter by dataset (optional)
- `limit`: Number of results (default: 50, max: 50)

**Response:**
```json
{
  "period": "daily",
  "dataset": "default", 
  "top": [
    {
      "id": 1,
      "user_id": 123,
      "username": "user@example.com",
      "strategy_id": 456,
      "strategy_name": "Top Strategy",
      "dataset": "default",
      "run_at": "2023-12-01T10:00:00",
      "return_pct": 15.5,
      "sharpe": 1.8,
      "max_drawdown": -5.2,
      "score": 92.1
    }
  ]
}
```

## Data Models

### User Model
```typescript
interface User {
  id?: number;
  email: string;
  created_at: string;
}
```

### Strategy Model
```typescript
interface Strategy {
  id?: number;
  name: string;
  prompt: string;
  code: string;
  created_at: string;
}
```

### Strategy Blueprint Model
```typescript
interface StrategyBlueprint {
  asset: string;
  timeframe?: string;
  entry: EntryCondition[];
  exit: ExitCondition[];
  risk?: RiskManagement;
  position_sizing?: "fixed" | "percent" | "risk_adjusted";
}

interface EntryCondition {
  indicator: "sma" | "ema" | "rsi" | "zscore" | "macd" | "bollinger";
  operator: ">" | "<" | ">=" | "<=" | "crosses_above" | "crosses_below";
  value?: number;
  params: IndicatorParams;
}

interface ExitCondition {
  indicator: "sma" | "ema" | "rsi" | "atr" | "macd";
  operator: ">" | "<" | ">=" | "<=" | "crosses_above" | "crosses_below";
  value?: number;
  params: IndicatorParams;
}

interface IndicatorParams {
  lookback?: number;
  threshold?: number;
  multiplier?: number;
}

interface RiskManagement {
  stop_loss?: number | string;
  take_profit?: number;
  trailing_stop?: number;
}
```

### Leaderboard Entry Model
```typescript
interface LeaderboardEntry {
  id: number;
  user_id?: number;
  username?: string;
  strategy_id?: number;
  strategy_name?: string;
  dataset?: string;
  run_at: string;
  return_pct: number;
  sharpe?: number;
  max_drawdown?: number;
  score: number;
  notes?: string;
}
```

## Error Handling

### Standard Error Response
```json
{
  "error": "Error message description"
}
```

### HTTP Status Codes
- `200`: Success
- `400`: Bad Request (validation errors)
- `401`: Unauthorized (invalid/missing token)
- `404`: Not Found
- `500`: Internal Server Error

## Frontend Integration Guidelines

### Authentication State Management
1. Store JWT token in localStorage/sessionStorage
2. Include `Authorization: Bearer <token>` header for protected routes
3. Handle token expiry (15 days) and redirect to login
4. Implement OTP input UI with 6-digit verification

### Strategy Builder UI
1. Visual form for StrategyBlueprint creation
2. Dropdown selections for indicators and operators
3. Dynamic parameter inputs based on indicator selection
4. Real-time preview of generated prompt

### Backtesting Integration
1. Code editor component for strategy editing
2. Chart component for plot visualization (Plotly.js)
3. Results display with key metrics
4. Export functionality for code and CSV

### Leaderboard Features
1. Filterable table with sorting
2. Period selection (daily/weekly/alltime)
3. Dataset filtering
4. User strategy submission interface

### Error Handling
1. Global error boundary for API errors
2. Form validation matching backend validators
3. Loading states for async operations
4. User-friendly error messages

## Environment Variables Required

### Backend (.env)
```env
DATABASE_URL=sqlite:///./database.db
REDIS_URL=redis://localhost:6379
JWT_SECRET=your-secret-key
GOOGLE_API_KEY=your-gemini-api-key
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email
SMTP_PASS=your-app-password
```

## Security Considerations

### Code Validation
- All strategy code is validated for dangerous imports
- AST parsing ensures valid Python syntax
- Sandboxed execution environment for backtesting

### Authentication
- JWT tokens with expiration
- OTP-based verification
- Redis-stored temporary tokens

### Rate Limiting
Consider implementing rate limiting for:
- OTP requests (prevent spam)
- Strategy generation (API costs)
- Backtest execution (resource intensive)

## Testing Strategy

### Frontend Testing Points
1. Authentication flow end-to-end
2. Strategy generation and editing
3. Backtest execution and visualization
4. Leaderboard submission and display
5. Export functionality

### API Integration Testing
1. Token refresh handling
2. Error state management
3. File upload/download
4. Real-time data updates

This documentation provides a complete reference for frontend development. Let me know if you need clarification on any specific endpoint, data model, or integration pattern!