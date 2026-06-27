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
        url: '/docs',
        transparentMode: 'top',
        children: (
          <div className="flex items-center gap-3 ml-auto">
            <a 
              href="https://flume.ojogulabs.xyz/signup" 
              className="hidden md:flex items-center justify-center px-4 py-1.5 text-sm font-medium text-white bg-primary rounded-lg hover:bg-primary/90 transition-colors"
            >
              Start processing
            </a>
          </div>
        )
      }}
      links={[
        { url: 'https://flume.ojogulabs.xyz/dashboard', text: 'Dashboard' },
        { url: 'mailto:hello@ojogulabs.xyz', text: 'Support' },
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
