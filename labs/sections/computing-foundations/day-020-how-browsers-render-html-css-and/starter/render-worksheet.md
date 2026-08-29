# Render worksheet — Day 020

Open `examples/page/index.html` in your own web browser, and use the static
inspector (`bash examples/inspect_page.sh examples/page/index.html`) alongside
the browser's developer tools. Fill in every blank in your own words.

## 1. What is in the DOM (structure — HTML)

- Page title (from the `<title>` element): __________
- Number of elements the inspector reports: __________
- Number the browser Console reports for `document.querySelectorAll('*').length`: __________
- Do those two numbers match? Why or why not? __________
- List the element types the page contains: __________

## 2. What the CSS changes (presentation — CSS)

- The `<style>` block defines exactly one rule. Write it out: __________
- Which element does it target, and what two things does it change? __________
- If you deleted the `<style>` block, what would still work, and what would change? __________

## 3. What the button does (behavior — JavaScript)

- Read the button's `onclick` code in the source. In one sentence, what will it do? __________
- **Predict before clicking:** after you click the button, the paragraph's text will read: __________
- Now click it. Was your prediction correct? __________
- Did clicking add or remove any DOM elements, or only change existing text? __________

## 4. Trace the pipeline for this page

In one short paragraph, walk this specific page through the five steps and name
what each produces:

1. Parse HTML → __________
2. Parse CSS → __________
3. Build the render tree → __________
4. Layout → __________
5. Paint → __________

Your paragraph: __________
