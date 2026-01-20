# Requirements Document

## Introduction

The Web Session Recorder is a full-stack application that captures and stores all browser interactions during a web session. The system consists of a Vue 3 frontend, Python FastAPI backend, and uses Playwright for browser automation. All browser interactions, network requests, and user actions are recorded to a SQLite database with real-time streaming capabilities via WebSocket. The system is designed for personal use with configuration-driven architecture using YAML files.

## Glossary

- **Session**: A single recording instance from browser launch to browser close
- **Event**: A captured user interaction or browser action (click, input, navigation, etc.)
- **Locator**: A strategy for identifying a DOM element (role, CSS selector, XPath, etc.)
- **Frontend**: Vue 3 + Vite + Element Plus web application
- **Backend**: Python FastAPI server with SQLAlchemy ORM
- **Recorder**: The Playwright-based browser automation component that captures events
- **Privacy_Mode**: Configuration setting controlling data sensitivity (none/partial/strict)
- **WebSocket_Stream**: Real-time event delivery channel from backend to frontend
- **Config_Manager**: Component responsible for reading and writing YAML configuration files
- **Database**: SQLite database storing sessions, events, and configuration
- **Browser_Controller**: Component managing Playwright browser lifecycle and context

## Requirements

### Requirement 1: Browser Control and Configuration

**User Story:** As a user, I want to control which browser to use and how it launches, so that I can record sessions in my preferred environment with preserved login state.

#### Acceptance Criteria

1. THE Browser_Controller SHALL support launching Chrome, Edge, and Firefox browsers
2. WHEN no browser is specified, THE Browser_Controller SHALL use the locally installed default browser
3. THE Browser_Controller SHALL support launching browsers in incognito mode
4. THE Browser_Controller SHALL support specifying a user data directory to preserve login state
5. THE Config_Manager SHALL read all browser settings from config/browser.yaml
6. THE config/browser.yaml file SHALL contain browser paths, launch options, and context options

### Requirement 2: Recording Session Management

**User Story:** As a user, I want to start and stop recording sessions with optional starting URLs, so that I can capture my browser interactions from any starting point.

#### Acceptance Criteria

1. WHEN a user starts a recording with a URL, THE Recorder SHALL launch the browser and navigate to that URL
2. WHEN a user starts a recording without a URL, THE Recorder SHALL launch the browser with a blank page
3. WHEN a recording is active, THE Recorder SHALL capture all user interactions until explicitly stopped
4. WHEN a user stops a recording, THE Recorder SHALL finalize the session and save all data to the Database
5. THE Backend SHALL provide a POST /api/sessions/start endpoint to initiate recording
6. THE Backend SHALL provide a POST /api/sessions/{id}/stop endpoint to terminate recording
7. THE Database SHALL store session metadata including run_id, start_url, start_time, end_time, status, browser_type, incognito, and event_count

### Requirement 3: Event Capture and Locator Generation

**User Story:** As a user, I want all my browser interactions captured with multiple locator strategies, so that I can reliably identify elements for automation or analysis.

#### Acceptance Criteria

1. THE Recorder SHALL capture click, dblclick, contextmenu, input, change, submit, keydown, dialog, download, and file_upload events
2. THE Recorder SHALL capture navigation events when the page URL changes
3. WHEN an event targets a DOM element, THE Recorder SHALL generate multiple locator strategies for that element
4. THE Recorder SHALL generate locators using role, label, data-testid, placeholder, text, CSS selector, and XPath strategies
5. THE Recorder SHALL capture page context including URL, title, and iframe information for each event
6. THE Recorder SHALL assign a sequential number to each event within a session
7. THE Database SHALL store events with session_id, seq, timestamp, event_type, page_url, page_title, target_data, locators, network_data, and raw_data

### Requirement 4: Network Request and Response Capture

**User Story:** As a user, I want to capture network requests and responses including full bodies, so that I can analyze API interactions and data flows.

#### Acceptance Criteria

1. THE Recorder SHALL capture all network requests made during a session
2. THE Recorder SHALL capture request method, URL, headers, and body
3. THE Recorder SHALL capture response status, headers, and body
4. THE Recorder SHALL store network data as part of event records in the Database
5. THE Config_Manager SHALL read network monitoring settings from config/recorder.yaml

### Requirement 5: Privacy Mode Configuration

**User Story:** As a user, I want to control data sensitivity levels, so that I can choose between full data capture and privacy protection.

#### Acceptance Criteria

1. THE Config_Manager SHALL support three privacy modes: none, partial, and strict
2. WHEN privacy mode is "none", THE Recorder SHALL save all data including passwords and tokens
3. WHEN privacy mode is "partial", THE Recorder SHALL mask sensitive fields while preserving structure
4. WHEN privacy mode is "strict", THE Recorder SHALL exclude all potentially sensitive data
5. THE Config_Manager SHALL read privacy mode settings from config/recorder.yaml
6. THE default privacy mode SHALL be "none"

### Requirement 6: Real-Time Event Streaming

