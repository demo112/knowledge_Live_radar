import { test as base } from '@playwright/test';
import { PyramidPage } from '../pages/pyramid.page';
import { PyramidDetailPage } from '../pages/pyramid-detail.page';
import { SourcesPage } from '../pages/sources.page';
import { ApprovalPage } from '../pages/approval.page';
import { SettingsPage } from '../pages/settings.page';
import { FeedPage } from '../pages/feed.page';

type MyFixtures = {
  pyramidPage: PyramidPage;
  pyramidDetailPage: PyramidDetailPage;
  sourcesPage: SourcesPage;
  approvalPage: ApprovalPage;
  settingsPage: SettingsPage;
  feedPage: FeedPage;
};

export const test = base.extend<MyFixtures>({
  pyramidPage: async ({ page }, use) => {
    await use(new PyramidPage(page));
  },
  pyramidDetailPage: async ({ page }, use) => {
    await use(new PyramidDetailPage(page));
  },
  sourcesPage: async ({ page }, use) => {
    await use(new SourcesPage(page));
  },
  approvalPage: async ({ page }, use) => {
    await use(new ApprovalPage(page));
  },
  settingsPage: async ({ page }, use) => {
    await use(new SettingsPage(page));
  },
  feedPage: async ({ page }, use) => {
    await use(new FeedPage(page));
  },
});
export { expect } from '@playwright/test';
