function escapeHtml(text) {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function renderInline(text) {
  let value = escapeHtml(text);
  value = value.replace(/`([^`]+)`/g, "<code>$1</code>");
  value = value.replace(/\[([^\]]+)\]\(([^)\s]+)\)/g, '<a href="$2">$1</a>');
  value = value.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  value = value.replace(/(^|[\s(])\*([^*\n]+)\*/g, "$1<em>$2</em>");
  return value;
}

function startsBlock(line) {
  if (/^(-{3,}|\*{3,})$/.test(line.trim())) {
    return true;
  }
  return /^(```|#{1,6}\s|>\s?|\||[-*]\s|\d+\.\s)/.test(line);
}

function splitRow(line) {
  return line.trim().replace(/^\|/, "").replace(/\|$/, "").split("|").map(function (cell) {
    return cell.trim();
  });
}

function renderTable(rows) {
  const parsed = rows.map(splitRow);
  let start = 0;
  let head = "";
  if (rows.length > 1 && /^\|?\s*:?-{3,}/.test(rows[1].trim())) {
    head = "<thead><tr>" + parsed[0].map(function (cell) {
      return "<th>" + renderInline(cell) + "</th>";
    }).join("") + "</tr></thead>";
    start = 2;
  }
  const body = parsed.slice(start).map(function (cells) {
    return "<tr>" + cells.map(function (cell) {
      return "<td>" + renderInline(cell) + "</td>";
    }).join("") + "</tr>";
  }).join("");
  return "<table>" + head + "<tbody>" + body + "</tbody></table>";
}

function renderList(lines, ordered) {
  const tag = ordered ? "ol" : "ul";
  const pattern = ordered ? /^\d+\.\s+/ : /^[-*]\s+/;
  const items = lines.map(function (line) {
    return "<li>" + renderInline(line.replace(pattern, "")) + "</li>";
  });
  return "<" + tag + ">" + items.join("") + "</" + tag + ">";
}

function renderMarkdown(source) {
  const lines = source.replace(/\r\n/g, "\n").replace(/\r/g, "\n").split("\n");
  const blocks = [];
  let index = 0;
  if (lines[0] === "---") {
    const end = lines.indexOf("---", 1);
    if (end !== -1) {
      blocks.push("<pre class=\"meta\">" + escapeHtml(lines.slice(1, end).join("\n")) + "</pre>");
      index = end + 1;
    }
  }
  while (index < lines.length) {
    const line = lines[index];
    if (line.trim() === "") {
      index += 1;
      continue;
    }
    if (line.startsWith("```")) {
      const code = [];
      index += 1;
      while (index < lines.length && !lines[index].startsWith("```")) {
        code.push(lines[index]);
        index += 1;
      }
      index += 1;
      blocks.push("<pre><code>" + escapeHtml(code.join("\n")) + "</code></pre>");
      continue;
    }
    if (/^#{1,6}\s/.test(line)) {
      const level = line.match(/^#+/)[0].length;
      const text = renderInline(line.replace(/^#+\s+/, ""));
      blocks.push("<h" + level + ">" + text + "</h" + level + ">");
      index += 1;
      continue;
    }
    if (/^(-{3,}|\*{3,})$/.test(line.trim())) {
      blocks.push("<hr>");
      index += 1;
      continue;
    }
    if (line.startsWith("|")) {
      const table = [];
      while (index < lines.length && lines[index].startsWith("|")) {
        table.push(lines[index]);
        index += 1;
      }
      blocks.push(renderTable(table));
      continue;
    }
    if (line.startsWith(">")) {
      const quote = [];
      while (index < lines.length && (lines[index].startsWith(">") || (lines[index].trim() === "" && lines[index + 1] && lines[index + 1].startsWith(">")))) {
        quote.push(lines[index].replace(/^>\s?/, ""));
        index += 1;
      }
      blocks.push("<blockquote>" + renderMarkdown(quote.join("\n")) + "</blockquote>");
      continue;
    }
    if (/^[-*]\s+/.test(line)) {
      const items = [];
      while (index < lines.length && /^[-*]\s+/.test(lines[index])) {
        items.push(lines[index]);
        index += 1;
      }
      blocks.push(renderList(items, false));
      continue;
    }
    if (/^\d+\.\s+/.test(line)) {
      const items = [];
      while (index < lines.length && /^\d+\.\s+/.test(lines[index])) {
        items.push(lines[index]);
        index += 1;
      }
      blocks.push(renderList(items, true));
      continue;
    }
    const paragraph = [];
    while (index < lines.length && lines[index].trim() !== "" && !startsBlock(lines[index])) {
      paragraph.push(lines[index]);
      index += 1;
    }
    let html = "";
    paragraph.forEach(function (part, partIndex) {
      const broken = /  $/.test(part);
      html += renderInline(part.replace(/  $/, ""));
      if (partIndex < paragraph.length - 1) {
        html += broken ? "<br>" : " ";
      }
    });
    blocks.push("<p>" + html + "</p>");
  }
  return blocks.join("\n");
}
