markdown
# mountComponent Function Documentation

## Overview
This function is used to mount a component with ARIA attributes. The purpose of this function is to test various ARIA 1.3 attributes such as `aria-braillelabel`, `aria-brailleroledescription`, `aria-colindextext` and `aria-rowindextext`.

## Usage
The function takes an object argument where each key-value pair represents a specific ARIA attribute to be tested. The keys are the names of the attributes (e.g., 'aria-braillelabel', 'aria-brailleroledescription') and their corresponding values represent the expected value for that attribute. 

## Examples
1. Testing `aria-braillelabel`:
```javascript
await mountComponent({'aria-braillelabel': 'Braille label text'});
```
2. Testing `aria-brailleroledescription`: