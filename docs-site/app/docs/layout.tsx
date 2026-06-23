import { DocsLayout } from 'fumadocs-ui/layouts/docs';
import type { ReactNode } from 'react';
import { source } from '@/app/source';
import { Wordmark } from '@/components/common/Wordmark';

export default function Layout({ children }: { children: ReactNode }) {
  return (
    <DocsLayout
      tree={source.pageTree}
      nav={{
        title: <Wordmark className="h-6" />,
        url: '/',
      }}
      links={[
        { url: '/', text: 'Dashboard' },
      ]}
      sidebar={{
        defaultOpenLevel: 1,
        collapsible: true,
      }}
    >
      {children}
    </DocsLayout>
  );
}
