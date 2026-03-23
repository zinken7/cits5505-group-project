# jQuery Component Usage Example

## Button Component

```js
export function PrimaryButton(text, onClick) {
  const $el = $("<button>")
    .addClass("bg-blue-500 text-white px-4 py-2 rounded-md")
    .text(text);

  if (onClick) {
    $el.on("click", onClick);
  }

  return $el;
}
```

---

## Usage

```js
PrimaryButton("Click me", () => {
  console.log("Button clicked");
}).appendTo("#container");
```

---

## Result

```html
<div id="container">
  <button class="bg-blue-500 text-white px-4 py-2 rounded-md">
    Click me
  </button>
</div>
```

---

## Pattern

This pattern can be applied to all other UI components (e.g., cards, modals, inputs).

---

## Workflow

1. Create a component function that returns a jQuery element.
2. Attach behavior (e.g., event handlers) inside the component.
3. Use the component function to generate and insert elements into the DOM.

---

## Notes

* This approach helps maintain **UI consistency at the structure and styling level**.
* It allows each team member to build **reusable UI components independently**.