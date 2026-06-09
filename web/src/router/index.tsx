import { createBrowserRouter } from 'react-router-dom'
import { LandingPage } from '@/pages/LandingPage'
import { BotPage } from '@/pages/BotPage'
import { PricingPage } from '@/pages/PricingPage'
import { CallbackPage } from '@/pages/CallbackPage'
import { LoginPage } from '@/pages/LoginPage'
import { DashboardPage } from '@/pages/DashboardPage'

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
    path: '/login',
    element: <LoginPage />,
  },
  {
    path: '/dashboard',
    element: <DashboardPage />,
  },
  {
    path: '/callback',
    element: <CallbackPage />,
  },
])