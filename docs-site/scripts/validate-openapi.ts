import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const SPEC_PATH = path.resolve(__dirname, '../../openapi.json');

async function validate() {
  console.log('--- Flume OpenAPI Validation ---');
  
  if (!fs.existsSync(SPEC_PATH)) {
    console.error(`❌ Error: openapi.json not found at ${SPEC_PATH}`);
    process.exit(1);
  }

  const content = fs.readFileSync(SPEC_PATH, 'utf-8');
  if (!content || content.trim() === '') {
    console.error('❌ Error: openapi.json is empty');
    process.exit(1);
  }

  let spec;
  try {
    spec = JSON.parse(content);
  } catch (e) {
    console.error('❌ Error: openapi.json is not valid JSON');
    process.exit(1);
  }

  if (!spec.paths || Object.keys(spec.paths).length === 0) {
    console.warn('⚠️ Warning: Spec contains no routes. Scaffolding will proceed but reference will be empty.');
  }

  const paths = Object.keys(spec.paths || {});
  const internalRoutes = paths.filter(p => p.startsWith('/v1/internal') || p.toLowerCase().includes('internal'));

  if (internalRoutes.length > 0) {
    console.error('❌ FATAL: Internal routes leaked into public API spec!');
    internalRoutes.forEach(p => console.error(`  - ${p}`));
    console.error('\nFix the backend upstream boundary before proceeding.');
    process.exit(1);
  }

  const tags = new Set<string>();
  paths.forEach(p => {
    const methods = Object.keys(spec.paths[p]);
    methods.forEach(m => {
      const op = spec.paths[p][m];
      if (op.tags) op.tags.forEach((t: string) => tags.add(t));
    });
  });

  console.log(`✅ Validation Passed:`);
  console.log(`  - Endpoints: ${paths.length}`);
  console.log(`  - Groups (Tags): ${Array.from(tags).join(', ') || 'None'}`);
  console.log(`  - Internal Leak Check: 0 internal routes found.`);
  console.log('--------------------------------\n');
}

validate().catch(err => {
  console.error(err);
  process.exit(1);
});
