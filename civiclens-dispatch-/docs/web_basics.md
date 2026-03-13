# Web Basics - HTML, CSS, JavaScript (Day 22)

## The Three Languages of the Web

Every web page is built with three technologies:

### 1. HTML (Structure)
**Purpose:** Defines WHAT content exists

**Example:**
```html
<h1>Title</h1>
<p>Paragraph of text</p>
<button>Click me</button>
```

**Think of it as:** The blueprint or skeleton

### 2. CSS (Style)
**Purpose:** Defines HOW content looks

**Example:**
```css
h1 {
    color: blue;
    font-size: 32px;
}
```

**Think of it as:** The paint and decorations

### 3. JavaScript (Behavior)
**Purpose:** Defines what content DOES

**Example:**
```javascript
button.addEventListener('click', function() {
    alert('Clicked!');
});
```

**Think of it as:** The actions and logic

---

## HTML Deep Dive

### Basic Structure
```html
<!DOCTYPE html>         <!-- Document type declaration -->
<html>                  <!-- Root element -->
  <head>                <!-- Metadata section -->
    <title>Page Title</title>
  </head>
  <body>                <!-- Visible content -->
    <h1>Hello!</h1>
  </body>
</html>
```

### Common HTML Tags

| Tag | Purpose | Example |
|-----|---------|---------|
| `<h1>` to `<h6>` | Headings | `<h1>Main Title</h1>` |
| `<p>` | Paragraph | `<p>Text here</p>` |
| `<div>` | Container (block) | `<div>Content</div>` |
| `<span>` | Container (inline) | `<span>Text</span>` |
| `<button>` | Button | `<button>Click</button>` |
| `<input>` | Input field | `<input type="text">` |
| `<form>` | Form container | `<form>...</form>` |
| `<table>` | Data table | `<table>...</table>` |
| `<img>` | Image | `<img src="photo.jpg">` |
| `<a>` | Link | `<a href="page.html">Link</a>` |

### HTML Attributes

Attributes provide additional information about elements:
```html
<input 
    type="text"           <!-- Type of input -->
    id="username"         <!-- Unique identifier -->
    name="username"       <!-- Form field name -->
    placeholder="Enter name"  <!-- Hint text -->
    required              <!-- Must be filled in -->
/>
```

### Forms

Forms collect user input:
```html
<form id="myForm">
    <label for="email">Email:</label>
    <input type="email" id="email" name="email" required>
    
    <button type="submit">Submit</button>
</form>
```

**Important attributes:**
- `id` - Unique identifier for JavaScript
- `name` - Field name when submitting data
- `required` - Makes field mandatory
- `type` - Defines input type (text, email, file, etc.)

---

## CSS Deep Dive

### Three Ways to Add CSS

**1. Inline (directly on element):**
```html
<p style="color: red;">Red text</p>
```

**2. Internal (in `<style>` tag):**
```html
<style>
    p { color: red; }
</style>
```

**3. External (separate .css file):**
```html
<link rel="stylesheet" href="styles.css">
```

**Best practice:** Use external CSS files for larger projects.

### CSS Selectors

**Tag selector:**
```css
p { color: black; }        /* All <p> tags */
```

**Class selector:**
```css
.warning { color: red; }   /* All elements with class="warning" */
```

**ID selector:**
```css
#header { color: blue; }   /* Element with id="header" */
```

**Descendant selector:**
```css
div p { color: green; }    /* All <p> inside <div> */
```

### The Box Model

Every HTML element is a box with:
```
┌─────────────────────────────┐
│         Margin              │ ← Space outside element
│  ┌──────────────────────┐  │
│  │      Border           │  │ ← Border around element
│  │  ┌────────────────┐  │  │
│  │  │   Padding      │  │  │ ← Space inside element
│  │  │  ┌──────────┐  │  │  │
│  │  │  │ Content  │  │  │  │ ← Actual content
│  │  │  └──────────┘  │  │  │
│  │  └────────────────┘  │  │
│  └──────────────────────┘  │
└─────────────────────────────┘
```

**CSS for box model:**
```css
div {
    width: 200px;           /* Content width */
    padding: 20px;          /* Space inside */
    border: 2px solid black;  /* Border */
    margin: 10px;           /* Space outside */
}
```

### Common CSS Properties

**Text:**
- `color` - Text color
- `font-size` - Size of text
- `font-weight` - Bold, normal, etc.
- `text-align` - left, center, right

