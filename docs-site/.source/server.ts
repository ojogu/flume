// @ts-nocheck
import { default as __fd_glob_23 } from "../content/docs/api-reference/health/meta.json?collection=meta"
import { default as __fd_glob_22 } from "../content/docs/webhooks/meta.json?collection=meta"
import { default as __fd_glob_21 } from "../content/docs/authentication/meta.json?collection=meta"
import { default as __fd_glob_20 } from "../content/docs/api-reference/meta.json?collection=meta"
import { default as __fd_glob_19 } from "../content/docs/meta.json?collection=meta"
import * as __fd_glob_18 from "../content/docs/api-reference/health/root_root_get.mdx?collection=docs"
import * as __fd_glob_17 from "../content/docs/webhooks/testing.mdx?collection=docs"
import * as __fd_glob_16 from "../content/docs/webhooks/subscriptions.mdx?collection=docs"
import * as __fd_glob_15 from "../content/docs/webhooks/security.mdx?collection=docs"
import * as __fd_glob_14 from "../content/docs/webhooks/payload.mdx?collection=docs"
import * as __fd_glob_13 from "../content/docs/webhooks/index.mdx?collection=docs"
import * as __fd_glob_12 from "../content/docs/webhooks/event-catalog.mdx?collection=docs"
import * as __fd_glob_11 from "../content/docs/webhooks/delivery.mdx?collection=docs"
import * as __fd_glob_10 from "../content/docs/authentication/rotating-keys.mdx?collection=docs"
import * as __fd_glob_9 from "../content/docs/authentication/index.mdx?collection=docs"
import * as __fd_glob_8 from "../content/docs/authentication/api-keys.mdx?collection=docs"
import * as __fd_glob_7 from "../content/docs/api-reference/index.mdx?collection=docs"
import * as __fd_glob_6 from "../content/docs/versioning.mdx?collection=docs"
import * as __fd_glob_5 from "../content/docs/rate-limits.mdx?collection=docs"
import * as __fd_glob_4 from "../content/docs/pagination.mdx?collection=docs"
import * as __fd_glob_3 from "../content/docs/index.mdx?collection=docs"
import * as __fd_glob_2 from "../content/docs/errors.mdx?collection=docs"
import * as __fd_glob_1 from "../content/docs/core-concepts.mdx?collection=docs"
import * as __fd_glob_0 from "../content/docs/changelog.mdx?collection=docs"
import { server } from 'fumadocs-mdx/runtime/server';
import type * as Config from '../source.config';

const create = server<typeof Config, import("fumadocs-mdx/runtime/types").InternalTypeConfig & {
  DocData: {
  }
}>({"doc":{"passthroughs":["extractedReferences"]}});

export const docs = await create.doc("docs", "content/docs", {"changelog.mdx": __fd_glob_0, "core-concepts.mdx": __fd_glob_1, "errors.mdx": __fd_glob_2, "index.mdx": __fd_glob_3, "pagination.mdx": __fd_glob_4, "rate-limits.mdx": __fd_glob_5, "versioning.mdx": __fd_glob_6, "api-reference/index.mdx": __fd_glob_7, "authentication/api-keys.mdx": __fd_glob_8, "authentication/index.mdx": __fd_glob_9, "authentication/rotating-keys.mdx": __fd_glob_10, "webhooks/delivery.mdx": __fd_glob_11, "webhooks/event-catalog.mdx": __fd_glob_12, "webhooks/index.mdx": __fd_glob_13, "webhooks/payload.mdx": __fd_glob_14, "webhooks/security.mdx": __fd_glob_15, "webhooks/subscriptions.mdx": __fd_glob_16, "webhooks/testing.mdx": __fd_glob_17, "api-reference/health/root_root_get.mdx": __fd_glob_18, });

export const meta = await create.meta("meta", "content/docs", {"meta.json": __fd_glob_19, "api-reference/meta.json": __fd_glob_20, "authentication/meta.json": __fd_glob_21, "webhooks/meta.json": __fd_glob_22, "api-reference/health/meta.json": __fd_glob_23, });