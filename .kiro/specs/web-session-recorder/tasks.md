# Implementation Plan: Web Session Recorder

## Overview

This implementation plan breaks down the web session recorder into discrete coding tasks. The system will be built incrementally, starting with core infrastructure, then adding recording capabilities, and finally building the frontend interface. Each task builds on previous work, with checkpoints to ensure stability.

## Tasks

- [x] 1. Set up project structure and configuration management
  - Create directory structure: backend/, frontend/, config/
  - Set up Python project with FastAPI, SQLAlchemy, Playwright, PyYAML (use local Python environment, no virtual environment)
  - Set up Vue 3 project with Vite, Element Plus, Axios
  - Create YAML configuration files: app.yaml, browser.yaml, recorder.yaml, database.yaml, locators.yaml
  - Implement Config_Manager class to load and validate YAML files
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [ ]* 1.1 Write property test for Config_Manager
  - **Property 14: Configuration File Loading**
  - **Validates: Requirements 1.5**

- [x] 2. Implement database layer and models
  - [x] 2.1 Create SQLAlchemy models for Session, Event, Config tables
    - Define Session model with all required columns
    - Define Event model with foreign key to Session
    - Define Config model for key-value storage
    - Add indexes for performance (session_id, seq)
    - _Requirements: 10.1, 10.2, 10.3_
  
  - [x] 2.2 Implement Database Layer class with CRUD operations
    - Implement create_session, update_session, get_session, list_sessions
    - Implement create_event, get_events with pagination
    - Implement get_config, set_config
    - Add transaction management and error handling
    - _Requirements: 10.6_
  
  - [ ]* 2.3 Write property test for session persistence round-trip
    - **Property 2: Session Persistence Round-Trip**
    - **Validates: Requirements 2.4, 2.7, 9.2, 9.4**
  
  - [ ]* 2.4 Write property test for event data completeness
    - **Property 3: Event Data Completeness**
    - **Validates: Requirements 3.5, 3.7, 9.5**
  
  - [ ]* 2.5 Write property test for incremental event persistence
    - **Property 10: Incremental Event Persistence**
    - **Validates: Requirements 10.6**

- [ ] 3. Implement locator generation system
  - [x] 3.1 Create Locator Generator class
    - Implement generate_role_locator method
    - Implement generate_label_locator method
    - Implement generate_testid_locator method
    - Implement generate_placeholder_locator method
    - Implement generate_text_locator method
    - Implement generate_css_locator method (fallback)
    - Implement generate_xpath_locator method (fallback)
    - Implement prioritize_locators method based on config/locators.yaml
    - _Requirements: 3.3, 3.4_
  
  - [ ]* 3.2 Write property test for multi-strategy locator generation
    - **Property 4: Multi-Strategy Locator Generation**
    - **Validates: Requirements 3.3, 3.4**
  
  - [ ]* 3.3 Write unit tests for specific locator strategies
    - Test role-based locator for button with accessible name
    - Test label-based locator for input with label
    - Test CSS and XPath fallback locators
    - _Requirements: 3.4_

