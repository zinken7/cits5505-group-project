# Frontend Component Docs Quick Guide

Use `docs.html` to quickly learn how each UI component works.

## Where to Start

1. Open `frontend/docs.html` in your browser.
2. Scroll to the component you want (Accordion, Avatar, Badge, etc.).
3. Read the **Raw HTML** block.
4. Compare it with the **Preview** block.
5. Copy the HTML pattern into your page and adjust classes/content.

## How to Use a Component in Your Page

1. Add the same HTML structure shown in the docs.
2. Keep the correct `data-ui` attribute (for example: `data-ui="accordion"`).
3. Make sure your page loads the shared UI script (`components/ui.js`).
4. If needed, initialize components with `window.UI.init()` after the DOM is ready.

## Tips

- Start from the smallest example first, then add custom styles.
- If a component has a JS API (like breadcrumbs), check the script example in the same section.
- Use the docs page as the source of truth for expected markup.