**User Story:** As a user, I want to see events in real-time as they are captured, so that I can monitor the recording session live.

#### Acceptance Criteria

1. THE Backend SHALL provide a WebSocket endpoint at /ws/sessions/{id}
2. WHEN an event is captured, THE Backend SHALL immediately push it through the WebSocket_Stream
3. THE Frontend SHALL connect to the WebSocket_Stream when viewing an active session
4. THE Frontend SHALL display events in real-time as they arrive through the WebSocket_Stream
5. WHEN the WebSocket connection is lost, THE Frontend SHALL attempt to reconnect automatically

### Requirement 7: Configuration File Management

**User Story:** As a developer, I want all system configuration in separate YAML files, so that I can easily customize behavior without code changes.

#### Acceptance Criteria

1. THE Config_Manager SHALL read configuration from config/app.yaml for application and server settings
2. THE Config_Manager SHALL read configuration from config/browser.yaml for browser paths and launch options
3. THE Config_Manager SHALL read configuration from config/recorder.yaml for recording strategy and event capture settings
4. THE Config_Manager SHALL read configuration from config/database.yaml for database connection and retention policy
5. THE Config_Manager SHALL read configuration from config/locators.yaml for locator generation strategies and priorities
6. THE Backend SHALL provide a GET /api/config endpoint to retrieve all configuration
7. THE Backend SHALL provide a PUT /api/config endpoint to update configuration files

### Requirement 8: Frontend User Interface

**User Story:** As a user, I want a web interface to start recordings, view sessions, and manage settings, so that I can interact with the system easily.

#### Acceptance Criteria

1. THE Frontend SHALL provide a home page with controls to start and stop recording with configuration options
2. THE Frontend SHALL provide a session list page displaying all recorded sessions
3. THE Frontend SHALL provide a session detail page showing event timeline and details for a specific session
4. THE Frontend SHALL provide a settings page for editing configuration files online
5. THE Frontend SHALL be built using Vue 3, Vite, and Element Plus
6. THE Frontend SHALL communicate with the Backend via RESTful API and WebSocket

### Requirement 9: Session and Event Retrieval API

**User Story:** As a user, I want to retrieve recorded sessions and their events, so that I can review and analyze past recordings.

#### Acceptance Criteria

1. THE Backend SHALL provide a GET /api/sessions endpoint to list all sessions
2. THE Backend SHALL provide a GET /api/sessions/{id} endpoint to retrieve session details
3. THE Backend SHALL provide a GET /api/sessions/{id}/events endpoint to retrieve all events for a session
4. THE Backend SHALL return session data including metadata and event counts
5. THE Backend SHALL return event data including all captured information and locators

### Requirement 10: Database Schema and Persistence

**User Story:** As a developer, I want a well-structured database schema, so that session data is organized and queryable.

#### Acceptance Criteria

1. THE Database SHALL have a sessions table with columns: run_id, start_url, start_time, end_time, status, browser_type, incognito, event_count
2. THE Database SHALL have an events table with columns: session_id, seq, timestamp, event_type, page_url, page_title, target_data, locators, network_data, raw_data
3. THE Database SHALL have a configs table for storing key-value configuration pairs
4. THE Backend SHALL use SQLAlchemy ORM to interact with the Database
5. THE Database SHALL use SQLite as the storage engine
6. THE Backend SHALL incrementally save events to the Database as they are captured

### Requirement 11: Iframe Event Capture

**User Story:** As a user, I want events inside iframes to be captured, so that I have complete visibility into all page interactions.

#### Acceptance Criteria

1. THE Recorder SHALL inject JavaScript into all frames including iframes
2. WHEN an event occurs inside an iframe, THE Recorder SHALL capture it with iframe context information
3. THE Recorder SHALL include iframe URL and identification in the event data
4. THE Recorder SHALL generate locators for elements inside iframes

### Requirement 12: Screenshot and Network Data Storage

**User Story:** As a user, I want optional storage of screenshots and large network responses, so that I can preserve visual evidence and detailed data.

#### Acceptance Criteria

1. THE Backend SHALL support optional screenshot capture during recording
2. WHEN screenshots are enabled, THE Backend SHALL save screenshots to a screenshots/ directory
3. THE Backend SHALL support optional storage of large network response bodies
4. WHEN network body storage is enabled, THE Backend SHALL save response bodies to a network/ directory
5. THE Config_Manager SHALL read screenshot and network storage settings from config/recorder.yaml

### Requirement 13: Technology Stack Implementation

**User Story:** As a developer, I want the system built with modern, reliable technologies, so that it is maintainable and performant.

#### Acceptance Criteria

1. THE Frontend SHALL be implemented using Vue 3 with Vite as the build tool
2. THE Frontend SHALL use Element Plus for UI components
3. THE Backend SHALL be implemented using Python FastAPI framework
4. THE Backend SHALL use SQLAlchemy for database ORM
5. THE Backend SHALL use Playwright for browser automation
6. THE Recorder SHALL inject JavaScript into pages for DOM event capture
7. THE system SHALL use SQLite for data persistence