- [ ] 4. Implement browser controller and event capturer
  - [x] 4.1 Create Browser Controller class
    - Implement launch_browser method supporting Chrome, Edge, Firefox
    - Implement create_context with incognito and user_data_dir options
    - Implement navigate method
    - Implement inject_capturer method to inject JavaScript
    - Implement close_browser method
    - _Requirements: 1.1, 1.2, 1.3, 1.4_
  
  - [x] 4.2 Create JavaScript injection script for DOM event capture
    - Capture click, dblclick, contextmenu events
    - Capture input, change, submit events
    - Capture keydown events (Enter, Escape)
    - Extract target element information (tag, attributes, text)
    - Extract page context (URL, title, iframe info)
    - Send events to Python via Playwright bridge
    - _Requirements: 3.1, 3.2, 13.6_
  
  - [x] 4.3 Create Event Capturer class
    - Implement inject_script method
    - Implement setup_listeners for Playwright events (navigation, dialog, download)
    - Implement handle_dom_event to process JavaScript-captured events
    - Implement handle_navigation for URL changes
    - Implement handle_dialog for alert/confirm/prompt
    - Implement handle_download for file downloads
    - Integrate with Locator Generator for each event
    - _Requirements: 3.1, 3.2, 3.6_
  
  - [ ]* 4.4 Write property test for event capture completeness
    - **Property 1: Event Capture Completeness**
    - **Validates: Requirements 2.3, 3.1, 3.2, 3.6**
  
  - [ ]* 4.5 Write unit tests for browser controller
    - Test launching Chrome, Edge, Firefox
    - Test incognito mode
    - Test user data directory
    - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [ ] 5. Implement network monitoring
  - [x] 5.1 Create Network Monitor class
    - Implement setup_monitoring to attach to Playwright page
    - Implement handle_request to capture request details
    - Implement handle_response to capture response details
    - Implement apply_privacy_filter based on privacy mode
    - Implement should_capture_request to filter static resources
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_
  
  - [ ]* 5.2 Write property test for network request capture completeness
    - **Property 5: Network Request Capture Completeness**
    - **Validates: Requirements 4.1, 4.2, 4.3, 4.4**
  
  - [ ]* 5.3 Write property test for privacy mode data masking
    - **Property 6: Privacy Mode Data Masking**
    - **Validates: Requirements 5.3, 5.4**
  
  - [ ]* 5.4 Write unit tests for privacy modes
    - Test "none" mode saves all data
    - Test "partial" mode masks sensitive fields
    - Test "strict" mode excludes sensitive data
    - _Requirements: 5.2, 5.3, 5.4_

- [x] 6. Checkpoint - Core recording functionality complete
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 7. Implement session manager and WebSocket streaming
  - [x] 7.1 Create Session Manager class
    - Implement create_session method
    - Implement start_recording method (launches browser, starts capture)
    - Implement stop_recording method (closes browser, finalizes session)
    - Implement handle_event method (saves to DB, streams via WebSocket)
    - Implement stream_event method for WebSocket broadcasting
    - Implement get_session and list_sessions methods
    - _Requirements: 2.1, 2.2, 2.3, 2.4_
  
  - [x] 7.2 Implement WebSocket server endpoint
    - Create /ws/sessions/{id} WebSocket endpoint
    - Handle client connections and disconnections
    - Broadcast events to connected clients
    - Implement reconnection handling
    - _Requirements: 6.1, 6.2_
  
  - [ ]* 7.3 Write property test for real-time event streaming
    - **Property 7: Real-Time Event Streaming**
    - **Validates: Requirements 6.2**
  
  - [ ]* 7.4 Write property test for WebSocket reconnection
    - **Property 15: WebSocket Reconnection**
    - **Validates: Requirements 6.5**

- [ ] 8. Implement iframe support
  - [x] 8.1 Extend Event Capturer for iframe handling
    - Inject JavaScript into all frames including iframes
    - Capture iframe context (is_iframe, frame_url)
    - Generate locators for iframe elements
    - Handle cross-origin iframe restrictions
    - _Requirements: 11.1, 11.2, 11.3, 11.4_
  
  - [ ]* 8.2 Write property test for iframe event capture with context
    - **Property 11: Iframe Event Capture with Context**
    - **Validates: Requirements 11.1, 11.2, 11.3, 11.4**
  
  - [ ]* 8.3 Write unit tests for iframe scenarios
    - Test event capture inside iframe
    - Test cross-origin iframe handling
    - _Requirements: 11.2_

- [ ] 9. Implement optional screenshot and network storage
  - [x] 9.1 Add screenshot capture functionality
    - Implement screenshot capture in Event Capturer
    - Save screenshots to screenshots/ directory with session and event reference
    - Make screenshot capture configurable via config/recorder.yaml
    - _Requirements: 12.1, 12.2_
  
  - [x] 9.2 Add network body storage functionality
    - Implement large response body storage in Network Monitor
    - Save response bodies to network/ directory with session and request reference
    - Make network storage configurable via config/recorder.yaml
    - _Requirements: 12.3, 12.4, 12.5_
  
  - [ ]* 9.3 Write property test for optional screenshot persistence
    - **Property 12: Optional Screenshot Persistence**
    - **Validates: Requirements 12.2**
  
  - [ ]* 9.4 Write property test for optional network body storage
    - **Property 13: Optional Network Body Storage**
    - **Validates: Requirements 12.4**

