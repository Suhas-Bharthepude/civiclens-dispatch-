📅 Day 19 – Environment Variables & Configuration

🎯 What You'll Learn Today

Using environment variables for secrets and configuration


🤔 Why This Matters

Database passwords, API keys, and other secrets must never be hardcoded in your code. If you accidentally push secrets to GitHub, anyone can see them and access your database or services!


💡 How It Applies to CivicLens

Your .env file stores:
* PostgreSQL connection details (username, password, database)
* API keys (maps, future AI services)
* Debug settings
* Upload directories


🧠 Core Concepts Explained (Complete Beginner Level)

What is an Environment Variable?
Think of environment variables like sticky notes your program can read when it starts up.
Bad way (hardcoded):

password = "secret123"  # 😱 NEVER DO THIS!
Good way (environment variable):

password = os.getenv("PASSWORD")  # ✅ Reads from .env file

### What is a `.env` File?

A `.env` file is a simple text file that stores configuration in `KEY=VALUE` format:
```
DATABASE_URL=postgresql://user:password@localhost/mydb
API_KEY=abc123xyz
DEBUG=True
Important: The .env file should be in your .gitignore so it's never committed to GitHub!
How Does It Work?
1. You create a .env file locally
2. Python reads it using python-dotenv
3. Your code accesses values with os.getenv()
4. Each developer/environment has their own .env file






📅 Day 20 – Testing Basics with pytest
🎯 What You'll Learn Today
Unit tests and simple API tests
🤔 Why This Matters
Tests show professionalism and help refactor safely. They catch bugs before users do!
💡 How It Applies to CivicLens
Testing incident creation & listing ensures your API works correctly

🧠 Core Concepts Explained (Complete Beginner Level)
What is Testing?
Simple analogy: Testing is like a quality control checklist.
Imagine you're building a toy car:

✅ Do the wheels spin?
✅ Does the door open?
✅ Does it roll straight?

In programming, automated tests are like having a robot that checks your code works correctly every time you make changes.
Why Write Tests?
Without tests:
python# You make a change to your code
# You manually test by:
# 1. Starting the server
# 2. Opening browser
# 3. Clicking through your app
# 4. Checking if everything still works
# This takes 10+ minutes every time!
With tests:
python# You make a change
# Run: pytest
# All tests run in 5 seconds
# ✅ Everything works!
What is pytest?
pytest is a Python testing framework. Think of it as a tool that:

Finds all your test files
Runs each test function
Reports which tests pass ✅ or fail ❌

Types of Tests

Unit Tests: Test one small piece of code in isolation

Example: "Does the add(2, 3) function return 5?"


Integration Tests: Test multiple pieces working together

Example: "Can I create an incident and then retrieve it?"


API Tests: Test your endpoints work correctly

Example: "Does POST /incidents return status code 201?"



Test Structure (AAA Pattern)
Every test follows this pattern:
pythondef test_something():
    # ARRANGE - Set up test data
    incident_data = {"description": "Test", "location": "123 St", "source": "test"}
    
    # ACT - Do the thing you're testing
    response = create_incident(incident_data)
    
    # ASSERT - Check if it worked correctly
    assert response.status_code == 201  # Check status code is 201 (Created)








📅 Day 21 – Buffer/Cleanup & Mini Review
🎯 What You'll Learn Today
Review concepts so far and prepare for the frontend phase
🤔 Why This Matters
Consolidation prevents gaps later. Clean code now means less confusion when we add React.
💡 How It Applies to CivicLens
You'll be ready to add the frontend (dispatcher dashboard and citizen form)

🧠 What is a "Buffer Day"?
Think of it like this:

You've been learning and building for 20 days straight
New concepts are stacking up
Code is accumulating
Now we pause, consolidate, and clean

It's like:

Organizing your desk before starting a new project
Reviewing your notes before an exam
Cleaning your kitchen before cooking a big meal

What we'll do:

✅ Review what we've built
🧹 Clean up code (remove dead code, improve comments)
📝 Update documentation
🔍 Refactor for clarity
🎯 Prepare for frontend development




📅 Day 22 – Web Basics: HTML/CSS/JS

🎯 What You'll Learn Today
Structure of web pages, styling, and scripts
🤔 Why This Matters
React builds on these fundamentals. Understanding HTML/CSS/JS makes React much easier.
💡 How It Applies to CivicLens
Your dispatcher dashboard and citizen form will be built with these technologies

🧠 Core Concepts Explained (Complete Beginner Level)
What is a Web Page?
A web page is like a document made of three layers:
1. HTML (Structure) - The skeleton/bones
    * Defines what content exists
    * Like the blueprint of a house
2. CSS (Style) - The skin/appearance
    * Defines how content looks
    * Like paint, furniture, decorations
3. JavaScript (Behavior) - The muscles/actions
    * Defines what content does
    * Like doors that open, lights that turn on



Analogy:
HTML = The frame of a car (chassis, seats, steering wheel)
CSS = The paint job and interior design
JavaScript = The engine and electronics that make it work
How Do They Work Together?
html<!-- HTML: Structure -->
<button>Click Me</button>

/* CSS: Style */
button {
    background-color: blue;
    color: white;
}

// JavaScript: Behavior
button.addEventListener('click', function() {
    alert('Button clicked!');
});
Result: A blue button with white text that shows an alert when clicked.

📖 HTML Fundamentals
What is HTML?
HTML = HyperText Markup Language
It's a way to tell the browser: "Put text here, an image there, a button below that."
HTML Tags
HTML uses tags (like labels) to mark what each piece of content is:
html<tagname>Content goes here</tagname>
  ↑                          ↑
Opening tag              Closing tag
Common tags:

<h1> to <h6> - Headings (h1 is biggest)
<p> - Paragraph
<div> - Generic container (division)
<span> - Inline container
<button> - Clickable button
<input> - Text input field
<img> - Image
<a> - Link (anchor)

Example:
html<h1>Emergency Incidents</h1>
<p>This is a paragraph of text.</p>
<button>Submit Report</button>
HTML Document Structure
Every HTML page has this basic structure:
html<!DOCTYPE html>           <!-- Tells browser this is HTML5 -->
<html>                    <!-- Root element - everything goes inside -->
  <head>                  <!-- Metadata - not visible on page -->
    <title>Page Title</title>
  </head>
  <body>                  <!-- Visible content goes here -->
    <h1>Hello World</h1>
  </body>
</html>

🎨 CSS Fundamentals
What is CSS?
CSS = Cascading Style Sheets
It tells the browser: "Make this text blue, that button large, this box centered."
CSS Syntax
cssselector {
    property: value;
}
Example:
cssh1 {
    color: blue;        /* Make heading blue */
    font-size: 32px;    /* Make it 32 pixels tall */
}
CSS Selectors
Select by tag:
cssp { color: black; }     /* All <p> tags */
Select by class:
css.warning { color: red; }   /* All elements with class="warning" */
Select by ID:
css#header { background: gray; }  /* Element with id="header" */
Common CSS Properties

color - Text color
background-color - Background color
font-size - Size of text
margin - Space outside element
padding - Space inside element
border - Border around element
width / height - Size of element


💻 JavaScript Fundamentals
What is JavaScript?
JavaScript makes web pages interactive and dynamic.
Without JavaScript: Static page (like a PDF)
With JavaScript: Interactive app (like Gmail)
JavaScript Basics
Variables:
javascriptlet name = "John";      // Can change
const age = 25;         // Cannot change
Functions:
javascriptfunction greet(name) {
    return "Hello " + name;
}

console.log(greet("Alice"));  // Prints: Hello Alice
Interacting with HTML:
javascript// Find an element by ID
let button = document.getElementById('myButton');

// Do something when clicked
button.addEventListener('click', function() {
    alert('Button was clicked!');
});




