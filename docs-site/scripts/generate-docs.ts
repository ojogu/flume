import { generateFiles } from 'fumadocs-openapi';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function generate() {
  const specPath = '../openapi.json';
  const outDir = 'content/docs/api-reference';

  console.log(`Generating API documentation from ${specPath}...`);

  try {
    await generateFiles({
      input: [specPath],
      output: outDir,
      per: 'operation',
      groupBy: 'tag',
    });
    console.log('✅ API documentation generated successfully.');
  } catch (err) {
    console.error('❌ Failed to generate API documentation:', err);
    process.exit(1);
  }
}

generate();
