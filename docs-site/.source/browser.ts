// @ts-nocheck
import { browser } from 'fumadocs-mdx/runtime/browser';
import type * as Config from '../source.config';

const create = browser<typeof Config, import("fumadocs-mdx/runtime/types").InternalTypeConfig & {
  DocData: {
  }
}>();
const browserCollections = {
  docs: create.doc("docs", {"changelog.mdx": () => import("../content/docs/changelog.mdx?collection=docs"), "core-concepts.mdx": () => import("../content/docs/core-concepts.mdx?collection=docs"), "errors.mdx": () => import("../content/docs/errors.mdx?collection=docs"), "index.mdx": () => import("../content/docs/index.mdx?collection=docs"), "pagination.mdx": () => import("../content/docs/pagination.mdx?collection=docs"), "rate-limits.mdx": () => import("../content/docs/rate-limits.mdx?collection=docs"), "versioning.mdx": () => import("../content/docs/versioning.mdx?collection=docs"), "api-reference/index.mdx": () => import("../content/docs/api-reference/index.mdx?collection=docs"), "authentication/api-keys.mdx": () => import("../content/docs/authentication/api-keys.mdx?collection=docs"), "authentication/index.mdx": () => import("../content/docs/authentication/index.mdx?collection=docs"), "authentication/rotating-keys.mdx": () => import("../content/docs/authentication/rotating-keys.mdx?collection=docs"), "webhooks/delivery.mdx": () => import("../content/docs/webhooks/delivery.mdx?collection=docs"), "webhooks/event-catalog.mdx": () => import("../content/docs/webhooks/event-catalog.mdx?collection=docs"), "webhooks/index.mdx": () => import("../content/docs/webhooks/index.mdx?collection=docs"), "webhooks/payload.mdx": () => import("../content/docs/webhooks/payload.mdx?collection=docs"), "webhooks/security.mdx": () => import("../content/docs/webhooks/security.mdx?collection=docs"), "webhooks/subscriptions.mdx": () => import("../content/docs/webhooks/subscriptions.mdx?collection=docs"), "webhooks/testing.mdx": () => import("../content/docs/webhooks/testing.mdx?collection=docs"), "api-reference/health/root_root_get.mdx": () => import("../content/docs/api-reference/health/root_root_get.mdx?collection=docs"), }),
};
export default browserCollections;