---
name: web-accessibility-a11y
description: Implement WCAG 2.2 AA compliant web accessibility across any frontend stack. Covers accessible HTML semantics, keyboard navigation, focus management, color contrast, ARIA landmarks, form accessibility, and screen reader UX.
---

# Web Accessibility (A11Y) - WCAG 2.2 Level AA Guide

A comprehensive, stack-agnostic engineering guide to building accessible, inclusive web applications adhering strictly to the W3C Web Content Accessibility Guidelines (WCAG) 2.2 Level AA standard.

## 1. Semantic HTML Foundation

The first rule of accessibility: **Use native HTML elements whenever possible.** Native elements have built-in keyboard navigation, focus handling, and assistive technology roles.

- Use `<main>` for primary page content (one per page).
- Use `<header>`, `<nav>`, `<aside>`, and `<footer>` for landmark regions.
- Use `<h1>` through `<h6>` in logical, strictly sequential order without skipping heading levels (e.g. do not jump from `<h2>` directly to `<h4>`).
- Use `<button>` for actions that trigger changes on the current page; use `<a>` with a valid `href` for navigation between URLs. Never use `<div onclick="...">` or `<a href="#">` as a pseudo-button.
- Use `<fieldset>` and `<legend>` to group related form controls (such as radio groups and checkbox lists).

## 2. Keyboard Navigation & Focus Management

Every interactive feature must be fully usable via keyboard alone (Tab, Shift+Tab, Enter, Space, Arrow keys, Escape).

- **Focus Rings**: Never remove the focus ring (`outline: none` without replacement is a critical accessibility failure).
  ```css
  :focus-visible {
    outline: 2px solid var(--focus-ring, #059669);
    outline-offset: 2px;
  }
  ```
- **Skip Links**: Include a hidden skip link as the very first element inside `<body>`:
  ```html
  <a href="#main-content" class="skip-to-content">Aller au contenu principal</a>
  ```
  ```css
  .skip-to-content {
    position: absolute;
    top: -100px;
    left: 1rem;
    background: #0f172a;
    color: #ffffff;
    padding: 0.5rem 1rem;
    z-index: 9999;
    border-radius: 4px;
    transition: top 150ms ease;
  }
  .skip-to-content:focus {
    top: 1rem;
  }
  ```
- **Modal Dialogs & Drawers**:
  - Trap keyboard focus inside the open dialog (Tab wraps from last element back to first).
  - Pressing `Escape` must immediately close the modal and return focus to the trigger button.
  - Set `aria-modal="true"` and `role="dialog"` on the modal container.
- **Dropdowns & Menus**:
  - Support `Escape` to close the menu.
  - Support `ArrowUp` and `ArrowDown` to traverse menu items.

## 3. Color Contrast & Visual Perception

- **Text Contrast**:
  - Regular text (< 18pt or < 14pt bold): Minimum contrast ratio of **4.5:1** against the background.
  - Large text (>= 18pt or >= 14pt bold): Minimum contrast ratio of **3:1**.
- **UI Components & Icons**:
  - Form borders, interactive icons, and focus indicators must achieve at least **3:1** contrast ratio against adjacent colors.
- **Color Independence**:
  - Never convey critical state using color alone. Pair color cues with explicit text, icons, or badges (e.g. an error must show a warning icon and error text, not merely turn the input border red).

## 4. Accessible Forms & Form Validation

- **Explicit Labeling**: Every form control must have an associated `<label>` using the `for` attribute matching the input's `id`:
  ```html
  <label for="user-email" class="form-label">Adresse e-mail</label>
  <input type="email" id="user-email" name="email" aria-describedby="email-hint" required>
  <span id="email-hint" class="form-text">Nous ne partagerons jamais votre adresse.</span>
  ```
- **Error Feedback**:
  - Mark invalid fields with `aria-invalid="true"`.
  - Link error messages via `aria-describedby="field-id-error"`.
  - Place focus on the first invalid field or summary alert upon form submission failure.
- **Autocomplete Attributes**: Include standard `autocomplete` tokens (`email`, `current-password`, `new-password`, `tel`, `name`, `address-line1`) on sensitive input fields to assist cognitive accessibility and password managers.

## 5. Media, Images & Icons

- **Informative Images**: Must have descriptive, concise `alt` text explaining the content and purpose.
- **Decorative Images**: Must use empty `alt=""` or `aria-hidden="true"` so screen readers ignore them.
- **Interactive SVG Icons**:
  - If the button has no visible text: add `aria-label="Description de l'action"` to the `<button>` and `aria-hidden="true"` on the `<svg>`.
  - If the button has visible text: hide the SVG icon with `aria-hidden="true"`.

## 6. Motion & Cognitive Accessibility

- Support reduced motion:
  ```css
  @media (prefers-reduced-motion: reduce) {
    *, ::before, ::after {
      animation-duration: 0.01ms !important;
      animation-iteration-count: 1 !important;
      transition-duration: 0.01ms !important;
      scroll-behavior: auto !important;
    }
  }
  ```
- Provide adequate touch targets on touch devices: Minimum **44px by 44px** for buttons, links, and form controls.

## 7. A11Y Audit Checklist

1. Can the entire page be operated using only Tab, Shift+Tab, Enter, Space, and Escape?
2. Is the focus indicator clearly visible on every single interactive element?
3. Do all images have either descriptive `alt` text or `alt=""`?
4. Do all input fields have programmatic labels via `for`/`id`?
5. Does text meet the 4.5:1 contrast requirement in both normal and dark modes?
6. Can the page be zoomed to 200% without breaking layouts or creating horizontal scrollbars?