**Box:**
- `width` / `height` - Size
- `padding` - Inside spacing
- `margin` - Outside spacing
- `border` - Border around element

**Background:**
- `background-color` - Background color
- `background-image` - Background image

**Layout:**
- `display` - How element is displayed (block, inline, flex)
- `position` - Positioning method (static, relative, absolute)

---

## JavaScript Deep Dive

### Variables
```javascript
let x = 10;        // Can be changed
const y = 20;      // Cannot be changed
var z = 30;        // Old way (don't use)
```

### Functions
```javascript
// Function declaration
function add(a, b) {
    return a + b;
}

// Arrow function (modern way)
const multiply = (a, b) => {
    return a * b;
};
```

### Working with the DOM

**DOM** = **D**ocument **O**bject **M**odel
- JavaScript's representation of the HTML page
- Lets you find, modify, and create HTML elements

**Finding elements:**
```javascript
// By ID
const element = document.getElementById('myId');

// By class name
const elements = document.getElementsByClassName('myClass');

// By CSS selector (most flexible)
const element = document.querySelector('.myClass');
const elements = document.querySelectorAll('p');
```

**Modifying elements:**
```javascript
// Change text content
element.textContent = "New text";

// Change HTML content
element.innerHTML = "<strong>Bold text</strong>";

// Change CSS
element.style.color = "red";

// Add CSS class
element.classList.add('active');

// Remove CSS class
element.classList.remove('active');
```

**Creating elements:**
```javascript
// Create new element
const newDiv = document.createElement('div');

// Set its content
newDiv.textContent = "Hello!";

// Add it to page
document.body.appendChild(newDiv);
```

### Events

Events are things that happen:
- User clicks button
- User types in input
- Page finishes loading
- Mouse moves over element

**Listening for events:**
```javascript
button.addEventListener('click', function() {
    console.log('Button clicked!');
});

input.addEventListener('input', function(event) {
    console.log('User typed:', event.target.value);
});

form.addEventListener('submit', function(event) {
    event.preventDefault();  // Stop form from submitting normally
    console.log('Form submitted!');
});
```

### Common Event Types

- `click` - Element was clicked
- `submit` - Form was submitted
- `input` - Input value changed
- `change` - Select/checkbox changed
- `load` - Page finished loading
- `mouseover` - Mouse moved over element

---

## How This Applies to CivicLens

### Current Prototype (vanilla-prototype.html)

**What it demonstrates:**

1. **Form for submitting incidents**
   - Text inputs for description/location
   - Dropdown for source
   - File inputs for audio/image
   - Submit button

2. **Table displaying incidents**
   - Shows all incident fields
   - Color-coded severity badges
   - Clickable rows

3. **JavaScript interactivity**
   - Form submission without page reload
   - Dynamic row addition to table
   - Success message display
   - Console logging for debugging

### What We'll Improve with React (Days 23+)

**Problems with current approach:**
- ❌ Manually creating HTML strings (error-prone)
- ❌ No separation between data and display
- ❌ Hard to manage complex state
- ❌ Lots of repetitive code

**React will give us:**
- ✅ Components (reusable UI pieces)
- ✅ Automatic re-rendering when data changes
- ✅ Clean separation of concerns
- ✅ Much less code for same functionality

---

## Key Takeaways

1. **HTML defines structure** - What elements exist
2. **CSS defines presentation** - How elements look
3. **JavaScript defines behavior** - What elements do

4. **The DOM is JavaScript's view of HTML** - You can manipulate it

5. **Event listeners make pages interactive** - Respond to user actions

6. **Forms collect user input** - Foundation of web applications

7. **This is how ALL web apps work** - Even complex frameworks like React use these fundamentals underneath

---

## Debugging Tips

### Browser Developer Tools

**How to open:**
- **Mac**: Cmd + Option + I
- **Windows**: F12 or Ctrl + Shift + I

**Useful tabs:**
- **Elements**: See HTML structure and CSS
- **Console**: See JavaScript logs and errors
- **Network**: See API requests (useful later)

### Common Issues

**"Nothing happens when I click"**
- Check browser console for JavaScript errors
- Verify event listener is attached
- Check element IDs match

**"Styles don't apply"**
- Check CSS selector spelling
- Check if class/ID exists in HTML
- Use browser inspector to see applied styles

**"Form submits but page reloads"**
- Add `event.preventDefault()` in submit handler

---

*Day 22 complete! Web fundamentals learned!* 🌐