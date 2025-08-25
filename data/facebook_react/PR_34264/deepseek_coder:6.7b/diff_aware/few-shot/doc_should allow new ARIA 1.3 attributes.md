markdown
# mountComponent Function Documentation

## Overview
This function is used to mount a component with ARIA attributes. It allows for testing of new ARIA 1.3 attributes such as `aria-braillelabel`, `aria-brailleroledescription`, `aria-colindextext` and `aria-rowindextext`.

## Usage
The function takes an object argument with the following keys:

### 'aria-braillelabel'
Used to set the Braille label text for a component. This is used by screen readers that support ARIA 1.3.

Example usage:
```javascript
await mountComponent({'aria-braillelabel': 'Braille label text'});
```

### 'aria-brailleroledescription'
Used to set the Braille role description for a component. This is used by screen readers that support ARIA 1.3.

Example usage:
```javascript
await mountComponent({'aria-brailleroledescription': 'Navigation menu'});
```

### 'aria-colindextext'
Used to set the column index text for a component. This is used by screen readers that support ARIA 1.3.

Example usage:
```javascript
await mountComponent({'aria-colindextext': 'Column A'});