- [ ] 10. Implement REST API endpoints
  - [x] 10.1 Create FastAPI application and routes
    - Implement POST /api/sessions/start endpoint
    - Implement POST /api/sessions/{id}/stop endpoint
    - Implement GET /api/sessions endpoint with pagination
    - Implement GET /api/sessions/{id} endpoint
    - Implement GET /api/sessions/{id}/events endpoint with pagination
    - Add CORS middleware
    - Add error handling middleware
    - _Requirements: 2.5, 2.6, 9.1, 9.2, 9.3_
  
  - [x] 10.2 Create configuration API endpoints
    - Implement GET /api/config endpoint
    - Implement PUT /api/config endpoint with validation
    - _Requirements: 7.6, 7.7_
  
  - [ ]* 10.3 Write property test for configuration round-trip
    - **Property 8: Configuration Round-Trip**
    - **Validates: Requirements 7.7**
  
  - [ ]* 10.4 Write property test for event retrieval completeness
    - **Property 9: Event Retrieval Completeness**
    - **Validates: Requirements 9.3**
  
  - [ ]* 10.5 Write unit tests for API endpoints
    - Test POST /api/sessions/start with and without URL
    - Test GET /api/sessions returns session list
    - Test GET /api/sessions/{id}/events with pagination
    - _Requirements: 2.5, 2.6, 9.1, 9.2, 9.3_

- [x] 11. Checkpoint - Backend complete
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 12. Implement frontend home page
  - [x] 12.1 Create Home page component with recording controls
    - Create Vue component with Element Plus form
    - Add URL input field (optional)
    - Add browser selection dropdown (Chrome, Edge, Firefox)
    - Add incognito mode toggle
    - Add user data directory input
    - Add Start Recording button (calls POST /api/sessions/start)
    - Add Stop Recording button (calls POST /api/sessions/{id}/stop)
    - Add real-time event counter display
    - _Requirements: 8.1_
  
  - [x] 12.2 Implement WebSocket client for real-time events
    - Connect to /ws/sessions/{id} when recording starts
    - Display events in real-time as they arrive
    - Update event counter
    - Handle connection errors and reconnection
    - _Requirements: 6.3, 6.4, 6.5_

- [ ] 13. Implement frontend session list page
  - [x] 13.1 Create Session List page component
    - Create Vue component with Element Plus table
    - Display columns: run_id, start_url, start_time, duration, event_count, status
    - Implement pagination
    - Add filters for date, browser, status
    - Add click handler to navigate to session detail
    - Call GET /api/sessions on mount
    - _Requirements: 8.2_

- [ ] 14. Implement frontend session detail page
  - [x] 14.1 Create Session Detail page component
    - Display session metadata
    - Create event timeline component (chronological list)
    - Create event detail viewer (expandable cards)
    - Display locators for each event
    - Display network request/response data
    - Display screenshots if available
    - Call GET /api/sessions/{id} and GET /api/sessions/{id}/events on mount
    - _Requirements: 8.3_

- [ ] 15. Implement frontend settings page
  - [x] 15.1 Create Settings page component
    - Create tabbed interface for each config file (app, browser, recorder, database, locators)
    - Implement YAML editor with syntax highlighting (use CodeMirror or Monaco)
    - Add validation before save
    - Add Reset to Defaults button
    - Call GET /api/config on mount
    - Call PUT /api/config on save
    - _Requirements: 8.4_

- [ ] 16. Implement frontend routing and navigation
  - [x] 16.1 Set up Vue Router
    - Create routes for Home, Session List, Session Detail, Settings
    - Create navigation menu component
    - Add route guards if needed
    - _Requirements: 8.6_

- [ ] 17. Final integration and testing
  - [x] 17.1 End-to-end integration tests
    - Test complete flow: start session → perform interactions → stop session → verify data
    - Test real-time streaming with WebSocket
    - Test configuration update and application
    - Test iframe event capture
    - _Requirements: All_
  
  - [ ]* 17.2 Run all property-based tests
    - Execute all 15 property tests with 100+ iterations each
    - Verify all properties pass
    - _Requirements: All_

- [x] 18. Final checkpoint - Project complete
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Use local Python environment (no virtual environment needed)
- Test tasks are optional and will not be implemented without explicit user approval
- Backend uses Python with FastAPI, SQLAlchemy, Playwright
- Frontend uses Vue 3 with Vite and Element Plus
- All configuration is externalized to YAML files
