# Web Development Cheat Sheet

## HTML Quick Reference

### Structure
```html
<!DOCTYPE html>
<html>
  <head>
    <title>Page Title</title>
    <meta charset="UTF-8">
  </head>
  <body>
    <!-- Content here -->
  </body>
</html>
```

### Common Tags
```html
<!-- Text -->
<h1>Heading 1</h1>
<p>Paragraph</p>
<span>Inline text</span>

<!-- Containers -->
<div>Block container</div>
<section>Semantic section</section>

<!-- Form Elements -->
<form>
    <label for="name">Name:</label>
    <input type="text" id="name" name="name" required>
    <textarea rows="4"></textarea>
    <select>
        <option value="1">Option 1</option>
    </select>
    <button type="submit">Submit</button>
</form>

<!-- Lists -->
<ul>                    <!-- Unordered (bullets) -->
    <li>Item 1</li>
</ul>
<ol>                    <!-- Ordered (numbers) -->
    <li>First</li>
</ol>

<!-- Table -->
<table>
    <thead>
        <tr><th>Header</th></tr>
    </thead>
    <tbody>
        <tr><td>Data</td></tr>
    </tbody>
</table>
```

---

## CSS Quick Reference

### Selectors
```css
/* Tag */
p { }

/* Class */
.className { }

/* ID */
#idName { }

/* Descendant */
div p { }

/* Multiple */
h1, h2, h3 { }
```

### Common Properties
```css
/* Text */
color: #333;
font-size: 16px;
font-weight: bold;
text-align: center;

/* Box */
width: 100px;
height: 100px;
padding: 10px;
margin: 20px;
border: 1px solid black;

/* Background */
background-color: blue;
background-image: url('image.jpg');

/* Display */
display: block;        /* Takes full width */
display: inline;       /* Stays in line */
display: none;         /* Hidden */
display: flex;         /* Flexbox layout */
```

### Colors
```css
/* Named */
color: red;

/* Hex */
color: #3498db;

/* RGB */
color: rgb(52, 152, 219);

/* RGBA (with transparency) */
color: rgba(52, 152, 219, 0.5);
```

---

## JavaScript Quick Reference

### Variables
```javascript
let x = 10;           // Can change
const y = 20;         // Cannot change
```

### Functions
```javascript
// Regular function
function add(a, b) {
    return a + b;
}

// Arrow function
const multiply = (a, b) => a * b;
```

### DOM Manipulation
```javascript
// Find elements
document.getElementById('id')
document.querySelector('.class')
document.querySelectorAll('p')

// Modify elements
element.textContent = "New text"
element.innerHTML = "<b>HTML</b>"
element.style.color = "red"

// Classes
element.classList.add('active')
element.classList.remove('active')
element.classList.toggle('active')

// Create elements
const div = document.createElement('div')
div.textContent = "Hello"
parent.appendChild(div)
```

### Events
```javascript
// Click
button.addEventListener('click', () => {
    console.log('Clicked!');
});

// Form submit
form.addEventListener('submit', (event) => {
    event.preventDefault();
    // Handle form data
});

// Input change
input.addEventListener('input', (event) => {
    console.log(event.target.value);
});
```

### Arrays
```javascript
const arr = [1, 2, 3];

// Add item
arr.push(4);

// Loop
arr.forEach(item => console.log(item));

// Map (transform)
const doubled = arr.map(x => x * 2);

// Filter
const evens = arr.filter(x => x % 2 === 0);
```

### Objects
```javascript
const person = {
    name: "John",
    age: 30,
    greet: function() {
        return "Hello " + this.name;
    }
};

// Access properties
console.log(person.name);
console.log(person['age']);
```

### Async/Await (for API calls)
```javascript
// Fetch data from API
async function getIncidents() {
    const response = await fetch('http://localhost:8000/incidents');
    const data = await response.json();
    console.log(data);
}
```

---

## Browser DevTools

### Opening DevTools
- **Mac**: Cmd + Option + I
- **Windows/Linux**: F12 or Ctrl + Shift + I

### Useful Tabs
- **Elements**: Inspect HTML and CSS
- **Console**: Run JavaScript, see logs and errors
- **Network**: See API requests/responses
- **Application**: View localStorage, cookies

### Console Commands
```javascript
console.log("Message")          // Print message
console.error("Error!")         // Print error
console.table(arrayOfObjects)   // Display table
console.clear()                 // Clear console
```

---

## Common Patterns

### Show/Hide Element
```javascript
// Hide
element.style.display = 'none';

// Show
element.style.display = 'block';

// Toggle with class
element.classList.toggle('hidden');
```

### Form Data
```javascript
form.addEventListener('submit', (event) => {
    event.preventDefault();
    
    const formData = new FormData(form);
    const name = formData.get('name');
    
    console.log('Name:', name);
});
```

### Update Table
```javascript
// Add row to table
const row = document.createElement('tr');
row.innerHTML = `
    <td>${data.id}</td>
    <td>${data.name}</td>
`;
tableBody.appendChild(row);
```

---

*Quick reference for Days 22-30* 📖