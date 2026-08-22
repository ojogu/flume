import { createBrowserRouter, Navigate } from 'react-router-dom'
import { LandingPage } from '@/pages/LandingPage'
import { BotPage } from '@/pages/BotPage'
import { BotBlockedPage } from '@/pages/BotBlockedPage'
import { PricingPage } from '@/pages/PricingPage'
import { PricingBlockedPage } from '@/pages/PricingBlockedPage'
import { WebPage } from '@/pages/WebPage'
import { WebHistoryPage } from '@/pages/WebHistoryPage'
import { CallbackPage } from '@/pages/CallbackPage'
import { LoginPage } from '@/pages/LoginPage'
import { NotFoundPage } from '@/pages/NotFoundPage'
import { ErrorPage } from '@/pages/ErrorPage'
import { DashboardShell } from '@/pages/dashboard/DashboardShell'
import { DashboardErrorPage } from '@/pages/dashboard/DashboardErrorPage'
import { DashboardNotFoundPage } from '@/pages/dashboard/DashboardNotFoundPage'
import { JobsPage } from '@/pages/dashboard/JobsPage'
import { JobDetailPage } from '@/pages/dashboard/JobDetailPage'
import { ApiKeysPage } from '@/pages/dashboard/ApiKeysPage'
import { WebhooksPage } from '@/pages/dashboard/WebhooksPage'
import { WebhookDetailPage } from '@/pages/dashboard/WebhookDetailPage'
import { PlatformsPage } from '@/pages/dashboard/PlatformsPage'
import { SupportPage } from '@/pages/dashboard/SupportPage'
import { AdminShell } from '@/pages/admin/AdminShell'
import { AdminLoginPage } from '@/pages/admin/AdminLoginPage'
import { AdminPlatformsPage } from '@/pages/admin/AdminPlatformsPage'
import { AdminStatsPage } from '@/pages/admin/AdminStatsPage'
import { PRICING_BLOCKED } from '@/lib/pricing'
import { BOT_BLOCKED } from '@/lib/bot'

export const router = createBrowserRouter([
  {
    errorElement: <ErrorPage />,
    children: [
      {
        path: '/',
        element: <LandingPage />,
      },
      {
        path: '/web',
        element: <WebPage />,
      },
      {
        path: '/web/history',
        element: <WebHistoryPage />,
      },
      {
        path: '/bot',
        element: BOT_BLOCKED ? <BotBlockedPage /> : <BotPage />,
      },
      {
        path: '/pricing',
        element: PRICING_BLOCKED ? <PricingBlockedPage /> : <PricingPage />,
      },
      {
        path: '/api',
        element: <Navigate to="/dashboard" replace />,
      },
      {
        path: '/login',
        element: <LoginPage />,
      },
      {
        path: '/dashboard',
        element: <DashboardShell />,
        errorElement: <DashboardErrorPage />,
        children: [
          {
            index: true,
            element: <Navigate to="jobs" replace />,
          },
          {
            path: 'jobs',
            element: <JobsPage />,
          },
          {
            path: 'jobs/:id',
            element: <JobDetailPage />,
          },
          {
            path: 'keys',
            element: <ApiKeysPage />,
          },
          {
            path: 'webhooks',
            element: <WebhooksPage />,
          },
          {
            path: 'webhooks/:id',
            element: <WebhookDetailPage />,
          },
          {
            path: 'platforms',
            element: <PlatformsPage />,
          },
          {
            path: 'support',
            element: <SupportPage />,
          },
          {
            path: '*',
            element: <DashboardNotFoundPage />,
          },
        ],
      },
      {
        path: '/admin',
        children: [
          {
            path: 'login',
            element: <AdminLoginPage />,
          },
          {
            element: <AdminShell />,
            children: [
              {
                index: true,
                element: <Navigate to="platforms" replace />,
              },
              {
                path: 'platforms',
                element: <AdminPlatformsPage />,
              },
              {
                path: 'stats',
                element: <AdminStatsPage />,
              },
            ],
          },
        ],
      },
      {
        path: '/callback',
        element: <CallbackPage />,
      },
      {
        path: '*',
        element: <NotFoundPage />,
      },
    ],
  },
])