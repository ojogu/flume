import type { MDXComponents } from 'mdx/types';
import defaultComponents from 'fumadocs-ui/mdx';
import { createOpenAPI } from 'fumadocs-openapi/server';

const { APIPage } = createOpenAPI();

export function useMDXComponents(components: MDXComponents): MDXComponents {
  return {
    ...defaultComponents,
    APIPage,
    ...components,
  };
}
