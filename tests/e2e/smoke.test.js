import test from 'node:test';
import assert from 'node:assert';
import fs from 'node:fs';
import path from 'node:path';

test('KnowDoc Phase 1 Repository Integrity', () => {
  const rootDir = process.cwd();

  // Verify core directories exist
  const requiredDirs = [
    'frontend',
    'backend',
    'ai-service',
    'docs/requirements',
    'docs/architecture',
    'docs/api',
    'docs/database',
    'docs/security',
    'docs/deployment',
    'infra/docker',
    'infra/scripts',
    '.github/workflows'
  ];

  for (const dir of requiredDirs) {
    const fullPath = path.join(rootDir, dir);
    assert.ok(fs.existsSync(fullPath), `Directory missing: ${dir}`);
  }

  // Verify critical configuration files exist
  const requiredFiles = [
    '.env.example',
    '.gitignore',
    'README.md',
    'infra/docker-compose.yml',
    'infra/scripts/init-pgvector.sql',
    'docs/architecture/HLD.md',
    'docs/architecture/LLD.md',
    'docs/architecture/diagrams/system-architecture.mmd',
    'docs/architecture/diagrams/document-ingestion.mmd',
    'docs/architecture/diagrams/question-answering.mmd'
  ];

  for (const file of requiredFiles) {
    const fullPath = path.join(rootDir, file);
    assert.ok(fs.existsSync(fullPath), `File missing: ${file}`);
  }
});

