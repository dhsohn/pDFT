document.addEventListener("DOMContentLoaded", () => {
  if (typeof mermaid === "undefined") {
    return;
  }
  mermaid.initialize({ startOnLoad: false });
  const blocks = document.querySelectorAll("pre code.language-mermaid");
  blocks.forEach((block) => {
    const pre = block.parentElement;
    const parent = pre.parentElement;
    const container = document.createElement("div");
    container.className = "mermaid";
    container.textContent = block.textContent;
    parent.replaceChild(container, pre);
  });
  mermaid.run({ querySelector: ".mermaid" });
});
