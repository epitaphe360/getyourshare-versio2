#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

let filesModified = 0;
let consolesRemoved = 0;

function removeConsoleLogs(filePath) {
  const content = fs.readFileSync(filePath, 'utf8');

  // Count console.log occurrences before
  const beforeCount = (content.match(/console\.log\(/g) || []).length;

  if (beforeCount === 0) {
    return;
  }

  // Remove console.log statements (various patterns)
  let newContent = content;

  // Pattern 1: Simple console.log('...')
  newContent = newContent.replace(/^\s*console\.log\([^;]*\);?\s*$/gm, '');

  // Pattern 2: console.log at end of line with semicolon
  newContent = newContent.replace(/\s*console\.log\([^)]*\);/g, '');

  // Pattern 3: console.log without semicolon
  newContent = newContent.replace(/\s*console\.log\([^)]*\)(?!\))/g, '');

  // Clean up multiple blank lines (more than 2 consecutive)
  newContent = newContent.replace(/\n\n\n+/g, '\n\n');

  // Count after
  const afterCount = (newContent.match(/console\.log\(/g) || []).length;
  const removed = beforeCount - afterCount;

  if (removed > 0) {
    fs.writeFileSync(filePath, newContent, 'utf8');
    filesModified++;
    consolesRemoved += removed;
    console.log(`✓ ${filePath}: Removed ${removed} console.log(s)`);
  }
}

function processDirectory(dir, extensions = ['.js', '.jsx']) {
  const entries = fs.readdirSync(dir, { withFileTypes: true });

  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);

    // Skip node_modules, build, dist directories
    if (entry.isDirectory()) {
      if (['node_modules', 'build', 'dist', '.git'].includes(entry.name)) {
        continue;
      }
      processDirectory(fullPath, extensions);
    } else if (entry.isFile()) {
      const ext = path.extname(entry.name);
      if (extensions.includes(ext)) {
        removeConsoleLogs(fullPath);
      }
    }
  }
}

// Start processing
const srcDir = path.join(__dirname, 'src');
console.log('Starting console.log removal...\n');
processDirectory(srcDir);
console.log(`\n✅ Done! Modified ${filesModified} files, removed ${consolesRemoved} console.log statements.`);
