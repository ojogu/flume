import { createBrowserRouter, Navigate } from 'react-router-dom'
import { LandingPage } from '@/pages/LandingPage'
import { BotPage } from '@/pages/BotPage'
import { PricingPage } from '@/pages/PricingPage'
import { CallbackPage } from '@/pages/CallbackPage'
import { LoginPage } from '@/pages/LoginPage'
import { NotFoundPage } from '@/pages/NotFoundPage'
import { ErrorPage } from '@/pages/ErrorPage'
import { DashboardShell } from '@/pages/dashboard/DashboardShell'
import { JobsPage } from '@/pages/dashboard/JobsPage'
import { JobDetailPage } from '@/pages/dashboard/JobDetailPage'
import { ApiKeysPage } from '@/pages/dashboard/ApiKeysPage'
import { WebhooksPage } from '@/pages/dashboard/WebhooksPage'
export const router = createBrowserRouter([
  {
    errorElement: <ErrorPage />,
    children: [
      {
        path: '/',
        element: <LandingPage />,
      },
      {
        path: '/bot',
        element: <BotPage />,
      },
      {
        path: '/pricing',
        element: <PricingPage />,
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