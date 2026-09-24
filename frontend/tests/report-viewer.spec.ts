import { test, expect } from '@playwright/test';
import { execFileSync } from 'node:child_process';
import { mkdtempSync, readFileSync } from 'node:fs';
import { join, resolve } from 'node:path';
import { tmpdir } from 'node:os';
import { pathToFileURL } from 'node:url';

const root = resolve(import.meta.dirname, '../..');
let output: string;
let episodes: { task_id: string; profile: string; attack_id: string | null; episode_id: string }[];

test.beforeAll(() => {
  output = mkdtempSync(join(tmpdir(), 'agentguard-viewer-'));
  const result = JSON.parse(
    execFileSync(
      process.env.AGENTGUARD_PYTHON || join(root, '.venv/bin/python'),
      [join(root, 'frontend/tests/report_fixture.py'), root, output],
      { cwd: root, encoding: 'utf8', timeout: 20_000 },
    ),
  );
  episodes = JSON.parse(readFileSync(join(result.run, 'report.json'), 'utf8')).episodes;
});

test('every payload selects its matching pair; clean and task switches stay consistent', async ({
  page,
}) => {
  const errors: string[] = [];
  const network: string[] = [];
  page.on('pageerror', (error) => errors.push(error.message));
  page.on('request', (request) => {
    if (/^https?:/.test(request.url())) network.push(request.url());
  });
  await page.goto(pathToFileURL(join(output, 'multi/explorer.html')).href);
  const task = page.getByRole('combobox', { name: 'Task', exact: true });
  const input = page.getByRole('combobox', { name: 'Input', exact: true });
  const attack = page.getByRole('combobox', { name: 'Attack variant' });
  for (const taskId of ['review-multi-attack', 'launch-scope']) {
    await task.selectOption(taskId);
    const ids = episodes.filter((r) => r.task_id === taskId && r.profile === 'baseline');
    for (const row of ids) {
      await input.selectOption(row.attack_id === null ? 'clean' : 'attacked');
      if (row.attack_id === null) await expect(attack).toBeDisabled();
      else await attack.selectOption(row.attack_id);
      await expect(page.locator('#left')).toContainText(row.episode_id);
      const defended = episodes.find(
        (r) => r.task_id === taskId && r.profile === 'defended' && r.attack_id === row.attack_id,
      )!;
      await expect(page.locator('#right')).toContainText(defended.episode_id);
    }
  }
  await expect(attack.locator('option')).toHaveCount(1);
  await expect(attack).toHaveValue('primary');
  expect(errors).toEqual([]);
  expect(network).toEqual([]);
});

test('published legacy reports still select clean and attacked episodes', async ({ page }) => {
  await page.goto(pathToFileURL(join(output, 'legacy/explorer.html')).href);
  await expect(page.locator('#accounting')).toContainText('84 scheduled episodes');
  await expect(page.getByRole('combobox', { name: 'Attack variant' })).toHaveValue('primary');
  await expect(page.locator('#left')).toContainText('Episode ');
  await page.getByRole('combobox', { name: 'Input', exact: true }).selectOption('clean');
  await expect(page.getByRole('combobox', { name: 'Attack variant' })).toBeDisabled();
  await expect(page.locator('#right')).toContainText('Task passed');
});
