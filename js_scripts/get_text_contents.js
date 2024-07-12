// Function to get the elements based on the varying part of the XPath
function getElements(xpathPattern, startIndex, endIndex) {
  const elements = [];
  for (let i = startIndex; i <= endIndex; i++) {
    const xpath = xpathPattern.replace("element", i);
    const element = document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
    if (element) {
      elements.push(element);
    }
  }
  return elements;
}

// Example usage
const xpathPattern = "/html/body/";
const startIndex = 1; // Adjust the start index according to your needs
const endIndex = 1000; // Adjust the end index according to your needs

const elements = getElements(xpathPattern, startIndex, endIndex);

// Extract text content and display all in a single line
const texts = elements.map(element => element.textContent.trim());
const singleLineText = texts.join(" ");
console.log(singleLineText);
