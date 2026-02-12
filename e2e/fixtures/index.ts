import { test as base } from '@playwright/test';
import { PyramidPage } from '../pages/pyramid.page';
import { SourcesPage } from '../pages/sources.page';

type MyFixtures = {
  pyramidPage: PyramidPage;
  sourcesPage: SourcesPage;
};

export const test = base.extend<MyFixtures>({
  pyramidPage: async ({ page }, use) => {
    await use(new PyramidPage(page));
  },
  sourcesPage: async ({ page }, use) => {
    await use(new SourcesPage(page));
  },
});
export { expect } from '@playwright/test';
