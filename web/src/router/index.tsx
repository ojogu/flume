import { createBrowserRouter, Navigate } from 'react-router-dom'
import { LandingPage } from '@/pages/LandingPage'
import { BotPage } from '@/pages/BotPage'
import { PricingPage } from '@/pages/PricingPage'
import { CallbackPage } from '@/pages/CallbackPage'
import { LoginPage } from '@/pages/LoginPage'
import { DashboardShell } from '@/pages/dashboard/DashboardShell'
import { JobsPage } from '@/pages/dashboard/JobsPage'
import { JobDetailPage } from '@/pages/dashboard/JobDetailPage'
import { ApiKeysPage } from '@/pages/dashboard/ApiKeysPage'
import { DocsPage } from '@/pages/DocsPage'

export const router = createBrowserRouter([
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
    element: <DocsPage />,
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
    ],
  },
  {
    path: '/callback',
    element: <CallbackPage />,
  },
])