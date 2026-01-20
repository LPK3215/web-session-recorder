/**
 * DOM Event Capturer - Injected into pages to capture user interactions
 * This script runs in the page context and sends events back to Python via Playwright
 */

(function() {
  'use strict';
  
  // Initialize recorder namespace
  window.__recorder__ = window.__recorder__ || {
    events: [],
    sendEvent: null
  };
  
  /**
   * Extract element information for locator generation
   */
  function captureElementInfo(element) {
    if (!element || !element.tagName) {
      return null;
    }
    
    const info = {
      tag: element.tagName.toLowerCase(),
      id: element.id || null,
      class: element.className || null,
      name: element.getAttribute('name') || null,
      type: element.getAttribute('type') || null,
      role: element.getAttribute('role') || null,
      aria_label: element.getAttribute('aria-label') || null,
      placeholder: element.getAttribute('placeholder') || null,
      data_testid: element.getAttribute('data-testid') || null,
      text: element.textContent ? element.textContent.trim().substring(0, 100) : null,
      value: element.value || null,
      attributes: {}
    };
    
    // Capture data-* attributes
    for (let attr of element.attributes) {
      if (attr.name.startsWith('data-')) {
        info.attributes[attr.name] = attr.value;
      }
    }
    
    // Find associated label
    if (element.id) {
      const label = document.querySelector(`label[for="${element.id}"]`);
      if (label) {
        info.label_text = label.textContent.trim();
      }
    }
    
    return info;
  }
  
  /**
   * Capture page context information including iframe details
   */
  function capturePageContext() {
    const isIframe = window !== window.top;
    const frameInfo = {
      is_iframe: isIframe,
      frame_url: isIframe ? window.location.href : null,
      frame_name: isIframe ? window.name : null,
      frame_id: null
    };
    
    // Try to get iframe element ID if we're in an iframe
    if (isIframe) {
      try {
        // This will fail for cross-origin iframes, which is expected
        const iframes = window.parent.document.getElementsByTagName('iframe');
        for (let iframe of iframes) {
          if (iframe.contentWindow === window) {
            frameInfo.frame_id = iframe.id || null;
            frameInfo.frame_src = iframe.src || null;
            break;
          }
        }
      } catch (e) {
        // Cross-origin restriction - this is expected and safe to ignore
        frameInfo.cross_origin_restricted = true;
      }
    }
    
    return {
      url: window.location.href,
      title: document.title,
      frame: frameInfo
    };
  }
  
  /**
   * Send event to Python via Playwright
   */
  function sendEventToPython(eventData) {
    // Store in buffer
    window.__recorder__.events.push(eventData);
    
    // Trigger custom event that Playwright can listen to
    window.dispatchEvent(new CustomEvent('__recorder_event__', {
      detail: eventData
    }));
  }
  
  /**
   * Create event data object
   */
  function createEventData(type, event, target) {
    return {
      type: type,
      timestamp: Date.now(),
      page: capturePageContext(),
      target: captureElementInfo(target || event.target),
      event_details: {
        clientX: event.clientX,
        clientY: event.clientY,
        button: event.button,
        key: event.key,
        code: event.code,
        altKey: event.altKey,
        ctrlKey: event.ctrlKey,
        shiftKey: event.shiftKey,
        metaKey: event.metaKey
      }
    };
  }
  
  // Event handlers
  
  function handleClick(event) {
    const eventData = createEventData('click', event);
    sendEventToPython(eventData);
  }
  
  function handleDblClick(event) {
    const eventData = createEventData('dblclick', event);
    sendEventToPython(eventData);
  }
  
  function handleContextMenu(event) {
    const eventData = createEventData('contextmenu', event);
    sendEventToPython(eventData);
  }
  
  function handleInput(event) {
    const target = event.target;
    const eventData = createEventData('input', event);
    
    // Add input-specific data
    eventData.input_data = {
      value_length: target.value ? target.value.length : 0,
      value_type: target.type || 'text',
      is_password: target.type === 'password',
      is_sensitive: target.type === 'password' || 
                    target.autocomplete === 'cc-number' ||
                    target.name?.toLowerCase().includes('password') ||
                    target.name?.toLowerCase().includes('token')
    };
    
    sendEventToPython(eventData);
  }
  
  function handleChange(event) {
    const eventData = createEventData('change', event);
    sendEventToPython(eventData);
  }
  
  function handleSubmit(event) {
    const eventData = createEventData('submit', event, event.target);
    sendEventToPython(eventData);
  }
  
  function handleKeyDown(event) {
    // Only capture specific keys
    const captureKeys = ['Enter', 'Escape', 'Tab'];
    if (captureKeys.includes(event.key)) {
      const eventData = createEventData('keydown', event);
      sendEventToPython(eventData);
    }
  }
  
  // Register event listeners
  const eventTypes = [
    { type: 'click', handler: handleClick },
    { type: 'dblclick', handler: handleDblClick },
    { type: 'contextmenu', handler: handleContextMenu },
    { type: 'input', handler: handleInput },
    { type: 'change', handler: handleChange },
    { type: 'submit', handler: handleSubmit },
    { type: 'keydown', handler: handleKeyDown }
  ];
  
  eventTypes.forEach(({ type, handler }) => {
    document.addEventListener(type, handler, true);
  });
  
  console.log('[Recorder] Event capturer initialized');
  
})();
